# GRUTA GESTAO - Instruções Iniciais

Bem-vindo ao sistema GRUTA GESTAO! Este documento guia você através dos primeiros passos.

## 1. Teste Local (Seu Computador)

### Passo 1: Preparar as Credenciais

1. Copiar o arquivo `gruta-gestao-7b3adc499256.json` que está em `Downloads`
2. Colar dentro da pasta `gruta-gestao-web/backend/`

```bash
cp ~/Downloads/gruta-gestao-7b3adc499256.json gruta-gestao-web/backend/
```

### Passo 2: Iniciar o Servidor

**No Windows (CMD ou PowerShell):**
```bash
cd gruta-gestao-web\backend
pip install -r requirements.txt
python server.py
```

**No Mac/Linux:**
```bash
cd gruta-gestao-web/backend
pip3 install -r requirements.txt
python3 server.py
```

Você deve ver:
```
[OK] Autenticacao Google Sheets bem-sucedida
 * Running on http://localhost:5000
```

### Passo 3: Abrir a Interface

Opção A - Clique duplo no arquivo:
- Ir para `gruta-gestao-web/frontend/`
- Duplo clique em `index.html`

Opção B - Servidor local (recomendado):
```bash
cd gruta-gestao-web/frontend
python -m http.server 8000
```
Então acesse: http://localhost:8000

Você verá a interface com:
- Seletor de CNPJ
- Dashboard com resumo
- Abas para Livro Diário, Fluxo de Caixa, etc.

### Passo 4: Testar as Funcionalidades

1. Selecionar um CNPJ no dropdown
2. Clicar nas abas para explorar os dados:
   - **Dashboard**: Resumo executivo com gráficos
   - **Livro Diário**: Todas as transações com filtros
   - **Fluxo de Caixa**: Entradas vs Saídas
   - **Contas**: A Pagar e Receber
   - **Planejamento**: Projeções futuras
   - **Análise**: Índices financeiros
   - **Cadastros**: Master data

3. Testar exportação:
   - Ir para "Livro Diário"
   - Clicar "Exportar CSV"

## 2. Deploy na Nuvem (Compartilhar com Donos)

### Opção Recomendada: Railway + Vercel (Gratuito)

**Passo 1: Criar Repositório no GitHub**

1. Ir para https://github.com/new
2. Criar repositório chamado `gruta-gestao`
3. Fazer upload dos arquivos:

```bash
cd gruta-gestao-web
git init
git add .
git commit -m "GRUTA GESTAO - Sistema de Gestao"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/gruta-gestao.git
git push -u origin main
```

**Passo 2: Deploy do Backend (Railway)**

1. Ir para https://railway.app
2. Conectar com GitHub
3. Criar novo projeto
4. Selecionar repositório `gruta-gestao`
5. Adicionar credenciais em "Variables"
6. Deploy automático!

Backend URL: `https://seu-app-railway.up.railway.app`

**Passo 3: Deploy do Frontend (Vercel)**

1. Ir para https://vercel.com
2. Conectar com GitHub
3. Importar repositório
4. Root Directory: `frontend`
5. Adicionar ENV: `REACT_APP_API_URL=https://seu-app-railway.up.railway.app/api`
6. Deploy!

Frontend URL: `https://seu-app.vercel.app`

### Compartilhar com Donos

Enviar para os donos do restaurante:

```
URL: https://seu-app.vercel.app

Eles podem:
✓ Ver dashboard em tempo real
✓ Filtrar transações por data/categoria
✓ Exportar dados em CSV
✓ Acompanhar fluxo de caixa diário
✓ Monitorar contas a pagar/receber
✓ Ver projeções financeiras
```

## 3. Dados Disponíveis

Cada CNPJ tem acesso a 11 abas de dados:

| Aba | Linhas | Descrição |
|-----|--------|-----------|
| Home | 35 | Página inicial |
| Livro Diário | 8.500+ | **Transações diárias** (principal) |
| FC | 165 | Fluxo de caixa consolidado |
| Planejamento | 145 | Projeções financeiras |
| A Pagar/Receber | 18 | Contas pendentes |
| Análise Fin | 6 | Resumo de análise |
| Cadastros | 144 | Contas e categorias |
| Gráficos | 109 | Dados para visualização |
| Instruções | 254 | Manual de uso |
| Contato | 27 | Contatos |
| Planilha1 | 0 | Vazia |

## 4. Troubleshooting Rápido

### "Erro ao conectar à API"
- Verificar se o servidor Flask está rodando
- Verificar se port 5000 está disponível
- Verificar credenciais no backend/

### "Nenhum CNPJ aparece"
- Confirmar que as planilhas foram criadas no Google Drive
- Verificar credenciais do Google
- Rodar: `curl http://localhost:5000/api/cnpjs`

### "Dados não aparecem"
- Aguardar 5 segundos (cache)
- Clicar em outro CNPJ e voltar
- Recarregar a página (F5)
- Verificar console do navegador (F12)

### "Exportação não funciona"
- Usar navegador atualizado (Chrome, Firefox, Safari)
- Verificar se há dados a exportar
- Tentar em incógnito (sem cache)

## 5. Configurações Opcionais

### Alterar tempo de sincronização
Em `frontend/js/app.js`, linha 48:
```javascript
}, 300000); // 5 minutos = 300000ms
            // Para 1 minuto: 60000
            // Para 30 segundos: 30000
```

### Adicionar autenticação
Ver seção "Segurança" em README.md

### Hospedar em outro serviço
Consultar DEPLOY.md para opções (Heroku, PythonAnywhere, etc)

## 6. Próximos Passos

1. ✓ Testar localmente
2. ✓ Fazer push para GitHub
3. ✓ Deploy Backend (Railway)
4. ✓ Deploy Frontend (Vercel)
5. ✓ Compartilhar URL com donos
6. Monitorar uso e feedback
7. Adicionar novas funcionalidades conforme necessário

## 7. Suporte

Se tiver dúvidas:
1. Consultar README.md
2. Consultar DEPLOY.md
3. Verificar console do navegador (F12 > Console)
4. Verificar logs do servidor

---

**Parabéns! Você tem um sistema profissional de gestão financeira pronto para uso!** 🎉

Qualquer dúvida, consulte a documentação ou os logs de erro.
