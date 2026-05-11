# Guia de Deploy - GRUTA GESTAO

## Deploy Rápido com Vercel + Railway

### Opção 1: Vercel (Frontend) + Railway (Backend) - RECOMENDADO

Esta é a configuração mais rápida e gratuita.

#### Passo 1: Preparar o GitHub

1. Fazer login em https://github.com
2. Ir para https://github.com/new
3. Criar novo repositório chamado `gruta-gestao`
4. Seguir as instruções para fazer commit dos arquivos

```bash
# Na pasta do projeto
git init
git add .
git commit -m "Inicial - GRUTA GESTAO"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/gruta-gestao.git
git push -u origin main
```

#### Passo 2: Deploy do Backend no Railway

1. Ir para https://railway.app
2. Fazer login/Registrar com GitHub
3. Clicar "New Project" > "Deploy from GitHub repo"
4. Selecionar `gruta-gestao`
5. Configurar as seguintes variáveis de ambiente:

```
PORT=5000
FLASK_ENV=production
```

6. Adicionar o arquivo de credenciais:
   - Ir para Settings > Variables
   - Adicionar um arquivo `gruta-gestao-7b3adc499256.json` com o conteúdo do credentials.json

7. Clique em "Deploy"

A aplicação estará disponível em: `https://seu-projeto-railway.up.railway.app`

#### Passo 3: Deploy do Frontend no Vercel

1. Ir para https://vercel.com
2. Fazer login com GitHub
3. Clicar "New Project"
4. Selecionar seu repositório `gruta-gestao`
5. Em "Root Directory", selecionar `frontend`
6. Em "Environment Variables", adicionar:

```
REACT_APP_API_URL=https://seu-projeto-railway.up.railway.app/api
```

Ou editar `frontend/js/app.js` linha 2:
```javascript
const API_URL = 'https://seu-projeto-railway.up.railway.app/api';
```

7. Clicar "Deploy"

Seu site estará em: `https://seu-projeto.vercel.app`

---

### Opção 2: Heroku (Tudo junto)

#### Passo 1: Instalar Heroku CLI

```bash
# Windows
npm install -g heroku

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Passo 2: Fazer Login e Criar App

```bash
heroku login
heroku create seu-app-gruta-gestao
```

#### Passo 3: Adicionar Credenciais

```bash
heroku config:set GOOGLE_CREDENTIALS_JSON="$(cat /path/to/gruta-gestao-7b3adc499256.json)"
```

#### Passo 4: Deploy

```bash
git push heroku main
```

Acessar em: `https://seu-app-gruta-gestao.herokuapp.com`

---

### Opção 3: PythonAnywhere (Backend simples)

1. Ir para https://www.pythonanywhere.com
2. Registrar conta gratuita
3. Fazer upload dos arquivos do backend
4. Configurar um "Web App" apontando para `server.py`
5. Adicionar as credenciais Google na seção de Files
6. Configurar a URL de acesso

---

## Configuração de CORS para Production

Se o frontend e backend estão em domínios diferentes, você precisa atualizar o CORS.

Em `backend/server.py`, modificar:

```python
CORS(app, origins=[
    "https://seu-projeto.vercel.app",
    "http://localhost:3000"  # Para desenvolvimento local
])
```

---

## Monitoramento em Production

### Ver logs do Railway
```bash
railway log
```

### Ver logs do Heroku
```bash
heroku logs --tail
```

### Testar a API

```bash
curl https://seu-app.com/api/health

# Resposta esperada:
# {"status":"online","timestamp":"2024-05-11T...","auth":"OK"}
```

---

## Troubleshooting

### Erro: "Credenciais não encontradas"
- Verificar se o arquivo JSON foi adicionado corretamente
- Na Railway: Settings > Variables > Adicionar arquivo
- No Heroku: `heroku config:get GOOGLE_CREDENTIALS_JSON`

### Erro: "CORS Error"
- Atualizar a variável `API_URL` no frontend
- Verificar se o backend está retornando headers CORS corretos

### Erro: "Módulo não encontrado"
- Garantir que `requirements.txt` está no backend
- Executar `pip install -r requirements.txt` localmente primeiro

### Aplicação lenta
- Ativar cache: Modificar `CACHE_DURATION` em `server.py`
- Usar CDN como CloudFlare
- Considerar upgrade de plano

---

## URL Pública para Compartilhar

Após deploy bem-sucedido, compartilhe a URL do Vercel:

```
https://seu-projeto.vercel.app
```

Os donos do restaurante podem acessar para:
- Ver dashboard em tempo real
- Filtrar transações
- Exportar dados
- Monitorar saúde financeira

---

## Próximos Passos

1. Testar todas as funcionalidades no navegador
2. Verificar responsividade em mobile
3. Compartilhar URL com os donos
4. Configurar alertas para anomalias financeiras
5. Adicionar autenticação (opcional) se necessário

Sucesso! 🚀
