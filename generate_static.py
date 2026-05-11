#!/usr/bin/env python3
import os
import json
import gspread
from datetime import datetime

# Configuração das planilhas
SPREADSHEET_IDS = {
    "95594065000119": "1ZNxygVnszQ4X-28b5OLckMjlMZ1C519ahLTP-DDU8AU",
    "65313187/0001-29": "1W159OU4uYApYA1i9YJjEnnVKfACwckDN6kOt29qwOCI"
}

CNPJ_NAMES = {
    "95594065000119": "GRUTA - Grutatagliarierodrigues",
    "65313187/0001-29": "GRUTA - Nova Empresa Delivery"
}

def get_credentials():
    """Obtém credenciais do Google"""
    try:
        credentials_path = os.path.expanduser("~") + r"\Downloads\gruta-gestao-6b88ee2d9c7b.json"
        if not os.path.exists(credentials_path):
            credentials_path = r"C:\Users\User\Downloads\gruta-gestao-6b88ee2d9c7b.json"

        if not os.path.exists(credentials_path):
            print(f"[ERRO] Arquivo de credenciais não encontrado em {credentials_path}")
            return None

        gc = gspread.service_account(filename=credentials_path)
        print(f"[OK] Credenciais carregadas")
        return gc
    except Exception as e:
        print(f"[ERRO] Falha ao carregar credenciais: {str(e)}")
        return None

def read_sheet_data(gc, spreadsheet_id, sheet_name):
    """Lê dados de uma aba específica"""
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        return data
    except Exception as e:
        print(f"[ERRO] Lendo aba '{sheet_name}': {str(e)}")
        return []

def format_value(value):
    """Formata valor para exibição"""
    if not value:
        return ""
    try:
        # Tenta converter para float se for número
        float_val = float(value)
        if float_val == int(float_val):
            return f"R$ {int(float_val):,.0f}".replace(",", ".")
        else:
            return f"R$ {float_val:,.2f}".replace(",", ".")
    except:
        return str(value)

def process_livro_diario(data):
    """Processa Livro Diário - retorna últimas 50 transações"""
    if len(data) <= 2:
        return []

    # Encontrar linha de cabeçalho
    header_row = 0
    for i, row in enumerate(data[:10]):
        if any(cell and 'Data' in str(cell) for cell in row):
            header_row = i
            break

    transactions = []
    for row in data[header_row + 1:]:
        if not any(row):
            continue
        try:
            trans = {
                "data": row[0] if len(row) > 0 else "",
                "descricao": row[1] if len(row) > 1 else "",
                "categoria": row[2] if len(row) > 2 else "",
                "valor": row[3] if len(row) > 3 else "0",
            }
            if trans["valor"] or trans["descricao"]:
                transactions.append(trans)
        except:
            continue

    return transactions[-50:]  # Últimas 50 transações

def get_cnpj_data(gc, cnpj):
    """Obtém todos os dados de um CNPJ"""
    spreadsheet_id = SPREADSHEET_IDS[cnpj]

    try:
        print(f"  Lendo dados do CNPJ {cnpj}...")

        # Ler abas principais
        livro_diario = read_sheet_data(gc, spreadsheet_id, "Livro Diário FC")
        fluxo_caixa = read_sheet_data(gc, spreadsheet_id, "FC")
        analise_fin = read_sheet_data(gc, spreadsheet_id, "Análise Fin")
        planejamento = read_sheet_data(gc, spreadsheet_id, "Planejamento Financeiro")
        apagar_receber = read_sheet_data(gc, spreadsheet_id, "A Pagar e A Receber ")

        return {
            "livro_diario": process_livro_diario(livro_diario),
            "fluxo_caixa": fluxo_caixa[:10] if fluxo_caixa else [],
            "analise_fin": analise_fin[:15] if analise_fin else [],
            "planejamento": planejamento[:20] if planejamento else [],
            "apagar_receber": apagar_receber[:25] if apagar_receber else [],
        }
    except Exception as e:
        print(f"[ERRO] Obtendo dados de {cnpj}: {str(e)}")
        return None

