@echo off
title Compilando APK Android - Gerador Pix (TechZone Sistemas)
echo ==================================================
echo Iniciando compilacao do APK Android (Gradle)...
echo ==================================================

cd android
call gradlew.bat assembleDebug
set GRADLE_EXIT=%ERRORLEVEL%
cd ..

if %GRADLE_EXIT% EQU 0 (
    if not exist dist mkdir dist
    copy /Y android\app\build\outputs\apk\debug\app-debug.apk dist\GeradorPix.apk
    echo.
    echo ==================================================
    echo APK COMPILADO COM SUCESSO!
    echo Arquivo disponivel em: dist\GeradorPix.apk
    echo ==================================================
) else (
    echo.
    echo [ERRO] Falha na compilacao do APK. Codigo: %GRADLE_EXIT%
)
pause
