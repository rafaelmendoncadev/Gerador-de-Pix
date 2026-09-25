package com.techzone.geradorpix.engine

import com.techzone.geradorpix.model.PixCharge
import java.text.Normalizer
import java.util.Locale

object PixEngine {

    fun removeAccents(text: String): String {
        val nfd = Normalizer.normalize(text, Normalizer.Form.NFD)
        return Regex("\\p{InCombiningDiacriticalMarks}+").replace(nfd, "")
    }

    fun sanitizeMerchantName(name: String, maxLen: Int = 25): String {
        val clean = removeAccents(name).trim().uppercase()
            .replace(Regex("[^A-Z0-9 ]"), "")
            .replace(Regex("\\s+"), " ")
        return if (clean.length > maxLen) clean.substring(0, maxLen) else clean
    }

    fun sanitizeMerchantCity(city: String, maxLen: Int = 15): String {
        val clean = removeAccents(city).trim().uppercase()
            .replace(Regex("[^A-Z0-9 ]"), "")
            .replace(Regex("\\s+"), " ")
        return if (clean.length > maxLen) clean.substring(0, maxLen) else clean
    }

    fun sanitizeTxid(txid: String?, maxLen: Int = 25): String {
        if (txid.isNullOrBlank()) return "***"
        val clean = removeAccents(txid).trim().replace(Regex("[^A-Za-z0-9]"), "")
        if (clean.isEmpty()) return "***"
        return if (clean.length > maxLen) clean.substring(0, maxLen) else clean
    }

    fun sanitizePixKey(key: String): String {
        val raw = key.trim()
        if (raw.contains("@")) return raw.lowercase()

        val digits = raw.replace(Regex("\\D"), "")
        if (digits.length == 11 || digits.length == 14) {
            return digits
        }
        return raw
    }

    fun formatTlv(tag: String, value: String): String {
        val length = value.toByteArray(Charsets.UTF_8).size
        val tagNum = tag.toIntOrNull() ?: 0
        return String.format(Locale.US, "%02d%02d%s", tagNum, length, value)
    }

    fun buildPayload(charge: PixCharge): String {
        val cleanKey = sanitizePixKey(charge.pixKey)
        val name = sanitizeMerchantName(charge.merchantName)
        val city = sanitizeMerchantCity(charge.merchantCity)
        val refTxid = sanitizeTxid(charge.txid)

        // 00: Payload Format Indicator
        val p00 = formatTlv("00", "01")

        // 26: Merchant Account Information
        val gui = formatTlv("00", "br.gov.bcb.pix")
        val keyTlv = formatTlv("01", cleanKey)
        val descTlv = if (!charge.description.isNullOrBlank()) {
            val cleanDesc = removeAccents(charge.description).trim()
            val limitedDesc = if (cleanDesc.length > 40) cleanDesc.substring(0, 40) else cleanDesc
            formatTlv("02", limitedDesc)
        } else {
            ""
        }
        val maiContent = gui + keyTlv + descTlv
        val p26 = formatTlv("26", maiContent)

        // 52: Merchant Category Code
        val p52 = formatTlv("52", "0000")

        // 53: Transaction Currency (986 = BRL)
        val p53 = formatTlv("53", "986")

        // 54: Transaction Amount (opcional se > 0)
        val p54 = if (charge.amount != null && charge.amount > 0.0) {
            val formattedAmount = String.format(Locale.US, "%.2f", charge.amount)
            formatTlv("54", formattedAmount)
        } else {
            ""
        }

        // 58: Country Code
        val p58 = formatTlv("58", "BR")

        // 59: Merchant Name
        val p59 = formatTlv("59", name)

        // 60: Merchant City
        val p60 = formatTlv("60", city)

        // 62: Additional Data Field Template (TxID)
        val txidTlv = formatTlv("05", refTxid)
        val p62 = formatTlv("62", txidTlv)

        // Concatena tudo até o campo 63
        val rawPayload = p00 + p26 + p52 + p53 + p54 + p58 + p59 + p60 + p62 + "6304"

        // Calcula e anexa CRC16
        val crc = Crc16.calculate(rawPayload)
        return rawPayload + crc
    }
}
