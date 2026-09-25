# Gerador de Pix Multiplataforma (Windows Desktop & Android Nativo) 🚀

Solução completa e moderna para gerar cobranças Pix rápidas no padrão oficial do **Banco Central do Brasil (BACEN / EMV-Co)**:
- 💻 **Versão Desktop (Windows):** Python + CustomTkinter + PyInstaller + Instalador Inno Setup.
- 📱 **Versão Mobile (Android):** 100% Nativo em **Kotlin + Jetpack Compose (Material 3)** + Compartilhamento direto no WhatsApp.

---

## ✨ Recursos

- 🔹 **Sistema 100% Customizável:** Qualquer usuário ou empresa pode cadastrar seus dados de recebedor (Nome/Razão Social, Chave Pix e Cidade) no primeiro acesso com fluxo guiado de onboarding.
- 🔹 **Validação Inteligente de Chave:** Reconhece e valida automaticamente formatos de CPF, CNPJ, Celular com DDD, E-mail ou Chave Aleatória (EVP).
- 🔹 **Painel de Configurações e Redefinição:** Permite alterar os dados cadastrados ou redefinir/zerar o cadastro com um clique a qualquer momento.
- 🔹 **Máscara Monetária Inteligente:** Campo de valor que formata automaticamente no padrão brasileiro (`R$ 0,00`), além de botões rápidos para somar valores (`+ R$ 10`, `+ R$ 20`, `+ R$ 50`, `+ R$ 100`, etc.).
- 🔹 **Compartilhamento Direto no Android:** Envio nativo do Copia e Cola formatado ou da imagem do QR Code diretamente para o **WhatsApp**, Telegram e outros aplicativos via Intent.
- 🔹 **QR Code em Alta Resolução:** Renderização nítida na tela com leitura garantida por qualquer aplicativo bancário (Nubank, Itaú, Bradesco, Inter, Santander, BB, Caixa, etc.).
- 🔹 **Pix Copia e Cola:** Botão dedicado com cópia direta para a área de transferência com confirmação visual e feedback háptico.
- 🔹 **Design Moderno e Alternador de Tema:** Suporte completo a Modo Escuro (Dark) e Modo Claro (Light) com detalhes na cor oficial do Pix (`#32BCAD`).
- 🔹 **Distribuição Completa:** Executável portátil (`.exe`), instalador Windows (`Setup.exe`) e pacote de instalação Android (`.apk`).

---

## 📁 Estrutura do Projeto

```
GeradorPix/
├── dist/                  # Diretório gerado com o executável final (.exe)
├── src/
│   ├── assets/            # Ícones e recursos visuais (.ico, .png)
│   ├── assets_generator.py# Utilitário para geração de ícones
│   ├── config_manager.py  # Carregamento e salvamento de preferências locais
│   ├── pix_engine.py      # Motor de montagem do payload EMV-Co e cálculo CRC16
│   └── ui_app.py          # Interface gráfica moderna com CustomTkinter
├── tests/
│   └── test_pix_engine.py # Testes automatizados de conformidade BACEN e CRC16
├── config.json            # Configurações salvas do recebedor
├── main.py                # Ponto de entrada do aplicativo
├── build_exe.py           # Script de compilação com PyInstaller
├── iniciar.bat            # Executa o aplicativo com um clique
├── compilar_exe.bat       # Compila o executável com um clique
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação
```

---

## 🚀 Como Executar

### Opção 1: Executável Direto (.exe)
Após a compilação, basta dar um duplo clique em:
```
dist\GeradorPix.exe
```

### Opção 2: Pelo Script Batch
Dê um duplo clique no arquivo:
```
iniciar.bat
```

### Opção 3: Via Terminal Python
1. Ative o ambiente virtual:
```powershell
.\.venv\Scripts\Activate.ps1
```
2. Inicie a aplicação:
```powershell
python main.py
```

---

## 🛠️ Como Compilar o Executável e o Instalador (.exe)

### 1. Compilar Apenas o Executável Portátil (.exe)
- Dê um duplo clique em `compilar_exe.bat` **OU**
- Execute no terminal:
```powershell
python build_exe.py
```
O executável final será gerado em `dist/GeradorPix.exe`.

### 2. Gerar o Instalador Windows Oficial (Inno Setup)
- Dê um duplo clique em `compilar_instalador.bat` **OU**
- Execute no terminal:
```powershell
python build_exe.py --installer
```
O instalador completo com suporte a desinstalação e atalhos será gerado em `dist/GeradorPix_Setup_v1.2.0.exe`.

### 3. Compilar o Aplicativo Android (.apk)
- Dê um duplo clique em `compilar_apk.bat` **OU**
- Execute no terminal:
```powershell
cd android
.\gradlew assembleDebug
```
O pacote de instalação para celular será gerado em:
```
dist/GeradorPix.apk
```

---

## 🧪 Testes Automatizados

Para rodar a suíte de testes de validação do motor Pix e CRC16 (Python):
```powershell
.\.venv\Scripts\pytest
```


