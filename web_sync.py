from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Callable

from storage_sqlite import (
    load_current_squad,
    load_future_matches,
    load_historic_players,
    load_matches,
)

DEFAULT_API_URL = "https://acervo-api-production.up.railway.app"
_timer_lock = threading.Lock()
_pending_timer: threading.Timer | None = None
_status_callback: Callable[[dict[str, Any]], None] | None = None


def _truthy(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "sim", "s", "on"}


def set_status_callback(callback: Callable[[dict[str, Any]], None] | None) -> None:
    global _status_callback
    _status_callback = callback


def _log_path(db_path: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(db_path)), "web_sync.log")


def _write_log(db_path: str, message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n"
    try:
        with open(_log_path(db_path), "a", encoding="utf-8") as f:
            f.write(line)
    except Exception:
        pass


def _emit_status(db_path: str, payload: dict[str, Any]) -> None:
    payload = dict(payload)
    payload.setdefault("log_path", _log_path(db_path))
    callback = _status_callback
    if callback is not None:
        try:
            callback(payload)
        except Exception:
            pass


def _read_settings(db_path: str) -> dict[str, str]:
    if not os.path.exists(db_path):
        return {}
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
    except Exception:
        return {}
    return {str(key): str(value) for key, value in rows}


def sync_config(db_path: str) -> dict[str, Any]:
    settings = _read_settings(db_path)
    token = (
        os.environ.get("ACERVO_ADMIN_TOKEN")
        or os.environ.get("ACERVO_WEB_ADMIN_TOKEN")
        or settings.get("web_sync_admin_token")
        or ""
    ).strip()
    api_url = (
        os.environ.get("ACERVO_API_URL")
        or settings.get("web_sync_api_url")
        or DEFAULT_API_URL
    ).strip().rstrip("/")
    enabled_raw = os.environ.get("ACERVO_AUTO_SYNC_WEB")
    if enabled_raw is None:
        enabled_raw = settings.get("web_sync_enabled")
    enabled = _truthy(enabled_raw) if enabled_raw is not None else bool(token)
    return {"enabled": enabled and bool(token), "api_url": api_url, "admin_token": token}


def build_state(db_path: str) -> dict[str, Any]:
    return {
        "matches": load_matches(db_path),
        "future_matches": load_future_matches(db_path),
        "current_squad": load_current_squad(db_path),
        "historic_players": load_historic_players(db_path),
    }


def _parse_match_date(value: Any) -> datetime | None:
    try:
        return datetime.strptime(str(value or "").strip(), "%d/%m/%Y")
    except Exception:
        return None


def _match_key(match: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(match.get("id") or "").strip(),
        str(match.get("data") or "").strip(),
        str(match.get("adversario") or "").strip().casefold(),
    )


def _latest_match(matches: list[dict[str, Any]]) -> dict[str, Any]:
    if not matches:
        return {}
    return max(
        matches,
        key=lambda item: (
            _parse_match_date(item.get("data")) or datetime.min,
            int(item.get("id") or 0) if str(item.get("id") or "").isdigit() else 0,
        ),
    )


def state_summary(state: dict[str, Any]) -> dict[str, Any]:
    matches = state.get("matches", []) if isinstance(state.get("matches"), list) else []
    future = state.get("future_matches", []) if isinstance(state.get("future_matches"), list) else []
    current = state.get("current_squad", {}) if isinstance(state.get("current_squad"), dict) else {}
    historic = state.get("historic_players", {}) if isinstance(state.get("historic_players"), dict) else {}
    latest = _latest_match(matches)
    return {
        "matches": len(matches),
        "future_matches": len(future),
        "current_squad": len(current.get("jogadores", [])) if isinstance(current.get("jogadores"), list) else 0,
        "historic_players": len(historic.get("jogadores", [])) if isinstance(historic.get("jogadores"), list) else 0,
        "latest_match": {
            "id": latest.get("id"),
            "data": latest.get("data"),
            "adversario": latest.get("adversario"),
            "competicao": latest.get("competicao"),
            "placar": latest.get("placar"),
        }
        if latest
        else None,
    }


def validate_no_remote_regression(local_state: dict[str, Any], remote_state: dict[str, Any]) -> None:
    """Bloqueia publicação quando o estado local está atrás do estado remoto."""
    local_matches = local_state.get("matches", []) if isinstance(local_state.get("matches"), list) else []
    remote_matches = remote_state.get("matches", []) if isinstance(remote_state.get("matches"), list) else []
    if not remote_matches:
        return

    local_latest = _latest_match(local_matches)
    remote_latest = _latest_match(remote_matches)
    local_latest_date = _parse_match_date(local_latest.get("data"))
    remote_latest_date = _parse_match_date(remote_latest.get("data"))
    local_keys = {_match_key(match) for match in local_matches}
    remote_latest_key = _match_key(remote_latest)

    if not local_latest:
        raise RuntimeError("Sync bloqueado: o estado remoto tem jogos e o banco local nao tem nenhum jogo.")
    if remote_latest_date and (not local_latest_date or remote_latest_date > local_latest_date):
        raise RuntimeError(
            "Sync bloqueado: o Railway tem um jogo mais recente que o banco local "
            f"({remote_latest.get('data')} {remote_latest.get('adversario')}). "
            "Faça git pull, atualize o PRD local e tente novamente."
        )
    if len(remote_matches) > len(local_matches):
        raise RuntimeError(
            "Sync bloqueado: o Railway tem mais jogos que o banco local "
            f"({len(remote_matches)} remoto x {len(local_matches)} local). "
            "Faça git pull e confira se o PRD local não está atrasado antes de publicar."
        )
    if remote_latest_key not in local_keys:
        raise RuntimeError(
            "Sync bloqueado: o ultimo jogo remoto nao existe no banco local "
            f"({remote_latest.get('data')} {remote_latest.get('adversario')}). "
            "Isso indica risco de sobrescrever uma atualização feita em outra máquina."
        )


def fetch_remote_state(api_url: str, admin_token: str, *, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{api_url.rstrip('/')}/admin/state",
        method="GET",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError("Resposta remota inesperada ao consultar /admin/state.")
    return data


def sync_state(db_path: str, *, reason: str = "desktop-change", timeout: int = 30) -> dict[str, Any]:
    config = sync_config(db_path)
    if not config["enabled"]:
        return {"ok": False, "skipped": True, "reason": "web sync disabled or missing token"}

    state = build_state(db_path)
    try:
        remote_state = fetch_remote_state(config["api_url"], config["admin_token"], timeout=timeout)
        validate_no_remote_regression(state, remote_state)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": f"Falha na trava anti-regressao: {detail}"}
    except Exception as exc:
        return {"ok": False, "error": f"Falha na trava anti-regressao: {exc}"}

    payload = {
        "reason": reason,
        "source": "StatsVasco desktop",
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "state": state,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{config['api_url']}/admin/sync-state",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config['admin_token']}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": detail}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    try:
        data = json.loads(raw)
    except Exception:
        data = {"raw": raw}
    if isinstance(data, dict):
        data.setdefault("ok", True)
        return data
    return {"ok": True, "response": data}


def schedule_sync_after_change(db_path: str, *, reason: str, delay: float = 1.5) -> None:
    config = sync_config(db_path)
    if not config["enabled"]:
        _emit_status(db_path, {"state": "disabled", "reason": reason})
        return

    def run() -> None:
        _emit_status(db_path, {"state": "syncing", "reason": reason})
        _write_log(db_path, f"iniciando reason={reason}")
        result = sync_state(db_path, reason=reason)
        if not result.get("ok"):
            _write_log(db_path, f"falhou reason={reason} result={result}")
            _emit_status(db_path, {"state": "error", "reason": reason, "result": result})
            print(f"[web-sync] falhou: {result}")
        else:
            _write_log(
                db_path,
                "ok "
                f"reason={reason} "
                f"matches={result.get('matches')} "
                f"future_matches={result.get('future_matches')} "
                f"current_squad={result.get('current_squad')}",
            )
            _emit_status(db_path, {"state": "success", "reason": reason, "result": result})
            print(
                "[web-sync] ok: "
                f"{result.get('matches')} jogos, "
                f"{result.get('future_matches')} futuros"
            )

    global _pending_timer
    with _timer_lock:
        if _pending_timer is not None:
            _pending_timer.cancel()
        _emit_status(db_path, {"state": "queued", "reason": reason, "delay": delay})
        _write_log(db_path, f"agendado reason={reason} delay={delay}")
        _pending_timer = threading.Timer(delay, run)
        _pending_timer.daemon = True
        _pending_timer.start()
