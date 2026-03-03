from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import datetime
from typing import Any

DB_FILENAME = "stats_vasco.sqlite3"
DEFAULT_TECNICO = "Fernando Diniz"

LIST_TYPES = (
    "clubes_adversarios",
    "jogadores_vasco",
    "jogadores_contra",
    "competicoes",
    "tecnicos",
)


def db_path_for(data_dir: str) -> str:
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, DB_FILENAME)


def _parse_data_iso(data_txt: str | None) -> str | None:
    txt = str(data_txt or "").strip()
    if not txt:
        return None
    try:
        return datetime.strptime(txt, "%d/%m/%Y").date().isoformat()
    except Exception:
        return None


def _open(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _json_load_file(path: str, default: Any):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return json.loads(content) if content else default
    except Exception:
        return default


def _normalize_listas(data: dict[str, Any] | None) -> dict[str, Any]:
    data = data if isinstance(data, dict) else {}
    out: dict[str, Any] = {}
    for key in LIST_TYPES:
        items = data.get(key, [])
        if not isinstance(items, list):
            items = []
        dedup = []
        seen = set()
        for item in items:
            value = str(item or "").strip()
            if not value:
                continue
            cf = value.casefold()
            if cf in seen:
                continue
            seen.add(cf)
            dedup.append(value)
        out[key] = sorted(dedup, key=str.casefold)
    tecnicos = out.get("tecnicos", [])
    if not tecnicos:
        tecnicos = [DEFAULT_TECNICO]
        out["tecnicos"] = tecnicos
    tecnico_atual = str(data.get("tecnico_atual", "") if isinstance(data, dict) else "").strip()
    if not tecnico_atual:
        tecnico_atual = tecnicos[0]
    if tecnico_atual not in tecnicos:
        tecnicos.append(tecnico_atual)
        tecnicos.sort(key=str.casefold)
    out["tecnico_atual"] = tecnico_atual
    return out


def _create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            team_type TEXT NOT NULL DEFAULT 'adversario'
        );

        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS coaches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS competitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS list_entries (
            list_type TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (list_type, value)
        );

        CREATE TABLE IF NOT EXISTS current_squad (
            player_id INTEGER PRIMARY KEY,
            position TEXT NOT NULL,
            condition TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS historic_players (
            player_id INTEGER PRIMARY KEY,
            position TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_text TEXT NOT NULL,
            date_iso TEXT,
            opponent_team_id INTEGER,
            competition_id INTEGER,
            location TEXT NOT NULL,
            vasco_goals INTEGER NOT NULL,
            opponent_goals INTEGER NOT NULL,
            observation TEXT NOT NULL DEFAULT '',
            coach_id INTEGER,
            table_position INTEGER,
            lineup_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (opponent_team_id) REFERENCES teams (id),
            FOREIGN KEY (competition_id) REFERENCES competitions (id),
            FOREIGN KEY (coach_id) REFERENCES coaches (id)
        );

        CREATE TABLE IF NOT EXISTS match_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            side TEXT NOT NULL,
            player_id INTEGER,
            player_name TEXT NOT NULL,
            goals INTEGER NOT NULL DEFAULT 1,
            club_name TEXT,
            is_disallowed INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players (id)
        );

        CREATE TABLE IF NOT EXISTS future_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_text TEXT NOT NULL,
            date_iso TEXT,
            match_text TEXT NOT NULL,
            is_home INTEGER,
            competition_id INTEGER,
            opponent_team_id INTEGER,
            FOREIGN KEY (competition_id) REFERENCES competitions (id),
            FOREIGN KEY (opponent_team_id) REFERENCES teams (id)
        );

        CREATE TABLE IF NOT EXISTS vasco_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            UNIQUE(competition_id, year),
            FOREIGN KEY (competition_id) REFERENCES competitions (id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(date_iso, id);
        CREATE INDEX IF NOT EXISTS idx_goals_match ON match_goals(match_id);
        CREATE INDEX IF NOT EXISTS idx_future_date ON future_matches(date_iso, id);
        CREATE INDEX IF NOT EXISTS idx_titles_year ON vasco_titles(year, id);
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO teams(name, team_type) VALUES (?, ?)",
        ("Vasco da Gama", "vasco"),
    )


