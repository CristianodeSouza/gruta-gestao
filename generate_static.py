#!/usr/bin/env python3
import os
import gspread
from datetime import datetime
import json

SPREADSHEET_IDS = {
    "95594065000119": "1ZNxygVnszQ4X-28b5OLckMjlMZ1C519ahLTP-DDU8AU",
    "65313187/0001-29": "1W159OU4uYApYA1i9YJjEnnVKfACwckDN6kOt29qwOCI"
}

CNPJ_NAMES = {
    "95594065000119": "GRUTA - Grutatagliarierodrigues",
    "65313187/0001-29": "GRUTA - Nova Empresa Delivery"
}

def get_credentials():
    try:
        credentials_path = r"C:\Users\User\Downloads\gruta-gestao-6b88ee2d9c7b.json"
        if not os.path.exists(credentials_path):
            return None
        gc = gspread.service_account(filename=credentials_path)
        return gc
    except:
        return None

def format_currency(value):
    """Formata valor como moeda brasileira: R$ 1.234,56"""
    if not value or value == '' or value == 0:
        return "R$ 0,00"
    try:
        float_val = float(str(value).replace(",", "."))
        # Formatar com 2 casas decimais
        formatted = f"{float_val:,.2f}"
        # Trocar . por @ temporariamente para evitar conflito
        formatted = formatted.replace(",", "@").replace(".", ",").replace("@", ".")
        return f"R$ {formatted}"
    except:
        return "R$ 0,00"

def read_livro_diario(gc, spreadsheet_id):
    try:
        spreadsheet = gc.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet("Livro Diário FC")
        data = worksheet.get_all_values()

        header_row = None
        for i, row in enumerate(data):
            if len(row) > 2 and 'Data' in row:
                header_row = i
                break

        if header_row is None:
            return []

        data_col = 2
        entrada_col = 8
        saida_col = 9
        descricao_col = 5

        transactions = []
        for row in data[header_row + 1:]:
            if not any(row):
                continue
            try:
                data_str = row[data_col] if len(row) > data_col else ""
                entrada = float(str(row[entrada_col]).replace(",", ".")) if len(row) > entrada_col and row[entrada_col] else 0
                saida = float(str(row[saida_col]).replace(",", ".")) if len(row) > saida_col and row[saida_col] else 0
                descricao = row[descricao_col] if len(row) > descricao_col else ""
                valor = entrada - saida

                if valor != 0 or descricao.strip():
                    transactions.append({
                        "data": data_str,
                        "entrada": entrada,
                        "saida": saida,
                        "valor": valor,
                        "descricao": descricao
                    })
            except:
                continue

        return transactions
    except Exception as e:
        return []

def get_cnpj_data(gc, cnpj):
    try:
        spreadsheet_id = SPREADSHEET_IDS[cnpj]
        transactions = read_livro_diario(gc, spreadsheet_id)

        total_entrada = sum(t["entrada"] for t in transactions)
        total_saida = sum(t["saida"] for t in transactions)
        saldo = total_entrada - total_saida

        dias_dados = {}
        for t in transactions:
            data = t["data"][:10] if len(t["data"]) >= 10 else t["data"]
            if data not in dias_dados:
                dias_dados[data] = {"entrada": 0, "saida": 0}
            dias_dados[data]["entrada"] += t["entrada"]
            dias_dados[data]["saida"] += t["saida"]

        return {
            "transactions": sorted(transactions, key=lambda x: x["data"], reverse=True),
            "summary": {
                "total_entrada": total_entrada,
                "total_saida": total_saida,
                "saldo": saldo,
                "total_transacoes": len(transactions),
                "ticket_medio": saldo / len(transactions) if transactions else 0,
                "margem": (saldo / total_entrada * 100) if total_entrada > 0 else 0,
            },
            "daily_data": dias_dados
        }
    except:
        return None

