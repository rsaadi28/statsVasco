#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.export_acervo_web import parse_date  # noqa: E402
from web_sync import DEFAULT_API_URL, build_state  # noqa: E402

DEFAULT_PRD_DB = Path.home() / "Library/Application Support/StatsVasco/stats_vasco.sqlite3"


def truthy(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "sim", "s", "on"}


def load_settings(db_path: Path) -> dict[str, str]:
    if not db_path.exists():
        return {}
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
    except Exception:
        return {}
    return {str(key): str(value) for key, value in rows}


def check_sqlite(db_path: Path) -> None:
    if not db_path.exists():
        raise SystemExit(f"Banco local PRD nao encontrado: {db_path}")
    with sqlite3.connect(db_path) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise SystemExit(f"Falha no integrity_check de {db_path}: {result}")


def resolve_api_url(args: argparse.Namespace, settings: dict[str, str]) -> str:
    return (
        args.api_url
        or os.environ.get("ACERVO_API_URL")
        or settings.get("web_sync_api_url")
        or DEFAULT_API_URL
    ).strip().rstrip("/")


def resolve_admin_token(args: argparse.Namespace, settings: dict[str, str]) -> str:
    token = (
        args.admin_token
        or os.environ.get("ACERVO_ADMIN_TOKEN")
        or os.environ.get("ACERVO_WEB_ADMIN_TOKEN")
        or settings.get("web_sync_admin_token")
        or ""
    ).strip()
    if not token:
        raise SystemExit(
            "Token admin nao encontrado. Configure uma vez com:\n"
            "  .venv/bin/python scripts/configure_web_sync.py\n"
            "ou rode com ACERVO_ADMIN_TOKEN no ambiente."
        )
    return token


def request_json(
    method: str,
    url: str,
    token: str,
    *,
    payload: Any | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    body = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"API retornou HTTP {exc.code} em {url}: {detail}") from exc
    except Exception as exc:
        raise SystemExit(f"Falha ao chamar {url}: {exc}") from exc

    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except Exception as exc:
        raise SystemExit(f"Resposta da API nao e JSON valido: {raw[:500]}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Resposta inesperada da API: {data!r}")
    return data


def latest_match(matches: list[dict[str, Any]]) -> dict[str, Any]:
    if not matches:
        return {}
    return max(matches, key=lambda item: parse_date(item.get("data")) or datetime.min)


def state_summary(state: dict[str, Any]) -> dict[str, Any]:
    matches = state.get("matches", []) if isinstance(state.get("matches"), list) else []
    future = state.get("future_matches", []) if isinstance(state.get("future_matches"), list) else []
    current = state.get("current_squad", {}) if isinstance(state.get("current_squad"), dict) else {}
    historic = state.get("historic_players", {}) if isinstance(state.get("historic_players"), dict) else {}
    latest = latest_match(matches)
    return {
        "matches": len(matches),
        "future_matches": len(future),
        "current_squad": len(current.get("jogadores", [])) if isinstance(current.get("jogadores"), list) else 0,
        "historic_players": len(historic.get("jogadores", [])) if isinstance(historic.get("jogadores"), list) else 0,
        "latest_match": {
            "data": latest.get("data"),
            "adversario": latest.get("adversario"),
            "competicao": latest.get("competicao"),
            "placar": latest.get("placar"),
        }
        if latest
        else None,
    }


def chunks(items: list[Any], size: int) -> list[list[Any]]:
    return [items[pos : pos + size] for pos in range(0, len(items), size)]


def sync_full(api_url: str, token: str, state: dict[str, Any], timeout: int) -> dict[str, Any]:
    payload = {
        "reason": "manual-prd-to-web",
        "source": "scripts/sync_prd_to_web.py",
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "state": state,
    }
    return request_json("POST", f"{api_url}/admin/sync-state", token, payload=payload, timeout=timeout)


def sync_matches(api_url: str, token: str, matches: list[dict[str, Any]], chunk_size: int, timeout: int) -> dict[str, Any]:
    inserted = updated = 0
    total_matches = None
    batches = chunks(matches, max(1, chunk_size))
    for index, batch in enumerate(batches, start=1):
        result = request_json("POST", f"{api_url}/admin/import-match", token, payload=batch, timeout=timeout)
        inserted += int(result.get("inserted") or 0)
        updated += int(result.get("updated") or 0)
        total_matches = result.get("total_matches", total_matches)
        print(
            f"Lote {index}/{len(batches)}: "
            f"inseridos={result.get('inserted')} atualizados={result.get('updated')} total_web={total_matches}"
        )
    return {"ok": True, "inserted": inserted, "updated": updated, "total_matches": total_matches}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sincroniza o banco local PRD do StatsVasco com o banco web no Railway. "
            "O modo padrao espelha o estado completo do SQLite local no Postgres web."
        )
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_PRD_DB, help=f"SQLite local PRD. Padrao: {DEFAULT_PRD_DB}")
    parser.add_argument("--api-url", default="", help=f"API Railway. Padrao: {DEFAULT_API_URL}")
    parser.add_argument("--admin-token", default="", help="Token admin. Se omitido, usa env ou settings do SQLite.")
    parser.add_argument(
        "--mode",
        choices=("full", "matches"),
        default="full",
        help="'full' sincroniza jogos, futuros, elenco e historico. 'matches' faz upsert somente dos jogos.",
    )
    parser.add_argument("--chunk-size", type=int, default=200, help="Tamanho dos lotes no modo matches.")
    parser.add_argument("--timeout", type=int, default=90, help="Timeout por requisicao HTTP, em segundos.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria enviado, sem alterar o banco web.")
    parser.add_argument(
        "--skip-remote-status",
        action="store_true",
        help="Nao consulta /admin/status antes/depois. Util se a API estiver indisponivel.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = args.db.expanduser().resolve()
    check_sqlite(db_path)
    settings = load_settings(db_path)
    api_url = resolve_api_url(args, settings)
    token = resolve_admin_token(args, settings)

    state = build_state(str(db_path))
    local_summary = state_summary(state)
    print(f"Banco local PRD: {db_path}")
    print(f"API web: {api_url}")
    print(f"Modo: {args.mode}")
    print(f"Resumo local: {json.dumps(local_summary, ensure_ascii=False)}")

    if not args.skip_remote_status:
        before = request_json("GET", f"{api_url}/admin/status", token, timeout=args.timeout)
        print(f"Web antes: {json.dumps(before, ensure_ascii=False)}")

    if args.dry_run:
        print("Dry-run ativo: nenhuma alteracao enviada para o banco web.")
        return

    if args.mode == "full":
        result = sync_full(api_url, token, state, args.timeout)
    else:
        matches = state.get("matches", [])
        if not isinstance(matches, list):
            raise SystemExit("Estado local invalido: matches nao e lista.")
        result = sync_matches(api_url, token, matches, args.chunk_size, args.timeout)
    print(f"Sync concluido: {json.dumps(result, ensure_ascii=False)}")

    if not args.skip_remote_status:
        after = request_json("GET", f"{api_url}/admin/status", token, timeout=args.timeout)
        print(f"Web depois: {json.dumps(after, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
