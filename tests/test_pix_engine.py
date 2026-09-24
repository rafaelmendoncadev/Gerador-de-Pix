"""Testes unitários para o módulo pix_engine."""

import unittest
from src.pix_engine import (
    PixCharge,
    calculate_crc16,
    format_tlv,
    remove_accents,
    sanitize_merchant_city,
    sanitize_merchant_name,
    sanitize_pix_key,
    sanitize_txid,
)


class TestPixEngine(unittest.TestCase):

    def test_remove_accents(self):
        self.assertEqual(remove_accents("Mendonça"), "Mendonca")
        self.assertEqual(remove_accents("Brasília"), "Brasilia")
        self.assertEqual(remove_accents("Ação & Reação"), "Acao & Reacao")

    def test_sanitize_merchant_name(self):
        name = "Rafael Vieira de Mendonça"
        sanitized = sanitize_merchant_name(name)
        self.assertEqual(sanitized, "RAFAEL VIEIRA DE MENDONCA")
        self.assertLessEqual(len(sanitized), 25)

        # Nome muito longo (deve cortar em 25)
        long_name = "Rafael Vieira de Mendonca da Silva Santos"
        self.assertEqual(len(sanitize_merchant_name(long_name)), 25)

    def test_sanitize_merchant_city(self):
        city = "Brasília"
        sanitized = sanitize_merchant_city(city)
        self.assertEqual(sanitized, "BRASILIA")
        self.assertLessEqual(len(sanitized), 15)

    def test_sanitize_txid(self):
        self.assertEqual(sanitize_txid(""), "***")
        self.assertEqual(sanitize_txid(None), "***")
        self.assertEqual(sanitize_txid("PEDIDO123"), "PEDIDO123")
        self.assertEqual(sanitize_txid("pedido 123!"), "pedido123")

    def test_sanitize_pix_key(self):
        self.assertEqual(sanitize_pix_key("601.903.701-06"), "60190370106")
        self.assertEqual(sanitize_pix_key(" 60190370106 "), "60190370106")
        self.assertEqual(sanitize_pix_key("email@exemplo.com"), "email@exemplo.com")
        self.assertEqual(
            sanitize_pix_key(" techzonesistemas@gmail.com "), "techzonesistemas@gmail.com"
        )

    def test_format_tlv(self):
        self.assertEqual(format_tlv("00", "01"), "000201")
        self.assertEqual(format_tlv("58", "BR"), "5802BR")

    def test_crc16_standard_vector(self):
        # O vetor padrão CRC16-CCITT (0x1021, init 0xFFFF) para '123456789' é 0x29B1
        self.assertEqual(calculate_crc16("123456789"), "29B1")

    def test_pix_charge_payload_structure(self):
        charge = PixCharge(
            pix_key="60190370106",
            merchant_name="Rafael Vieira de Mendonça",
            merchant_city="Brasília",
            amount=50.00,
            txid="TESTE01",
        )
        payload = charge.build_payload()

        # Deve iniciar com '000201'
        self.assertTrue(payload.startswith("000201"))
        # Deve conter a chave
        self.assertIn("60190370106", payload)
        # Deve conter o identificador BACEN Pix
        self.assertIn("br.gov.bcb.pix", payload)
        # Deve conter o nome sem acento
        self.assertIn("RAFAEL VIEIRA DE MENDONCA", payload)
        # Deve conter a cidade
        self.assertIn("BRASILIA", payload)
        # Deve conter o valor formatado
        self.assertIn("540550.00", payload)
        # Deve conter o TxID
        self.assertIn("TESTE01", payload)
        # Deve terminar com 6304 + 4 caracteres hexadecimais
        self.assertRegex(payload, r"6304[0-9A-F]{4}$")

        # Verificação do próprio CRC do payload
        content_for_crc = payload[:-4]
        expected_crc = calculate_crc16(content_for_crc)
        self.assertEqual(payload[-4:], expected_crc)

    def test_pix_charge_without_amount(self):
        charge = PixCharge(
            pix_key="60190370106",
            merchant_name="Rafael Vieira de Mendonça",
            merchant_city="Brasília",
            amount=0.0,
        )
        payload = charge.build_payload()
        # Não deve incluir a tag 54 quando o valor for 0 ou None
        self.assertNotIn("540", payload)
        self.assertIn("62070503***", payload)  # TxID default ***

    def test_qr_code_generation(self):
        charge = PixCharge(
            pix_key="60190370106",
            merchant_name="Rafael Vieira de Mendonça",
            merchant_city="Brasília",
            amount=25.50,
        )
        img = charge.generate_qr_code_image()
        self.assertIsNotNone(img)
        self.assertEqual(img.mode, "RGB")
        self.assertGreater(img.width, 100)
    def test_pix_charge_with_techzone_email(self):
        charge = PixCharge(
            pix_key="techzonesistemas@gmail.com",
            merchant_name="Rafael Vieira de Mendonça",
            merchant_city="Brasília",
            amount=15.00,
        )
        payload = charge.build_payload()
        self.assertIn("techzonesistemas@gmail.com", payload)
        self.assertIn("RAFAEL VIEIRA DE MENDONCA", payload)
        self.assertIn("BRASILIA", payload)
        self.assertIn("540515.00", payload)
        self.assertTrue(payload.startswith("000201"))
        self.assertRegex(payload, r"6304[0-9A-F]{4}$")
        content_for_crc = payload[:-4]
        self.assertEqual(payload[-4:], calculate_crc16(content_for_crc))


if __name__ == "__main__":
    unittest.main()
