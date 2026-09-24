@echo off
title Gerador Pix Desktop - TechZone Sistemas
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe main.py
) else (
    python main.py
)
pause
