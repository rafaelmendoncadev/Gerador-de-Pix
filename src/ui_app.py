"""Interface Gráfica do Gerador Pix Desktop desenvolvida em CustomTkinter."""

from __future__ import annotations

import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Any, Dict, Optional

import customtkinter as ctk
from PIL import Image

from src.config_manager import (
    format_pix_key_display,
    is_config_valid,
    load_config,
    reset_config,
    save_config,
    validate_pix_key_type,
)
from src.pix_engine import PixCharge


# Cores do Tema Pix
PIX_TEAL = "#32BCAD"
PIX_TEAL_HOVER = "#24A395"
SUCCESS_GREEN = "#10B981"
DARK_BG = "#11111B"
DARK_CARD = "#181825"
DARK_INPUT = "#1E1E2E"
BORDER_COLOR = "#313244"
APP_VERSION = "1.2.0"


class SettingsDialog(ctk.CTkToplevel):
    """Janela modal para cadastrar/editar os dados do recebedor (Chave, Nome e Cidade)."""

    def __init__(self, parent: "PixApp", config: Dict[str, Any]):
        super().__init__(parent)
        self.parent = parent
        self.config = config

        self.is_first_time = not is_config_valid(config)

        if self.is_first_time:
            self.title("Bem-vindo ao Gerador Pix - Cadastro Inicial")
            title_text = "Cadastro do Recebedor Pix"
            subtitle_text = "Informe seus dados para começar a gerar cobranças com QR Code."
            save_btn_text = "✨ Salvar e Começar"
        else:
            self.title("Configurações do Recebedor Pix")
            title_text = "Configurar Dados do Recebedor"
            subtitle_text = "Esses dados são utilizados para gerar o QR Code e o Copia e Cola."
            save_btn_text = "💾 Salvar Alterações"

        dialog_height = 520 if not self.is_first_time else 460
        self.geometry(f"540x{dialog_height}")
        self.resizable(False, False)
        self.grab_set()  # Modal

        self.configure(fg_color=("#F1F5F9", DARK_BG))

        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(20, 5))

        subtitle_label = ctk.CTkLabel(
            self,
            text=subtitle_text,
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray70"),
        )
        subtitle_label.pack(pady=(0, 15))

        # Formulário
        form_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", DARK_CARD), corner_radius=12)
        form_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # Nome
        ctk.CTkLabel(
            form_frame,
            text="Nome Completo ou Razão Social (até 25 caracteres):",
            font=ctk.CTkFont(weight="bold", size=13),
        ).pack(anchor="w", padx=20, pady=(15, 4))
        self.name_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Ex: João da Silva ou Minha Loja LTDA",
            fg_color=("#F8FAFC", DARK_INPUT),
        )
        self.name_entry.insert(0, config.get("beneficiary_name", ""))
        self.name_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Chave Pix
        ctk.CTkLabel(
            form_frame,
            text="Chave Pix (CPF, CNPJ, Celular com DDD, E-mail ou Aleatória):",
            font=ctk.CTkFont(weight="bold", size=13),
        ).pack(anchor="w", padx=20, pady=(5, 4))
        self.key_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Ex: 123.456.789-00, loja@email.com, 11999998888...",
            fg_color=("#F8FAFC", DARK_INPUT),
        )
        self.key_entry.insert(0, config.get("pix_key", ""))
        self.key_entry.pack(fill="x", padx=20, pady=(0, 10))

        # Cidade
        ctk.CTkLabel(
            form_frame,
            text="Cidade do Recebedor (até 15 caracteres):",
            font=ctk.CTkFont(weight="bold", size=13),
        ).pack(anchor="w", padx=20, pady=(5, 4))
        self.city_entry = ctk.CTkEntry(
            form_frame,
            height=38,
            placeholder_text="Ex: São Paulo, Rio de Janeiro, Curitiba...",
            fg_color=("#F8FAFC", DARK_INPUT),
        )
        self.city_entry.insert(0, config.get("city", ""))
        self.city_entry.pack(fill="x", padx=20, pady=(0, 15))

        # Botões principais
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(0, 10))

        if not self.is_first_time:
            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="Cancelar",
                fg_color=("gray75", "gray30"),
                hover_color=("gray65", "gray40"),
                text_color=("#1E293B", "#FFFFFF"),
                height=38,
                command=self.destroy,
            )
            cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))

        save_btn = ctk.CTkButton(
            btn_frame,
            text=save_btn_text,
            fg_color=PIX_TEAL,
            hover_color=PIX_TEAL_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            height=38,
            command=self.save_settings,
        )
        save_btn.pack(
            side="right" if not self.is_first_time else "left",
            fill="x",
            expand=True,
            padx=(10 if not self.is_first_time else 0, 0),
        )

        # Botão de redefinição / limpeza (apenas se já houver dados cadastrados)
        if not self.is_first_time:
            reset_btn = ctk.CTkButton(
                self,
                text="🗑️ Limpar / Redefinir Cadastro",
                fg_color="#DC2626",
                hover_color="#B91C1C",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=12, weight="bold"),
                height=32,
                command=self.confirm_reset,
            )
            reset_btn.pack(padx=25, pady=(0, 15))

    def confirm_reset(self):
        if messagebox.askyesno(
            "Confirmar Limpeza",
            "Deseja realmente apagar todos os dados cadastrados?\n\nO sistema voltará ao estado inicial em branco.",
            icon="warning",
        ):
            self.config.clear()
            self.config.update(reset_config())
            self.parent.config_data = self.config.copy()
            self.parent.update_beneficiary_display()
            self.destroy()
            messagebox.showinfo("Cadastro Limpo", "Todos os dados foram redefinidos com sucesso!")
            self.parent.open_settings()

    def save_settings(self):
        new_name = self.name_entry.get().strip()
        new_key = self.key_entry.get().strip()
        new_city = self.city_entry.get().strip()

        if len(new_name) < 2:
            messagebox.showwarning("Atenção", "Por favor, informe o Nome Completo ou Razão Social do recebedor.")
            self.name_entry.focus()
            return

        is_valid, key_type, err_msg = validate_pix_key_type(new_key)
        if not is_valid:
            messagebox.showwarning("Chave Pix Inválida", err_msg)
            self.key_entry.focus()
            return

        if len(new_city) < 2:
            messagebox.showwarning("Atenção", "Por favor, informe a Cidade do recebedor.")
            self.city_entry.focus()
            return

        self.config["beneficiary_name"] = new_name
        self.config["pix_key"] = new_key
        self.config["city"] = new_city

        save_config(self.config)
        self.parent.config_data = self.config.copy()
        self.parent.update_beneficiary_display()
        self.destroy()
        messagebox.showinfo(
            "Sucesso",
            f"Cadastro salvo com sucesso!\n\nRecebedor: {new_name}\nTipo de Chave: {key_type}\nCidade: {new_city}",
        )


