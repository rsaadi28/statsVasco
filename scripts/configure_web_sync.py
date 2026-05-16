#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import sqlite3
from pathlib import Path

DEFAULT_DB = Path.home() / "Library/Application Support/StatsVasco/stats_vasco.sqlite3"
DEFAULT_API_URL = "https://acervo-api-production.up.railway.app"


def set_setting(db_path: Path, key: str, value: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT INTO settings(key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configura sync automatico do desktop para o Acervo web.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help=f"SQLite do desktop. Padrao: {DEFAULT_DB}")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help=f"API Railway. Padrao: {DEFAULT_API_URL}")
    parser.add_argument("--admin-token", default="", help="Token admin. Se omitido, sera pedido sem eco no terminal.")
    parser.add_argument("--disable", action="store_true", help="Desativa o sync automatico.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = args.db.expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"Banco nao encontrado: {db_path}")

    if args.disable:
        set_setting(db_path, "web_sync_enabled", "0")
        print(f"Sync automatico desativado em {db_path}")
        return

    token = args.admin_token.strip() or getpass.getpass("ACERVO_ADMIN_TOKEN: ").strip()
    if not token:
        raise SystemExit("Token admin nao informado.")

    set_setting(db_path, "web_sync_enabled", "1")
    set_setting(db_path, "web_sync_api_url", args.api_url.strip().rstrip("/"))
    set_setting(db_path, "web_sync_admin_token", token)
    print(f"Sync automatico ativado em {db_path}")


if __name__ == "__main__":
    main()
