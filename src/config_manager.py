"""Gerenciador de configurações e preferências persistidas do aplicativo."""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Any, Dict, Tuple

DEFAULT_CONFIG: Dict[str, Any] = {
    "beneficiary_name": "",
    "pix_key": "",
    "city": "",
    "theme": "Dark",
    "default_description": "",
}


def get_default_config_path() -> str:
    """Retorna o caminho padrão para o arquivo config.json."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.json")


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Carrega as configurações salvas ou retorna os valores padrão."""
    path = config_path or get_default_config_path()
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG, path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(data: Dict[str, Any], config_path: str | None = None) -> bool:
    """Salva as configurações no arquivo json."""
    path = config_path or get_default_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def reset_config(config_path: str | None = None) -> Dict[str, Any]:
    """Restaura as configurações para o padrão inicial limpo e salva no arquivo."""
    path = config_path or get_default_config_path()
    clean_config = DEFAULT_CONFIG.copy()
    save_config(clean_config, path)
    return clean_config


def is_config_valid(config: Dict[str, Any] | None) -> bool:
    """Verifica se os dados essenciais do recebedor (nome, chave e cidade) estão preenchidos."""
    if not config:
        return False
    name = str(config.get("beneficiary_name", "")).strip()
    key = str(config.get("pix_key", "")).strip()
    city = str(config.get("city", "")).strip()
    return bool(name and key and city)


def validate_pix_key_type(key: str) -> Tuple[bool, str, str]:
    """Identifica o tipo de chave Pix e valida o formato básico.

    Retorna: (é_valido, tipo_detectado, mensagem_erro_se_houver)
    """
    raw = key.strip()
    if not raw:
        return False, "Vazio", "A chave Pix não pode estar vazia."

    # E-mail: contém @ e pelo menos um ponto no domínio
    if "@" in raw:
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if re.match(email_pattern, raw):
            return True, "E-mail", ""
        return False, "E-mail", "Formato de e-mail inválido (ex: recebedor@exemplo.com)."

    # Chave Aleatória (UUID / EVP: 8-4-4-4-12 caracteres hexadecimais)
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if re.match(uuid_pattern, raw):
        return True, "Chave Aleatória (EVP)", ""

    # Chave aleatória sem hífens (32 hex)
    if len(raw) == 32 and re.match(r"^[0-9a-fA-F]{32}$", raw):
        return True, "Chave Aleatória (EVP)", ""

    digits = re.sub(r"\D", "", raw)

    # Telefone internacional (+55...)
    if raw.startswith("+"):
        if len(digits) in (12, 13) and digits.startswith("55"):
            return True, "Telefone", ""
        return False, "Telefone", "Número com código do país inválido (ex: +5511999999999)."

    # CPF (11 dígitos)
    if len(digits) == 11 and not any(c.isalpha() for c in raw):
        return True, "CPF / Celular", ""

    # CNPJ (14 dígitos)
    if len(digits) == 14 and not any(c.isalpha() for c in raw):
        return True, "CNPJ", ""

    # Telefone fixo nacional (10 dígitos)
    if len(digits) == 10 and not any(c.isalpha() for c in raw):
        return True, "Telefone", ""

    return False, "Desconhecido", "Chave inválida. Use CPF, CNPJ, Celular com DDD, E-mail ou Chave Aleatória."


def format_pix_key_display(key: str) -> str:
    """Formata a chave para exibição visual amigável (CPF, CNPJ, Telefone, etc)."""
    if not key or not key.strip():
        return "Não configurada"

    raw = key.strip()
    digits = re.sub(r"\D", "", raw)

    if "@" in raw:
        return raw.lower()

    if len(digits) == 11 and not any(c.isalpha() for c in raw):
        # Se parece celular (DDD + 9 dígitos começando com 9)
        if len(raw) == 11 and raw[2] == "9":
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        # CPF: 000.000.000-00
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    elif len(digits) == 14:
        # CNPJ: 00.000.000/0000-00
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    elif len(digits) == 10 and not any(c.isalpha() for c in raw):
        # Telefone fixo: (00) 0000-0000
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

    return raw
