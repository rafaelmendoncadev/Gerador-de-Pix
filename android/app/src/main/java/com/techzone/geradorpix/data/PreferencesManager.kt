package com.techzone.geradorpix.data

import android.content.Context
import android.content.SharedPreferences
import com.techzone.geradorpix.model.BeneficiaryData

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("gerador_pix_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_NAME = "beneficiary_name"
        private const val KEY_PIX_KEY = "pix_key"
        private const val KEY_CITY = "city"
        private const val KEY_DEFAULT_DESC = "default_description"
        private const val KEY_DARK_THEME = "is_dark_theme"
    }

    fun getBeneficiary(): BeneficiaryData {
        return BeneficiaryData(
            name = prefs.getString(KEY_NAME, "") ?: "",
            pixKey = prefs.getString(KEY_PIX_KEY, "") ?: "",
            city = prefs.getString(KEY_CITY, "") ?: "",
            defaultDescription = prefs.getString(KEY_DEFAULT_DESC, "") ?: ""
        )
    }

    fun saveBeneficiary(data: BeneficiaryData) {
        prefs.edit()
            .putString(KEY_NAME, data.name.trim())
            .putString(KEY_PIX_KEY, data.pixKey.trim())
            .putString(KEY_CITY, data.city.trim())
            .putString(KEY_DEFAULT_DESC, data.defaultDescription.trim())
            .apply()
    }

    fun clearBeneficiary() {
        prefs.edit()
            .remove(KEY_NAME)
            .remove(KEY_PIX_KEY)
            .remove(KEY_CITY)
            .remove(KEY_DEFAULT_DESC)
            .apply()
    }

    fun isDarkTheme(systemDark: Boolean): Boolean {
        return prefs.getBoolean(KEY_DARK_THEME, systemDark)
    }

    fun setDarkTheme(isDark: Boolean) {
        prefs.edit().putBoolean(KEY_DARK_THEME, isDark).apply()
    }
}
