package com.techzone.geradorpix.engine

data class ValidationResult(
    val isValid: Boolean,
    val type: String,
    val errorMessage: String = ""
)

object PixKeyValidator {

    fun validate(key: String): ValidationResult {
        val raw = key.trim()
        if (raw.isEmpty()) {
            return ValidationResult(false, "Vazio", "A chave Pix não pode estar vazia.")
        }

        // E-mail
        if (raw.contains("@")) {
            val emailRegex = Regex("^[\\w.-]+@[\\w.-]+\\.\\w{2,}$")
            return if (emailRegex.matches(raw)) {
                ValidationResult(true, "E-mail")
            } else {
                ValidationResult(false, "E-mail", "Formato de e-mail inválido (ex: contato@empresa.com).")
            }
        }

        // Chave Aleatória (UUID / EVP)
        val uuidRegex = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
        if (uuidRegex.matches(raw)) {
            return ValidationResult(true, "Chave Aleatória (EVP)")
        }

        if (raw.length == 32 && Regex("^[0-9a-fA-F]{32}$").matches(raw)) {
            return ValidationResult(true, "Chave Aleatória (EVP)")
        }

        val digits = raw.replace(Regex("\\D"), "")

        // Telefone internacional com +55
        if (raw.startsWith("+")) {
            return if ((digits.length == 12 || digits.length == 13) && digits.startsWith("55")) {
                ValidationResult(true, "Telefone")
            } else {
                ValidationResult(false, "Telefone", "Telefone internacional inválido (ex: +5511999999999).")
            }
        }

        // CPF (11 dígitos)
        if (digits.length == 11 && !raw.any { it.isLetter() }) {
            return ValidationResult(true, "CPF / Celular")
        }

        // CNPJ (14 dígitos)
        if (digits.length == 14 && !raw.any { it.isLetter() }) {
            return ValidationResult(true, "CNPJ")
        }

        // Telefone fixo (10 dígitos)
        if (digits.length == 10 && !raw.any { it.isLetter() }) {
            return ValidationResult(true, "Telefone")
        }

        return ValidationResult(
            false,
            "Desconhecido",
            "Chave Pix inválida. Use CPF, CNPJ, Celular, E-mail ou Chave Aleatória."
        )
    }

    fun formatDisplay(key: String): String {
        val raw = key.trim()
        if (raw.isEmpty()) return "Não configurada"
        if (raw.contains("@")) return raw.lowercase()

        val digits = raw.replace(Regex("\\D"), "")
        return when {
            digits.length == 11 && digits.length >= 3 && digits[2] == '9' ->
                "(${digits.substring(0, 2)}) ${digits.substring(2, 7)}-${digits.substring(7)}"
            digits.length == 11 ->
                "${digits.substring(0, 3)}.${digits.substring(3, 6)}.${digits.substring(6, 9)}-${digits.substring(9)}"
            digits.length == 14 ->
                "${digits.substring(0, 2)}.${digits.substring(2, 5)}.${digits.substring(5, 8)}/${digits.substring(8, 12)}-${digits.substring(12)}"
            digits.length == 10 ->
                "(${digits.substring(0, 2)}) ${digits.substring(2, 6)}-${digits.substring(6)}"
            else -> raw
        }
    }
}
