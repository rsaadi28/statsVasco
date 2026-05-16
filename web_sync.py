from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from typing import Any

from storage_sqlite import (
    load_current_squad,
    load_future_matches,
    load_historic_players,
    load_matches,
)

DEFAULT_API_URL = "https://acervo-api-production.up.railway.app"
_timer_lock = threading.Lock()
_pending_timer: threading.Timer | None = None


def _truthy(value: Any) -> bool:
    return str(value or "").strip().casefold() in {"1", "true", "yes", "y", "sim", "s", "on"}


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


def sync_state(db_path: str, *, reason: str = "desktop-change", timeout: int = 30) -> dict[str, Any]:
    config = sync_config(db_path)
    if not config["enabled"]:
        return {"ok": False, "skipped": True, "reason": "web sync disabled or missing token"}

    payload = {
        "reason": reason,
        "source": "StatsVasco desktop",
        "sent_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "state": build_state(db_path),
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
        return

    def run() -> None:
        result = sync_state(db_path, reason=reason)
        if not result.get("ok"):
            print(f"[web-sync] falhou: {result}")
        else:
            print(
                "[web-sync] ok: "
                f"{result.get('matches')} jogos, "
                f"{result.get('future_matches')} futuros"
            )

    global _pending_timer
    with _timer_lock:
        if _pending_timer is not None:
            _pending_timer.cancel()
        _pending_timer = threading.Timer(delay, run)
        _pending_timer.daemon = True
        _pending_timer.start()
