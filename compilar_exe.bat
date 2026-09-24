@echo off
title Compilando Gerador Pix para Executavel Windows (.exe)
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe build_exe.py
) else (
    python build_exe.py
)
pause