def _ensure_player(conn: sqlite3.Connection, name: str) -> int | None:
    txt = str(name or "").strip()
    if not txt:
        return None
    conn.execute("INSERT OR IGNORE INTO players(name) VALUES (?)", (txt,))
    row = conn.execute("SELECT id FROM players WHERE name = ?", (txt,)).fetchone()
    return int(row["id"]) if row else None


def _ensure_team(conn: sqlite3.Connection, name: str, team_type: str = "adversario") -> int | None:
    txt = str(name or "").strip()
    if not txt:
        return None
    conn.execute(
        "INSERT OR IGNORE INTO teams(name, team_type) VALUES (?, ?)",
        (txt, team_type or "adversario"),
    )
    row = conn.execute("SELECT id FROM teams WHERE name = ?", (txt,)).fetchone()
    return int(row["id"]) if row else None


def _ensure_competition(conn: sqlite3.Connection, name: str) -> int | None:
    txt = str(name or "").strip()
    if not txt:
        return None
    conn.execute("INSERT OR IGNORE INTO competitions(name) VALUES (?)", (txt,))
    row = conn.execute("SELECT id FROM competitions WHERE name = ?", (txt,)).fetchone()
    return int(row["id"]) if row else None


def _ensure_coach(conn: sqlite3.Connection, name: str) -> int | None:
    txt = str(name or "").strip()
    if not txt:
        return None
    conn.execute("INSERT OR IGNORE INTO coaches(name) VALUES (?)", (txt,))
    row = conn.execute("SELECT id FROM coaches WHERE name = ?", (txt,)).fetchone()
    return int(row["id"]) if row else None


def _parse_goal_item(item: Any) -> tuple[str | None, int, str | None]:
    if isinstance(item, dict):
        name = str(item.get("nome", "")).strip()
        club = str(item.get("clube", "")).strip() or None
        try:
            goals = int(item.get("gols", 1))
        except Exception:
            goals = 1
    else:
        name = str(item or "").strip()
        club = None
        goals = 1
    if not name:
        return None, 0, club
    return name, max(1, goals), club


