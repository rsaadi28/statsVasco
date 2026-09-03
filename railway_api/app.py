from __future__ import annotations

import hmac
import os
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from scripts.export_acervo_web import POS_ORDER, build_runtime_from_state, parse_date
from web_sync import validate_no_remote_regression

from .state import init_db, load_state, save_state_key

APP_NAME = "Acervo Vasco API"

app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.environ.get("ACERVO_ALLOWED_ORIGINS", "*").split(",")],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["authorization", "content-type", "x-admin-token"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def _admin_token_from_header(authorization: str | None, x_admin_token: str | None) -> str:
    if x_admin_token:
        return x_admin_token.strip()
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.casefold() == "bearer":
            return token.strip()
    return ""


def require_admin(authorization: str | None, x_admin_token: str | None) -> None:
    expected = os.environ.get("ACERVO_ADMIN_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=500, detail="ACERVO_ADMIN_TOKEN não configurado no servidor.")
    provided = _admin_token_from_header(authorization, x_admin_token)
    if not provided or not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Token de admin inválido.")


def _data_token_from_header(authorization: str | None, x_acervo_data_token: str | None) -> str:
    if x_acervo_data_token:
        return x_acervo_data_token.strip()
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.casefold() == "bearer":
            return token.strip()
    return ""


def require_data_access(authorization: str | None, x_acervo_data_token: str | None) -> None:
    expected = os.environ.get("ACERVO_DATA_TOKEN", "").strip()
    if not expected:
        return
    provided = _data_token_from_header(authorization, x_acervo_data_token)
    if not provided or not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Chave de acesso inválida.")


def _score(match: dict[str, Any]) -> tuple[int, int]:
    placar = match.get("placar") if isinstance(match.get("placar"), dict) else {}
    try:
        vasco = int(placar.get("vasco"))
        adv = int(placar.get("adversario"))
    except Exception as exc:
        raise ValueError("placar precisa conter vasco e adversario como inteiros.") from exc
    if vasco < 0 or adv < 0:
        raise ValueError("placar não pode ter gols negativos.")
    return vasco, adv


def validate_match(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Cada jogo precisa ser um objeto JSON.")
    match = dict(raw)
    if "horario" not in match and "hora" in match:
        match["horario"] = match.get("hora")
    if "escalacao_partida" not in match and isinstance(match.get("escalacao"), dict):
        match["escalacao_partida"] = match.get("escalacao")

    data = str(match.get("data") or "").strip()
    adversario = str(match.get("adversario") or "").strip()
    if not data or not parse_date(data):
        raise ValueError("data obrigatória em dd/mm/aaaa.")
    if not adversario:
        raise ValueError("adversario obrigatório.")
    local = str(match.get("local") or "").strip()
    if local and local not in {"casa", "fora"}:
        raise ValueError("local precisa ser casa ou fora.")
    _score(match)
    match["data"] = data
    match["adversario"] = adversario
    match["local"] = local or "casa"
    return match


def validate_future_match(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Cada jogo futuro precisa ser um objeto JSON.")
    item = dict(raw)
    if "hora" not in item and "horario" in item:
        item["hora"] = item.get("horario")
    if "campeonato" not in item and "competicao" in item:
        item["campeonato"] = item.get("competicao")
    if "local" not in item and "estadio" in item:
        item["local"] = item.get("estadio")

    data = str(item.get("data") or "").strip()
    jogo = str(item.get("jogo") or "").strip()
    if not data or not parse_date(data):
        raise ValueError("data obrigatória em dd/mm/aaaa para jogo futuro.")
    if not jogo:
        adversario = str(item.get("adversario") or "").strip()
        em_casa = item.get("em_casa", item.get("emCasa"))
        if adversario:
            jogo = f"Vasco x {adversario}" if em_casa is not False else f"{adversario} x Vasco"
    if not jogo:
        raise ValueError("jogo obrigatório para jogo futuro.")
    em_casa = item.get("em_casa", item.get("emCasa"))
    if em_casa is not None:
        em_casa = bool(em_casa)
    return {
        "jogo": jogo,
        "data": data,
        "em_casa": em_casa,
        "local": str(item.get("local") or "").strip(),
        "hora": str(item.get("hora") or "").strip(),
        "campeonato": str(item.get("campeonato") or "").strip(),
    }


def validate_current_squad(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        raw = {"jogadores": raw}
    if not isinstance(raw, dict):
        raise ValueError("current_squad precisa ser objeto JSON.")
    jogadores = raw.get("jogadores", [])
    if not isinstance(jogadores, list):
        raise ValueError("current_squad.jogadores precisa ser lista.")
    out = []
    for player in jogadores:
        if not isinstance(player, dict):
            continue
        nome = str(player.get("nome") or "").strip()
        if not nome:
            continue
        out.append(
            {
                "nome": nome,
                "posicao": str(player.get("posicao") or "").strip(),
                "condicao": str(player.get("condicao") or "").strip(),
                "capitao": bool(player.get("capitao")),
            }
        )
    return {"jogadores": out, "tecnico": str(raw.get("tecnico") or "").strip()}


def validate_historic_players(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        raw = {"jogadores": raw}
    if not isinstance(raw, dict):
        raise ValueError("historic_players precisa ser objeto JSON.")
    jogadores = raw.get("jogadores", [])
    if not isinstance(jogadores, list):
        raise ValueError("historic_players.jogadores precisa ser lista.")
    out = []
    for player in jogadores:
        if not isinstance(player, dict):
            continue
        nome = str(player.get("nome") or "").strip()
        if not nome:
            continue
        item = dict(player)
        item["nome"] = nome
        item["posicao"] = str(item.get("posicao") or "").strip()
        out.append(item)
    return {"jogadores": out}


def validate_state_payload(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Payload de sync precisa ser um objeto JSON.")
    state = raw.get("state") if isinstance(raw.get("state"), dict) else raw
    missing = [key for key in ("matches", "future_matches", "current_squad", "historic_players") if key not in state]
    if missing:
        raise ValueError(f"Payload de sync incompleto. Campos ausentes: {', '.join(missing)}.")
    matches_raw = state.get("matches")
    future_raw = state.get("future_matches")
    if not isinstance(matches_raw, list):
        raise ValueError("matches precisa ser lista.")
    if not isinstance(future_raw, list):
        raise ValueError("future_matches precisa ser lista.")
    return {
        "matches": [validate_match(item) for item in matches_raw],
        "future_matches": [validate_future_match(item) for item in future_raw],
        "current_squad": validate_current_squad(state.get("current_squad")),
        "historic_players": validate_historic_players(state.get("historic_players")),
    }


def validate_partial_state_payload(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("Payload de atualização parcial precisa ser um objeto JSON.")
    state = raw.get("state") if isinstance(raw.get("state"), dict) else raw
    allowed = ("future_matches", "current_squad", "historic_players")
    present = [key for key in allowed if key in state]
    if not present:
        raise ValueError(
            "Informe ao menos um de: future_matches, current_squad ou historic_players."
        )
    updates: dict[str, Any] = {}
    if "future_matches" in state:
        future_matches = state["future_matches"]
        if not isinstance(future_matches, list):
            raise ValueError("future_matches precisa ser lista.")
        updates["future_matches"] = [validate_future_match(item) for item in future_matches]
    if "current_squad" in state:
        updates["current_squad"] = validate_current_squad(state["current_squad"])
    if "historic_players" in state:
        updates["historic_players"] = validate_historic_players(state["historic_players"])
    return updates


def match_key(match: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(match.get("data") or "").strip().casefold(),
        str(match.get("adversario") or "").strip().casefold(),
        str(match.get("competicao") or "").strip().casefold(),
    )


def merge_matches(existing: list[dict[str, Any]], incoming: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    items = [item for item in existing if isinstance(item, dict)]
    index = {match_key(item): pos for pos, item in enumerate(items)}
    inserted = updated = 0
    for match in incoming:
        key = match_key(match)
        if key in index:
            items[index[key]] = match
            updated += 1
        else:
            index[key] = len(items)
            items.append(match)
            inserted += 1
    items.sort(key=lambda item: (parse_date(item.get("data")) or datetime.min, str(item.get("adversario") or "")))
    return items, inserted, updated


def update_current_squad_from_match(current: dict[str, Any], match: dict[str, Any]) -> dict[str, Any]:
    lineup = match.get("escalacao_partida")
    if not isinstance(lineup, dict):
        return current

    existing = current.get("jogadores", []) if isinstance(current, dict) else []
    pos_by_name = {
        str(player.get("nome") or "").strip(): str(player.get("posicao") or "").strip()
        for player in existing
        if isinstance(player, dict) and str(player.get("nome") or "").strip()
    }
    captain = str(match.get("capitao") or "").strip()
    status_by_name: dict[str, str] = {}

    titulares = lineup.get("titulares_por_posicao") if isinstance(lineup.get("titulares_por_posicao"), dict) else {}
    for pos in POS_ORDER:
        for name in titulares.get(pos, []) if isinstance(titulares.get(pos, []), list) else []:
            clean = str(name).strip()
            if clean:
                pos_by_name[clean] = pos
                status_by_name[clean] = "Titular"

    status_sources = [
        ("reservas", "Reserva"),
        ("nao_relacionados", "Não Relacionado"),
        ("lesionados", "Lesionado"),
        ("suspensos", "Suspenso"),
        ("servindo_selecao", "Servindo a seleção"),
    ]
    for key, status in status_sources:
        names = lineup.get(key, [])
        if not isinstance(names, list):
            continue
        for name in names:
            clean = str(name).strip()
            if clean:
                status_by_name.setdefault(clean, status)

    for player in existing:
        if not isinstance(player, dict):
            continue
        name = str(player.get("nome") or "").strip()
        if not name or name in status_by_name:
            continue
        if str(player.get("condicao") or "").strip() == "Emprestado":
            status_by_name[name] = "Emprestado"
        else:
            status_by_name[name] = "Não Relacionado"

    jogadores = [
        {
            "nome": name,
            "posicao": pos_by_name.get(name) or "Meio-Campista",
            "condicao": status,
            "capitao": bool(captain and name == captain),
        }
        for name, status in sorted(status_by_name.items(), key=lambda pair: pair[0].casefold())
    ]
    return {"jogadores": jogadores, "tecnico": str(match.get("tecnico") or current.get("tecnico") or "").strip()}


def runtime_js() -> str:
    state = load_state()
    return build_runtime_from_state(
        state.get("matches", []),
        state.get("future_matches", []),
        state.get("current_squad", {}),
        state.get("historic_players", {}),
        source_label="Railway Postgres",
    )


@app.get("/health")
def health() -> dict[str, Any]:
    state = load_state()
    return {
        "ok": True,
        "matches": len(state.get("matches", [])),
        "future_matches": len(state.get("future_matches", [])),
    }


@app.get("/data-runtime.js")
def data_runtime(
    authorization: str | None = Header(default=None),
    x_acervo_data_token: str | None = Header(default=None),
) -> Response:
    require_data_access(authorization, x_acervo_data_token)
    return Response(
        runtime_js(),
        media_type="application/javascript; charset=utf-8",
        headers={"Cache-Control": "no-store, max-age=0", "Access-Control-Allow-Origin": "*"},
    )


@app.post("/admin/import-match")
async def import_match(
    request: Request,
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> JSONResponse:
    require_admin(authorization, x_admin_token)
    payload = await request.json()
    raw_items = payload if isinstance(payload, list) else [payload]
    try:
        matches = [validate_match(item) for item in raw_items]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state = load_state()
    merged, inserted, updated = merge_matches(state.get("matches", []), matches)
    save_state_key("matches", merged)
    current_squad = state.get("current_squad", {"jogadores": [], "tecnico": ""})
    for match in matches:
        current_squad = update_current_squad_from_match(current_squad, match)
    save_state_key("current_squad", current_squad)
    return JSONResponse(
        {
            "ok": True,
            "inserted": inserted,
            "updated": updated,
            "total_matches": len(merged),
        }
    )


@app.post("/admin/sync-state")
async def sync_state(
    request: Request,
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> JSONResponse:
    require_admin(authorization, x_admin_token)
    payload = await request.json()
    try:
        state = validate_state_payload(payload)
        validate_no_remote_regression(state, load_state())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    for key, value in state.items():
        save_state_key(key, value)
    return JSONResponse(
        {
            "ok": True,
            "matches": len(state["matches"]),
            "future_matches": len(state["future_matches"]),
            "current_squad": len(state["current_squad"].get("jogadores", [])),
            "historic_players": len(state["historic_players"].get("jogadores", [])),
        }
    )


@app.get("/admin/state")
def admin_state(
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_admin(authorization, x_admin_token)
    return load_state()


@app.post("/admin/update-state")
async def update_state(
    request: Request,
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> JSONResponse:
    """Atualiza agenda/elenco/histórico sem substituir o acervo de partidas."""
    require_admin(authorization, x_admin_token)
    payload = await request.json()
    try:
        updates = validate_partial_state_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for key, value in updates.items():
        save_state_key(key, value)
    return JSONResponse(
        {
            "ok": True,
            "updated_keys": list(updates),
            "future_matches": len(updates["future_matches"])
            if "future_matches" in updates
            else None,
            "current_squad": len(updates["current_squad"].get("jogadores", []))
            if "current_squad" in updates
            else None,
            "historic_players": len(updates["historic_players"].get("jogadores", []))
            if "historic_players" in updates
            else None,
        }
    )


@app.get("/admin/status")
def admin_status(
    authorization: str | None = Header(default=None),
    x_admin_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_admin(authorization, x_admin_token)
    state = load_state()
    return {
        "matches": len(state.get("matches", [])),
        "future_matches": len(state.get("future_matches", [])),
        "current_squad": len(state.get("current_squad", {}).get("jogadores", [])),
        "historic_players": len(state.get("historic_players", {}).get("jogadores", [])),
    }
