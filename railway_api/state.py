from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

STATE_KEYS = {
    "matches": [],
    "future_matches": [],
    "current_squad": {"jogadores": [], "tecnico": ""},
    "historic_players": {"jogadores": []},
}


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL não configurada.")
    return url


@contextmanager
def connection():
    with psycopg.connect(database_url(), row_factory=dict_row) as conn:
        yield conn


def init_db() -> None:
    with connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS acervo_state (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        for key, default in STATE_KEYS.items():
            conn.execute(
                """
                INSERT INTO acervo_state(key, value)
                VALUES (%s, %s::jsonb)
                ON CONFLICT (key) DO NOTHING
                """,
                (key, psycopg.types.json.Jsonb(default)),
            )


def load_state() -> dict[str, Any]:
    init_db()
    with connection() as conn:
        rows = conn.execute("SELECT key, value FROM acervo_state").fetchall()
    state = {key: default for key, default in STATE_KEYS.items()}
    for row in rows:
        state[row["key"]] = row["value"]
    return state


def save_state_key(key: str, value: Any) -> None:
    if key not in STATE_KEYS:
        raise ValueError(f"Chave de estado inválida: {key}")
    with connection() as conn:
        conn.execute(
            """
            INSERT INTO acervo_state(key, value, updated_at)
            VALUES (%s, %s::jsonb, now())
            ON CONFLICT (key) DO UPDATE
            SET value = excluded.value, updated_at = now()
            """,
            (key, psycopg.types.json.Jsonb(value)),
        )


def replace_state(state: dict[str, Any]) -> None:
    init_db()
    for key, default in STATE_KEYS.items():
        save_state_key(key, state.get(key, default))