def generate_html(all_data):
    """Gera HTML estático com todos os dados"""

    html_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GRUTA GESTAO - Gestão Financeira Completa</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }

        .header {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1rem; opacity: 0.9; }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .selector {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            display: flex;
            gap: 1rem;
            align-items: center;
        }

        .selector label {
            font-weight: 600;
            margin-right: 1rem;
        }

        .selector select {
            padding: 0.8rem 1rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
            flex: 1;
            max-width: 400px;
        }

        .info-box {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .info-box h2 {
            color: #2196F3;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            border-bottom: 2px solid #2196F3;
            padding-bottom: 0.5rem;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .card {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }

        .card h3 {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 0.5rem;
        }

        .card .value {
            font-size: 1.8rem;
            font-weight: bold;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 2rem;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .table thead {
            background: #f5f5f5;
            border-bottom: 2px solid #ddd;
        }

        .table th {
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #333;
        }

        .table td {
            padding: 0.8rem 1rem;
            border-bottom: 1px solid #eee;
        }

        .table tbody tr:hover {
            background: #f9f9f9;
        }

        .table tbody tr:last-child td {
            border-bottom: none;
        }

        .timestamp {
            text-align: center;
            color: #999;
            font-size: 0.9rem;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid #eee;
        }

        .footer {
            background: #212121;
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 2rem;
        }

        .hidden {
            display: none;
        }

        @media (max-width: 768px) {
            .header h1 { font-size: 1.8rem; }
            .container { padding: 1rem; }
            .selector { flex-direction: column; align-items: stretch; }
            .selector select { max-width: 100%; }
            .table th, .table td { padding: 0.6rem; font-size: 0.9rem; }
            .cards { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>GRUTA GESTÃO</h1>
        <p>Sistema de Gestão Financeira - Dados Atualizados</p>
    </div>

    <div class="container">
        <div class="selector">
            <label for="cnpj-select">Selecione a Empresa:</label>
            <select id="cnpj-select" onchange="changeCNPJ()">
'''

    # Adicionar opções de CNPJ
    for cnpj in SPREADSHEET_IDS.keys():
        html_content += f'                <option value="{cnpj}">{cnpj} - {CNPJ_NAMES[cnpj]}</option>\n'

    html_content += '''            </select>
        </div>
'''

    # Gerar seções para cada CNPJ
    for cnpj, data in all_data.items():
        if not data:
            continue

        html_content += f'''
        <div id="cnpj-{cnpj}" class="cnpj-section">
            <!-- LIVRO DIÁRIO -->
            <div class="info-box">
                <h2>📊 Livro Diário - Transações Recentes</h2>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Descrição</th>
                            <th>Categoria</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
'''

        # Adicionar linhas de transações
        for trans in data["livro_diario"][:50]:
            html_content += f'''                        <tr>
                            <td>{trans.get("data", "")}</td>
                            <td>{trans.get("descricao", "")}</td>
                            <td>{trans.get("categoria", "")}</td>
                            <td>{format_value(trans.get("valor", ""))}</td>
                        </tr>
'''

        html_content += '''                    </tbody>
                </table>
            </div>

            <!-- FLUXO DE CAIXA -->
            <div class="info-box">
                <h2>💰 Fluxo de Caixa</h2>
                <table class="table">
                    <thead>
                        <tr>
'''

        # Cabeçalhos do Fluxo de Caixa
        if data["fluxo_caixa"] and len(data["fluxo_caixa"]) > 0:
            header_row = data["fluxo_caixa"][0]
            for col in header_row:
                html_content += f'                            <th>{col}</th>\n'

        html_content += '''                        </tr>
                    </thead>
                    <tbody>
'''

        # Dados do Fluxo de Caixa
        if data["fluxo_caixa"]:
            for row in data["fluxo_caixa"][1:10]:
                html_content += '                        <tr>\n'
                for cell in row:
                    html_content += f'                            <td>{format_value(cell)}</td>\n'
                html_content += '                        </tr>\n'

        html_content += '''                    </tbody>
                </table>
            </div>

            <!-- ANÁLISE FINANCEIRA -->
            <div class="info-box">
                <h2>📈 Análise Financeira</h2>
                <table class="table">
                    <thead>
                        <tr>
'''

        # Cabeçalhos da Análise Financeira
        if data["analise_fin"] and len(data["analise_fin"]) > 0:
            header_row = data["analise_fin"][0]
            for col in header_row:
                html_content += f'                            <th>{col}</th>\n'

        html_content += '''                        </tr>
                    </thead>
                    <tbody>
'''

        # Dados da Análise Financeira
        if data["analise_fin"]:
            for row in data["analise_fin"][1:]:
                html_content += '                        <tr>\n'
                for cell in row:
                    html_content += f'                            <td>{format_value(cell)}</td>\n'
                html_content += '                        </tr>\n'

        html_content += '''                    </tbody>
                </table>
            </div>

            <!-- PLANEJAMENTO FINANCEIRO -->
            <div class="info-box">
                <h2>🎯 Planejamento Financeiro</h2>
                <table class="table">
                    <thead>
                        <tr>
'''

        # Cabeçalhos do Planejamento
        if data["planejamento"] and len(data["planejamento"]) > 0:
            header_row = data["planejamento"][0]
            for col in header_row:
                html_content += f'                            <th>{col}</th>\n'

        html_content += '''                        </tr>
                    </thead>
                    <tbody>
'''

        # Dados do Planejamento
        if data["planejamento"]:
            for row in data["planejamento"][1:]:
                html_content += '                        <tr>\n'
                for cell in row:
                    html_content += f'                            <td>{format_value(cell)}</td>\n'
                html_content += '                        </tr>\n'

        html_content += '''                    </tbody>
                </table>
            </div>

            <!-- CONTAS A PAGAR E RECEBER -->
            <div class="info-box">
                <h2>💳 Contas a Pagar e Receber</h2>
                <table class="table">
                    <thead>
                        <tr>
'''

        # Cabeçalhos de Contas
        if data["apagar_receber"] and len(data["apagar_receber"]) > 0:
            header_row = data["apagar_receber"][0]
            for col in header_row:
                html_content += f'                            <th>{col}</th>\n'

        html_content += '''                        </tr>
                    </thead>
                    <tbody>
'''

        # Dados de Contas
        if data["apagar_receber"]:
            for row in data["apagar_receber"][1:]:
                html_content += '                        <tr>\n'
                for cell in row:
                    html_content += f'                            <td>{format_value(cell)}</td>\n'
                html_content += '                        </tr>\n'

        html_content += '''                    </tbody>
                </table>
            </div>
        </div>
'''

    # Script JavaScript para trocar entre CNPJs
    html_content += '''
        <script>
            function changeCNPJ() {
                const selected = document.getElementById('cnpj-select').value;
                const sections = document.querySelectorAll('.cnpj-section');
                sections.forEach(section => {
                    section.classList.add('hidden');
                });
                document.getElementById('cnpj-' + selected).classList.remove('hidden');
            }

            // Mostrar primeiro CNPJ ao carregar
            window.addEventListener('DOMContentLoaded', function() {
                changeCNPJ();
            });
        </script>

        <div class="timestamp">
            Dados gerados em: ''' + datetime.now().strftime("%d/%m/%Y às %H:%M:%S") + '''
            <br>
            Para atualizar, execute novamente: <code>python generate_static.py</code>
        </div>
    </div>

    <div class="footer">
        <p>GRUTA GESTÃO © 2024</p>
        <p>Sistema de Gestão Financeira - Versão Estática</p>
    </div>
</body>
</html>
'''

    return html_content

def main():
    print("[INICIANDO] Geração de HTML estático com dados do Google Sheets")
    print()

    # Obter credenciais
    gc = get_credentials()
    if not gc:
        print("[ERRO] Não foi possível obter credenciais. Abortando.")
        return

    # Coletar dados de todos os CNPJs
    print("[PROCESSANDO] Coletando dados...")
    all_data = {}
    for cnpj in SPREADSHEET_IDS.keys():
        data = get_cnpj_data(gc, cnpj)
        all_data[cnpj] = data

    # Gerar HTML
    print("[GERANDO] Criando arquivo HTML...")
    html_content = generate_html(all_data)

    # Salvar arquivo
    output_path = "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[OK] Arquivo gerado com sucesso: {output_path}")
    print()
    print("[PRÓXIMOS PASSOS]")
    print("1. Abra 'index.html' em um navegador para visualizar")
    print("2. Para fazer upload para GitHub Pages, execute:")
    print("   git add index.html")
    print("   git commit -m 'Atualizar dados do Google Sheets'")
    print("   git push origin main")
    print()

if __name__ == "__main__":
    main()
