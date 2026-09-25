package com.techzone.geradorpix.engine

/**
 * Cálculo oficial do CRC16-CCITT (Polinômio 0x1021, valor inicial 0xFFFF)
 * conforme a especificação do Banco Central do Brasil para Pix EMV-Co.
 */
object Crc16 {
    fun calculate(payload: String): String {
        var crc = 0xFFFF
        val bytes = payload.toByteArray(Charsets.UTF_8)
        for (b in bytes) {
            crc = crc xor ((b.toInt() and 0xFF) shl 8)
            for (i in 0 until 8) {
                crc = if ((crc and 0x8000) != 0) {
                    ((crc shl 1) xor 0x1021) and 0xFFFF
                } else {
                    (crc shl 1) and 0xFFFF
                }
            }
        }
        return String.format("%04X", crc)
    }
}
