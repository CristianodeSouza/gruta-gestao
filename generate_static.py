#!/usr/bin/env python3
import os
import gspread
from datetime import datetime, timedelta
import json
from collections import defaultdict

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
    if not value or value == '' or value == 0:
        return "R$ 0,00"
    try:
        float_val = float(str(value).replace(",", "."))
        formatted = f"{float_val:,.2f}"
        formatted = formatted.replace(",", "@").replace(".", ",").replace("@", ".")
        return f"R$ {formatted}"
    except:
        return "R$ 0,00"

def parse_date(date_str):
    for fmt in ["%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

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

        data_col, entrada_col, saida_col, descricao_col = 2, 8, 9, 5
        transactions = []

        for row in data[header_row + 1:]:
            if not any(row):
                continue
            try:
                data_str = row[data_col] if len(row) > data_col else ""
                entrada = float(str(row[entrada_col]).replace(",", ".")) if len(row) > entrada_col and row[entrada_col] else 0
                saida = float(str(row[saida_col]).replace(",", ".")) if len(row) > saida_col and row[saida_col] else 0
                descricao = row[descricao_col] if len(row) > descricao_col else ""

                parsed_date = parse_date(data_str)
                if parsed_date:
                    transactions.append({
                        "data": data_str,
                        "data_obj": parsed_date,
                        "entrada": entrada,
                        "saida": saida,
                        "descricao": descricao
                    })
            except:
                continue

        return sorted(transactions, key=lambda x: x["data_obj"], reverse=True)
    except:
        return []

def calculate_period_metrics(transactions, days_back):
    cutoff = datetime.now() - timedelta(days=days_back)
    period_trans = [t for t in transactions if t["data_obj"] >= cutoff]

    if not period_trans:
        return None

    return {
        "entrada": sum(t["entrada"] for t in period_trans),
        "saida": sum(t["saida"] for t in period_trans),
        "count": len(period_trans)
    }

def generate_insights(transactions):
    insights = []

    if not transactions:
        return insights

    today_metrics = calculate_period_metrics(transactions, 1)
    week_metrics = calculate_period_metrics(transactions, 7)
    month_metrics = calculate_period_metrics(transactions, 30)
    prev_month_metrics = calculate_period_metrics([t for t in transactions if t["data_obj"] < (datetime.now() - timedelta(days=30))], 30)

    # Comparação com mês anterior
    if month_metrics and prev_month_metrics and prev_month_metrics["entrada"] > 0:
        growth = ((month_metrics["entrada"] - prev_month_metrics["entrada"]) / prev_month_metrics["entrada"]) * 100
        if growth > 10:
            insights.append(f"📈 Receita em alta! Crescimento de {growth:.1f}% vs mês anterior")
        elif growth < -10:
            insights.append(f"📉 Atenção! Queda de {abs(growth):.1f}% na receita vs mês anterior")

    # Análise de despesa
    if month_metrics and month_metrics["entrada"] > 0:
        expense_ratio = (month_metrics["saida"] / month_metrics["entrada"]) * 100
        if expense_ratio > 70:
            insights.append(f"⚠️ Despesas altas! Consumem {expense_ratio:.1f}% da receita")
        elif expense_ratio < 30:
            insights.append(f"✅ Eficiência ótima! Despesas apenas {expense_ratio:.1f}% da receita")

    # Ticket médio
    if week_metrics and week_metrics["count"] > 0:
        ticket = week_metrics["entrada"] / week_metrics["count"]
        insights.append(f"💰 Ticket médio (7 dias): {format_currency(ticket)}")

    # Dias com movimento
    if today_metrics and today_metrics["entrada"] > 0:
        if week_metrics and week_metrics["count"] > 0:
            avg_daily = week_metrics["entrada"] / 7
            if today_metrics["entrada"] > avg_daily * 1.3:
                insights.append(f"🎯 Hoje foi um ótimo dia! {((today_metrics['entrada']/avg_daily - 1) * 100):.0f}% acima da média")

    # Sazonalidade por dia da semana
    day_totals = defaultdict(lambda: {"entrada": 0, "count": 0})
    for t in transactions[-90:]:  # últimos 90 dias
        day_name = t["data_obj"].strftime("%A")
        day_totals[day_name]["entrada"] += t["entrada"]
        day_totals[day_name]["count"] += 1

    if day_totals:
        best_day = max(day_totals.items(), key=lambda x: x[1]["entrada"] / max(x[1]["count"], 1) if x[1]["count"] > 0 else 0)
        day_pt = {"Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta", "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo"}
        insights.append(f"📅 Melhor dia da semana: {day_pt.get(best_day[0], best_day[0])}")

    # Concentração de receita
    if month_metrics and month_metrics["count"] > 0:
        top_10_pct = sum(t["entrada"] for t in transactions[:int(len(transactions) * 0.1)])
        if month_metrics["entrada"] > 0:
            concentration = (top_10_pct / month_metrics["entrada"]) * 100
            if concentration > 40:
                insights.append(f"🎯 {concentration:.0f}% da receita vem de poucos clientes - diversificar é importante")

    return insights[:5]  # Top 5 insights

def categorize_by_description(transactions):
    categories = defaultdict(float)
    for t in transactions[-1000:]:  # últimos 1000 para análise
        desc_lower = t["descricao"].lower()
        if "alim" in desc_lower or "comida" in desc_lower or "pedido" in desc_lower:
            categories["Alimentação"] += t["entrada"] if t["entrada"] > 0 else -t["saida"]
        elif "fornec" in desc_lower or "compra" in desc_lower or "suprimento" in desc_lower:
            categories["Fornecimento"] += t["entrada"] if t["entrada"] > 0 else -t["saida"]
        elif "pessoal" in desc_lower or "salário" in desc_lower or "folha" in desc_lower:
            categories["Pessoal"] += t["entrada"] if t["entrada"] > 0 else -t["saida"]
        elif "aluguel" in desc_lower or "imóvel" in desc_lower or "locação" in desc_lower:
            categories["Aluguel"] += t["entrada"] if t["entrada"] > 0 else -t["saida"]
        else:
            categories["Outros"] += t["entrada"] if t["entrada"] > 0 else -t["saida"]

    return categories

def get_daily_data(transactions):
    daily = defaultdict(lambda: {"entrada": 0, "saida": 0})
    for t in transactions[-90:]:  # últimos 90 dias
        date_key = t["data_obj"].strftime("%Y-%m-%d")
        daily[date_key]["entrada"] += t["entrada"]
        daily[date_key]["saida"] += t["saida"]
    return daily

def get_cnpj_data(gc, cnpj):
    try:
        spreadsheet_id = SPREADSHEET_IDS[cnpj]
        transactions = read_livro_diario(gc, spreadsheet_id)

        total_entrada = sum(t["entrada"] for t in transactions)
        total_saida = sum(t["saida"] for t in transactions)
        saldo = total_entrada - total_saida

        month_metrics = calculate_period_metrics(transactions, 30) or {"entrada": 0, "saida": 0, "count": 0}
        week_metrics = calculate_period_metrics(transactions, 7) or {"entrada": 0, "saida": 0, "count": 0}

        margem = (month_metrics["saida"] / month_metrics["entrada"] * 100) if month_metrics["entrada"] > 0 else 0
        ticket = month_metrics["entrada"] / month_metrics["count"] if month_metrics["count"] > 0 else 0

        insights = generate_insights(transactions)
        categories = categorize_by_description(transactions)
        daily_data = get_daily_data(transactions)

        return {
            "transactions": transactions,
            "total_entrada": total_entrada,
            "total_saida": total_saida,
            "saldo": saldo,
            "month_entrada": month_metrics["entrada"],
            "month_saida": month_metrics["saida"],
            "week_entrada": week_metrics["entrada"],
            "week_saida": week_metrics["saida"],
            "margem": margem,
            "ticket_medio": ticket,
            "total_transacoes": len(transactions),
            "insights": insights,
            "categories": categories,
            "daily_data": daily_data
        }
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return None

def generate_html(all_data):
    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>GRUTA GESTAO - Dashboard Inteligente</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        html, body { width: 100%; height: 100%; overflow-x: hidden; }
        :root {
            --primary: #1f2937; --accent: #3b82f6; --success: #10b981;
            --danger: #ef4444; --warning: #f59e0b; --light: #f9fafb;
            --border: #e5e7eb; --text: #111827; --text-light: #6b7280;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--light); color: var(--text); display: flex;
            flex-direction: column; height: 100vh;
        }
        header {
            background: var(--primary); color: white; padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); flex-shrink: 0;
        }
        .header-content {
            max-width: 1400px; margin: 0 auto; display: flex;
            justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;
        }
        .header-title { font-size: 1.25rem; font-weight: 700; flex: 1; min-width: 200px; }
        select {
            padding: 0.75rem 1rem; border: 1px solid var(--border);
            border-radius: 6px; font-size: 1rem; background: white; cursor: pointer; min-width: 280px;
        }
        select:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
        main { flex: 1; overflow-y: auto; padding: 1rem; -webkit-overflow-scrolling: touch; }
        .container { max-width: 1400px; margin: 0 auto; }

        .insights-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .insights-title {
            font-size: 1rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;
        }
        .insights-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; }
        .insight-item {
            background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 6px;
            border-left: 4px solid rgba(255,255,255,0.5);
        }

        .kpi-section {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 1rem; margin-bottom: 1.5rem;
        }
        .kpi {
            background: white; border-radius: 8px; padding: 1.25rem 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid var(--accent);
        }
        .kpi.success { border-left-color: var(--success); }
        .kpi.danger { border-left-color: var(--danger); }
        .kpi.warning { border-left-color: var(--warning); }
        .kpi-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
        .kpi-label { font-size: 0.75rem; color: var(--text-light); margin-bottom: 0.25rem; text-transform: uppercase; font-weight: 600; letter-spacing: 0.3px; }
        .kpi-value { font-size: 1.5rem; font-weight: 700; color: var(--text); line-height: 1.1; word-break: break-word; }
        .kpi-subtext { font-size: 0.8rem; color: var(--text-light); margin-top: 0.25rem; }

        .charts-section { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .chart-card { background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .chart-title { font-size: 1rem; font-weight: 700; margin-bottom: 0.75rem; color: var(--text); border-bottom: 2px solid var(--accent); padding-bottom: 0.5rem; }
        .chart-container { position: relative; height: 250px; width: 100%; }

        .table-section { background: white; border-radius: 8px; padding: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
        .table-title { font-size: 1rem; font-weight: 700; margin-bottom: 1rem; color: var(--text); }
        .table-wrapper { overflow-x: auto; -webkit-overflow-scrolling: touch; }
        table { width: 100%; border-collapse: collapse; }
        table thead { background: #f5f5f5; border-bottom: 2px solid var(--border); }
        table th { padding: 1rem; text-align: left; font-weight: 600; color: var(--text); font-size: 0.9rem; }
        table td { padding: 1rem; border-bottom: 1px solid var(--border); }
        table tbody tr:hover { background: #f9f9f9; }
        .value-positive { color: var(--success); font-weight: 600; }
        .value-negative { color: var(--danger); font-weight: 600; }

        .hidden { display: none; }
        footer { padding: 1rem; font-size: 0.8rem; color: var(--text-light); text-align: center; border-top: 1px solid var(--border); }

        @media (max-width: 768px) {
            .insights-list { grid-template-columns: 1fr; }
            .kpi-section { grid-template-columns: 1fr 1fr; }
            .charts-section { grid-template-columns: 1fr; }
            .chart-container { height: 200px; }
            table th, table td { padding: 0.8rem; font-size: 0.85rem; }
            .header-title { font-size: 1rem; }
            select { min-width: 100%; }
        }

        @media (max-width: 480px) {
            .kpi-section { grid-template-columns: 1fr; }
            .chart-container { height: 180px; }
            table td[data-label]:before { content: attr(data-label) ": "; font-weight: 700; }
            table, table thead, table tbody, table th, table td, table tr { display: block; }
            table thead { display: none; }
            table tr { border-bottom: 2px solid var(--border); margin-bottom: 1rem; }
            table td { padding: 0.75rem 0; text-align: right; }
            table td[data-label]:before { float: left; }
            footer { font-size: 0.7rem; padding: 0.75rem; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="header-title">🎯 GRUTA GESTAO - Dashboard Inteligente</div>
            <select id="cnpj-select" onchange="changeCNPJ()">
'''

    for cnpj in SPREADSHEET_IDS.keys():
        html += f'                <option value="{cnpj}">{CNPJ_NAMES[cnpj]}</option>\n'

    html += '''            </select>
        </div>
    </header>

    <main>
        <div class="container">
'''

    chart_data = {}

    for cnpj, data in all_data.items():
        if not data:
            continue

        # Preparar dados para gráficos
        days = sorted(data["daily_data"].keys())[-30:]
        daily_entrada = [data["daily_data"][d]["entrada"] for d in days]
        daily_saida = [data["daily_data"][d]["saida"] for d in days]

        chart_data[cnpj] = {
            "days": days,
            "entrada": daily_entrada,
            "saida": daily_saida,
            "categories": list(data["categories"].keys()),
            "categoria_valores": list(data["categories"].values()),
        }

        # Insights
        html += f'''            <div id="cnpj-{cnpj}" class="cnpj-section">
                <div class="insights-section">
                    <div class="insights-title">💡 Insights Gerenciais</div>
                    <div class="insights-list">
'''

        for insight in data["insights"]:
            html += f'                        <div class="insight-item">{insight}</div>\n'

        html += '''                    </div>
                </div>

                <div class="kpi-section">
                    <div class="kpi success">
                        <div class="kpi-icon">📈</div>
                        <div class="kpi-label">Receita (30 dias)</div>
                        <div class="kpi-value">''' + format_currency(data["month_entrada"]) + '''</div>
                        <div class="kpi-subtext">Total: ''' + format_currency(data["total_entrada"]) + '''</div>
                    </div>

                    <div class="kpi danger">
                        <div class="kpi-icon">📉</div>
                        <div class="kpi-label">Despesa (30 dias)</div>
                        <div class="kpi-value">''' + format_currency(data["month_saida"]) + '''</div>
                        <div class="kpi-subtext">Total: ''' + format_currency(data["total_saida"]) + '''</div>
                    </div>

                    <div class="kpi success">
                        <div class="kpi-icon">💰</div>
                        <div class="kpi-label">Saldo</div>
                        <div class="kpi-value">''' + format_currency(data["saldo"]) + '''</div>
                        <div class="kpi-subtext">Líquido</div>
                    </div>

                    <div class="kpi warning">
                        <div class="kpi-icon">📊</div>
                        <div class="kpi-label">Margem Despesa</div>
                        <div class="kpi-value">''' + f'{data["margem"]:.1f}%' + '''</div>
                        <div class="kpi-subtext">% da receita</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-icon">💵</div>
                        <div class="kpi-label">Ticket Médio</div>
                        <div class="kpi-value">''' + format_currency(data["ticket_medio"]) + '''</div>
                        <div class="kpi-subtext">Por transação</div>
                    </div>

                    <div class="kpi">
                        <div class="kpi-icon">📅</div>
                        <div class="kpi-label">Semana Atual</div>
                        <div class="kpi-value">''' + format_currency(data["week_entrada"]) + '''</div>
                        <div class="kpi-subtext">7 últimos dias</div>
                    </div>
                </div>

                <div class="charts-section">
                    <div class="chart-card">
                        <div class="chart-title">📈 Fluxo de Caixa (30 dias)</div>
                        <div class="chart-container">
                            <canvas id="chart-cash-''' + cnpj + '''"></canvas>
                        </div>
                    </div>

                    <div class="chart-card">
                        <div class="chart-title">🎯 Receita vs Despesa</div>
                        <div class="chart-container">
                            <canvas id="chart-pie-''' + cnpj + '''"></canvas>
                        </div>
                    </div>

                    <div class="chart-card">
                        <div class="chart-title">📂 Distribuição por Categoria</div>
                        <div class="chart-container">
                            <canvas id="chart-cat-''' + cnpj + '''"></canvas>
                        </div>
                    </div>
                </div>

                <div class="table-section">
                    <div class="table-title">📋 Últimas Transações</div>
                    <div class="table-wrapper">
                        <table>
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Descrição</th>
                                    <th>Entrada</th>
                                    <th>Saída</th>
                                    <th>Saldo</th>
                                </tr>
                            </thead>
                            <tbody>
'''

        for trans in data["transactions"][:25]:
            entrada_display = format_currency(trans["entrada"]) if trans["entrada"] > 0 else "-"
            saida_display = format_currency(trans["saida"]) if trans["saida"] > 0 else "-"
            valor = trans["entrada"] - trans["saida"]
            valor_class = "value-positive" if valor > 0 else "value-negative"
            descricao = trans["descricao"][:30]

            html += f'''                                <tr>
                                    <td data-label="Data">{trans["data"][:10]}</td>
                                    <td data-label="Descrição">{descricao}</td>
                                    <td data-label="Entrada">{entrada_display}</td>
                                    <td data-label="Saída">{saida_display}</td>
                                    <td data-label="Saldo" class="{valor_class}">{format_currency(valor)}</td>
                                </tr>
'''

        html += '''                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
'''

    html += '''        </div>
    </main>

    <footer>
        <p>Dashboard Inteligente | Atualizado em ''' + datetime.now().strftime("%d/%m/%Y %H:%M") + ''' | Execute: python generate_static.py</p>
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

            // Gráfico de Fluxo de Caixa
            const ctxCash = document.getElementById('chart-cash-' + cnpj);
            if (ctxCash && charts['cash-' + cnpj]) charts['cash-' + cnpj].destroy();
            if (ctxCash) {
                charts['cash-' + cnpj] = new Chart(ctxCash, {
                    type: 'line',
                    data: {
                        labels: data.days,
                        datasets: [
                            {
                                label: 'Receita',
                                data: data.entrada,
                                borderColor: '#10b981',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                tension: 0.3,
                                fill: true
                            },
                            {
                                label: 'Despesa',
                                data: data.saida,
                                borderColor: '#ef4444',
                                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                tension: 0.3,
                                fill: true
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: true, position: 'top' } },
                        scales: { y: { beginAtZero: true } }
                    }
                });
            }

            // Gráfico Receita vs Despesa
            const ctxPie = document.getElementById('chart-pie-' + cnpj);
            if (ctxPie && charts['pie-' + cnpj]) charts['pie-' + cnpj].destroy();
            if (ctxPie) {
                const totalEntrada = data.entrada.reduce((a, b) => a + b, 0);
                const totalSaida = data.saida.reduce((a, b) => a + b, 0);
                charts['pie-' + cnpj] = new Chart(ctxPie, {
                    type: 'doughnut',
                    data: {
                        labels: ['Receita', 'Despesa'],
                        datasets: [{
                            data: [totalEntrada, totalSaida],
                            backgroundColor: ['#10b981', '#ef4444'],
                            borderColor: ['#059669', '#dc2626'],
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

            // Gráfico de Categorias
            const ctxCat = document.getElementById('chart-cat-' + cnpj);
            if (ctxCat && charts['cat-' + cnpj]) charts['cat-' + cnpj].destroy();
            if (ctxCat) {
                charts['cat-' + cnpj] = new Chart(ctxCat, {
                    type: 'bar',
                    data: {
                        labels: data.categories,
                        datasets: [{
                            label: 'Valor',
                            data: data.categoria_valores,
                            backgroundColor: [
                                '#3b82f6',
                                '#10b981',
                                '#f59e0b',
                                '#ef4444',
                                '#8b5cf6'
                            ]
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: { x: { beginAtZero: true } }
                    }
                });
            }
        }

        window.addEventListener('load', () => {
            const first = document.getElementById('cnpj-select').value;
            changeCNPJ();
        });
    </script>
</body>
</html>
'''
    return html

print("[Gerando Dashboard Inteligente...]")

gc = get_credentials()
if not gc:
    print("[ERRO] Falha na autenticação com Google")
    exit(1)

all_data = {}
for cnpj in SPREADSHEET_IDS.keys():
    print(f"[Processando {cnpj}...]")
    all_data[cnpj] = get_cnpj_data(gc, cnpj)

print("[Gerando HTML...]")
html = generate_html(all_data)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

file_size = len(html) / 1024
print(f"[OK] Dashboard gerada: {file_size:.0f}KB")
