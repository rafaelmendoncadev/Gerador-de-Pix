@echo off
title Compilando Gerador Pix (.exe) e Instalador Windows
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe build_exe.py
) else (
    python build_exe.py
)
pause
