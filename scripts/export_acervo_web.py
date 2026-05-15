#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage_sqlite import (  # noqa: E402
    bootstrap_database,
    db_path_for,
    load_current_squad,
    load_future_matches,
    load_historic_players,
    load_matches,
)

WEB_DIR = ROOT / "Acervo Vasco"
OUT_FILE = WEB_DIR / "data-runtime.js"
POS_ORDER = [
    "Goleiro",
    "Lateral-Direito",
    "Zagueiro",
    "Lateral-Esquerdo",
    "Volante",
    "Meio-Campista",
    "Atacante",
]
LINEUP_EXTRA_KEYS = ("reservas", "nao_relacionados", "lesionados", "suspensos", "servindo_selecao")


def parse_date(value: str | None) -> datetime | None:
    try:
        return datetime.strptime(str(value or "").strip(), "%d/%m/%Y")
    except Exception:
        return None


def year_of(match: dict[str, Any]) -> int | None:
    d = parse_date(match.get("data"))
    return d.year if d else None


def result_of(match: dict[str, Any]) -> str:
    placar = match.get("placar") if isinstance(match.get("placar"), dict) else {}
    v = int(placar.get("vasco", 0) or 0)
    a = int(placar.get("adversario", 0) or 0)
    if v > a:
        return "V"
    if v < a:
        return "D"
    return "E"


def score_tuple(match: dict[str, Any]) -> tuple[int, int]:
    placar = match.get("placar") if isinstance(match.get("placar"), dict) else {}
    return int(placar.get("vasco", 0) or 0), int(placar.get("adversario", 0) or 0)


def scoreline(match: dict[str, Any]) -> str:
    v, a = score_tuple(match)
    adv = str(match.get("adversario") or "Adversário")
    return f"Vasco {v} x {a} {adv}"


def pct_points(v: int, e: int, total: int) -> float:
    return round(((v * 3 + e) / (total * 3) * 100), 1) if total else 0.0


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def goal_count(items: Any) -> Counter[str]:
    out: Counter[str] = Counter()
    if not isinstance(items, list):
        return out
    for item in items:
        if isinstance(item, dict):
            name = str(item.get("nome") or "").strip()
            count = max(1, safe_int(item.get("gols"), 1))
        else:
            name = str(item or "").strip()
            count = 1
        if name:
            out[name] += count
    return out


def expanded_goal_names(items: Any) -> list[str]:
    names: list[str] = []
    for name, count in goal_count(items).items():
        names.extend([name] * count)
    return names


