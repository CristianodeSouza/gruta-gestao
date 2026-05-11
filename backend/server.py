#!/usr/bin/env python3
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import gspread
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuracao das planilhas
SPREADSHEET_IDS = {
    "95594065000119": "1ZNxygVnszQ4X-28b5OLckMjlMZ1C519ahLTP-DDU8AU",
    "65313187/0001-29": "1W159OU4uYApYA1i9YJjEnnVKfACwckDN6kOt29qwOCI"
}

# Cache de dados
data_cache = {}
cache_timestamp = {}
CACHE_DURATION = 300  # 5 minutos

# Inicializar gspread
try:
    credentials_path = os.path.expanduser("~") + r"\Downloads\gruta-gestao-7b3adc499256.json"
    if not os.path.exists(credentials_path):
        credentials_path = r"C:\Users\User\Downloads\gruta-gestao-7b3adc499256.json"
    gc = gspread.service_account(filename=credentials_path)
    print(f"[OK] Autenticacao Google Sheets bem-sucedida")
except Exception as e:
    print(f"[ERRO] Falha na autenticacao: {str(e)}")
    gc = None

def read_sheet_data(spreadsheet_id, sheet_name):
    """Le dados de uma planilha especifica"""
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        return data
    except Exception as e:
        print(f"[ERRO] Lendo sheet {sheet_name}: {str(e)}")
        return []

def process_livro_diario(data):
    """Processa Livro Diario FC - principais transacoes"""
    if len(data) <= 2:
        return []

    # Pular linhas vazias de cabecalho
    header_row = 0
    for i, row in enumerate(data[:10]):
        if any(cell and 'Data' in str(cell) for cell in row):
            header_row = i
            break

    transactions = []
    for row in data[header_row + 1:]:
        if not any(row):  # Skip empty rows
            continue
        try:
            # Mapear colunas (estrutura pode variar)
            trans = {
                "data": row[0] if len(row) > 0 else "",
                "descricao": row[1] if len(row) > 1 else "",
                "categoria": row[2] if len(row) > 2 else "",
                "valor": float(row[3]) if len(row) > 3 and row[3] else 0,
            }
            if trans["valor"] != 0 or trans["descricao"]:
                transactions.append(trans)
        except:
            continue

    return transactions[-100:]  # Ultimas 100 transacoes

def process_fluxo_caixa(data):
    """Processa Fluxo de Caixa resumido"""
    summary = {
        "mes_atual": "",
        "entradas": 0,
        "saidas": 0,
        "saldo": 0,
        "por_categoria": {}
    }

    if len(data) > 2:
        for row in data[1:]:
            if len(row) > 2:
                try:
                    valor = float(row[2]) if row[2] else 0
                    if valor != 0:
                        summary["entradas"] += abs(valor) if valor > 0 else 0
                        summary["saidas"] += abs(valor) if valor < 0 else 0
                except:
                    continue

    summary["saldo"] = summary["entradas"] - summary["saidas"]
    return summary