def generate_html(all_data):
    """Gera dashboard gerencial profissional e responsiva"""

    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GRUTA GESTAO - Dashboard Gerencial</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        html, body {
            width: 100%;
            height: 100%;
            overflow-x: hidden;
        }

        :root {
            --primary: #1f2937;
            --accent: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --light: #f9fafb;
            --border: #e5e7eb;
            --text: #111827;
            --text-light: #6b7280;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--light);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            background: var(--primary);
            color: white;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .header-title {
            font-size: 1.25rem;
            font-weight: 700;
            flex: 1;
            min-width: 200px;
        }

        select {
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 1rem;
            background: white;
            cursor: pointer;
            min-width: 280px;
        }

        select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        main {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            -webkit-overflow-scrolling: touch;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .kpi-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .kpi {
            background: white;
            border-radius: 8px;
            padding: 1.25rem 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid var(--accent);
        }

        .kpi.success { border-left-color: var(--success); }
        .kpi.danger { border-left-color: var(--danger); }

        .kpi-icon {
            font-size: 1.75rem;
            margin-bottom: 0.5rem;
        }

        .kpi-label {
            font-size: 0.75rem;
            color: var(--text-light);
            margin-bottom: 0.25rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text);
            line-height: 1.1;
            word-break: break-word;
        }

        .kpi-change {
            font-size: 0.75rem;
            color: var(--text-light);
            margin-top: 0.25rem;
        }

        .kpi-change.positive { color: var(--success); }
        .kpi-change.negative { color: var(--danger); }

        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .chart-card {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .chart-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: var(--text);
            border-bottom: 2px solid var(--accent);
            padding-bottom: 0.5rem;
        }

        .chart-container {
            position: relative;
            height: 250px;
            width: 100%;
        }

        .table-section {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            overflow: hidden;
        }

        .table-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: var(--text);
            border-bottom: 2px solid var(--accent);
            padding-bottom: 0.5rem;
        }

        .table-wrapper {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th {
            background: var(--light);
            padding: 0.75rem 0.5rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            border-bottom: 2px solid var(--border);
        }

        td {
            padding: 0.75rem 0.5rem;
            border-bottom: 1px solid var(--border);
        }

        tbody tr:hover {
            background: var(--light);
        }

        .value-positive {
            color: var(--success);
            font-weight: 600;
        }

        .value-negative {
            color: var(--danger);
            font-weight: 600;
        }

        footer {
            background: white;
            border-top: 1px solid var(--border);
            padding: 1rem;
            text-align: center;
            color: var(--text-light);
            font-size: 0.8rem;
            flex-shrink: 0;
        }

        .hidden { display: none; }

        /* RESPONSIVO MOBILE */
        @media (max-width: 768px) {
            header {
                padding: 0.75rem;
            }

            .header-content {
                flex-direction: column;
                align-items: stretch;
            }

            .header-title {
                font-size: 1.1rem;
                text-align: center;
            }

            select {
                min-width: 100%;
                width: 100%;
            }

            main {
                padding: 0.75rem;
            }

            .kpi-section {
                grid-template-columns: 1fr 1fr;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }

            .kpi {
                padding: 1rem 0.75rem;
            }

            .kpi-icon {
                font-size: 1.5rem;
                margin-bottom: 0.25rem;
            }

            .kpi-label {
                font-size: 0.7rem;
            }

            .kpi-value {
                font-size: 1.25rem;
            }

            .charts-section {
                grid-template-columns: 1fr;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }

            .chart-card {
                padding: 0.75rem;
            }

            .chart-title {
                font-size: 0.95rem;
                margin-bottom: 0.5rem;
            }

            .chart-container {
                height: 200px;
            }

            .table-section {
                padding: 0.75rem;
                margin-bottom: 1rem;
            }

            .table-title {
                font-size: 0.95rem;
            }

            table {
                font-size: 0.8rem;
            }

            th, td {
                padding: 0.5rem 0.4rem;
                font-size: 0.75rem;
            }

            /* Stack coluna de valores */
            thead {
                display: none;
            }

            tbody tr {
                display: block;
                border: 1px solid var(--border);
                border-radius: 6px;
                margin-bottom: 0.75rem;
                padding: 0.75rem;
                background: white;
            }

            td {
                display: block;
                border: none;
                padding: 0.5rem 0;
                text-align: left;
                border-bottom: 1px solid var(--border);
            }

            td:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }

            td:before {
                content: attr(data-label);
                font-weight: 600;
                display: inline-block;
                width: 100px;
                color: var(--text-light);
                font-size: 0.75rem;
                text-transform: uppercase;
                margin-right: 0.5rem;
            }

            footer {
                padding: 0.75rem;
                font-size: 0.75rem;
            }
        }

        @media (max-width: 480px) {
            .kpi-section {
                grid-template-columns: 1fr;
            }

            .header-title {
                font-size: 1rem;
            }

            .kpi-value {
                font-size: 1.1rem;
            }

            .chart-container {
                height: 180px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="header-title">GRUTA GESTAO Dashboard</div>
            <select id="cnpj-select" onchange="changeCNPJ()">
'''

    for cnpj in SPREADSHEET_IDS.keys():
        html += f'                <option value="{cnpj}">{cnpj}</option>\n'

    html += '''            </select>
        </div>
    </header>

    <main>
        <div class="container">
'''

    # Gerar dados para gráficos
    chart_data = {}

    for cnpj, data in all_data.items():
        if not data:
            continue

        summary = data["summary"]
        saldo_type = "positive" if summary["saldo"] >= 0 else "negative"

        # Preparar dados para gráficos
        days = sorted(data["daily_data"].keys())[-30:]  # Últimos 30 dias
        daily_entrada = [data["daily_data"][d]["entrada"] for d in days]
        daily_saida = [data["daily_data"][d]["saida"] for d in days]

        chart_data[cnpj] = {
            "days": days,
            "entrada": daily_entrada,
            "saida": daily_saida,
            "total_entrada": summary["total_entrada"],
            "total_saida": summary["total_saida"]
        }

        html += f'''
            <div id="cnpj-{cnpj}" class="cnpj-section">
                <div class="kpi-section">
                    <div class="kpi success">
                        <div class="kpi-icon">📈</div>
                        <div class="kpi-label">Receita</div>
                        <div class="kpi-value">{format_currency(summary["total_entrada"])}</div>
                    </div>

                    <div class="kpi danger">
                        <div class="kpi-icon">📉</div>
                        <div class="kpi-label">Despesa</div>
                        <div class="kpi-value">{format_currency(summary["total_saida"])}</div>
                    </div>

                    <div class="kpi {saldo_type}">
                        <div class="kpi-icon">💰</div>
                        <div class="kpi-label">Saldo</div>
                        <div class="kpi-value">{format_currency(summary["saldo"])}</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-label">Margem</div>
                        <div class="kpi-value">{summary["margem"]:.1f}%</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-icon">💵</div>
                        <div class="kpi-label">Ticket</div>
                        <div class="kpi-value">{format_currency(summary["ticket_medio"])}</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-icon">🔢</div>
                        <div class="kpi-label">Total</div>
                        <div class="kpi-value">{summary["total_transacoes"]}</div>
                    </div>
                </div>

                <div class="charts-section">
                    <div class="chart-card">
                        <div class="chart-title">Fluxo de Caixa (30 dias)</div>
                        <div class="chart-container">
                            <canvas id="chart-cash-{cnpj}"></canvas>
                        </div>
                    </div>

                    <div class="chart-card">
                        <div class="chart-title">Receita vs Despesa</div>
                        <div class="chart-container">
                            <canvas id="chart-pie-{cnpj}"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-section">
                    <div class="table-title">Ultimas Transacoes</div>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Descricao</th>
                                    <th>Entrada</th>
                                    <th>Saida</th>
                                    <th>Saldo</th>
                                </tr>
                            </thead>
                            <tbody>
'''

        for trans in data["transactions"][:25]:
            entrada_display = format_currency(trans["entrada"]) if trans["entrada"] > 0 else "-"
            saida_display = format_currency(trans["saida"]) if trans["saida"] > 0 else "-"
            valor_class = "value-positive" if trans["valor"] > 0 else "value-negative"
            descricao = trans["descricao"][:30]

            html += f'''                                <tr>
                                    <td data-label="Data">{trans["data"][:10]}</td>
                                    <td data-label="Descricao">{descricao}</td>
                                    <td data-label="Entrada">{entrada_display}</td>
                                    <td data-label="Saida">{saida_display}</td>
                                    <td data-label="Saldo" class="{valor_class}">{format_currency(trans["valor"])}</td>
                                </tr>
'''

        html += '''                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
'''

    html += '''
        </div>
    </main>

    <footer>
        <p>Atualizado em ''' + datetime.now().strftime("%d/%m/%Y %H:%M") + ''' | Execute: python generate_static.py</p>
    </footer>

    <script>
        const chartData = ''' + json.dumps(chart_data) + ''';
        let charts = {};

        function changeCNPJ() {
            const selected = document.getElementById('cnpj-select').value;
            document.querySelectorAll('.cnpj-section').forEach(s => s.classList.add('hidden'));
            document.getElementById('cnpj-' + selected).classList.remove('hidden');
            initCharts(selected);
        }

        function initCharts(cnpj) {
            const data = chartData[cnpj];
            if (!data) return;

            const ctxCash = document.getElementById('chart-cash-' + cnpj);
            const ctxPie = document.getElementById('chart-pie-' + cnpj);

            if (charts['cash-' + cnpj]) charts['cash-' + cnpj].destroy();
            if (charts['pie-' + cnpj]) charts['pie-' + cnpj].destroy();

            charts['cash-' + cnpj] = new Chart(ctxCash, {
                type: 'line',
                data: {
                    labels: data.days,
                    datasets: [
                        {
                            label: 'Entradas',
                            data: data.entrada,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.3,
                            fill: true,
                            borderWidth: 2,
                            pointRadius: 3,
                            pointBackgroundColor: '#10b981'
                        },
                        {
                            label: 'Saidas',
                            data: data.saida,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            tension: 0.3,
                            fill: true,
                            borderWidth: 2,
                            pointRadius: 3,
                            pointBackgroundColor: '#ef4444'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, position: 'bottom' },
                        filler: { propagate: true }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { callback: function(v) { return 'R$ ' + v.toFixed(0); } } }
                    }
                }
            });

            charts['pie-' + cnpj] = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: ['Receita', 'Despesa'],
                    datasets: [{
                        data: [data.total_entrada, data.total_saida],
                        backgroundColor: ['#10b981', '#ef4444'],
                        borderColor: ['white', 'white'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: true, position: 'bottom' } }
                }
            });
        }

        window.addEventListener('DOMContentLoaded', () => {
            changeCNPJ();
        });

        window.addEventListener('resize', () => {
            const selected = document.getElementById('cnpj-select').value;
            if (chartData[selected]) {
                initCharts(selected);
            }
        });
    </script>
</body>
</html>
'''

    return html

def main():
    print("[Gerando Dashboard...]")
    gc = get_credentials()
    if not gc:
        print("[ERRO] Credenciais nao encontradas")
        return

    print("[Processando dados...]")
    all_data = {}
    for cnpj in SPREADSHEET_IDS.keys():
        data = get_cnpj_data(gc, cnpj)
        all_data[cnpj] = data

    print("[Gerando HTML...]")
    html_content = generate_html(all_data)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    size = os.path.getsize("index.html") / 1024
    print(f"[OK] Dashboard gerada: {size:.0f}KB")

if __name__ == "__main__":
    main()