def expanded_goal_events(items: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return events
    for item in items:
        if isinstance(item, dict):
            name = str(item.get("nome") or "").strip()
            count = max(1, safe_int(item.get("gols"), 1))
            minutes = item.get("minutos")
            periods = item.get("periodos")
            if not isinstance(minutes, list):
                minutes = [item.get("minuto")] if item.get("minuto") is not None else []
            if not isinstance(periods, list):
                periods = [item.get("periodo")] if item.get("periodo") else []
            extra = {
                "penalti": bool(item.get("penalti")),
                "contra": bool(item.get("contra")) or "contra" in name.casefold(),
            }
        else:
            name = str(item or "").strip()
            count = 1
            minutes = []
            periods = []
            extra = {"penalti": False, "contra": "contra" in name.casefold()}
        if not name:
            continue
        for i in range(count):
            event = {
                "nome": name,
                "minuto": minutes[i] if i < len(minutes) else None,
                "periodo": periods[i] if i < len(periods) else "",
            }
            if extra["penalti"]:
                event["penalti"] = True
            if extra["contra"]:
                event["contra"] = True
            events.append(event)
    return events


def card_names(items: Any) -> list[str]:
    out: list[str] = []
    if not isinstance(items, list):
        return out
    for item in items:
        name = str(item.get("nome") if isinstance(item, dict) else item or "").strip()
        if name:
            out.append(name)
    return out


def red_cards(items: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return out
    for item in items:
        if isinstance(item, dict):
            name = str(item.get("nome") or "").strip()
            minute = item.get("minuto")
            period = str(item.get("periodo") or "")
            reason = str(item.get("motivo") or "").strip()
        else:
            name = str(item or "").strip()
            minute = None
            period = ""
            reason = ""
        if name:
            out.append({"nome": name, "minuto": minute, "periodo": period, "motivo": reason})
    return out


def normalize_lineup(raw: Any) -> dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    titulares_raw = raw.get("titulares_por_posicao") if isinstance(raw.get("titulares_por_posicao"), dict) else {}
    titulares = {
        pos: [str(n).strip() for n in titulares_raw.get(pos, []) if str(n).strip()]
        for pos in POS_ORDER
    }
    lineup: dict[str, Any] = {
        "formacao": str(raw.get("formacao") or "—"),
        "titulares_por_posicao": titulares,
        "substituicoes": [],
    }
    for key in LINEUP_EXTRA_KEYS:
        values = raw.get(key, [])
        lineup[key] = [str(n).strip() for n in values if str(n).strip()] if isinstance(values, list) else []
    subs = raw.get("substituicoes", [])
    if isinstance(subs, list):
        for sub in subs:
            if not isinstance(sub, dict):
                continue
            saiu = str(sub.get("sai") or sub.get("jogador_saiu") or "").strip()
            entrou = str(sub.get("entra") or sub.get("jogador_entrou") or "").strip()
            if not (saiu or entrou):
                continue
            lineup["substituicoes"].append(
                {
                    "sai": saiu,
                    "entra": entrou,
                    "minuto": sub.get("minuto"),
                    "periodo": str(sub.get("periodo") or ""),
                }
            )
    return lineup


def participant_names(lineup: dict[str, Any]) -> tuple[set[str], set[str]]:
    titulares: set[str] = set()
    reservas_entraram: set[str] = set()
    for names in lineup.get("titulares_por_posicao", {}).values():
        for name in names:
            titulares.add(name)
    for sub in lineup.get("substituicoes", []):
        if sub.get("entra"):
            reservas_entraram.add(str(sub["entra"]))
    return titulares, reservas_entraram


def match_detail(match: dict[str, Any], fallback_id: int) -> dict[str, Any]:
    v, a = score_tuple(match)
    arbitragem = match.get("arbitragem") if isinstance(match.get("arbitragem"), dict) else {}
    lineup = normalize_lineup(match.get("escalacao_partida") or match.get("escalacao"))
    return {
        "id": match.get("db_match_id") or fallback_id,
        "data": match.get("data") or "—",
        "adversario": match.get("adversario") or "Adversário",
        "competicao": match.get("competicao") or "—",
        "fase": match.get("fase") or "—",
        "local": match.get("local") or "casa",
        "estadio": match.get("estadio") or "—",
        "horario": match.get("horario") or "—",
        "tecnico": match.get("tecnico") or "—",
        "capitao": match.get("capitao") or "—",
        "placar": {"vasco": v, "adversario": a},
        "agregado": None,
        "gols_vasco": expanded_goal_events(match.get("gols_vasco")),
        "gols_adversario": expanded_goal_events(match.get("gols_adversario")),
        "cartoes_amarelos_vasco": card_names(match.get("cartoes_amarelos_vasco")),
        "cartoes_vermelhos_vasco": red_cards(match.get("cartoes_vermelhos_vasco")),
        "publico_pagante": match.get("publico_pagante") or 0,
        "publico_presente": match.get("publico_presente") or 0,
        "renda": match.get("renda") or 0,
        "arbitragem": {
            "arbitro": arbitragem.get("arbitro") or "—",
            "auxiliares": arbitragem.get("auxiliares") if isinstance(arbitragem.get("auxiliares"), list) else [],
            "var": arbitragem.get("var") or "—",
        },
        "escalacao": lineup,
        "observacao": match.get("observacao") or "Detalhe importado do banco local.",
    }


def aggregate_matches(matches: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(matches)
    v = e = d = gp = gc = 0
    publico_pagante = publico_presente = 0
    renda = 0.0
    invicta = jejum = cur_invicta = cur_jejum = 0
    for match in matches:
        res = result_of(match)
        gpv, gca = score_tuple(match)
        gp += gpv
        gc += gca
        publico_pagante += match.get("publico_pagante") or 0
        publico_presente += match.get("publico_presente") or 0
        renda += float(match.get("renda") or 0)
        if res == "V":
            v += 1
            cur_invicta += 1
            cur_jejum = 0
        elif res == "E":
            e += 1
            cur_invicta += 1
            cur_jejum += 1
        else:
            d += 1
            cur_invicta = 0
            cur_jejum += 1
        invicta = max(invicta, cur_invicta)
        jejum = max(jejum, cur_jejum)
    return {
        "jogos": total,
        "vitorias": v,
        "empates": e,
        "derrotas": d,
        "gols_pro": gp,
        "gols_contra": gc,
        "saldo": gp - gc,
        "aproveitamento": pct_points(v, e, total),
        "media_pro": round(gp / total, 2) if total else 0,
        "media_contra": round(gc / total, 2) if total else 0,
        "maior_invicta": invicta,
        "maior_jejum": jejum,
        "publico_pagante": publico_pagante,
        "publico_presente": publico_presente,
        "renda": round(renda, 2),
    }


def build_seasons(jogos: list[dict[str, Any]], current_squad: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    grouped: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for idx, match in enumerate(jogos, start=1):
        y = year_of(match)
        if y:
            grouped[y].append((idx, match))

    capitao_atual = ""
    for player in current_squad.get("jogadores", []):
        if isinstance(player, dict) and player.get("capitao"):
            capitao_atual = str(player.get("nome") or "")
            break

    seasons: dict[str, Any] = {}
    hints: dict[str, str] = {}
    for year, items in sorted(grouped.items(), reverse=True):
        items.sort(key=lambda im: (parse_date(im[1].get("data")) or datetime.min, im[0]))
        matches = [m for _, m in items]
        resumo = aggregate_matches(matches)
        scorers: Counter[str] = Counter()
        coach_periods: dict[str, dict[str, Any]] = {}
        season_games: list[dict[str, Any]] = []
        brasileiro_round = 0
        for fallback_id, match in items:
            match_id = match.get("db_match_id") or fallback_id
            gpv, gca = score_tuple(match)
            scorers.update(goal_count(match.get("gols_vasco")))
            coach = str(match.get("tecnico") or "—")
            period = coach_periods.setdefault(coach, {"nome": coach, "jogos": 0, "_first": match.get("data"), "_last": match.get("data")})
            period["jogos"] += 1
            period["_last"] = match.get("data")
            if "Brasileiro" in str(match.get("competicao") or ""):
                brasileiro_round += 1
            entry = {
                "id": match_id,
                "data": match.get("data") or "—",
                "local": match.get("local") or "casa",
                "competicao": match.get("competicao") or "—",
                "adversario": match.get("adversario") or "Adversário",
                "resultado": result_of(match),
                "placar": [gpv, gca],
                "tecnico": coach,
                "estadio": match.get("estadio") or "—",
                "publico": match.get("publico_presente") or match.get("publico_pagante") or 0,
            }
            if "Brasileiro" in str(match.get("competicao") or ""):
                entry["rodada"] = brasileiro_round
            if isinstance(match.get("posicao_tabela"), int):
                entry["posicao"] = match["posicao_tabela"]
            season_games.append(entry)
        tecnicos = []
        for period in coach_periods.values():
            first = str(period.pop("_first") or "")
            last = str(period.pop("_last") or "")
            period["periodo"] = first[:5] if first == last else f"{first[:5]} – {last[:5]}"
            tecnicos.append(period)
        artilheiros = [{"nome": nome, "gols": gols} for nome, gols in scorers.most_common(20)]
        seasons[str(year)] = {
            "ano": year,
            "tecnicos": tecnicos,
            "capitao_atual": capitao_atual,
            "resumo": resumo,
            "jogos": season_games,
            "artilheiros": artilheiros or [{"nome": "—", "gols": 0}],
        }
        hints[str(year)] = f"{resumo['jogos']}j · {resumo['vitorias']}V {resumo['empates']}E {resumo['derrotas']}D · {resumo['aproveitamento']:.1f}%"
    return seasons, hints


def build_retros(jogos: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in jogos:
        adv = str(match.get("adversario") or "").strip()
        if not adv:
            continue
        v, a = score_tuple(match)
        grouped[adv].append(
            {
                "data": match.get("data") or "—",
                "competicao": match.get("competicao") or "—",
                "local": match.get("local") or "casa",
                "placar": [v, a],
                "res": result_of(match),
                "gols_vasco": expanded_goal_names(match.get("gols_vasco")),
                "gols_adv": expanded_goal_names(match.get("gols_adversario")),
            }
        )
    out: dict[str, Any] = {}
    for adv, matches in grouped.items():
        matches.sort(key=lambda m: parse_date(m.get("data")) or datetime.min, reverse=True)
        out[adv] = {"adversario": adv, "jogos": matches}
    return out


def split_future_opponent(match_text: str) -> str:
    text = str(match_text or "").strip()
    if " x " not in text:
        return text.replace("Vasco", "").strip(" -")
    left, right = text.split(" x ", 1)
    return right.strip() if "vasco" in left.casefold() else left.strip()


def build_future(jogos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for match in jogos:
        adv = split_future_opponent(match.get("jogo", ""))
        out.append(
            {
                "data": match.get("data") or "—",
                "hora": match.get("hora") or match.get("horario") or "—",
                "adv": adv or "Adversário",
                "local": "casa" if match.get("em_casa") is True else "fora" if match.get("em_casa") is False else "—",
                "estadio": match.get("local") or match.get("estadio") or "—",
                "competicao": match.get("campeonato") or "—",
            }
        )
    out.sort(key=lambda m: parse_date(m["data"]) or datetime.max)
    return out


def build_general(jogos: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    resumo = aggregate_matches(jogos)
    scorers: Counter[str] = Counter()
    against: Counter[str] = Counter()
    for match in jogos:
        scorers.update(goal_count(match.get("gols_vasco")))
        against.update(goal_count(match.get("gols_adversario")))
    totais = {
        "jogos": resumo["jogos"],
        "vitorias": resumo["vitorias"],
        "empates": resumo["empates"],
        "derrotas": resumo["derrotas"],
        "gp": resumo["gols_pro"],
        "gc": resumo["gols_contra"],
        "saldo": resumo["saldo"],
        "aprov": resumo["aproveitamento"],
        "media_gp": resumo["media_pro"],
        "media_gc": resumo["media_contra"],
        "maior_invicta": resumo["maior_invicta"],
        "maior_derrotas": resumo["maior_jejum"],
    }
    return (
        totais,
        [{"nome": n, "gols": g} for n, g in scorers.most_common(80)],
        [{"nome": n, "gols": g} for n, g in against.most_common(80)],
    )


def build_yearly(jogos: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    by_year: dict[int, list[dict[str, Any]]] = defaultdict(list)
    scorers_by_year: dict[str, Counter[str]] = defaultdict(Counter)
    all_scorers: Counter[str] = Counter()
    for match in jogos:
        y = year_of(match)
        if not y:
            continue
        by_year[y].append(match)
        goals = goal_count(match.get("gols_vasco"))
        scorers_by_year[str(y)].update(goals)
        all_scorers.update(goals)
    yearly = []
    totals = {"jogos": 0, "v": 0, "e": 0, "d": 0, "gp": 0, "gc": 0}
    for y, matches in sorted(by_year.items(), reverse=True):
        resumo = aggregate_matches(matches)
        item = {
            "ano": y,
            "v": resumo["vitorias"],
            "e": resumo["empates"],
            "d": resumo["derrotas"],
            "gp": resumo["gols_pro"],
            "gc": resumo["gols_contra"],
            "aprov": resumo["aproveitamento"],
        }
        yearly.append(item)
        totals["jogos"] += resumo["jogos"]
        totals["v"] += resumo["vitorias"]
        totals["e"] += resumo["empates"]
        totals["d"] += resumo["derrotas"]
        totals["gp"] += resumo["gols_pro"]
        totals["gc"] += resumo["gols_contra"]
    artilheiros_por_ano = {
        year: [{"nome": n, "gols": g} for n, g in counter.most_common(20)]
        for year, counter in scorers_by_year.items()
    }
    artilheiros_geral = [{"nome": n, "gols": g} for n, g in all_scorers.most_common(80)]
    return yearly, totals, artilheiros_por_ano, artilheiros_geral


def build_group_tables(jogos: list[dict[str, Any]], key_func) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in jogos:
        key = key_func(match)
        if key:
            grouped[key].append(match)
    table = []
    games_by_key = {}
    for key, matches in grouped.items():
        matches.sort(key=lambda m: parse_date(m.get("data")) or datetime.min)
        resumo = aggregate_matches(matches)
        game_rows = []
        for match in reversed(matches):
            game_rows.append(
                {
                    "data": match.get("data") or "—",
                    "local": match.get("local") or "—",
                    "competicao": match.get("competicao") or "—",
                    "adv": match.get("adversario") or "Adversário",
                    "res": result_of(match),
                    "placar": scoreline(match),
                }
            )
        games_by_key[key] = game_rows
        table.append(
            {
                "nome": key,
                "jogos": resumo["jogos"],
                "v": resumo["vitorias"],
                "e": resumo["empates"],
                "d": resumo["derrotas"],
                "gp": resumo["gols_pro"],
                "gc": resumo["gols_contra"],
                "primeiro": {"data": matches[0].get("data") or "—", "placar": scoreline(matches[0])},
                "ultimo": {"data": matches[-1].get("data") or "—", "placar": scoreline(matches[-1])},
            }
        )
    table.sort(key=lambda row: (-row["jogos"], row["nome"].casefold()))
    return table, games_by_key


def build_coaches(jogos: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in jogos:
        coach = str(match.get("tecnico") or "").strip()
        if coach:
            grouped[coach].append(match)
    table = []
    passages = {}
    for coach, matches in grouped.items():
        matches.sort(key=lambda m: parse_date(m.get("data")) or datetime.min)
        resumo = aggregate_matches(matches)
        scorers = Counter()
        for match in matches:
            scorers.update(goal_count(match.get("gols_vasco")))
        top = scorers.most_common(1)
        maior = {"nome": top[0][0], "gols": top[0][1]} if top else None
        table.append(
            {
                "nome": coach,
                "jogos": resumo["jogos"],
                "casa": sum(1 for m in matches if m.get("local") == "casa"),
                "fora": sum(1 for m in matches if m.get("local") == "fora"),
                "v": resumo["vitorias"],
                "e": resumo["empates"],
                "d": resumo["derrotas"],
                "gp": resumo["gols_pro"],
                "gc": resumo["gols_contra"],
                "saldo": resumo["saldo"],
                "aprov": resumo["aproveitamento"],
                "maior_goleador": maior,
            }
        )
        period = f"{matches[0].get('data', '')} – {matches[-1].get('data', '')}"
        passages[coach] = {
            "resumo": {"jogos": resumo["jogos"], "v": resumo["vitorias"], "e": resumo["empates"], "d": resumo["derrotas"]},
            "passagens": [
                {
                    "idx": 1,
                    "jogos": resumo["jogos"],
                    "v": resumo["vitorias"],
                    "e": resumo["empates"],
                    "d": resumo["derrotas"],
                    "gp": resumo["gols_pro"],
                    "gc": resumo["gols_contra"],
                    "saldo": resumo["saldo"],
                    "aprov": resumo["aproveitamento"],
                    "artilheiro": maior or {"nome": "—", "gols": 0},
                    "periodo": period,
                }
            ],
            "jogos": [
                {
                    "data": m.get("data") or "—",
                    "local": m.get("local") or "—",
                    "competicao": m.get("competicao") or "—",
                    "adv": m.get("adversario") or "Adversário",
                    "res": result_of(m),
                    "placar": scoreline(m),
                    "passagem": 1,
                }
                for m in reversed(matches)
            ],
        }
    table.sort(key=lambda row: (-row["jogos"], row["nome"].casefold()))
    return table, passages


def player_presence(jogos: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "jogos_participacao": 0,
            "minutos": 0,
            "jogos_titular": 0,
            "jogos_reserva": 0,
            "gols": 0,
            "amarelos": 0,
            "vermelhos": 0,
            "ved": {"v": 0, "e": 0, "d": 0},
            "partidas": [],
        }
    )
    for match in jogos:
        lineup = normalize_lineup(match.get("escalacao_partida") or match.get("escalacao"))
        titulares, reservas_entraram = participant_names(lineup)
        scorers = goal_count(match.get("gols_vasco"))
        yellows = Counter(card_names(match.get("cartoes_amarelos_vasco")))
        reds = Counter(c["nome"] for c in red_cards(match.get("cartoes_vermelhos_vasco")))
        res = result_of(match)
        for name in sorted(titulares | reservas_entraram | set(scorers)):
            st = stats[name]
            titular = name in titulares
            participou = titular or name in reservas_entraram
            if participou:
                st["jogos_participacao"] += 1
                st["minutos"] += 90 if titular else 25
                st["jogos_titular" if titular else "jogos_reserva"] += 1
                st["ved"][res.lower()] += 1
            st["gols"] += scorers.get(name, 0)
            st["amarelos"] += yellows.get(name, 0)
            st["vermelhos"] += reds.get(name, 0)
            v, a = score_tuple(match)
            st["partidas"].append(
                {
                    "data": match.get("data") or "—",
                    "adv": match.get("adversario") or "Adversário",
                    "placar": f"{v}x{a}",
                    "res": res,
                    "titular": titular,
                    "minutos": 90 if titular else 25 if name in reservas_entraram else 0,
                    "gols": scorers.get(name, 0),
                    "amarelo": yellows.get(name, 0) > 0,
                    "vermelho": reds.get(name, 0) > 0,
                }
            )
    return stats


def build_players(
    jogos: list[dict[str, Any]],
    current_squad: dict[str, Any],
    historic_players: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    presence = player_presence(jogos)
    positions: dict[str, str] = {}
    squad_status: dict[str, str] = {}
    captains: set[str] = set()
    emprestados: list[dict[str, Any]] = []

    status_map = {
        "Titular": "titular",
        "Reserva": "reserva",
        "Não Relacionado": "nao-rel",
        "Nao Relacionado": "nao-rel",
        "Lesionado": "lesionado",
        "Suspenso": "suspenso",
        "Servindo a seleção": "selecao",
        "Servindo a selecao": "selecao",
        "Emprestado": "emprestado",
    }
    for player in current_squad.get("jogadores", []):
        if not isinstance(player, dict):
            continue
        name = str(player.get("nome") or "").strip()
        if not name:
            continue
        positions[name] = str(player.get("posicao") or "—")
        status = status_map.get(str(player.get("condicao") or ""), "reserva")
        squad_status[name] = status
        if player.get("capitao"):
            captains.add(name)
        if status == "emprestado":
            emprestados.append({"nome": name, "posicao": positions[name], "clube": "—", "ate": "—"})

    for player in historic_players.get("jogadores", []):
        if isinstance(player, dict) and player.get("nome"):
            positions.setdefault(str(player["nome"]), str(player.get("posicao") or "—"))

    names = set(positions) | set(presence)
    elenco_rows = []
    jogadores: dict[str, Any] = {}
    for name in sorted(names, key=str.casefold):
        st = presence.get(name, {})
        games = int(st.get("jogos_participacao", 0) or 0)
        minutes = int(st.get("minutos", 0) or 0)
        goals = int(st.get("gols", 0) or 0)
        titular = int(st.get("jogos_titular", 0) or 0)
        reserva = int(st.get("jogos_reserva", 0) or 0)
        status = squad_status.get(name, "ex")
        pos = positions.get(name, "—")
        elenco_rows.append({"nome": name, "posicao": pos, "status": status, "minutos": minutes, "numero": None, "gols": goals})
        stats = {
            "jogos_participacao": games,
            "minutos": minutes,
            "media_minutos": round(minutes / games, 2) if games else 0,
            "jogos_titular": titular,
            "jogos_reserva": reserva,
            "nao_entrou": 0,
            "nao_relacionado": 0,
            "lesionado": 0,
            "suspenso": 0,
            "selecao": 0,
            "gols": goals,
            "jogos_capitao": 0,
            "partidas_marcou": sum(1 for p in st.get("partidas", []) if p.get("gols")),
            "gols_titular": goals,
            "gols_banco": 0,
            "media_gols": round(goals / games, 2) if games else 0,
            "amarelos": int(st.get("amarelos", 0) or 0),
            "vermelhos": int(st.get("vermelhos", 0) or 0),
            "amarelos_acumulados": int(st.get("amarelos", 0) or 0) % 3,
            "suspensao_pendente": False,
            "media_min_entre_gols": round(minutes / goals) if goals else None,
            "ved": st.get("ved", {"v": 0, "e": 0, "d": 0}),
        }
        jogadores[name] = {
            "nome": name,
            "nome_completo": name,
            "posicao": pos,
            "numero": None,
            "nascimento": "—",
            "naturalidade": "—",
            "altura_cm": None,
            "pe": "—",
            "capitao_atual": name in captains,
            "contratado_de": "—",
            "status_atual": status,
            "passagens": [
                {
                    "id": "p1",
                    "periodo": "Acervo",
                    "estreia": st.get("partidas", [{}])[0].get("data", "—") if st.get("partidas") else "—",
                    "saida": "Ainda no elenco" if status != "ex" else "—",
                    "idx": 1,
                    "stats": stats,
                    "partidas": st.get("partidas", []),
                }
            ],
        }
    return elenco_rows, jogadores, emprestados


def build_details(jogos: list[dict[str, Any]]) -> dict[str, Any]:
    details: dict[str, Any] = {}
    for fallback_id, match in enumerate(jogos, start=1):
        detail = match_detail(match, fallback_id)
        details[str(detail["id"])] = detail
        details[f"{detail['data']}|{detail['adversario']}"] = detail
    return details


def js_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def build_runtime(db_path: Path) -> str:
    bootstrap_database(str(db_path))
    jogos = load_matches(str(db_path))
    futuros = load_future_matches(str(db_path))
    current_squad = load_current_squad(str(db_path))
    historic_players = load_historic_players(str(db_path))

    seasons, hints = build_seasons(jogos, current_squad)
    details = build_details(jogos)
    geral, artilheiros, carrascos = build_general(jogos)
    yearly, yearly_totals, artilheiros_por_ano, artilheiros_geral = build_yearly(jogos)
    estadios, jogos_por_estadio = build_group_tables(jogos, lambda m: str(m.get("estadio") or "").strip())
    arbitros, jogos_por_arbitro = build_group_tables(
        jogos,
        lambda m: str((m.get("arbitragem") or {}).get("arbitro") or "").strip()
        if isinstance(m.get("arbitragem"), dict)
        else "",
    )
    tecnicos, passagens_tecnicos = build_coaches(jogos)
    elenco_data, jogadores, emprestados = build_players(jogos, current_squad, historic_players)

    latest_year = max((int(y) for y in seasons), default=None)
    latest_detail = None
    if jogos:
        latest_match = max(enumerate(jogos, start=1), key=lambda im: (parse_date(im[1].get("data")) or datetime.min, im[0]))
        latest_detail = match_detail(latest_match[1], latest_match[0])

    lines = [
        "// Acervo Vasco — dados gerados automaticamente.",
        f"// Fonte: {db_path}",
        f"// Gerado em: {datetime.now().isoformat(timespec='seconds')}",
        "window.ACERVO_RUNTIME_LOADED = true;",
        f"window.ACERVO_SEASONS = {js_value(seasons)};",
        f"window.ACERVO_YEAR_HINTS = {js_value(hints)};",
    ]
    if latest_year and str(latest_year) in seasons:
        lines.append(f"window.SEASON_{latest_year} = window.ACERVO_SEASONS[{json.dumps(str(latest_year))}];")
        if latest_year == 2026:
            lines.append("window.SEASON_2026 = window.ACERVO_SEASONS['2026'];")
    lines.extend(
        [
            f"window.PARTIDAS_DETALHES = {js_value(details)};",
            f"window.PARTIDA_PAYSANDU = {js_value(latest_detail or {})};",
            f"window.GERAL_TOTAIS = {js_value(geral)};",
            f"window.ARTILHEIROS_VASCO = {js_value(artilheiros)};",
            f"window.CARRASCOS = {js_value(carrascos)};",
            f"window.RETROSPECTOS = {js_value(build_retros(jogos))};",
            f"window.JOGOS_FUTUROS = {js_value(build_future(futuros))};",
            f"window.ELENCO_DATA = {js_value(elenco_data)};",
            f"window.JOGADORES = {js_value(jogadores)};",
            f"window.EMPRESTADOS = {js_value(emprestados)};",
            f"window.TECNICOS = {js_value(tecnicos)};",
            f"window.PASSAGENS_TECNICOS = {js_value(passagens_tecnicos)};",
            f"window.ESTADIOS = {js_value(estadios)};",
            f"window.JOGOS_POR_ESTADIO = {js_value(jogos_por_estadio)};",
            f"window.ARBITROS = {js_value(arbitros)};",
            f"window.JOGOS_POR_ARBITRO = {js_value(jogos_por_arbitro)};",
            f"window.YEARLY = {js_value(yearly)};",
            f"window.YEARLY_TOTAIS = {js_value(yearly_totals)};",
            f"window.ARTILHEIROS_POR_ANO = {js_value(artilheiros_por_ano)};",
            f"window.ARTILHEIROS_GERAL = {js_value(artilheiros_geral)};",
            """
window.gameSeriesForYear = function(ano) {
  const season = window.ACERVO_SEASONS && window.ACERVO_SEASONS[String(ano)];
  if (!season) return [];
  return season.jogos.map((j, i) => ({ idx: i + 1, res: j.resultado, gp: j.placar[0], gc: j.placar[1], comp: j.competicao, adv: j.adversario, data: j.data }));
};
window.gameSeriesGeral = function() {
  return Object.keys(window.ACERVO_SEASONS || {})
    .sort((a, b) => Number(a) - Number(b))
    .flatMap((ano) => window.gameSeriesForYear(Number(ano)).map((j) => ({ ...j, ano: Number(ano) })));
};
""".strip(),
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta o SQLite do StatsVasco para o runtime do protótipo Acervo Vasco.")
    parser.add_argument("--db", default=db_path_for(str(ROOT)), help="Caminho do stats_vasco.sqlite3.")
    parser.add_argument("--out", default=str(OUT_FILE), help="Arquivo JS de saída.")
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(build_runtime(db_path), encoding="utf-8")
    print(f"Exportado: {out_path}")


if __name__ == "__main__":
    main()
