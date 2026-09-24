"""Testes unitários para os módulos pix_engine e config_manager."""

import unittest
from src.config_manager import (
    format_pix_key_display,
    is_config_valid,
    reset_config,
    validate_pix_key_type,
)
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
        self.assertEqual(remove_accents("São Paulo"), "Sao Paulo")
        self.assertEqual(remove_accents("Brasília"), "Brasilia")
        self.assertEqual(remove_accents("Ação & Reação"), "Acao & Reacao")

    def test_sanitize_merchant_name(self):
        name = "TechZone Sistemas LTDA"
        sanitized = sanitize_merchant_name(name)
        self.assertEqual(sanitized, "TECHZONE SISTEMAS LTDA")
        self.assertLessEqual(len(sanitized), 25)

        # Nome muito longo (deve cortar em 25)
        long_name = "Super Empresa de Servicos de Tecnologia e Pagamentos LTDA"
        self.assertEqual(len(sanitize_merchant_name(long_name)), 25)

    def test_sanitize_merchant_city(self):
        city = "São Paulo"
        sanitized = sanitize_merchant_city(city)
        self.assertEqual(sanitized, "SAO PAULO")
        self.assertLessEqual(len(sanitized), 15)

    def test_sanitize_txid(self):
        self.assertEqual(sanitize_txid(""), "***")
        self.assertEqual(sanitize_txid(None), "***")
        self.assertEqual(sanitize_txid("PEDIDO123"), "PEDIDO123")
        self.assertEqual(sanitize_txid("pedido 123!"), "pedido123")

    def test_sanitize_pix_key(self):
        self.assertEqual(sanitize_pix_key("123.456.789-00"), "12345678900")
        self.assertEqual(sanitize_pix_key(" 12345678900 "), "12345678900")
        self.assertEqual(sanitize_pix_key("contato@empresa.com"), "contato@empresa.com")
        self.assertEqual(
            sanitize_pix_key(" contato@empresa.com "), "contato@empresa.com"
        )

    def test_format_tlv(self):
        self.assertEqual(format_tlv("00", "01"), "000201")
        self.assertEqual(format_tlv("58", "BR"), "5802BR")

    def test_crc16_standard_vector(self):
        # O vetor padrão CRC16-CCITT (0x1021, init 0xFFFF) para '123456789' é 0x29B1
        self.assertEqual(calculate_crc16("123456789"), "29B1")

    def test_pix_charge_payload_structure(self):
        charge = PixCharge(
            pix_key="12345678900",
            merchant_name="Empresa Exemplo LTDA",
            merchant_city="Sao Paulo",
            amount=50.00,
            txid="TESTE01",
        )
        payload = charge.build_payload()

        # Deve iniciar com '000201'
        self.assertTrue(payload.startswith("000201"))
        # Deve conter a chave
        self.assertIn("12345678900", payload)
        # Deve conter o identificador BACEN Pix
        self.assertIn("br.gov.bcb.pix", payload)
        # Deve conter o nome sem acento
        self.assertIn("EMPRESA EXEMPLO LTDA", payload)
        # Deve conter a cidade
        self.assertIn("SAO PAULO", payload)
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
            pix_key="12345678900",
            merchant_name="Empresa Exemplo LTDA",
            merchant_city="Sao Paulo",
            amount=0.0,
        )
        payload = charge.build_payload()
        # Não deve incluir a tag 54 quando o valor for 0 ou None
        self.assertNotIn("540", payload)
        self.assertIn("62070503***", payload)  # TxID default ***

    def test_qr_code_generation(self):
        charge = PixCharge(
            pix_key="12345678900",
            merchant_name="Empresa Exemplo LTDA",
            merchant_city="Sao Paulo",
            amount=25.50,
        )
        img = charge.generate_qr_code_image()
        self.assertIsNotNone(img)
        self.assertEqual(img.mode, "RGB")
        self.assertGreater(img.width, 100)
        self.assertGreater(img.height, 100)

    def test_pix_charge_with_custom_email_key(self):
        charge = PixCharge(
            pix_key="pagamentos@minhaloja.com.br",
            merchant_name="Minha Loja Online",
            merchant_city="Rio de Janeiro",
            amount=99.90,
        )
        payload = charge.build_payload()
        self.assertIn("pagamentos@minhaloja.com.br", payload)
        self.assertIn("MINHA LOJA ONLINE", payload)
        self.assertIn("RIO DE JANEIRO", payload)
        self.assertIn("540599.90", payload)
        self.assertTrue(payload.startswith("000201"))
        self.assertRegex(payload, r"6304[0-9A-F]{4}$")
        content_for_crc = payload[:-4]
        self.assertEqual(payload[-4:], calculate_crc16(content_for_crc))


class TestConfigManager(unittest.TestCase):

    def test_is_config_valid(self):
        # Vazio ou incompleto
        self.assertFalse(is_config_valid(None))
        self.assertFalse(is_config_valid({}))
        self.assertFalse(is_config_valid({"beneficiary_name": "Teste", "pix_key": "", "city": ""}))
        self.assertFalse(is_config_valid({"beneficiary_name": "Teste", "pix_key": "123", "city": ""}))

        # Válido com os 3 campos essenciais
        self.assertTrue(
            is_config_valid({
                "beneficiary_name": "Empresa LTDA",
                "pix_key": "empresa@teste.com",
                "city": "São Paulo",
            })
        )

    def test_validate_pix_key_type(self):
        # Vazio
        valid, tipo, err = validate_pix_key_type("")
        self.assertFalse(valid)
        self.assertEqual(tipo, "Vazio")

        # E-mail
        valid, tipo, err = validate_pix_key_type("financeiro@loja.com")
        self.assertTrue(valid)
        self.assertEqual(tipo, "E-mail")

        valid, tipo, err = validate_pix_key_type("invalido@")
        self.assertFalse(valid)

        # CPF
        valid, tipo, err = validate_pix_key_type("123.456.789-01")
        self.assertTrue(valid)

        # CNPJ
        valid, tipo, err = validate_pix_key_type("12.345.678/0001-90")
        self.assertTrue(valid)
        self.assertEqual(tipo, "CNPJ")

        # Telefone
        valid, tipo, err = validate_pix_key_type("+5511999998888")
        self.assertTrue(valid)
        self.assertEqual(tipo, "Telefone")

        # EVP / Chave Aleatória
        valid, tipo, err = validate_pix_key_type("123e4567-e89b-12d3-a456-426614174000")
        self.assertTrue(valid)
        self.assertEqual(tipo, "Chave Aleatória (EVP)")

    def test_format_pix_key_display(self):
        self.assertEqual(format_pix_key_display(""), "Não configurada")
        self.assertEqual(format_pix_key_display("teste@email.com"), "teste@email.com")
        self.assertEqual(format_pix_key_display("12345678901"), "123.456.789-01")
        self.assertEqual(format_pix_key_display("12345678000195"), "12.345.678/0001-95")


if __name__ == "__main__":
    unittest.main()
