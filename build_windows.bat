@echo off
chcp 65001 >nul
title MeteoApp - Compilador de Ejecutable

echo =============================================
echo   MeteoApp - Build Script para Windows
echo =============================================
echo.

REM 1. Verificar que Python esta disponible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en el sistema.
    echo Instala Python 3.10+ desde https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

echo [1/5] Verificando Python...
python --version
echo.

REM 2. Crear entorno virtual
echo [2/5] Creando entorno virtual...
if exist .venv (
    echo       El entorno virtual ya existe. Se usara el actual.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat
echo.

REM 3. Instalar dependencias
echo [3/5] Instalando dependencias del proyecto...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo.

REM 4. Instalar PyInstaller
echo [4/5] Instalando PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de PyInstaller.
    pause
    exit /b 1
)
echo.

REM 5. Compilar el ejecutable
echo [5/5] Compilando MeteoApp.exe...
echo        Esto puede tardar unos minutos...
python -m flet pack main.py --name MeteoApp
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la compilacion del ejecutable.
    pause
    exit /b 1
)
echo.

REM 6. Mover el ejecutable a la raiz del proyecto
echo Moviendo MeteoApp.exe a la raiz del proyecto...
move /Y dist\MeteoApp\MeteoApp.exe . 2>nul

REM Mover carpeta _internal (dependencias del ejecutable)
if exist dist\MeteoApp\_internal (
    if exist _internal (
        echo       Reemplazando _internal anterior...
        rmdir /s /q _internal
    )
    move dist\MeteoApp\_internal .
)

REM Limpiar carpetas temporales
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul

echo.
echo =============================================
echo    LISTO! MeteoApp.exe creado exitosamente.
echo.
echo    Para ejecutar: doble clic en MeteoApp.exe
echo    El codigo fuente sigue disponible en:
echo      - main.py
echo      - utils/
echo      - views/
echo =============================================
echo.
pause
