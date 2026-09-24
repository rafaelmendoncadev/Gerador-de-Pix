# Gerador de Pix Desktop com QR Code 🚀

Aplicativo Desktop moderno para Windows em Python com **CustomTkinter**, desenvolvido especialmente para gerar cobranças Pix rápidas no padrão oficial do **Banco Central do Brasil (BACEN / EMV-Co)**.

---

## ✨ Recursos

- 🔹 **Sistema 100% Customizável:** Qualquer usuário ou empresa pode cadastrar seus dados de recebedor (Nome/Razão Social, Chave Pix e Cidade) no primeiro acesso com fluxo guiado de onboarding.
- 🔹 **Validação Inteligente de Chave:** Reconhece e valida automaticamente formatos de CPF, CNPJ, Celular com DDD, E-mail ou Chave Aleatória (EVP).
- 🔹 **Painel de Configurações e Redefinição:** Permite alterar os dados cadastrados ou redefinir/zerar o cadastro com um clique a qualquer momento.
- 🔹 **Máscara Monetária Inteligente:** Campo de valor que formata automaticamente no padrão brasileiro (`R$ 0,00`), além de botões rápidos para somar valores (`+ R$ 10`, `+ R$ 50`, `+ R$ 100`, etc.).
- 🔹 **Identificador e Descrição:** Suporte opcional a identificador de pedido (TxID) e mensagem da cobrança para o pagador.
- 🔹 **QR Code em Alta Resolução:** Renderização nítida na tela com leitura garantida por qualquer aplicativo bancário (Nubank, Itaú, Bradesco, Inter, Santander, BB, Caixa, etc.).
- 🔹 **Pix Copia e Cola:** Botão dedicado com cópia direta para a área de transferência do Windows e confirmação visual.
- 🔹 **Exportação de Imagem PNG:** Salva o QR Code diretamente em arquivo `.png` com seletor de pastas nativo.
- 🔹 **Design Moderno e Alternador de Tema:** Suporte completo a Modo Escuro (Dark) e Modo Claro (Light) com detalhes na cor oficial do Pix (`#32BCAD`).
- 🔹 **Executável Windows (.exe) e Instalador:** Disponível tanto em executável único portátil quanto em instalador oficial Windows completo.

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

---

## 🧪 Testes Automatizados

Para rodar a suíte de testes de validação do motor Pix e CRC16:
```powershell
.\.venv\Scripts\pytest
```

