#!/bin/bash

# Script para iniciar GRUTA GESTAO localmente

echo "========================================"
echo "GRUTA GESTAO - Sistema de Gestão"
echo "========================================"
echo ""

# Verificar se Python esta instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 nao encontrado. Por favor instale Python 3.8+"
    exit 1
fi

# Verificar se pip esta instalado
if ! command -v pip3 &> /dev/null; then
    echo "[ERRO] pip3 nao encontrado"
    exit 1
fi

# Ir para o diretorio do backend
cd backend

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "[ERRO] arquivo requirements.txt nao encontrado"
    exit 1
fi

# Verificar se credenciais existem
if [ ! -f "gruta-gestao-7b3adc499256.json" ]; then
    echo "[AVISO] Arquivo de credenciais nao encontrado"
    echo "[INFO] Copie o arquivo para: $(pwd)/gruta-gestao-7b3adc499256.json"
    echo ""
fi

# Instalar dependencias
echo "[INFO] Instalando dependencias Python..."
pip3 install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao instalar dependencias"
    exit 1
fi

echo "[OK] Dependencias instaladas"
echo ""

# Iniciar servidor
echo "[INFO] Iniciando servidor Flask..."
echo "[INFO] API disponivel em: http://localhost:5000"
echo "[INFO] Frontend em: file://$(pwd)/../frontend/index.html"
echo ""
echo "Pressione CTRL+C para parar"
echo ""

python3 server.py
