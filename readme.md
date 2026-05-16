# StatsVasco

## Persistencia de dados

- O app agora usa SQLite (`stats_vasco.sqlite3`) em vez de JSON como base principal.
- Na primeira execucao, os JSONs legados sao migrados automaticamente para o banco.
- Diagrama de relacionamentos: [docs/DIAGRAMA_RELACIONAMENTOS.md](docs/DIAGRAMA_RELACIONAMENTOS.md)

## Rodar em desenvolvimento

### macOS / Linux
1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install --upgrade pip pyinstaller`
4. `python main.py`

### Web / Acervo Vasco
- Rodar servidor local: `python3 web_app.py`
- Abrir: `http://127.0.0.1:8000`
- O web serve o protótipo em `Acervo Vasco/` e fica somente leitura por padrão.
- Depois de importar jogos no desktop, inclusive jogos futuros, sincronize o web/Railway com: `.venv/bin/python scripts/sync_desktop_to_web.py --seed-railway`
- Para o desktop publicar automaticamente após salvar jogo/elenco/futuros, configure uma vez com: `.venv/bin/python scripts/configure_web_sync.py`
- Para gerar apenas o runtime local do protótipo, sem subir Railway: `python3 scripts/export_acervo_web.py`
- Deploy Vercel: `cd "Acervo Vasco" && vercel deploy --prod`
- API Railway: `https://acervo-api-production.up.railway.app`
- Runtime usado pelo site: `https://acervo-vasco.vercel.app/api/data-runtime`
- O endpoint direto do Railway `GET /data-runtime.js` exige `ACERVO_DATA_TOKEN`.
- Para produção protegida, mantenha `Acervo Vasco/data-runtime.js` sem dados reais e alimente o Railway com seed/import.
- Seed do banco Railway a partir do SQLite local: `railway run --service Postgres sh -c 'DATABASE_URL="$DATABASE_PUBLIC_URL" .venv/bin/python -m railway_api.seed_from_sqlite'`
- Deploy da API Railway: `railway up --service acervo-api --detach -m "Deploy Acervo Vasco API"`
- Arquitetura dos dados web: [docs/ARQUITETURA_WEB_E_DADOS.md](docs/ARQUITETURA_WEB_E_DADOS.md)

### Windows (Prompt de Comando)
1. `python -m venv .venv`
2. `.venv\Scripts\activate`
3. `pip install --upgrade pip pyinstaller matplotlib`
4. `python main.py`

## Gerar builds

### macOS
- Rode: `./build_mac.sh`
- Guia completo: `GUIA_INSTALACAO_MAC.md`

### Windows
- Rode: `build_windows.bat`
- Guia completo: `GUIA_INSTALACAO_WINDOWS.md`
