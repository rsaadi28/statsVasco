# Arquitetura do Acervo Vasco Web

## Decisão atual

O projeto web público deve ser somente leitura.

- A interface principal é o protótipo em `Acervo Vasco/`.
- O servidor local `web_app.py` serve esse protótipo na raiz (`/`).
- As rotas de escrita (`POST/PUT /api/jogos`) ficam desligadas por padrão.
- O arquivo `Acervo Vasco/data-runtime.js` é a ponte entre banco e protótipo.

Enquanto `data-runtime.js` estiver vazio, o protótipo usa os dados mockados originais. Depois que o banco local for atualizado, rode:

```bash
python3 scripts/export_acervo_web.py
```

Esse comando lê `stats_vasco.sqlite3` e sobrescreve `Acervo Vasco/data-runtime.js` com os dados calculados para a interface.

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

Para atualizar o site só enviando um JSON, use um backend separado do site público:

1. Banco online: Supabase/Postgres ou Neon/Postgres.
2. Área admin privada: upload do JSON do jogo.
3. Função backend: valida o JSON, evita duplicidade, grava nas tabelas e recalcula agregados.
4. Saída pública: gera um `site-data.json` ou `data-runtime.js` em storage/CDN.
5. Web público: só lê esse arquivo ou uma API `GET`, sem cadastro nem escrita.

Modelo prático no Supabase:

- `matches`, `match_goals`, `match_cards`, `players`, `teams`, `competitions`, `current_squad`.
- `match_imports` para guardar o JSON bruto, status, erro e data de importação.
- Edge Function privada `import-match-json` para validar e inserir.
- View ou job `public_site_data` para montar o JSON consumido pelo frontend.
- Storage público com `site-data.json` versionado por timestamp.

O site público não precisa login porque ele não grava nada. Só o endpoint admin de importação precisa autenticação.

## Por que não deixar o web importar direto?

Porque isso expõe a parte mais sensível do sistema: validação, deduplicação e escrita no banco. Mesmo que não haja usuário final, uma rota pública de importação exigiria autenticação, rate limit, auditoria e rollback.

Separar o importador privado do site público deixa o acervo mais seguro e mantém a interface rápida.
