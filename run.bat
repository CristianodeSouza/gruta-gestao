@echo off
REM Script para iniciar GRUTA GESTAO no Windows

echo.
echo ========================================
echo GRUTA GESTAO - Sistema de Gestao
echo ========================================
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Por favor instale Python 3.8+
    pause
    exit /b 1
)

REM Ir para o diretorio do backend
cd backend

REM Verificar se requirements.txt existe
if not exist "requirements.txt" (
    echo [ERRO] arquivo requirements.txt nao encontrado
    pause
    exit /b 1
)

REM Verificar se credenciais existem
if not exist "gruta-gestao-7b3adc499256.json" (
    echo [AVISO] Arquivo de credenciais nao encontrado
    echo [INFO] Copie o arquivo para: %cd%\gruta-gestao-7b3adc499256.json
    echo.
)

REM Instalar dependencias
echo [INFO] Instalando dependencias Python...
pip install -q -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas
echo.

REM Iniciar servidor
echo [INFO] Iniciando servidor Flask...
echo [INFO] API disponivel em: http://localhost:5000
echo [INFO] Frontend em: file://%cd%\..\frontend\index.html
echo.
echo Pressione CTRL+C para parar
echo.

python server.py
pause
