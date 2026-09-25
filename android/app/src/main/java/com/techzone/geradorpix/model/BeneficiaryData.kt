package com.techzone.geradorpix.model

data class BeneficiaryData(
    val name: String = "",
    val pixKey: String = "",
    val city: String = "",
    val defaultDescription: String = ""
) {
    fun isValid(): Boolean {
        return name.trim().length >= 2 && pixKey.trim().isNotEmpty() && city.trim().length >= 2
    }
}
