package com.techzone.geradorpix.ui.screens

import android.graphics.Bitmap
import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.techzone.geradorpix.data.PreferencesManager
import com.techzone.geradorpix.engine.PixEngine
import com.techzone.geradorpix.engine.PixKeyValidator
import com.techzone.geradorpix.model.BeneficiaryData
import com.techzone.geradorpix.model.PixCharge
import com.techzone.geradorpix.ui.theme.PixTeal
import com.techzone.geradorpix.ui.theme.SuccessGreen
import com.techzone.geradorpix.util.QrCodeGenerator
import com.techzone.geradorpix.util.ShareHelper
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    prefs: PreferencesManager,
    isDarkTheme: Boolean,
    onToggleTheme: () -> Unit
) {
    val context = LocalContext.current
    var beneficiary by remember { mutableStateOf(prefs.getBeneficiary()) }
    var showSettingsDialog by remember { mutableStateOf(!beneficiary.isValid()) }

    var centsValue by remember { mutableLongStateOf(0L) }
    var txid by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }

    var generatedPayload by remember { mutableStateOf<String?>(null) }
    var generatedQrBitmap by remember { mutableStateOf<Bitmap?>(null) }

    fun formatCentsToReais(cents: Long): String {
        val reais = cents / 100.0
        return String.format(Locale("pt", "BR"), "R$ %,.2f", reais)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = "❖ PIX",
                            color = PixTeal,
                            fontWeight = FontWeight.Black,
                            fontSize = 20.sp
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "Gerador Pix v1.2.0",
                            fontWeight = FontWeight.Bold,
                            fontSize = 17.sp
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onToggleTheme) {
                        Icon(
                            imageVector = if (isDarkTheme) Icons.Default.LightMode else Icons.Default.DarkMode,
                            contentDescription = "Alternar Tema",
                            tint = MaterialTheme.colorScheme.onSurface
                        )
                    }
                    IconButton(onClick = { showSettingsDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Configurações",
                            tint = PixTeal
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(12.dp))

            // ------------------------------------
            // 1. Card do Beneficiário
            // ------------------------------------
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { showSettingsDialog = true },
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Box(
                        modifier = Modifier
                            .size(46.dp)
                            .clip(CircleShape)
                            .background(PixTeal.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = Icons.Default.Person,
                            contentDescription = null,
                            tint = PixTeal,
                            modifier = Modifier.size(26.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(14.dp))

                    Column(modifier = Modifier.weight(1f)) {
                        if (beneficiary.isValid()) {
                            Text(
                                text = beneficiary.name,
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp,
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                            Text(
                                text = "Chave: ${PixKeyValidator.formatDisplay(beneficiary.pixKey)}",
                                fontSize = 12.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                                maxLines = 1,
                                overflow = TextOverflow.Ellipsis
                            )
                            Text(
                                text = "Cidade: ${beneficiary.city}",
                                fontSize = 12.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        } else {
                            Text(
                                text = "⚠️ Nenhum recebedor cadastrado",
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                color = PixTeal
                            )
                            Text(
                                text = "Toque aqui para cadastrar seus dados Pix",
                                fontSize = 12.sp,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                            )
                        }
                    }

                    Icon(
                        imageVector = Icons.Default.Edit,
                        contentDescription = "Editar",
                        tint = PixTeal,
                        modifier = Modifier.size(20.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // ------------------------------------
            // 2. Campo de Valor Monetário
            // ------------------------------------
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Valor da Cobrança",
                        fontWeight = FontWeight.SemiBold,
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = formatCentsToReais(centsValue),
                        fontSize = 32.sp,
                        fontWeight = FontWeight.Black,
                        color = PixTeal
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    // Chips de Valores Rápidos
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf(
                            1000L to "+ R$ 10",
                            2000L to "+ R$ 20",
                            5000L to "+ R$ 50",
                            10000L to "+ R$ 100"
                        ).forEach { (addCents, label) ->
                            AssistChip(
                                onClick = { centsValue += addCents },
                                label = { Text(label, fontSize = 11.sp, fontWeight = FontWeight.SemiBold) },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(8.dp)
                            )
                        }
                    }

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 4.dp),
                        horizontalArrangement = Arrangement.Center
                    ) {
                        TextButton(
                            onClick = { centsValue = 0L },
                            enabled = centsValue > 0L
                        ) {
                            Icon(Icons.Default.Clear, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Zerar Valor", fontSize = 12.sp)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // ------------------------------------
            // 3. Campos Opcionais (TxID e Descrição)
            // ------------------------------------
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    OutlinedTextField(
                        value = txid,
                        onValueChange = { if (it.length <= 25) txid = it },
                        label = { Text("Identificador do Pedido / TxID (Opcional)") },
                        placeholder = { Text("Ex: PEDIDO123") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    OutlinedTextField(
                        value = description,
                        onValueChange = { if (it.length <= 40) description = it },
                        label = { Text("Mensagem da Cobrança (Opcional)") },
                        placeholder = { Text("Ex: Mensalidade, Serviço, Produto...") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(12.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // ------------------------------------
            // 4. Botão Gerar Cobrança
            // ------------------------------------
            Button(
                onClick = {
                    if (!beneficiary.isValid()) {
                        Toast.makeText(context, "Cadastre seus dados de recebedor antes de gerar.", Toast.LENGTH_LONG).show()
                        showSettingsDialog = true
                        return@Button
                    }

                    val amountReais = if (centsValue > 0) centsValue / 100.0 else null
                    val charge = PixCharge(
                        pixKey = beneficiary.pixKey,
                        merchantName = beneficiary.name,
                        merchantCity = beneficiary.city,
                        amount = amountReais,
                        txid = txid.ifBlank { null },
                        description = description.ifBlank { null }
                    )

                    val payload = PixEngine.buildPayload(charge)
                    val bitmap = QrCodeGenerator.generate(payload, size = 650)

                    generatedPayload = payload
                    generatedQrBitmap = bitmap

                    Toast.makeText(context, "QR Code gerado com sucesso!", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PixTeal)
            ) {
                Icon(Icons.Default.QrCode, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "⚡ Gerar Cobrança Pix",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = Color.White
                )
            }

            // ------------------------------------
            // 5. Exibição do Resultado (QR Code e Ações)
            // ------------------------------------
            if (generatedPayload != null && generatedQrBitmap != null) {
                Spacer(modifier = Modifier.height(18.dp))

                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(20.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Cobrança Pronta para Pagamento",
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp,
                            color = SuccessGreen
                        )

                        Spacer(modifier = Modifier.height(14.dp))

                        // QR Code Image
                        Box(
                            modifier = Modifier
                                .size(240.dp)
                                .clip(RoundedCornerShape(16.dp))
                                .background(Color.White)
                                .padding(12.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Image(
                                bitmap = generatedQrBitmap!!.asImageBitmap(),
                                contentDescription = "QR Code Pix",
                                modifier = Modifier.fillMaxSize()
                            )
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Copia e Cola preview
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(MaterialTheme.colorScheme.surfaceVariant)
                                .clickable {
                                    ShareHelper.copyToClipboard(context, generatedPayload!!)
                                }
                                .padding(12.dp)
                        ) {
                            Text(
                                text = generatedPayload!!,
                                maxLines = 2,
                                overflow = TextOverflow.Ellipsis,
                                fontSize = 11.sp,
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f)
                            )
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Ações Rápidas
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Button(
                                onClick = {
                                    ShareHelper.copyToClipboard(context, generatedPayload!!)
                                },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(10.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = PixTeal)
                            ) {
                                Icon(Icons.Default.ContentCopy, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("Copiar", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                            }

                            Button(
                                onClick = {
                                    val shareMsg = buildString {
                                        append("Pagamento Pix para ${beneficiary.name}\n")
                                        if (centsValue > 0) {
                                            append("Valor: ${formatCentsToReais(centsValue)}\n")
                                        }
                                        if (description.isNotBlank()) {
                                            append("Referente: $description\n")
                                        }
                                        append("\nChave Copia e Cola:\n${generatedPayload}")
                                    }
                                    ShareHelper.shareText(context, shareMsg)
                                },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(10.dp),
                                colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen)
                            ) {
                                Icon(Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
                                Spacer(modifier = Modifier.width(6.dp))
                                Text("WhatsApp", fontSize = 13.sp, fontWeight = FontWeight.Bold)
                            }
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        OutlinedButton(
                            onClick = {
                                val caption = if (centsValue > 0)
                                    "QR Code Pix - ${formatCentsToReais(centsValue)} (${beneficiary.name})"
                                else
                                    "QR Code Pix - ${beneficiary.name}"
                                ShareHelper.shareQrCodeImage(context, generatedQrBitmap!!, caption)
                            },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Icon(Icons.Default.Image, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Compartilhar Imagem do QR Code", fontSize = 13.sp)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(30.dp))
        }
    }

    if (showSettingsDialog) {
        SettingsDialog(
            initialData = beneficiary,
            onDismiss = { showSettingsDialog = false },
            onSave = { updated ->
                prefs.saveBeneficiary(updated)
                beneficiary = updated
                showSettingsDialog = false
            },
            onReset = {
                prefs.clearBeneficiary()
                beneficiary = BeneficiaryData()
                generatedPayload = null
                generatedQrBitmap = null
            }
        )
    }
}
