package com.techzone.geradorpix.model

data class PixCharge(
    val pixKey: String,
    val merchantName: String,
    val merchantCity: String,
    val amount: Double? = null,
    val txid: String? = null,
    val description: String? = null
)
