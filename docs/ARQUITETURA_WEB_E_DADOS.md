# Arquitetura do Acervo Vasco Web

## Decisão atual

O projeto web público deve ser somente leitura.

- A interface principal é o protótipo em `Acervo Vasco/`.
- Produção web: `https://acervo-vasco.vercel.app`.
- API de dados: `https://acervo-api-production.up.railway.app`.
- Banco online: Postgres no Railway.
- O site público carrega `Acervo Vasco/data-runtime.js` como fallback e depois carrega `/api/data-runtime` pela Vercel.
- A function `/api/data-runtime` injeta a chave secreta do ambiente Vercel e busca `GET /data-runtime.js` no Railway.
- O endpoint direto do Railway exige `ACERVO_DATA_TOKEN`.

Enquanto `data-runtime.js` estiver vazio, o protótipo usa os dados mockados originais. Depois que o banco do app desktop for atualizado, rode:

```bash
.venv/bin/python scripts/sync_desktop_to_web.py --seed-railway
```

Esse comando copia o SQLite do desktop em `~/Library/Application Support/StatsVasco/stats_vasco.sqlite3` para o projeto de dev, aplica os ajustes conhecidos de calendario futuro, gera um dump em `dumps/` e alimenta o Postgres do Railway.

## Sync automatico pelo desktop

O desktop tambem pode publicar automaticamente quando salva dados locais. O fluxo e:

1. O app grava no SQLite local.
2. O modulo `web_sync.py` monta o estado completo (`matches`, `future_matches`, `current_squad`, `historic_players`).
3. O desktop envia esse estado para `POST /admin/sync-state` na API Railway.
4. A API substitui o estado no Postgres e o web recalcula o runtime na proxima leitura.

Para ativar em uma maquina, configure a chave admin uma vez:

```bash
.venv/bin/python scripts/configure_web_sync.py
```

O token fica no SQLite local do desktop, nao no codigo. Tambem e possivel usar variaveis de ambiente:

```bash
export ACERVO_AUTO_SYNC_WEB=1
export ACERVO_API_URL=https://acervo-api-production.up.railway.app
export ACERVO_ADMIN_TOKEN=...
python main.py
```

Sem token admin configurado, o desktop apenas salva localmente e nao tenta publicar.

Para gerar apenas o runtime local do protótipo, sem subir dados para o Railway, rode:

```bash
python3 scripts/export_acervo_web.py
```

Esse comando lê `stats_vasco.sqlite3` e sobrescreve `Acervo Vasco/data-runtime.js` com os dados calculados para a interface.

Em produção, o runtime remoto do Railway sobrescreve esse fallback local através da function da Vercel.
Para manter os dados protegidos, não publique um `data-runtime.js` exportado com dados reais na Vercel; use o seed/import da API Railway para alimentar o banco online.

## Fluxo em produção com Railway

O deploy ficou dividido em duas partes:

1. Vercel hospeda a pasta `Acervo Vasco/` como site estático.
2. Vercel expõe `/api/data-runtime`, uma function serverless que protege a chave.
3. Railway hospeda a API FastAPI em `railway_api/`.
4. Railway Postgres guarda o estado do acervo em JSONB.
5. A API gera o mesmo `data-runtime.js` que o protótipo já entende.
6. O navegador baixa o script pela Vercel e atualiza a interface sem login e sem escrita pública.

Comandos principais:

```bash
cd "Acervo Vasco"
vercel deploy --prod
```

```bash
railway up --service acervo-api --detach -m "Deploy Acervo Vasco API"
```

Variáveis necessárias:

- Railway `acervo-api`: `DATABASE_URL`, `ACERVO_ADMIN_TOKEN`, `ACERVO_DATA_TOKEN`, `ACERVO_ALLOWED_ORIGINS`.
- Vercel `production`: `ACERVO_API_URL`, `ACERVO_DATA_TOKEN`.

```bash
railway run --service Postgres sh -c 'DATABASE_URL="$DATABASE_PUBLIC_URL" .venv/bin/python -m railway_api.seed_from_sqlite'
```

Verificações:

```bash
curl https://acervo-api-production.up.railway.app/health
curl -i https://acervo-api-production.up.railway.app/data-runtime.js
curl -H "Referer: https://acervo-vasco.vercel.app/" https://acervo-vasco.vercel.app/api/data-runtime
```

O primeiro `curl` para `data-runtime.js` deve retornar `401` sem chave. O segundo deve retornar o JavaScript porque passa pelo proxy da Vercel.

## Importação de jogo por JSON

O endpoint privado para alimentar o banco online é:

```text
POST https://acervo-api-production.up.railway.app/admin/import-match
```

Ele aceita um jogo ou uma lista de jogos no mesmo formato JSON usado pelo acervo. A autenticação fica no header `Authorization: Bearer <ACERVO_ADMIN_TOKEN>` ou `x-admin-token: <ACERVO_ADMIN_TOKEN>`.

Exemplo:

```bash
curl -X POST https://acervo-api-production.up.railway.app/admin/import-match \
  -H "Authorization: Bearer $ACERVO_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  --data @ultimo-jogo.json
```

A API valida o JSON, evita duplicidade usando `data + adversario + competicao`, salva no Postgres e recalcula o runtime entregue para o site.

## Fluxo simples sem banco online

Este é o menor fluxo operacional:

1. Gerar o JSON do último jogo no formato do importador do desktop.
2. Importar esse JSON no app desktop.
3. Validar o desktop.
4. Rodar `python3 scripts/export_acervo_web.py`.
5. Publicar a pasta `Acervo Vasco/` em um host estático.

Vantagem: simples, barato e sem painel online.

Limitação: a atualização do site depende de gerar e publicar o arquivo `data-runtime.js`.

## Fluxo recomendado com banco online

Para atualizar o site só enviando um JSON, use um backend separado do site público. No projeto atual isso já está implementado com Railway:

1. Banco online: Railway Postgres.
2. API privada: `POST /admin/import-match`.
3. Função backend: valida o JSON, evita duplicidade, grava no JSONB e recalcula agregados.
4. Saída consumida pelo site: `GET /api/data-runtime` na Vercel, com busca protegida no Railway.
5. Web público: só lê esse arquivo, sem cadastro nem escrita.

O modelo atual prioriza simplicidade: uma tabela `acervo_state` guarda `matches`, `future_matches`, `current_squad` e `historic_players` como JSONB. Se o volume ou a necessidade de relatórios crescer, dá para evoluir para tabelas normalizadas sem mexer no contrato público do site.

O site público não precisa login porque ele não grava nada. O endpoint admin de importação precisa autenticação, e o endpoint de dados do Railway exige chave. Para vender acesso no futuro, o ideal é emitir chaves por cliente no backend, com limite de uso e logs por chave; nunca colocar uma chave vendável diretamente no JavaScript do navegador.

## Por que não deixar o web importar direto?

Porque isso expõe a parte mais sensível do sistema: validação, deduplicação e escrita no banco. Mesmo que não haja usuário final, uma rota pública de importação exigiria autenticação, rate limit, auditoria e rollback.

Separar o importador privado do site público deixa o acervo mais seguro e mantém a interface rápida.
