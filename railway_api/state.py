from __future__ import annotations

import os
from collections.abc import Callable
from copy import deepcopy
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


def mutate_state_key(key: str, mutator: Callable[[Any], Any]) -> Any:
    """Atualiza uma chave com lock de linha e devolve o valor persistido."""
    if key not in STATE_KEYS:
        raise ValueError(f"Chave de estado inválida: {key}")
    init_db()
    with connection() as conn:
        row = conn.execute(
            "SELECT value FROM acervo_state WHERE key = %s FOR UPDATE",
            (key,),
        ).fetchone()
        current = row["value"] if row else deepcopy(STATE_KEYS[key])
        updated = mutator(current)
        conn.execute(
            """
            UPDATE acervo_state
            SET value = %s::jsonb, updated_at = now()
            WHERE key = %s
            """,
            (psycopg.types.json.Jsonb(updated), key),
        )
    return updated


def replace_state(state: dict[str, Any]) -> None:
    init_db()
    for key, default in STATE_KEYS.items():
        save_state_key(key, state.get(key, default))
