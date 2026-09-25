package com.techzone.geradorpix

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.runtime.*
import com.techzone.geradorpix.data.PreferencesManager
import com.techzone.geradorpix.ui.screens.MainScreen
import com.techzone.geradorpix.ui.theme.GeradorPixTheme

class MainActivity : ComponentActivity() {

    private lateinit var prefs: PreferencesManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        prefs = PreferencesManager(this)

        setContent {
            val systemDark = isSystemInDarkTheme()
            var isDarkTheme by remember { mutableStateOf(prefs.isDarkTheme(systemDark)) }

            GeradorPixTheme(darkTheme = isDarkTheme) {
                MainScreen(
                    prefs = prefs,
                    isDarkTheme = isDarkTheme,
                    onToggleTheme = {
                        val newDark = !isDarkTheme
                        isDarkTheme = newDark
                        prefs.setDarkTheme(newDark)
                    }
                )
            }
        }
    }
}
