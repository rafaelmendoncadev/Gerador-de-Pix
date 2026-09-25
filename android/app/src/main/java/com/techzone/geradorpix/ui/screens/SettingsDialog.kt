package com.techzone.geradorpix.ui.screens

import android.widget.Toast
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.techzone.geradorpix.engine.PixKeyValidator
import com.techzone.geradorpix.model.BeneficiaryData
import com.techzone.geradorpix.ui.theme.ErrorRed
import com.techzone.geradorpix.ui.theme.PixTeal

@Composable
fun SettingsDialog(
    initialData: BeneficiaryData,
    onDismiss: () -> Unit,
    onSave: (BeneficiaryData) -> Unit,
    onReset: () -> Unit
) {
    val context = LocalContext.current
    val isFirstTime = !initialData.isValid()

    var name by remember { mutableStateOf(initialData.name) }
    var pixKey by remember { mutableStateOf(initialData.pixKey) }
    var city by remember { mutableStateOf(initialData.city) }

    var showResetConfirm by remember { mutableStateOf(false) }

    val keyValidation = remember(pixKey) {
        if (pixKey.isNotBlank()) PixKeyValidator.validate(pixKey) else null
    }

    Dialog(
        onDismissRequest = {
            if (!isFirstTime) onDismiss()
        },
        properties = DialogProperties(
            dismissOnBackPress = !isFirstTime,
            dismissOnClickOutside = !isFirstTime,
            usePlatformDefaultWidth = false
        )
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .wrapContentHeight()
                .padding(vertical = 16.dp),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surface
            )
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = if (isFirstTime) "👋 Bem-vindo!" else "⚙️ Configurações",
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold,
                    color = PixTeal
                )

                Text(
                    text = if (isFirstTime)
                        "Cadastre seus dados de recebedor para começar a gerar cobranças Pix com QR Code."
                    else
                        "Atualize os dados do recebedor que serão inseridos no QR Code e no Copia e Cola.",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                    modifier = Modifier.padding(top = 6.dp, bottom = 18.dp)
                )

                // Nome do Beneficiário
                OutlinedTextField(
                    value = name,
                    onValueChange = { if (it.length <= 25) name = it },
                    label = { Text("Nome / Razão Social (até 25 letras)") },
                    placeholder = { Text("Ex: Minha Loja ou João Silva") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                )

                Spacer(modifier = Modifier.height(14.dp))

                // Chave Pix
                OutlinedTextField(
                    value = pixKey,
                    onValueChange = { pixKey = it },
                    label = { Text("Chave Pix") },
                    placeholder = { Text("CPF, CNPJ, Celular, E-mail ou EVP") },
                    singleLine = true,
                    isError = keyValidation != null && !keyValidation.isValid,
                    supportingText = {
                        if (keyValidation != null) {
                            if (keyValidation.isValid) {
                                Text("Tipo detectado: ${keyValidation.type}", color = PixTeal)
                            } else {
                                Text(keyValidation.errorMessage, color = ErrorRed)
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Cidade
                OutlinedTextField(
                    value = city,
                    onValueChange = { if (it.length <= 15) city = it },
                    label = { Text("Cidade do Recebedor (até 15 letras)") },
                    placeholder = { Text("Ex: São Paulo, Rio, Brasília...") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Botão Salvar
                Button(
                    onClick = {
                        if (name.trim().length < 2) {
                            Toast.makeText(context, "Informe o Nome do recebedor.", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        val validation = PixKeyValidator.validate(pixKey)
                        if (!validation.isValid) {
                            Toast.makeText(context, validation.errorMessage, Toast.LENGTH_LONG).show()
                            return@Button
                        }
                        if (city.trim().length < 2) {
                            Toast.makeText(context, "Informe a Cidade do recebedor.", Toast.LENGTH_SHORT).show()
                            return@Button
                        }

                        onSave(
                            BeneficiaryData(
                                name = name.trim(),
                                pixKey = pixKey.trim(),
                                city = city.trim()
                            )
                        )
                        Toast.makeText(context, "Dados salvos com sucesso!", Toast.LENGTH_SHORT).show()
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(48.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PixTeal)
                ) {
                    Text(
                        text = if (isFirstTime) "✨ Salvar e Começar" else "💾 Salvar Alterações",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = Color.White
                    )
                }

                if (!isFirstTime) {
                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(44.dp),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text("Cancelar", color = MaterialTheme.colorScheme.onSurface)
                    }

                    Spacer(modifier = Modifier.height(18.dp))

                    TextButton(
                        onClick = { showResetConfirm = true },
                        colors = ButtonDefaults.textButtonColors(contentColor = ErrorRed)
                    ) {
                        Icon(Icons.Default.Delete, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("🗑️ Limpar / Redefinir Cadastro", fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                    }
                }
            }
        }
    }

    if (showResetConfirm) {
        AlertDialog(
            onDismissRequest = { showResetConfirm = false },
            title = { Text("Confirmar Limpeza") },
            text = { Text("Deseja realmente apagar todos os dados cadastrados?\n\nO aplicativo voltará ao estado inicial em branco.") },
            confirmButton = {
                TextButton(
                    onClick = {
                        showResetConfirm = false
                        onReset()
                        Toast.makeText(context, "Cadastro limpo com sucesso!", Toast.LENGTH_SHORT).show()
                    }
                ) {
                    Text("Sim, Limpar", color = ErrorRed, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showResetConfirm = false }) {
                    Text("Cancelar")
                }
            }
        )
    }
}
