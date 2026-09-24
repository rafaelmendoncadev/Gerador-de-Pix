"""Gerenciador de configurações e preferências persistidas do aplicativo."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "beneficiary_name": "Rafael Vieira de Mendonça",
    "pix_key": "techzonesistemas@gmail.com",
    "city": "Brasília",
    "theme": "Dark",
    "default_description": "",
}


import sys


def get_default_config_path() -> str:
    """Retorna o caminho padrão para o arquivo config.json."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.json")


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Carrega as configurações salvas ou retorna os valores padrão."""
    path = config_path or get_default_config_path()
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG, path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Garante que chaves faltantes recebam o valor padrão
            config = DEFAULT_CONFIG.copy()
            config.update(data)
            return config
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_config(data: Dict[str, Any], config_path: str | None = None) -> bool:
    """Salva as configurações no arquivo json."""
    path = config_path or get_default_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def format_pix_key_display(key: str) -> str:
    """Formata a chave para exibição visual amigável (CPF, CNPJ, etc)."""
    digits = re.sub(r"\D", "", key)
    if len(digits) == 11:
        # CPF: 000.000.000-00
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    elif len(digits) == 14:
        # CNPJ: 00.000.000/0000-00
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    elif len(digits) in (10, 11) and not any(c.isalpha() for c in key):
        # Telefone: (00) 00000-0000
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        else:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return key
