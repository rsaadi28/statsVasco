#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DB = Path.home() / "Library/Application Support/StatsVasco/stats_vasco.sqlite3"
DEV_DB = ROOT / "stats_vasco.sqlite3"
DUMP_DIR = ROOT / "dumps"

FUTURE_FIXES = [
    {
        "match_text": "Internacional-RS x Vasco",
        "date_text": "16/05/2026",
        "date_iso": "2026-05-16",
        "stadium": "Beira-Rio",
        "match_time": "18:30",
    },
    {
        "match_text": "Olimpia x Vasco",
        "date_text": "20/05/2026",
        "date_iso": "2026-05-20",
        "stadium": "Defensores del Chaco",
        "match_time": "19:00",
    },
    {
        "match_text": "Vasco x Red Bull Bragantino-SP",
        "date_text": "24/05/2026",
        "date_iso": "2026-05-24",
        "stadium": "São Januário",
        "match_time": "20:30",
    },
    {
        "match_text": "Vasco x Barracas Central",
        "date_text": "27/05/2026",
        "date_iso": "2026-05-27",
        "stadium": "São Januário",
        "match_time": "21:30",
    },
    {
        "match_text": "Vasco x Atlético-MG",
        "date_text": "31/05/2026",
        "date_iso": "2026-05-31",
        "stadium": "São Januário",
        "match_time": "16:00",
    },
]


def check_db(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Banco nao encontrado: {path}")
    with sqlite3.connect(path) as conn:
        result = conn.execute("PRAGMA integrity_check").fetchone()
    if not result or result[0] != "ok":
        raise SystemExit(f"Falha no integrity_check de {path}: {result}")


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0])


def normalize_future_matches(db_path: Path) -> int:
    updated = 0
    with sqlite3.connect(db_path) as conn:
        for item in FUTURE_FIXES:
            cur = conn.execute(
                """
                UPDATE future_matches
                   SET date_text = ?,
                       date_iso = ?,
                       stadium = ?,
                       match_time = ?
                 WHERE match_text = ?
                """,
                (
                    item["date_text"],
                    item["date_iso"],
                    item["stadium"],
                    item["match_time"],
                    item["match_text"],
                ),
            )
            updated += cur.rowcount
    return updated


def make_dump(db_path: Path, dump_dir: Path) -> Path:
    dump_dir.mkdir(parents=True, exist_ok=True)
    out = dump_dir / f"stats_vasco_{timestamp()}.sql.gz"
    with sqlite3.connect(db_path) as conn, gzip.open(out, "wt", encoding="utf-8") as gz:
        for line in conn.iterdump():
            gz.write(line)
            gz.write("\n")
    return out


def runtime_summary(db_path: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    from scripts.export_acervo_web import build_future, parse_date  # noqa: WPS433
    from storage_sqlite import load_current_squad, load_future_matches, load_matches  # noqa: WPS433

    jogos = load_matches(str(db_path))
    futuros = load_future_matches(str(db_path))
    current_squad = load_current_squad(str(db_path))
    latest = max(jogos, key=lambda j: parse_date(j.get("data")) or datetime.min) if jogos else {}
    latest_date = parse_date(latest.get("data")) if latest else None
    web_futures = build_future(futuros, after_date=latest_date)
    return {
        "matches": len(jogos),
        "future_matches": len(futuros),
        "web_future_matches": len(web_futures),
        "current_squad": len(current_squad.get("jogadores", [])),
        "latest_match": {
            "data": latest.get("data"),
            "adversario": latest.get("adversario"),
            "placar": latest.get("placar"),
        },
        "first_web_future": web_futures[0] if web_futures else None,
    }


def seed_railway() -> None:
    cmd = [
        "railway",
        "run",
        "--service",
        "Postgres",
        "sh",
        "-c",
        'DATABASE_URL="$DATABASE_PUBLIC_URL" .venv/bin/python -m railway_api.seed_from_sqlite',
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sincroniza o SQLite do app desktop com o dev/web e opcionalmente sobe para Railway."
    )
    parser.add_argument("--desktop-db", type=Path, default=DESKTOP_DB, help=f"SQLite do desktop. Padrao: {DESKTOP_DB}")
    parser.add_argument("--dev-db", type=Path, default=DEV_DB, help=f"SQLite de dev/web. Padrao: {DEV_DB}")
    parser.add_argument("--dump-dir", type=Path, default=DUMP_DIR, help=f"Pasta dos dumps. Padrao: {DUMP_DIR}")
    parser.add_argument("--seed-railway", action="store_true", help="Alimenta o Postgres do Railway apos sincronizar.")
    parser.add_argument("--skip-future-fixes", action="store_true", help="Nao aplica os ajustes conhecidos de calendario futuro.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    desktop_db = args.desktop_db.expanduser().resolve()
    dev_db = args.dev_db.expanduser().resolve()

    check_db(desktop_db)
    backup = None
    if dev_db.exists():
        backup = dev_db.with_name(f"{dev_db.stem}.dev_before_desktop_sync_{timestamp()}{dev_db.suffix}")
        shutil.copy2(dev_db, backup)

    shutil.copy2(desktop_db, dev_db)
    fixed = 0 if args.skip_future_fixes else normalize_future_matches(dev_db)
    check_db(dev_db)

    with sqlite3.connect(dev_db) as conn:
        counts = {
            "matches": table_count(conn, "matches"),
            "future_matches": table_count(conn, "future_matches"),
            "current_squad": table_count(conn, "current_squad"),
        }

    dump = make_dump(dev_db, args.dump_dir.expanduser().resolve())
    summary = runtime_summary(dev_db)

    print(f"Banco desktop: {desktop_db}")
    print(f"Banco dev: {dev_db}")
    if backup:
        print(f"Backup dev: {backup}")
    print(f"Dump: {dump}")
    print(f"Ajustes de jogos futuros aplicados: {fixed}")
    print(f"SQLite: {counts}")
    print(f"Runtime web: {summary}")

    if args.seed_railway:
        seed_railway()
        print("Railway seed concluido.")
    else:
        print("Railway nao atualizado. Para subir, rode novamente com --seed-railway.")


if __name__ == "__main__":
    main()
