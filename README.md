# GRUTA GESTAO - Sistema Completo de Gestão Financeira

Aplicação web responsiva para gestão financeira completa do restaurante GRUTA, com suporte a 2 CNPJs independentes.

## Funcionalidades

✓ **Dashboard Executivo** - Resumo de entradas, saídas, saldo e últimas transações
✓ **Livro Diário** - 8.500+ transações com filtros por descrição e categoria
✓ **Fluxo de Caixa** - Resumo mensal com gráficos
✓ **Contas a Pagar/Receber** - Gestão de contas pendentes
✓ **Planejamento Financeiro** - Projeções e planejamento
✓ **Análise Financeira** - Índices e tendências
✓ **Cadastros** - Master data de contas e categorias
✓ **Exportação** - Download de dados em CSV
✓ **Múltiplos CNPJs** - Suporte a 2 empresas independentes
✓ **Responsivo** - Funciona em desktop, tablet e mobile
✓ **Sincronização** - Atualização automática a cada 5 minutos

## Estrutura do Projeto

```
gruta-gestao-web/
├── backend/
│   ├── server.py          # API Flask
│   └── requirements.txt    # Dependências Python
├── frontend/
│   ├── index.html         # Interface HTML
│   ├── css/
│   │   └── style.css      # Estilos responsivos
│   └── js/
│       └── app.js         # Lógica da aplicação
└── README.md
```

## Instalação Local

### Pré-requisitos
- Python 3.8+
- Node.js/npm (opcional, para servir frontend)
- Navegador moderno

### 1. Configurar Backend

```bash
cd backend
pip install -r requirements.txt
```

Copiar o arquivo de credenciais do Google:
```bash
cp ~/Downloads/gruta-gestao-7b3adc499256.json .
```

### 2. Iniciar o Servidor

```bash
python server.py
```

A API estará disponível em `http://localhost:5000`

### 3. Abrir a Interface

Opção A - Arquivo local:
```bash
cd frontend
# Abrir index.html no navegador
```

Opção B - Servidor local (Python):
```bash
cd frontend
python -m http.server 8000
# Acessar http://localhost:8000
```

## API Endpoints

### Listar CNPJs
```
GET /api/cnpjs
```

### Resumo Executivo
```
GET /api/cnpj/{cnpj}/summary
```

### Livro Diário
```
GET /api/cnpj/{cnpj}/livro-diario?descricao=...&categoria=...
```

### Fluxo de Caixa
```
GET /api/cnpj/{cnpj}/fluxo-caixa
```

### Contas a Pagar/Receber
```
GET /api/cnpj/{cnpj}/contas
```

### Planejamento Financeiro
```
GET /api/cnpj/{cnpj}/planejamento
```

### Análise Financeira
```
GET /api/cnpj/{cnpj}/analise
```

### Cadastros
```
GET /api/cnpj/{cnpj}/cadastros
```

### Dados Completos
```
GET /api/cnpj/{cnpj}/completo
```

## Deploy na Nuvem

### Opção 1: Vercel (Recomendado para Frontend)

1. Fork este repositório no GitHub
2. Ir para https://vercel.com
3. Importar o repositório
4. Configure a variável de ambiente `API_URL` apontando para o backend

### Opção 2: Heroku (para Backend)

```bash
heroku create seu-app-name
heroku config:set GOOGLE_CREDENTIALS_JSON="$(cat credentials.json)"
git push heroku main
```

### Opção 3: Railway.app (Backend + Frontend)

1. Conectar GitHub
2. Selecionar o repositório
3. Configurar as variáveis de ambiente
4. Deploy automático

## Configuração

### Variáveis de Ambiente

```bash
# Backend
PORT=5000
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json

# Frontend (em index.html ou config.js)
API_URL=http://localhost:5000/api
```

### CNPJs Suportados

- **95594065000119** - GRUTA Restaurante Grutatagliarierodrigues
- **65313187/0001-29** - GRUTA Nova Empresa Delivery

## Dados Disponíveis

Cada CNPJ possui 11 abas de dados:

1. **Home** - Página inicial (35 linhas)
2. **Instruções FC** - Manual de fluxo de caixa (254 linhas)
3. **Livro Diário FC** - Transações diárias (~8.500 linhas)
4. **FC** - Fluxo de caixa consolidado (165 linhas, 59 colunas mensais)
5. **Gráficos** - Dados para visualização (109 linhas)
6. **Análise Fin** - Resumo financeiro (6 linhas)
7. **Planejamento Financeiro** - Projeções (145 linhas, 54 colunas mensais)
8. **A Pagar e A Receber** - Contas pendentes (18 linhas)
9. **Cadastros** - Master data (144 linhas)
10. **Contato** - Informações de contato (27 linhas)
11. **Planilha1** - Vazia

## Performance

- Cache de 5 minutos para dados
- Sincronização automática em background
- Tabelas paginadas até 100 registros
- Gráficos otimizados com Chart.js

## Suporte

Para reportar problemas ou sugerir melhorias, abra uma issue no GitHub.

## Licença

Privado - Uso exclusivo GRUTA Gestão

## Autores

Desenvolvido com ❤️ usando Python Flask, HTML5, CSS3 e JavaScript vanilla.

Data: Maio de 2026
