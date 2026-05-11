// Configuracao
const API_URL = 'http://localhost:5000/api';
let currentCNPJ = null;
let currentData = null;
let charts = {};

// Elementos DOM
const cnpjSelect = document.getElementById('cnpj-select');
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const filterDescricao = document.getElementById('filter-descricao');
const filterCategoria = document.getElementById('filter-categoria');
const btnExport = document.getElementById('btn-export');
const syncStatus = document.getElementById('sync-status');
const syncTime = document.getElementById('sync-time');
const footerTimestamp = document.getElementById('footer-timestamp');

// Inicializacao
document.addEventListener('DOMContentLoaded', () => {
    loadCNPJs();
    setupEventListeners();
    startAutoSync();
});

// ===== API CALLS =====

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erro na API: ${endpoint}`, error);
        updateSyncStatus(false);
        return null;
    }
}

async function loadCNPJs() {
    const data = await fetchAPI('/cnpjs');
    if (data && data.cnpjs) {
        cnpjSelect.innerHTML = '';
        data.cnpjs.forEach(cnpj => {
            const option = document.createElement('option');
            option.value = cnpj;
            option.textContent = cnpj;
            cnpjSelect.appendChild(option);
        });

        // Selecionar primeiro CNPJ
        if (data.cnpjs.length > 0) {
            cnpjSelect.value = data.cnpjs[0];
            loadCNPJData(data.cnpjs[0]);
        }
    }
}

async function loadCNPJData(cnpj) {
    if (!cnpj) return;

    currentCNPJ = cnpj;
    const data = await fetchAPI(`/cnpj/${cnpj}/completo`);

    if (data) {
        currentData = data;
        updateSyncStatus(true);
        updateAllTabs();
    }
}

// ===== SYNC =====

function startAutoSync() {
    setInterval(() => {
        if (currentCNPJ) {
            loadCNPJData(currentCNPJ);
        }
    }, 300000); // A cada 5 minutos
}

function updateSyncStatus(online) {
    const now = new Date();
    syncTime.textContent = now.toLocaleTimeString('pt-BR');
    footerTimestamp.textContent = now.toLocaleTimeString('pt-BR');

    if (online) {
        syncStatus.classList.remove('offline');
        syncStatus.textContent = '●';
    } else {
        syncStatus.classList.add('offline');
        syncStatus.textContent = '✕';
    }
}

// ===== TAB NAVIGATION =====

function setupEventListeners() {
    // Tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchTab(tabName);
        });
    });

    // CNPJ Selector
    cnpjSelect.addEventListener('change', (e) => {
        loadCNPJData(e.target.value);
    });

    // Filters
    filterDescricao.addEventListener('input', debounce(() => {
        updateLivroDiario();
    }, 500));

    filterCategoria.addEventListener('input', debounce(() => {
        updateLivroDiario();
    }, 500));

    // Export
    btnExport.addEventListener('click', exportToCSV);
}

function switchTab(tabName) {
    // Remover ativo de todos os abas
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });

    // Ativar aba selecionada
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
}

// ===== UPDATE FUNCTIONS =====

async function updateAllTabs() {
    updateDashboard();
    updateLivroDiario();
    updateFluxoCaixa();
    updateContas();
    updatePlanejamento();
    updateAnalise();
    updateCadastros();
}

function updateDashboard() {
    if (!currentData) return;

    const fc = currentData.fluxo_caixa;
    const livro = currentData.livro_diario;

    // Atualizar cards
    document.getElementById('card-entradas').textContent = formatCurrency(fc.entradas);
    document.getElementById('card-saidas').textContent = formatCurrency(fc.saidas);
    document.getElementById('card-saldo').textContent = formatCurrency(fc.saldo);
    document.getElementById('card-transacoes').textContent = livro.length;

    // Atualizar tabela de transacoes recentes
    const tableRecentes = document.getElementById('table-recentes');
    tableRecentes.innerHTML = '<thead><tr><th>Data</th><th>Descricao</th><th>Categoria</th><th>Valor</th></tr></thead><tbody>';

    livro.slice(0, 10).forEach(trans => {
        tableRecentes.innerHTML += `
            <tr>
                <td>${trans.data}</td>
                <td>${trans.descricao}</td>
                <td>${trans.categoria}</td>
                <td>${formatCurrency(trans.valor)}</td>
            </tr>
        `;
    });

    // Atualizar grafico resumo
    updateChart('chartResumo', {
        type: 'doughnut',
        data: {
            labels: ['Entradas', 'Saidas'],
            datasets: [{
                data: [fc.entradas, fc.saidas],
                backgroundColor: ['#4CAF50', '#f44336'],
                borderColor: '#fff'
            }]
        }
    });
}

function updateLivroDiario() {
    if (!currentData) return;

    let livro = currentData.livro_diario;

    // Aplicar filtros
    const descricao = filterDescricao.value.toLowerCase();
    const categoria = filterCategoria.value.toLowerCase();

    if (descricao) {
        livro = livro.filter(t => t.descricao.toLowerCase().includes(descricao));
    }
    if (categoria) {
        livro = livro.filter(t => t.categoria.toLowerCase().includes(categoria));
    }

    // Atualizar tabela
    const table = document.getElementById('table-livro-diario');
    table.innerHTML = '<thead><tr><th>Data</th><th>Descricao</th><th>Categoria</th><th>Valor</th></tr></thead><tbody>';

    livro.forEach(trans => {
        table.innerHTML += `
            <tr>
                <td>${trans.data}</td>
                <td>${trans.descricao}</td>
                <td>${trans.categoria}</td>
                <td>${formatCurrency(trans.valor)}</td>
            </tr>
        `;
    });

    if (livro.length === 0) {
        table.innerHTML += '<tr class="loading-row"><td colspan="4">Nenhuma transacao encontrada</td></tr>';
    }
}

function updateFluxoCaixa() {
    if (!currentData) return;

    const fc = currentData.fluxo_caixa;

    document.getElementById('fluxo-entradas').textContent = formatCurrency(fc.entradas);
    document.getElementById('fluxo-saidas').textContent = formatCurrency(fc.saidas);
    document.getElementById('fluxo-saldo').textContent = formatCurrency(fc.saldo);

    // Grafico fluxo
    updateChart('chartFluxo', {
        type: 'bar',
        data: {
            labels: ['Entradas', 'Saidas', 'Saldo'],
            datasets: [{
                label: 'Valores',
                data: [fc.entradas, fc.saidas, fc.saldo],
                backgroundColor: ['#4CAF50', '#f44336', '#2196F3']
            }]
        }
    });
}

function updateContas() {
    if (!currentData) return;

    const contas = currentData.apagar_receber;

    // Calcular totais (baseado em valores numericos)
    let totalReceber = 0, totalPagar = 0;

    contas.forEach(conta => {
        // Assumir que pares de colunas alternadas representam valores
        for (let i = 4; i < conta.length; i++) {
            const val = parseFloat(conta[i]) || 0;
            if (val > 0) totalReceber += val;
            if (val < 0) totalPagar += Math.abs(val);
        }
    });

    document.getElementById('total-receber').textContent = formatCurrency(totalReceber);
    document.getElementById('total-pagar').textContent = formatCurrency(totalPagar);

    // Atualizar tabela
    const table = document.getElementById('table-contas');
    table.innerHTML = '<thead><tr><th>Descricao</th><th>Valor</th><th>Data</th><th>Status</th></tr></thead><tbody>';

    contas.slice(0, 20).forEach(conta => {
        const desc = conta[0] || conta[1] || 'Sem descricao';
        const valor = conta[4] || 0;
        const data = conta[2] || '--';
        const status = valor > 0 ? 'A Receber' : 'A Pagar';

        table.innerHTML += `
            <tr>
                <td>${desc}</td>
                <td>${formatCurrency(valor)}</td>
                <td>${data}</td>
                <td>${status}</td>
            </tr>
        `;
    });
}

function updatePlanejamento() {
    if (!currentData) return;

    const planejamento = currentData.planejamento;

    // Atualizar tabela
    const table = document.getElementById('table-planejamento');
    table.innerHTML = '<thead><tr><th>Periodo</th><th>Previso Entradas</th><th>Previso Saidas</th><th>Previso Saldo</th></tr></thead><tbody>';

    planejamento.slice(0, 12).forEach((linha, idx) => {
        if (!linha || linha.length === 0) return;

        const periodo = linha[0] || `Mes ${idx+1}`;
        const entradas = parseFloat(linha[1]) || 0;
        const saidas = parseFloat(linha[2]) || 0;
        const saldo = entradas - saidas;

        table.innerHTML += `
            <tr>
                <td>${periodo}</td>
                <td>${formatCurrency(entradas)}</td>
                <td>${formatCurrency(saidas)}</td>
                <td>${formatCurrency(saldo)}</td>
            </tr>
        `;
    });

    // Grafico planejamento
    const periodos = [];
    const entradas = [];
    const saidas = [];

    planejamento.slice(0, 12).forEach(linha => {
        if (linha && linha.length > 2) {
            periodos.push(linha[0] || 'N/A');
            entradas.push(parseFloat(linha[1]) || 0);
            saidas.push(parseFloat(linha[2]) || 0);
        }
    });

    updateChart('chartPlanejamento', {
        type: 'line',
        data: {
            labels: periodos,
            datasets: [
                {
                    label: 'Entradas',
                    data: entradas,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Saidas',
                    data: saidas,
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.4
                }
            ]
        }
    });
}

function updateAnalise() {
    if (!currentData) return;

    const analise = currentData.analise_fin;
    const fc = currentData.fluxo_caixa;

    // Calcular metricas
    const totalEntradas = fc.entradas || 1;
    const saudeFinanceira = fc.saldo > 0 ? 'Saudavel' : 'Critica';
    const tendencia = fc.saldo > 0 ? 'Crescente' : 'Decrescente';
    const margem = totalEntradas > 0 ? ((fc.saldo / totalEntradas) * 100).toFixed(1) : 0;

    document.getElementById('analise-saude').textContent = saudeFinanceira;
    document.getElementById('analise-tendencia').textContent = tendencia;
    document.getElementById('analise-margem').textContent = `${margem}%`;

    // Atualizar tabela
    const table = document.getElementById('table-analise');
    table.innerHTML = '<thead><tr><th>Metrica</th><th>Valor</th><th>Status</th></tr></thead><tbody>';

    const metricas = [
        { nome: 'Saude Financeira', valor: saudeFinanceira, status: fc.saldo > 0 ? '✓' : '✗' },
        { nome: 'Tendencia', valor: tendencia, status: fc.saldo > 0 ? '↑' : '↓' },
        { nome: 'Margem Operacional', valor: `${margem}%`, status: margem > 10 ? 'Boa' : 'Baixa' },
        { nome: 'Total Entradas', valor: formatCurrency(fc.entradas), status: '✓' },
        { nome: 'Total Saidas', valor: formatCurrency(fc.saidas), status: '✓' }
    ];

    metricas.forEach(metrica => {
        table.innerHTML += `
            <tr>
                <td>${metrica.nome}</td>
                <td>${metrica.valor}</td>
                <td>${metrica.status}</td>
            </tr>
        `;
    });
}

function updateCadastros() {
    if (!currentData) return;

    const cadastros = currentData.cadastros;

    // Atualizar tabela
    const table = document.getElementById('table-cadastros');
    table.innerHTML = '<thead><tr><th>ID</th><th>Nome</th><th>Tipo</th><th>Saldo</th><th>Status</th></tr></thead><tbody>';

    cadastros.slice(0, 50).forEach((linha, idx) => {
        if (!linha || linha.length === 0) return;

        const id = idx + 1;
        const nome = linha[1] || 'Sem nome';
        const tipo = linha[2] || '--';
        const saldo = formatCurrency(parseFloat(linha[3]) || 0);
        const status = 'Ativo';

        table.innerHTML += `
            <tr>
                <td>${id}</td>
                <td>${nome}</td>
                <td>${tipo}</td>
                <td>${saldo}</td>
                <td>${status}</td>
            </tr>
        `;
    });
}

// ===== CHARTS =====

function updateChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    // Destruir chart anterior se existir
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    // Criar novo chart
    charts[canvasId] = new Chart(ctx, {
        type: config.type,
        data: config.data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: config.type === 'doughnut' || config.type === 'pie' ? {} : {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toLocaleString('pt-BR');
                        }
                    }
                }
            }
        }
    });
}

// ===== EXPORT =====

function exportToCSV() {
    if (!currentData || !currentData.livro_diario) return;

    let csv = 'Data,Descricao,Categoria,Valor\n';

    currentData.livro_diario.forEach(trans => {
        csv += `"${trans.data}","${trans.descricao}","${trans.categoria}",${trans.valor}\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `livro-diario-${currentCNPJ}-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ===== UTILITIES =====

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value || 0);
}

function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Sincronizacao inicial
updateSyncStatus(true);
