"""Pix Engine - Gerador de Payload EMV-Co e QR Code compatível com o Banco Central do Brasil."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional
import qrcode
from PIL import Image


def remove_accents(text: str) -> str:
    """Remove acentos e caracteres não ASCII."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def sanitize_merchant_name(name: str, max_len: int = 25) -> str:
    """Sanitiza o nome do beneficiário conforme norma BACEN (max 25 caracteres, maiúsculas, sem acento)."""
    clean = remove_accents(name).strip().upper()
    clean = re.sub(r"[^A-Z0-9 ]", "", clean)
    clean = re.sub(r"\s+", " ", clean)
    return clean[:max_len]


def sanitize_merchant_city(city: str, max_len: int = 15) -> str:
    """Sanitiza a cidade do beneficiário conforme norma BACEN (max 15 caracteres, maiúsculas, sem acento)."""
    clean = remove_accents(city).strip().upper()
    clean = re.sub(r"[^A-Z0-9 ]", "", clean)
    clean = re.sub(r"\s+", " ", clean)
    return clean[:max_len]


def sanitize_txid(txid: Optional[str], max_len: int = 25) -> str:
    """Sanitiza o identificador da transação (TxID). Se vazio, retorna '***'."""
    if not txid or not txid.strip():
        return "***"
    clean = remove_accents(txid).strip()
    clean = re.sub(r"[^A-Za-z0-9]", "", clean)
    return clean[:max_len] or "***"


def sanitize_pix_key(key: str) -> str:
    """Limpa a chave pix (se for CPF/CNPJ ou telefone, remove pontuação)."""
    raw = key.strip()
    # Se for e-mail, mantém formato
    if "@" in raw:
        return raw.lower()
    # Se contiver apenas dígitos e pontuações comuns de CPF/CNPJ/Telefone, mantém apenas números
    digits_only = re.sub(r"\D", "", raw)
    if len(digits_only) in (11, 14):  # CPF ou CNPJ
        return digits_only
    if len(digits_only) in (10, 11) and not any(c.isalpha() for c in raw):  # Telefone
        # Se for telefone sem código do país, adiciona +55 se necessário ou mantém digits
        return raw
    # Chave aleatória (UUID) ou outro formato
    return raw


def format_tlv(tag: str, value: str) -> str:
    """Formata um campo no padrão TLV (Tag-Length-Value)."""
    length = len(value.encode("utf-8"))
    return f"{tag:0>2}{length:0>2}{value}"


def calculate_crc16(payload: str) -> str:
    """Calcula o CRC16-CCITT (Polinômio 0x1021, valor inicial 0xFFFF)."""
    crc = 0xFFFF
    for byte in payload.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


@dataclass
class PixCharge:
    pix_key: str
    merchant_name: str
    merchant_city: str
    amount: Optional[float] = None
    txid: Optional[str] = None
    description: Optional[str] = None

    def build_payload(self) -> str:
        """Monta o payload completo do Pix (Copia e Cola)."""
        clean_key = sanitize_pix_key(self.pix_key)
        name = sanitize_merchant_name(self.merchant_name)
        city = sanitize_merchant_city(self.merchant_city)
        ref_txid = sanitize_txid(self.txid)

        # 00: Payload Format Indicator
        p_00 = format_tlv("00", "01")

        # 26: Merchant Account Information
        gui = format_tlv("00", "br.gov.bcb.pix")
        key = format_tlv("01", clean_key)
        sub_26 = gui + key
        if self.description:
            # Descrição adicional (opcional no campo 26 subtag 02)
            desc_clean = remove_accents(self.description).strip()[:40]
            if desc_clean:
                sub_26 += format_tlv("02", desc_clean)
        p_26 = format_tlv("26", sub_26)

        # 52: Merchant Category Code
        p_52 = format_tlv("52", "0000")

        # 53: Transaction Currency (986 = Real BRL)
        p_53 = format_tlv("53", "986")

        # 54: Transaction Amount (opcional se não fornecido ou zero)
        p_54 = ""
        if self.amount is not None and self.amount > 0:
            formatted_amount = f"{self.amount:.2f}"
            p_54 = format_tlv("54", formatted_amount)

        # 58: Country Code
        p_58 = format_tlv("58", "BR")

        # 59: Merchant Name
        p_59 = format_tlv("59", name)

        # 60: Merchant City
        p_60 = format_tlv("60", city)

        # 62: Additional Data Field Template
        sub_62 = format_tlv("05", ref_txid)
        p_62 = format_tlv("62", sub_62)

        # Junção parcial sem CRC
        raw_payload = p_00 + p_26 + p_52 + p_53 + p_54 + p_58 + p_59 + p_60 + p_62

        # 63: CRC16 com tag 63 e tamanho 04
        crc_prefix = raw_payload + "6304"
        crc_value = calculate_crc16(crc_prefix)

        return crc_prefix + crc_value

    def generate_qr_code_image(
        self,
        box_size: int = 10,
        border: int = 2,
        fill_color: str = "#0F172A",
        back_color: str = "#FFFFFF",
    ) -> Image.Image:
        """Gera a imagem PIL do QR Code a partir do payload Pix."""
        payload = self.build_payload()
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        return img.convert("RGB")