def get_cnpj_data(cnpj):
    """Obtem todos os dados de um CNPJ"""
    cache_key = f"data_{cnpj}"

    # Verificar cache
    if cache_key in data_cache:
        if time.time() - cache_timestamp.get(cache_key, 0) < CACHE_DURATION:
            return data_cache[cache_key]

    if cnpj not in SPREADSHEET_IDS or not gc:
        return None

    spreadsheet_id = SPREADSHEET_IDS[cnpj]

    try:
        # Ler todas as abas
        livro_diario = read_sheet_data(spreadsheet_id, "Livro Diário FC")
        fluxo_caixa = read_sheet_data(spreadsheet_id, "FC")
        analise_fin = read_sheet_data(spreadsheet_id, "Análise Fin")
        planejamento = read_sheet_data(spreadsheet_id, "Planejamento Financeiro")
        apagar_receber = read_sheet_data(spreadsheet_id, "A Pagar e A Receber ")
        cadastros = read_sheet_data(spreadsheet_id, "Cadastros")
        graficos = read_sheet_data(spreadsheet_id, "Gráficos")

        cnpj_data = {
            "cnpj": cnpj,
            "timestamp": datetime.now().isoformat(),
            "livro_diario": process_livro_diario(livro_diario),
            "fluxo_caixa": process_fluxo_caixa(fluxo_caixa),
            "analise_fin": analise_fin[:10] if analise_fin else [],
            "planejamento": planejamento[:20] if planejamento else [],
            "apagar_receber": apagar_receber[:20] if apagar_receber else [],
            "cadastros": cadastros[:50] if cadastros else [],
            "graficos": graficos[:30] if graficos else [],
        }

        # Armazenar em cache
        data_cache[cache_key] = cnpj_data
        cache_timestamp[cache_key] = time.time()

        return cnpj_data

    except Exception as e:
        print(f"[ERRO] Obtendo dados de {cnpj}: {str(e)}")
        return None

# ROTAS DA API

@app.route('/api/health', methods=['GET'])
def health():
    """Status da API"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "auth": "OK" if gc else "ERRO"
    })

@app.route('/api/cnpjs', methods=['GET'])
def list_cnpjs():
    """Lista todos os CNPJs disponiveis"""
    return jsonify({
        "cnpjs": list(SPREADSHEET_IDS.keys())
    })

@app.route('/api/cnpj/<cnpj>/summary', methods=['GET'])
def get_summary(cnpj):
    """Resumo executivo de um CNPJ"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "resumo": data["fluxo_caixa"],
        "ultima_atualizacao": data["timestamp"]
    })

@app.route('/api/cnpj/<cnpj>/livro-diario', methods=['GET'])
def get_livro_diario(cnpj):
    """Livro Diario - Transacoes"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    # Aplicar filtros
    filtro_descricao = request.args.get('descricao', '').lower()
    filtro_categoria = request.args.get('categoria', '').lower()

    transacoes = data["livro_diario"]

    if filtro_descricao:
        transacoes = [t for t in transacoes if filtro_descricao in t.get("descricao", "").lower()]
    if filtro_categoria:
        transacoes = [t for t in transacoes if filtro_categoria in t.get("categoria", "").lower()]

    return jsonify({
        "cnpj": cnpj,
        "total": len(transacoes),
        "transacoes": transacoes
    })

@app.route('/api/cnpj/<cnpj>/fluxo-caixa', methods=['GET'])
def get_fluxo_caixa(cnpj):
    """Fluxo de Caixa - Resumo Financeiro"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "fluxo_caixa": data["fluxo_caixa"],
        "livro_diario_total": len(data["livro_diario"])
    })

@app.route('/api/cnpj/<cnpj>/analise', methods=['GET'])
def get_analise(cnpj):
    """Analise Financeira"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "analise": data["analise_fin"]
    })

@app.route('/api/cnpj/<cnpj>/contas', methods=['GET'])
def get_contas(cnpj):
    """Contas a Pagar e Receber"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "contas": data["apagar_receber"]
    })

@app.route('/api/cnpj/<cnpj>/planejamento', methods=['GET'])
def get_planejamento(cnpj):
    """Planejamento Financeiro"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "planejamento": data["planejamento"]
    })

@app.route('/api/cnpj/<cnpj>/cadastros', methods=['GET'])
def get_cadastros(cnpj):
    """Cadastros - Contas e Categorias"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify({
        "cnpj": cnpj,
        "cadastros": data["cadastros"]
    })

@app.route('/api/cnpj/<cnpj>/completo', methods=['GET'])
def get_completo(cnpj):
    """Todos os dados de um CNPJ"""
    data = get_cnpj_data(cnpj)
    if not data:
        return jsonify({"erro": "CNPJ nao encontrado"}), 404

    return jsonify(data)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"erro": "Endpoint nao encontrado"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