class PixApp(ctk.CTk):
    """Janela principal do aplicativo Gerador Pix Desktop."""

    def __init__(self):
        super().__init__()

        self.config_data = load_config()

        # Configura tema inicial
        initial_theme = self.config_data.get("theme", "Dark")
        ctk.set_appearance_mode(initial_theme)
        ctk.set_default_color_theme("blue")

        self.title(f"Gerador de Pix v{APP_VERSION} - Pagamentos Rápidos")
        self.geometry("1000x720")
        self.minsize(920, 680)

        # Estado da cobrança
        self.current_payload: Optional[str] = None
        self.current_qr_img: Optional[Image.Image] = None
        self.cents_value: int = 0  # Armazena o valor digitado em centavos (ex: 5000 = R$ 50,00)

        # Ícone da janela
        if getattr(sys, "frozen", False):
            base_assets = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            icon_path = os.path.join(base_assets, "src", "assets", "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(base_assets, "assets", "icon.ico")
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, "assets", "icon.ico")

        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        self._build_ui()
        self.update_beneficiary_display()

        # Onboarding: se for primeiro acesso ou dados incompletos, abre o cadastro automaticamente
        if not is_config_valid(self.config_data):
            self.after(300, self.open_settings)

    def _build_ui(self):
        self.configure(fg_color=("#F1F5F9", DARK_BG))

        # -----------------------------
        # 1. Header Superior
        # -----------------------------
        header_frame = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", DARK_CARD),
            corner_radius=0,
            height=70,
        )
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Logo e Título
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=12)

        logo_badge = ctk.CTkLabel(
            title_box,
            text="❖ PIX",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=PIX_TEAL,
        )
        logo_badge.pack(side="left", padx=(0, 12))

        app_title = ctk.CTkLabel(
            title_box,
            text=f"Gerador de Cobrança com QR Code  v{APP_VERSION}",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        app_title.pack(side="left")

        # Ações do Header (Tema e Config)
        header_actions = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_actions.pack(side="right", padx=20, pady=12)

        self.theme_btn = ctk.CTkButton(
            header_actions,
            text="🌓 Tema",
            width=85,
            height=34,
            fg_color=("gray85", "#262637"),
            hover_color=("gray75", "#323247"),
            text_color=("#1E293B", "#CDD6F4"),
            command=self.toggle_theme,
        )
        self.theme_btn.pack(side="right", padx=(8, 0))

        self.config_btn = ctk.CTkButton(
            header_actions,
            text="⚙️ Configurações",
            width=120,
            height=34,
            fg_color=("gray85", "#262637"),
            hover_color=("gray75", "#323247"),
            text_color=("#1E293B", "#CDD6F4"),
            command=self.open_settings,
        )
        self.config_btn.pack(side="right")

        # -----------------------------
        # 2. Card de Informações do Beneficiário
        # -----------------------------
        beneficiary_card = ctk.CTkFrame(
            self,
            fg_color=("#FFFFFF", DARK_CARD),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", BORDER_COLOR),
        )
        beneficiary_card.pack(fill="x", padx=20, pady=(15, 10))

        ben_inner = ctk.CTkFrame(beneficiary_card, fg_color="transparent")
        ben_inner.pack(fill="x", padx=16, pady=12)

        # Ícone de cartão
        card_icon = ctk.CTkLabel(
            ben_inner,
            text="💳",
            font=ctk.CTkFont(size=24),
        )
        card_icon.pack(side="left", padx=(0, 12))

        ben_text_frame = ctk.CTkFrame(ben_inner, fg_color="transparent")
        ben_text_frame.pack(side="left", fill="x", expand=True)

        self.ben_name_label = ctk.CTkLabel(
            ben_text_frame,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        self.ben_name_label.pack(anchor="w")

        self.ben_details_label = ctk.CTkLabel(
            ben_text_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("gray40", "gray70"),
            anchor="w",
        )
        self.ben_details_label.pack(anchor="w")

        edit_ben_btn = ctk.CTkButton(
            ben_inner,
            text="Alterar Chave",
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=("gray85", "#262637"),
            hover_color=("gray75", "#323247"),
            text_color=("#1E293B", "#CDD6F4"),
            command=self.open_settings,
        )
        edit_ben_btn.pack(side="right")

        # -----------------------------
        # 3. Conteúdo Principal (2 Colunas)
        # -----------------------------
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # --- Coluna Esquerda: Formulário de Entrada ---
        left_card = ctk.CTkFrame(
            main_content,
            fg_color=("#FFFFFF", DARK_CARD),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", BORDER_COLOR),
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        form_container = ctk.CTkScrollableFrame(left_card, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            form_container,
            text="Dados da Cobrança",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", pady=(0, 15))

        # Campo: Valor com Máscara Monetária
        ctk.CTkLabel(
            form_container,
            text="Valor a Receber (R$):",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.amount_entry = ctk.CTkEntry(
            form_container,
            height=46,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color=("#F8FAFC", DARK_INPUT),
            text_color=PIX_TEAL,
            justify="center",
        )
        self.amount_entry.pack(fill="x", pady=(0, 6))
        self.amount_entry.insert(0, "R$ 0,00")
        self.amount_entry.bind("<Key>", self._handle_currency_key)
        self.amount_entry.bind("<BackSpace>", self._handle_currency_backspace)
        self.amount_entry.bind("<FocusIn>", lambda e: self.amount_entry.icursor(tk.END))

        # Atalhos rápidos de valores
        chips_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        chips_frame.pack(fill="x", pady=(0, 18))

        quick_amounts = [
            ("+ R$ 10", 10.0),
            ("+ R$ 20", 20.0),
            ("+ R$ 50", 50.0),
            ("+ R$ 100", 100.0),
            ("+ R$ 500", 500.0),
        ]
        for text, val in quick_amounts:
            btn = ctk.CTkButton(
                chips_frame,
                text=text,
                width=62,
                height=28,
                font=ctk.CTkFont(size=11),
                fg_color=("gray85", "#262637"),
                hover_color=("gray75", "#323247"),
                text_color=("#1E293B", "#CDD6F4"),
                command=lambda v=val: self._add_quick_amount(v),
            )
            btn.pack(side="left", padx=3)

        zerar_btn = ctk.CTkButton(
            chips_frame,
            text="Zerar",
            width=50,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("gray85", "#35222E"),
            hover_color=("gray75", "#482637"),
            text_color=("#B91C1C", "#F87171"),
            command=self._reset_amount,
        )
        zerar_btn.pack(side="left", padx=3)

        # Campo: Identificador da Transação (TxID)
        ctk.CTkLabel(
            form_container,
            text="Identificador / Pedido (Opcional):",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.txid_entry = ctk.CTkEntry(
            form_container,
            height=38,
            placeholder_text="Ex: PEDIDO101 (sem espaços)",
            fg_color=("#F8FAFC", DARK_INPUT),
        )
        self.txid_entry.pack(fill="x", pady=(0, 16))

        # Campo: Mensagem / Descrição para o Pagador
        ctk.CTkLabel(
            form_container,
            text="Descrição / Mensagem (Opcional):",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.desc_entry = ctk.CTkEntry(
            form_container,
            height=38,
            placeholder_text="Ex: Pagamento de serviço / Compra",
            fg_color=("#F8FAFC", DARK_INPUT),
        )
        self.desc_entry.pack(fill="x", pady=(0, 24))

        # Botão Principal: Gerar QR Code Pix
        self.generate_btn = ctk.CTkButton(
            form_container,
            text="⚡ Gerar QR Code Pix",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=PIX_TEAL,
            hover_color=PIX_TEAL_HOVER,
            text_color="#FFFFFF",
            command=self.generate_pix,
        )
        self.generate_btn.pack(fill="x", pady=(0, 10))

        # Botão Limpar
        clear_btn = ctk.CTkButton(
            form_container,
            text="Limpar Campos",
            height=36,
            fg_color=("gray85", "#262637"),
            hover_color=("gray75", "#323247"),
            text_color=("#1E293B", "#CDD6F4"),
            command=self.clear_fields,
        )
        clear_btn.pack(fill="x")

        # --- Coluna Direita: Exibição do QR Code e Ações ---
        right_card = ctk.CTkFrame(
            main_content,
            fg_color=("#FFFFFF", DARK_CARD),
            corner_radius=12,
            border_width=1,
            border_color=("gray80", BORDER_COLOR),
        )
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        qr_container = ctk.CTkScrollableFrame(right_card, fg_color="transparent")
        qr_container.pack(fill="both", expand=True, padx=20, pady=15)

        ctk.CTkLabel(
            qr_container,
            text="QR Code e Pagamento",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Área de renderização do QR Code
        self.qr_frame = ctk.CTkFrame(
            qr_container,
            fg_color=("#FFFFFF", "#FFFFFF"),
            corner_radius=16,
            width=270,
            height=270,
            border_width=2,
            border_color=("gray85", "#E2E8F0"),
        )
        self.qr_frame.pack(pady=(5, 12))
        self.qr_frame.pack_propagate(False)

        self.qr_label = ctk.CTkLabel(
            self.qr_frame,
            text="Preencha o valor e clique em\n'Gerar QR Code Pix'",
            font=ctk.CTkFont(size=13),
            text_color="gray40",
        )
        self.qr_label.place(relx=0.5, rely=0.5, anchor="center")

        # Badge com o valor gerado
        self.amount_badge = ctk.CTkLabel(
            qr_container,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=PIX_TEAL,
        )
        self.amount_badge.pack(pady=(0, 8))

        # Caixa do Código Copia e Cola
        ctk.CTkLabel(
            qr_container,
            text="Código Pix Copia e Cola:",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", pady=(0, 4))

        self.payload_textbox = ctk.CTkTextbox(
            qr_container,
            height=65,
            font=ctk.CTkFont(size=11, family="Consolas"),
            fg_color=("#F8FAFC", DARK_INPUT),
            wrap="char",
        )
        self.payload_textbox.pack(fill="x", pady=(0, 12))
        self.payload_textbox.insert("1.0", "O código Pix Copia e Cola aparecerá aqui.")
        self.payload_textbox.configure(state="disabled")

        # Botões de Ação
        actions_frame = ctk.CTkFrame(qr_container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 5))

        self.copy_btn = ctk.CTkButton(
            actions_frame,
            text="📋 Copiar Código Pix",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=PIX_TEAL,
            hover_color=PIX_TEAL_HOVER,
            text_color="#FFFFFF",
            state="disabled",
            command=self.copy_payload,
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.save_btn = ctk.CTkButton(
            actions_frame,
            text="💾 Salvar Imagem (PNG)",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("gray85", "#262637"),
            hover_color=("gray75", "#323247"),
            text_color=("#1E293B", "#CDD6F4"),
            state="disabled",
            command=self.save_qr_image,
        )
        self.save_btn.pack(side="right", fill="x", expand=True, padx=(6, 0))

        # Status / Feedback toast
        self.status_label = ctk.CTkLabel(
            qr_container,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=SUCCESS_GREEN,
        )
        self.status_label.pack(pady=(6, 0))

    # -----------------------------
    # Manipulação da Máscara Monetária
    # -----------------------------
    def _format_cents(self, cents: int) -> str:
        reais = cents / 100.0
        # Formata com separador de milhar por ponto e decimal por vírgula
        formatted = f"{reais:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"

    def _handle_currency_key(self, event):
        if event.char.isdigit():
            # Limita a 10 dígitos (até R$ 99.999.999,99)
            if self.cents_value < 1000000000:
                self.cents_value = self.cents_value * 10 + int(event.char)
                self._update_amount_display()
            return "break"
        elif event.keysym in ("Left", "Right", "Tab"):
            return None
        return "break"

    def _handle_currency_backspace(self, event):
        self.cents_value = self.cents_value // 10
        self._update_amount_display()
        return "break"

    def _update_amount_display(self):
        formatted = self._format_cents(self.cents_value)
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, formatted)

    def _add_quick_amount(self, value_reais: float):
        self.cents_value += int(value_reais * 100)
        self._update_amount_display()

    def _reset_amount(self):
        self.cents_value = 0
        self._update_amount_display()

    # -----------------------------
    # Ações do Beneficiário
    # -----------------------------
    def update_beneficiary_display(self):
        if is_config_valid(self.config_data):
            name = str(self.config_data.get("beneficiary_name", "")).strip()
            key = str(self.config_data.get("pix_key", "")).strip()
            city = str(self.config_data.get("city", "")).strip()
            formatted_key = format_pix_key_display(key)
            self.ben_name_label.configure(text=f"Recebedor: {name}")
            self.ben_details_label.configure(
                text=f"Chave Pix: {formatted_key}  •  Cidade: {city}"
            )
        else:
            self.ben_name_label.configure(text="Recebedor: Nenhum recebedor cadastrado")
            self.ben_details_label.configure(
                text="Clique no botão ⚙️ ao lado para cadastrar seus dados"
            )

    def open_settings(self):
        SettingsDialog(self, self.config_data)

    def toggle_theme(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.config_data["theme"] = new_mode
        save_config(self.config_data)

    # -----------------------------
    # Geração do Pix
    # -----------------------------
    def generate_pix(self):
        if not is_config_valid(self.config_data):
            messagebox.showwarning(
                "Cadastro Obrigatório",
                "Antes de gerar cobranças Pix, é necessário cadastrar os dados do recebedor.\n\nA tela de cadastro será aberta agora.",
            )
            self.open_settings()
            return

        amount_reais = self.cents_value / 100.0

        txid = self.txid_entry.get().strip() or None
        description = self.desc_entry.get().strip() or None

        name = str(self.config_data.get("beneficiary_name", "")).strip()
        key = str(self.config_data.get("pix_key", "")).strip()
        city = str(self.config_data.get("city", "")).strip()

        charge = PixCharge(
            pix_key=key,
            merchant_name=name,
            merchant_city=city,
            amount=amount_reais if amount_reais > 0 else None,
            txid=txid,
            description=description,
        )

        try:
            payload = charge.build_payload()
            qr_img = charge.generate_qr_code_image(box_size=10, border=2)
        except Exception as e:
            messagebox.showerror("Erro ao Gerar Pix", f"Ocorreu um erro: {e}")
            return

        self.current_payload = payload
        self.current_qr_img = qr_img

        # Renderiza imagem no CustomTkinter
        display_img = ctk.CTkImage(light_image=qr_img, dark_image=qr_img, size=(240, 240))
        self.qr_label.configure(image=display_img, text="")

        # Atualiza badge de valor
        if amount_reais > 0:
            formatted_val = self._format_cents(self.cents_value)
            self.amount_badge.configure(text=f"Cobrança: {formatted_val}")
        else:
            self.amount_badge.configure(text="Cobrança com valor aberto (livre)")

        # Atualiza caixa do copia e cola
        self.payload_textbox.configure(state="normal")
        self.payload_textbox.delete("1.0", tk.END)
        self.payload_textbox.insert("1.0", payload)
        self.payload_textbox.configure(state="disabled")

        # Habilita botões
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")

        self.show_status("✅ Código Pix gerado com sucesso!")

    def copy_payload(self):
        if not self.current_payload:
            return

        self.clipboard_clear()
        self.clipboard_append(self.current_payload)
        self.update()

        # Feedback visual no botão
        original_text = self.copy_btn.cget("text")
        original_color = self.copy_btn.cget("fg_color")
        self.copy_btn.configure(text="✅ Código Copiado!", fg_color=SUCCESS_GREEN)

        def restore():
            self.copy_btn.configure(text=original_text, fg_color=original_color)

        self.after(2000, restore)
        self.show_status("📋 Copiado para a área de transferência!")

    def save_qr_image(self):
        if not self.current_qr_img:
            return

        name_slug = re.sub(r"[^a-zA-Z0-9]", "_", self.config_data.get("beneficiary_name", "pix")).lower()
        val_slug = f"_{self.cents_value // 100}reais" if self.cents_value > 0 else ""
        default_filename = f"pix_{name_slug}{val_slug}.png"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png"), ("Todos os arquivos", "*.*")],
            initialfile=default_filename,
            title="Salvar Imagem do QR Code Pix",
        )

        if file_path:
            try:
                self.current_qr_img.save(file_path, format="PNG")
                self.show_status(f"💾 Salvo em: {os.path.basename(file_path)}")
                messagebox.showinfo(
                    "Salvo com Sucesso",
                    f"A imagem do QR Code Pix foi salva em:\n{file_path}",
                )
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def clear_fields(self):
        self._reset_amount()
        self.txid_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.current_payload = None
        self.current_qr_img = None
        self.qr_label.configure(
            image=None,
            text="Preencha o valor e clique em\n'Gerar QR Code Pix'",
        )
        self.amount_badge.configure(text="")
        self.payload_textbox.configure(state="normal")
        self.payload_textbox.delete("1.0", tk.END)
        self.payload_textbox.insert("1.0", "O código Pix Copia e Cola aparecerá aqui.")
        self.payload_textbox.configure(state="disabled")
        self.copy_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.status_label.configure(text="")

    def show_status(self, text: str):
        self.status_label.configure(text=text)
        self.after(4000, lambda: self.status_label.configure(text=""))
