@echo off
REM Script para compilar o WhatsApp Message Sender em executável
REM Requer PyInstaller instalado

echo.
echo ============================================================
echo WhatsApp Message Sender - Compilador de Executavel
echo ============================================================
echo.

REM Verifica se PyInstaller está instalado
python -m PyInstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] PyInstaller nao esta instalado!
    echo.
    echo Instale com o comando:
    echo   pip install pyinstaller
    echo.
    pause
    exit /b 1
)

echo [OK] PyInstaller encontrado
echo.
echo Compilando executavel...
echo.

REM Compila usando o arquivo .spec
python -m PyInstaller WhatsAppSender.spec

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [OK] Executavel criado com sucesso!
    echo ============================================================
    echo.
    echo Localizacao: dist\WhatsApp Message Sender.exe
    echo.
    echo Proximos passos:
    echo 1. O arquivo .exe esta na pasta "dist"
    echo 2. Voce pode copiar a pasta "dist" para qualquer lugar
    echo 3. Crie um atalho para o executavel no seu desktop
    echo.
) else (
    echo.
    echo [ERRO] Falha na compilacao
    echo.
)

pause