def save_listas(db_path: str, data: dict[str, Any]) -> None:
    listas = _normalize_listas(data)
    with _open(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM list_entries")
        for list_type in LIST_TYPES:
            for value in listas.get(list_type, []):
                conn.execute(
                    "INSERT INTO list_entries(list_type, value) VALUES (?, ?)",
                    (list_type, value),
                )
                if list_type == "clubes_adversarios":
                    _ensure_team(conn, value, "adversario")
                elif list_type in ("jogadores_vasco", "jogadores_contra"):
                    _ensure_player(conn, value)
                elif list_type == "competicoes":
                    _ensure_competition(conn, value)
                elif list_type == "tecnicos":
                    _ensure_coach(conn, value)
        conn.execute(
            "INSERT INTO settings(key, value) VALUES ('tecnico_atual', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (listas.get("tecnico_atual") or DEFAULT_TECNICO,),
        )


def load_listas(db_path: str) -> dict[str, Any]:
    with _open(db_path) as conn:
        _create_schema(conn)
        out = {k: [] for k in LIST_TYPES}
        rows = conn.execute(
            "SELECT list_type, value FROM list_entries ORDER BY list_type, lower(value), value"
        ).fetchall()
        for row in rows:
            lt = row["list_type"]
            if lt in out:
                out[lt].append(row["value"])
        tecnico = conn.execute(
            "SELECT value FROM settings WHERE key = 'tecnico_atual'"
        ).fetchone()
    out = _normalize_listas({**out, "tecnico_atual": tecnico["value"] if tecnico else ""})
    return out


def save_matches(db_path: str, jogos: list[dict[str, Any]]) -> None:
    if not isinstance(jogos, list):
        jogos = []
    with _open(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM match_goals")
        conn.execute("DELETE FROM matches")

        for jogo in jogos:
            if not isinstance(jogo, dict):
                continue
            adversario = str(jogo.get("adversario", "")).strip()
            competicao = str(jogo.get("competicao", "")).strip()
            tecnico = str(jogo.get("tecnico", "")).strip()
            placar = jogo.get("placar") if isinstance(jogo.get("placar"), dict) else {}
            try:
                vasco_goals = int(placar.get("vasco", 0))
            except Exception:
                vasco_goals = 0
            try:
                adv_goals = int(placar.get("adversario", 0))
            except Exception:
                adv_goals = 0

            op_team_id = _ensure_team(conn, adversario, "adversario")
            comp_id = _ensure_competition(conn, competicao)
            coach_id = _ensure_coach(conn, tecnico)

            lineup = jogo.get("escalacao_partida")
            if not isinstance(lineup, dict):
                lineup = jogo.get("escalacao") if isinstance(jogo.get("escalacao"), dict) else {}

            cursor = conn.execute(
                """
                INSERT INTO matches(
                    date_text, date_iso, opponent_team_id, competition_id, location,
                    vasco_goals, opponent_goals, observation, coach_id, table_position, lineup_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(jogo.get("data", "")).strip(),
                    _parse_data_iso(jogo.get("data")),
                    op_team_id,
                    comp_id,
                    str(jogo.get("local", "")).strip() or "casa",
                    max(0, vasco_goals),
                    max(0, adv_goals),
                    str(jogo.get("observacao", "")).strip(),
                    coach_id,
                    jogo.get("posicao_tabela") if isinstance(jogo.get("posicao_tabela"), int) else None,
                    json.dumps(lineup, ensure_ascii=False),
                ),
            )
            match_id = int(cursor.lastrowid)

            for item in jogo.get("gols_vasco", []) if isinstance(jogo.get("gols_vasco"), list) else []:
                name, goals, club = _parse_goal_item(item)
                if not name:
                    continue
                player_id = _ensure_player(conn, name)
                conn.execute(
                    """
                    INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
                    VALUES (?, 'vasco', ?, ?, ?, ?, 0)
                    """,
                    (match_id, player_id, name, goals, club),
                )

            for item in jogo.get("gols_adversario", []) if isinstance(jogo.get("gols_adversario"), list) else []:
                name, goals, club = _parse_goal_item(item)
                if not name:
                    continue
                player_id = _ensure_player(conn, name)
                conn.execute(
                    """
                    INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
                    VALUES (?, 'adversario', ?, ?, ?, ?, 0)
                    """,
                    (match_id, player_id, name, goals, club or adversario or None),
                )

            anulados = jogo.get("gols_anulados") if isinstance(jogo.get("gols_anulados"), dict) else {}
            for item in anulados.get("vasco", []) if isinstance(anulados.get("vasco"), list) else []:
                name, goals, club = _parse_goal_item(item)
                if not name:
                    continue
                player_id = _ensure_player(conn, name)
                conn.execute(
                    """
                    INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
                    VALUES (?, 'vasco', ?, ?, ?, ?, 1)
                    """,
                    (match_id, player_id, name, goals, club),
                )
            for item in anulados.get("adversario", []) if isinstance(anulados.get("adversario"), list) else []:
                name, goals, club = _parse_goal_item(item)
                if not name:
                    continue
                player_id = _ensure_player(conn, name)
                conn.execute(
                    """
                    INSERT INTO match_goals(match_id, side, player_id, player_name, goals, club_name, is_disallowed)
                    VALUES (?, 'adversario', ?, ?, ?, ?, 1)
                    """,
                    (match_id, player_id, name, goals, club or adversario or None),
                )


def load_matches(db_path: str) -> list[dict[str, Any]]:
    with _open(db_path) as conn:
        _create_schema(conn)
        rows = conn.execute(
            """
            SELECT m.id, m.date_text, t.name AS adversario, c.name AS competicao,
                   m.location, m.vasco_goals, m.opponent_goals, m.observation,
                   ch.name AS tecnico, m.table_position, m.lineup_json
            FROM matches m
            LEFT JOIN teams t ON t.id = m.opponent_team_id
            LEFT JOIN competitions c ON c.id = m.competition_id
            LEFT JOIN coaches ch ON ch.id = m.coach_id
            ORDER BY m.id
            """
        ).fetchall()

        goals_by_match: dict[int, dict[str, list[dict[str, Any]]]] = {}
        goals_rows = conn.execute(
            """
            SELECT match_id, side, player_name, goals, club_name, is_disallowed
            FROM match_goals
            ORDER BY id
            """
        ).fetchall()
        for g in goals_rows:
            mid = int(g["match_id"])
            bucket = goals_by_match.setdefault(
                mid,
                {
                    "gols_vasco": [],
                    "gols_adversario": [],
                    "anulados_vasco": [],
                    "anulados_adversario": [],
                },
            )
            payload = {"nome": g["player_name"], "gols": int(g["goals"])}
            if g["club_name"]:
                payload["clube"] = g["club_name"]
            side = g["side"]
            is_dis = bool(g["is_disallowed"])
            if side == "vasco":
                (bucket["anulados_vasco"] if is_dis else bucket["gols_vasco"]).append(payload)
            else:
                (bucket["anulados_adversario"] if is_dis else bucket["gols_adversario"]).append(payload)

    jogos: list[dict[str, Any]] = []
    for row in rows:
        mid = int(row["id"])
        g = goals_by_match.get(mid, {})
        lineup = {}
        try:
            lineup_raw = row["lineup_json"]
            if lineup_raw:
                lineup = json.loads(lineup_raw)
        except Exception:
            lineup = {}

        jogos.append(
            {
                "data": row["date_text"] or "",
                "adversario": row["adversario"] or "",
                "competicao": row["competicao"] or "",
                "local": row["location"] or "",
                "placar": {
                    "vasco": int(row["vasco_goals"] or 0),
                    "adversario": int(row["opponent_goals"] or 0),
                },
                "gols_vasco": g.get("gols_vasco", []),
                "gols_adversario": g.get("gols_adversario", []),
                "gols_anulados": {
                    "vasco": g.get("anulados_vasco", []),
                    "adversario": g.get("anulados_adversario", []),
                },
                "observacao": row["observation"] or "",
                "tecnico": row["tecnico"] or "",
                "posicao_tabela": row["table_position"],
                "escalacao_partida": lineup if isinstance(lineup, dict) else {},
            }
        )
    return jogos


def save_future_matches(db_path: str, jogos: list[dict[str, Any]]) -> None:
    if not isinstance(jogos, list):
        jogos = []
    with _open(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM future_matches")
        for jogo in jogos:
            if not isinstance(jogo, dict):
                continue
            match_text = str(jogo.get("jogo", "")).strip()
            date_text = str(jogo.get("data", "")).strip()
            is_home_raw = jogo.get("em_casa")
            is_home = None if is_home_raw is None else (1 if bool(is_home_raw) else 0)
            competicao = str(jogo.get("campeonato", "")).strip()

            adversario = ""
            if " x " in match_text:
                p1, p2 = match_text.split(" x ", 1)
                if "vasco" in p1.casefold():
                    adversario = p2.strip()
                elif "vasco" in p2.casefold():
                    adversario = p1.strip()

            op_team_id = _ensure_team(conn, adversario, "adversario") if adversario else None
            comp_id = _ensure_competition(conn, competicao)
            conn.execute(
                """
                INSERT INTO future_matches(date_text, date_iso, match_text, is_home, competition_id, opponent_team_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    date_text,
                    _parse_data_iso(date_text),
                    match_text,
                    is_home,
                    comp_id,
                    op_team_id,
                ),
            )


def load_future_matches(db_path: str) -> list[dict[str, Any]]:
    with _open(db_path) as conn:
        _create_schema(conn)
        rows = conn.execute(
            """
            SELECT f.date_text, f.match_text, f.is_home, c.name AS campeonato
            FROM future_matches f
            LEFT JOIN competitions c ON c.id = f.competition_id
            ORDER BY f.id
            """
        ).fetchall()

    return [
        {
            "jogo": row["match_text"] or "",
            "data": row["date_text"] or "",
            "em_casa": None if row["is_home"] is None else bool(row["is_home"]),
            "campeonato": row["campeonato"] or "",
        }
        for row in rows
    ]


def save_current_squad(db_path: str, dados: dict[str, Any]) -> None:
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": [], "tecnico": ""}

    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []
    tecnico = str(dados.get("tecnico", "") or "").strip()

    with _open(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM current_squad")
        for item in jogadores:
            if isinstance(item, dict):
                nome = str(item.get("nome", "")).strip()
                posicao = str(item.get("posicao", "")).strip()
                condicao = str(item.get("condicao", "")).strip()
            else:
                nome = str(item or "").strip()
                posicao = ""
                condicao = ""
            if not nome:
                continue
            pid = _ensure_player(conn, nome)
            if pid is None:
                continue
            conn.execute(
                "INSERT OR REPLACE INTO current_squad(player_id, position, condition) VALUES (?, ?, ?)",
                (pid, posicao, condicao),
            )
        conn.execute(
            "INSERT INTO settings(key, value) VALUES ('elenco_tecnico', ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (tecnico,),
        )


def load_current_squad(db_path: str) -> dict[str, Any]:
    with _open(db_path) as conn:
        _create_schema(conn)
        rows = conn.execute(
            """
            SELECT p.name, s.position, s.condition
            FROM current_squad s
            JOIN players p ON p.id = s.player_id
            ORDER BY lower(p.name), p.name
            """
        ).fetchall()
        tecnico = conn.execute(
            "SELECT value FROM settings WHERE key = 'elenco_tecnico'"
        ).fetchone()

    return {
        "jogadores": [
            {
                "nome": row["name"],
                "posicao": row["position"] or "",
                "condicao": row["condition"] or "",
            }
            for row in rows
        ],
        "tecnico": tecnico["value"] if tecnico else "",
    }


def save_historic_players(db_path: str, dados: dict[str, Any]) -> None:
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": []}

    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []

    with _open(db_path) as conn:
        _create_schema(conn)
        conn.execute("DELETE FROM historic_players")
        for item in jogadores:
            if isinstance(item, dict):
                nome = str(item.get("nome", "")).strip()
                posicao = str(item.get("posicao", "")).strip()
            else:
                nome = str(item or "").strip()
                posicao = ""
            if not nome:
                continue
            pid = _ensure_player(conn, nome)
            if pid is None:
                continue
            conn.execute(
                "INSERT OR REPLACE INTO historic_players(player_id, position) VALUES (?, ?)",
                (pid, posicao),
            )


def load_historic_players(db_path: str) -> dict[str, Any]:
    with _open(db_path) as conn:
        _create_schema(conn)
        rows = conn.execute(
            """
            SELECT p.name, h.position
            FROM historic_players h
            JOIN players p ON p.id = h.player_id
            ORDER BY lower(p.name), p.name
            """
        ).fetchall()
    return {
        "jogadores": [{"nome": row["name"], "posicao": row["position"] or ""} for row in rows]
    }


def _save_titles_conn(conn: sqlite3.Connection, titulos: list[dict[str, Any]]) -> None:
    if not isinstance(titulos, list):
        titulos = []
    _create_schema(conn)
    conn.execute("DELETE FROM vasco_titles")
    seen: set[tuple[int, int]] = set()
    for item in titulos:
        if not isinstance(item, dict):
            continue
        campeonato = str(item.get("campeonato", "")).strip()
        if not campeonato:
            continue
        try:
            ano = int(item.get("ano", 0))
        except Exception:
            continue
        if ano < 1900 or ano > 2100:
            continue
        comp_id = _ensure_competition(conn, campeonato)
        if comp_id is None:
            continue
        key = (comp_id, ano)
        if key in seen:
            continue
        seen.add(key)
        conn.execute(
            "INSERT OR IGNORE INTO vasco_titles(competition_id, year) VALUES (?, ?)",
            (comp_id, ano),
        )


def save_titles(db_path: str, titulos: list[dict[str, Any]]) -> None:
    with _open(db_path) as conn:
        _save_titles_conn(conn, titulos)


def load_titles(db_path: str) -> list[dict[str, Any]]:
    with _open(db_path) as conn:
        _create_schema(conn)
        rows = conn.execute(
            """
            SELECT c.name AS campeonato, t.year AS ano
            FROM vasco_titles t
            JOIN competitions c ON c.id = t.competition_id
            ORDER BY t.year, lower(c.name), c.name
            """
        ).fetchall()
    return [
        {
            "campeonato": row["campeonato"] or "",
            "ano": int(row["ano"] or 0),
        }
        for row in rows
        if row["campeonato"]
    ]


def backup_database_snapshot(data_dir: str, db_path: str) -> None:
    if not os.path.exists(db_path):
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "stats_vasco"
    for nome in os.listdir(data_dir):
        if nome.startswith(f"{prefix}.backup_") and nome.endswith(".sqlite3"):
            try:
                os.remove(os.path.join(data_dir, nome))
            except Exception:
                pass
    target = os.path.join(data_dir, f"{prefix}.backup_{ts}.sqlite3")
    try:
        shutil.copy2(db_path, target)
    except Exception:
        pass


def _migrate_from_json(db_path: str, json_paths: dict[str, str]) -> None:
    jogos = _json_load_file(json_paths.get("jogos", ""), [])
    futuros = _json_load_file(json_paths.get("futuros", ""), [])
    listas = _json_load_file(
        json_paths.get("listas", ""),
        {
            "clubes_adversarios": [],
            "jogadores_vasco": [],
            "jogadores_contra": [],
            "competicoes": [],
            "tecnicos": [DEFAULT_TECNICO],
            "tecnico_atual": DEFAULT_TECNICO,
        },
    )
    elenco = _json_load_file(json_paths.get("elenco", ""), {"jogadores": [], "tecnico": ""})
    historico = _json_load_file(json_paths.get("historico", ""), {"jogadores": []})
    titulos = _json_load_file(json_paths.get("titulos", ""), [])

    save_listas(db_path, listas)
    save_matches(db_path, jogos)
    save_future_matches(db_path, futuros)
    save_current_squad(db_path, elenco)
    save_historic_players(db_path, historico)
    save_titles(db_path, titulos)


def bootstrap_database(db_path: str, json_paths: dict[str, str] | None = None) -> None:
    with _open(db_path) as conn:
        _create_schema(conn)
        row = conn.execute("SELECT value FROM metadata WHERE key = 'json_migrated_v1'").fetchone()
        if row is not None:
            return

    if json_paths:
        _migrate_from_json(db_path, json_paths)

    with _open(db_path) as conn:
        conn.execute(
            "INSERT INTO metadata(key, value) VALUES('json_migrated_v1', '1') "
            "ON CONFLICT(key) DO UPDATE SET value='1'"
        )

    listas = load_listas(db_path)
    save_listas(db_path, listas)

    # Migração pontual de títulos legados sem depender do fluxo principal de migração v1.
    with _open(db_path) as conn:
        _create_schema(conn)
        titulos_row = conn.execute(
            "SELECT value FROM metadata WHERE key = 'titles_json_migrated_v1'"
        ).fetchone()
        if titulos_row is None and json_paths:
            legacy_titles = _json_load_file(json_paths.get("titulos", ""), [])
            if isinstance(legacy_titles, list) and legacy_titles:
                _save_titles_conn(conn, legacy_titles)
            conn.execute(
                "INSERT INTO metadata(key, value) VALUES('titles_json_migrated_v1', '1') "
                "ON CONFLICT(key) DO UPDATE SET value='1'"
            )
