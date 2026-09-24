"""Ponto de entrada do aplicativo Gerador Pix."""

import sys
import os

# Garante que o diretório raiz esteja no PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ui_app import PixApp


def main():
    app = PixApp()
    app.mainloop()


if __name__ == "__main__":
    main()
