#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_PRD_DB = Path.home() / "Library/Application Support/StatsVasco/stats_vasco.sqlite3"

SOURCE_URLS = {
    "indice_netvasco": "https://www.netvasco.com.br/futebol/index2000.shtml",
    "estatisticas_netvasco": "https://www.netvasco.com.br/futebol/estatisticas2000",
    "brasileiro_mauro_prais": "https://www.netvasco.com.br/mauroprais/vasco/2000br.html",
    "confirmacao_2000_03_01": "https://www.netvasco.com.br/n/379745/confira-os-jogos-do-vasco-na-historia-em-1-de-marco",
    "palmeiras_oficial_2000_03_01": "https://www.palmeiras.com.br/lightbox_galeria/torneio-rio-sao-paulo-2000/",
    "verdazzo_2000_03_01": "https://www.verdazzo.com.br/jogo/20000301-palmeiras-x-vasco-da-gama-torneio-rio-sao-paulo-2000/",
    "vaskipedia_tecnico_alcir": "https://vaskipedia.com/treinador/alcir-portella/",
    "folha_londrina_lopes_reassume": "https://www.folhadelondrina.com.br/esporte/lopes-reassume-o-comando-do-vasco-na-2-feira-258317.html",
    "vaskipedia_2000_06_11": "https://vaskipedia.com/jogo/campeonato-estadual/vascoxflamengo/4827/",
    "supervasco_tita_2000": "https://www.supervasco.com/noticias/vice-em-2000-tita-traz-pessimas-recordacoes-como-treinador-do-vasco-31439.html",
    "soccerzz_mundial_final": "https://www.soccerzz.com/match/2000-01-14-corinthians-vasco/348077",
    "zerozero_mercosul_final": "https://www.zerozero.pt/jogo/2000-12-20-palmeiras-vasco/1111830",
}

DETAIL_SOURCE_CANDIDATES = [
    {
        "jogo": "01/03/2000 Palmeiras-SP x Vasco",
        "campos": "estadio, arbitragem, cartões do Vasco, escalação, técnico, gols adversários",
        "fonte": "Palmeiras oficial + Verdazzo",
        "status": "confirmado para SQL de enriquecimento",
    },
    {
        "jogo": "14/01/2000 Corinthians x Vasco",
        "campos": "estadio, horario, arbitragem, publico, escalação, reservas, técnico",
        "fonte": "Soccerzz/Football-Lineups/Wikipedia",
        "status": "candidato para próxima leva",
    },
    {
        "jogo": "20/12/2000 Palmeiras-SP x Vasco",
        "campos": "estadio, arbitragem, cartões, escalação, técnico, gols e minutos",
        "fonte": "NetVasco especial + Zerozero/Playmaker/Verdazzo",
        "status": "candidato para próxima leva",
    },
    {
        "jogo": "Jogos de Brasileiro/Mercosul/Rio-SP",
        "campos": "estadio, tecnico, escalação, gols, cartões quando disponível",
        "fonte": "oGol/Zerozero/PlaymakerStats/Soccerzz + páginas oficiais dos adversários",
        "status": "fonte complementar por jogo",
    },
]

EXPECTED_TOTALS = {
    "jogos": 89,
    "vitorias": 51,
    "empates": 19,
    "derrotas": 19,
    "gols_pro": 176,
    "gols_contra": 103,
}

EXPECTED_COMPETITION_TOTALS = {
    "Amistoso": (3, 3, 0, 0, 12, 0),
    "Campeonato Brasileiro Serie A": (32, 15, 9, 8, 54, 49),
    "Campeonato Carioca": (22, 15, 3, 4, 57, 20),
    "Copa do Brasil": (5, 2, 3, 0, 8, 5),
    "Copa Mercosul": (13, 8, 1, 4, 23, 13),
    "Mundial de Clubes": (4, 3, 1, 0, 7, 2),
    "Torneio Rio-São Paulo": (10, 5, 2, 3, 15, 14),
}


@dataclass(frozen=True)
class ExpectedMatch:
    date: str
    opponent: str
    competition: str
    location: str
    vasco_goals: int
    opponent_goals: int
    vasco_scorers: str
    source: str = "NetVasco 2000"


EXPECTED_MATCHES = [
    ExpectedMatch("03/01/2000", "Sel. Argélia", "Amistoso", "casa", 7, 0, "Donizete (2), Juninho, Romário, Felipe, Dedé, Viola"),
    ExpectedMatch("06/01/2000", "South Melbourne", "Mundial de Clubes", "casa", 2, 0, "Felipe, Edmundo"),
    ExpectedMatch("08/01/2000", "Manchester United", "Mundial de Clubes", "fora", 3, 1, "Romário (2), Edmundo"),
    ExpectedMatch("11/01/2000", "Necaxa", "Mundial de Clubes", "casa", 2, 1, "Odvan, Romário"),
    ExpectedMatch("14/01/2000", "Corinthians", "Mundial de Clubes", "fora", 0, 0, "-"),
    ExpectedMatch("23/01/2000", "Palmeiras-SP", "Torneio Rio-São Paulo", "casa", 3, 3, "Romário (2), Viola"),
    ExpectedMatch("27/01/2000", "Fluminense-RJ", "Torneio Rio-São Paulo", "fora", 2, 1, "Romário (2)"),
    ExpectedMatch("30/01/2000", "Corinthians", "Torneio Rio-São Paulo", "casa", 1, 0, "Romário"),
    ExpectedMatch("05/02/2000", "Palmeiras-SP", "Torneio Rio-São Paulo", "fora", 1, 2, "Romário"),
    ExpectedMatch("09/02/2000", "Fluminense-RJ", "Torneio Rio-São Paulo", "casa", 1, 0, "Romário"),
    ExpectedMatch("13/02/2000", "Corinthians", "Torneio Rio-São Paulo", "fora", 1, 1, "Romário"),
    ExpectedMatch("19/02/2000", "São Paulo-SP", "Torneio Rio-São Paulo", "fora", 3, 0, "Gilberto, Dedé, Romário"),
    ExpectedMatch("23/02/2000", "São Paulo-SP", "Torneio Rio-São Paulo", "casa", 2, 1, "Romário (2)"),
    ExpectedMatch("26/02/2000", "Palmeiras-SP", "Torneio Rio-São Paulo", "casa", 1, 2, "Romário"),
    ExpectedMatch("01/03/2000", "Palmeiras-SP", "Torneio Rio-São Paulo", "fora", 0, 4, "-", "NetVasco - jogos em 1º de março"),
    ExpectedMatch("12/03/2000", "Madureira-RJ", "Campeonato Carioca", "casa", 2, 0, "Edmundo (2)"),
    ExpectedMatch("15/03/2000", "Botafogo-PB", "Copa do Brasil", "fora", 3, 1, "Edmundo, Dedé, P. Miranda"),
    ExpectedMatch("18/03/2000", "Bangu-RJ", "Campeonato Carioca", "casa", 3, 0, "Edmundo, A. Oliveira, Pedrinho"),
    ExpectedMatch("22/03/2000", "Friburguense", "Campeonato Carioca", "fora", 1, 0, "Edmundo"),
    ExpectedMatch("25/03/2000", "Americano-RJ", "Campeonato Carioca", "casa", 6, 0, "Romário (4), Edmundo, P. Miranda"),
    ExpectedMatch("29/03/2000", "Olaria-RJ", "Campeonato Carioca", "fora", 4, 1, "Romário (3), Edmundo"),
    ExpectedMatch("02/04/2000", "Fluminense-RJ", "Campeonato Carioca", "fora", 3, 2, "Luciano (contra), Romário, Edmundo"),
    ExpectedMatch("09/04/2000", "Botafogo", "Campeonato Carioca", "casa", 0, 0, "-"),
    ExpectedMatch("12/04/2000", "V. Redonda", "Campeonato Carioca", "fora", 3, 0, "J. Baiano, P. Miranda, Odvan"),
    ExpectedMatch("15/04/2000", "América", "Campeonato Carioca", "fora", 3, 1, "Romário (2), Pedrinho"),
    ExpectedMatch("19/04/2000", "Cabo Frio", "Campeonato Carioca", "casa", 5, 0, "Romário (2), Odvan, Viola, P. Miranda"),
    ExpectedMatch("23/04/2000", "Flamengo-RJ", "Campeonato Carioca", "fora", 5, 1, "Romário (3), Felipe, Pedrinho"),
    ExpectedMatch("27/04/2000", "Ponte Preta-SP", "Copa do Brasil", "casa", 1, 1, "Romário"),
    ExpectedMatch("30/04/2000", "Madureira-RJ", "Campeonato Carioca", "fora", 3, 1, "Pedrinho (2), Viola"),
    ExpectedMatch("03/05/2000", "Ponte Preta-SP", "Copa do Brasil", "fora", 1, 0, "Gilberto"),
    ExpectedMatch("06/05/2000", "América", "Campeonato Carioca", "casa", 1, 2, "Viola"),
    ExpectedMatch("10/05/2000", "Americano-RJ", "Campeonato Carioca", "fora", 2, 0, "Romário, Pedrinho"),
    ExpectedMatch("13/05/2000", "Olaria-RJ", "Campeonato Carioca", "casa", 6, 1, "Romário (2), Gilberto, Viola, Amaral, L. Cláudio (contra)"),
    ExpectedMatch("17/05/2000", "Bangu-RJ", "Campeonato Carioca", "fora", 4, 1, "Viola (2), Romário, Dedé"),
    ExpectedMatch("21/05/2000", "Fluminense-RJ", "Campeonato Carioca", "casa", 0, 1, "-"),
    ExpectedMatch("24/05/2000", "Fluminense-RJ", "Copa do Brasil", "fora", 1, 1, "Pedrinho"),
    ExpectedMatch("28/05/2000", "Flamengo-RJ", "Campeonato Carioca", "casa", 3, 3, "Edmundo, Juninho, Viola"),
    ExpectedMatch("31/05/2000", "Fluminense-RJ", "Copa do Brasil", "casa", 2, 2, "Edmundo (2)"),
    ExpectedMatch("04/06/2000", "Friburguense", "Campeonato Carioca", "casa", 1, 0, "Juninho"),
    ExpectedMatch("07/06/2000", "Botafogo", "Campeonato Carioca", "fora", 1, 1, "Edmundo"),
    ExpectedMatch("11/06/2000", "Flamengo-RJ", "Campeonato Carioca", "fora", 0, 3, "-"),
    ExpectedMatch("17/06/2000", "Flamengo-RJ", "Campeonato Carioca", "casa", 1, 2, "Viola"),
    ExpectedMatch("30/06/2000", "Rio Branco", "Amistoso", "fora", 2, 0, "Odvan"),
    ExpectedMatch("22/07/2000", "São Cristóvão", "Amistoso", "fora", 3, 0, "Luiz Cláudio, Felipe, Zada"),
    ExpectedMatch("29/07/2000", "Sport-PE", "Campeonato Brasileiro Serie A", "casa", 0, 2, "-"),
    ExpectedMatch("01/08/2000", "Peñarol", "Copa Mercosul", "fora", 3, 4, "Viola (2), Romário"),
    ExpectedMatch("06/08/2000", "Cruzeiro-MG", "Campeonato Brasileiro Serie A", "casa", 3, 3, "Viola (2), Romário"),
    ExpectedMatch("11/08/2000", "Corinthians", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Romário"),
    ExpectedMatch("13/08/2000", "Guarani-SP", "Campeonato Brasileiro Serie A", "fora", 1, 0, "Viola"),
    ExpectedMatch("16/08/2000", "Santa Cruz-PE", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Romário"),
    ExpectedMatch("20/08/2000", "Ponte Preta-SP", "Campeonato Brasileiro Serie A", "casa", 2, 1, "Romário (2)"),
    ExpectedMatch("24/08/2000", "San Lorenzo", "Copa Mercosul", "casa", 3, 0, "Romário (2), Fabiano Eller"),
    ExpectedMatch("27/08/2000", "Portuguesa", "Campeonato Brasileiro Serie A", "fora", 2, 2, "Luiz Cláudio (2)"),
    ExpectedMatch("31/08/2000", "Atlético-MG", "Copa Mercosul", "fora", 0, 2, "-"),
    ExpectedMatch("05/09/2000", "Atlético-PR", "Campeonato Brasileiro Serie A", "casa", 2, 2, "Viola, Romário"),
    ExpectedMatch("07/09/2000", "Peñarol", "Copa Mercosul", "casa", 1, 1, "Romário"),
    ExpectedMatch("10/09/2000", "Bahia-BA", "Campeonato Brasileiro Serie A", "fora", 1, 3, "Felipe"),
    ExpectedMatch("13/09/2000", "Fluminense-RJ", "Campeonato Brasileiro Serie A", "casa", 4, 3, "Romário (2), Juninho, Juninho Paulista"),
    ExpectedMatch("20/09/2000", "América-MG", "Campeonato Brasileiro Serie A", "casa", 4, 0, "Romário (2), Juninho, Euller"),
    ExpectedMatch("24/09/2000", "Juventude-RS", "Campeonato Brasileiro Serie A", "fora", 2, 1, "Romário (2)"),
    ExpectedMatch("28/09/2000", "San Lorenzo", "Copa Mercosul", "fora", 2, 0, "Juninho, Romário"),
    ExpectedMatch("04/10/2000", "Atlético-MG", "Campeonato Brasileiro Serie A", "casa", 4, 0, "Juninho (2), Nasa, Pedrinho"),
    ExpectedMatch("11/10/2000", "Vitória-BA", "Campeonato Brasileiro Serie A", "casa", 2, 2, "Romário, Juninho Paulista"),
    ExpectedMatch("14/10/2000", "Santos", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Juninho Paulista"),
    ExpectedMatch("17/10/2000", "Atlético-MG", "Copa Mercosul", "casa", 2, 0, "Romário, Juninho Paulista"),
    ExpectedMatch("21/10/2000", "Gama-DF", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Romário"),
    ExpectedMatch("24/10/2000", "Goiás-GO", "Campeonato Brasileiro Serie A", "casa", 2, 1, "Juninho, Juninho Paulista"),
    ExpectedMatch("27/10/2000", "Flamengo-RJ", "Campeonato Brasileiro Serie A", "fora", 0, 4, "-"),
    ExpectedMatch("31/10/2000", "R. Central", "Copa Mercosul", "casa", 1, 0, "Juninho Paulista"),
    ExpectedMatch("03/11/2000", "Coritiba-PR", "Campeonato Brasileiro Serie A", "fora", 1, 0, "Júnior Baiano"),
    ExpectedMatch("05/11/2000", "Internacional-RS", "Campeonato Brasileiro Serie A", "fora", 0, 2, "-"),
    ExpectedMatch("08/11/2000", "R. Central", "Copa Mercosul", "fora", 0, 1, "-"),
    ExpectedMatch("10/11/2000", "Palmeiras-SP", "Campeonato Brasileiro Serie A", "fora", 0, 3, "-"),
    ExpectedMatch("12/11/2000", "Botafogo", "Campeonato Brasileiro Serie A", "casa", 1, 2, "Pedrinho"),
    ExpectedMatch("16/11/2000", "Grêmio-RS", "Campeonato Brasileiro Serie A", "fora", 1, 0, "Jorginho"),
    ExpectedMatch("19/11/2000", "São Paulo-SP", "Campeonato Brasileiro Serie A", "casa", 0, 4, "-"),
    ExpectedMatch("22/11/2000", "River Plate", "Copa Mercosul", "fora", 4, 1, "Romário, Júnior Baiano, Juninho Paulista, Pedrinho"),
    ExpectedMatch("25/11/2000", "Bahia-BA", "Campeonato Brasileiro Serie A", "fora", 3, 3, "Clébson, Romário, Juninho"),
    ExpectedMatch("28/11/2000", "Bahia-BA", "Campeonato Brasileiro Serie A", "casa", 3, 2, "Euller (2), Juninho Paulista"),
    ExpectedMatch("30/11/2000", "River Plate", "Copa Mercosul", "casa", 1, 0, "Juninho Paulista"),
    ExpectedMatch("03/12/2000", "Paraná-PR", "Campeonato Brasileiro Serie A", "casa", 3, 1, "Romário (2), Juninho Paulista"),
    ExpectedMatch("06/12/2000", "Palmeiras-SP", "Copa Mercosul", "casa", 2, 0, "Juninho, Romário"),
    ExpectedMatch("09/12/2000", "Paraná-PR", "Campeonato Brasileiro Serie A", "fora", 0, 1, "-"),
    ExpectedMatch("12/12/2000", "Palmeiras-SP", "Copa Mercosul", "fora", 0, 1, "-"),
    ExpectedMatch("16/12/2000", "Cruzeiro-MG", "Campeonato Brasileiro Serie A", "casa", 2, 2, "Euller (2)"),
    ExpectedMatch("20/12/2000", "Palmeiras-SP", "Copa Mercosul", "fora", 4, 3, "Romário (3), Juninho Paulista"),
    ExpectedMatch("23/12/2000", "Cruzeiro-MG", "Campeonato Brasileiro Serie A", "fora", 3, 1, "Juninho, Euller, Romário"),
    ExpectedMatch("27/12/2000", "São Caetano-SP", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Romário"),
    ExpectedMatch("18/01/2001", "São Caetano-SP", "Campeonato Brasileiro Serie A", "casa", 3, 1, "Juninho, Jorginho Paulista, Romário", "NetVasco - jogo válido por 2000"),
]

EXPECTED_TIMES = [
    "20:45",
    "20:45", "18:15", "20:45", "20:00",
    "19:00", "20:30", "19:00", "16:00", "20:30", "18:30", "16:00", "21:40", "16:00", "21:40",
    "17:00", "15:30", "16:00", "20:30", "16:00", "20:30", "17:00", "17:00", "20:30", "16:00", "20:30", "18:30",
    "20:30", "15:00", "21:40", "16:00", "20:30", "16:00", "21:40", "17:00", "20:30", "17:00", "20:30", "17:00",
    "21:40", "18:30", "16:00", "21:00", "15:00",
    "16:00", "19:15", "17:00", "20:30", "18:30", "22:00", "17:00", "19:30", "18:30", "21:15", "20:30", "15:45",
    "18:30", "20:30", "20:30", "18:00", "21:40", "20:30", "22:00", "15:45", "21:40", "18:00", "20:30", "21:40",
    "19:00", "20:30", "16:00", "20:30", "20:30", "17:00", "20:30", "16:00", "22:00", "16:00", "21:40", "21:40",
    "16:00", "21:45", "16:00", "21:45", "16:00", "21:45", "16:00", "21:40", "16:00",
]

EXPECTED_TIME_BY_RAW = {
    (m.date, m.opponent, m.competition): time
    for m, time in zip(EXPECTED_MATCHES, EXPECTED_TIMES, strict=True)
}

KNOWN_RICH_DETAILS = {
    ("01/03/2000", "Palmeiras-SP", "Torneio Rio-São Paulo"): {
        "estadio": "Morumbi",
        "arbitro": "Jorge Travassos dos Santos",
        "escalacao_status": "confirmada",
        "cartoes_status": "confirmados",
        "fonte": "Palmeiras oficial + Verdazzo + NetVasco",
    },
    ("14/01/2000", "Corinthians", "Mundial de Clubes"): {
        "estadio": "Maracanã",
        "arbitro": "Dick Jol",
        "publico_presente": "73000",
        "escalacao_status": "fonte encontrada, pendente de SQL",
        "fonte": "Soccerzz + Wikipedia",
    },
    ("20/12/2000", "Palmeiras-SP", "Copa Mercosul"): {
        "estadio": "Palestra Itália (Parque Antártica)",
        "arbitro": "Márcio Rezende",
        "escalacao_status": "fonte encontrada, pendente de SQL",
        "cartoes_status": "fonte encontrada, pendente de SQL",
        "fonte": "NetVasco especial + Zerozero/Playmaker + Verdazzo",
    },
}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def norm(value: str) -> str:
    value = strip_accents(value or "").casefold().strip()
    for token in ("-rj", "-sp", "-mg", "-pr", "-pe", "-pb", "-ba", "-rs", "-df", "-go"):
        value = value.replace(token, "")
    replacements = {
        "campeonato brasileiro serie a": "brasileiro",
        "campeonato brasileiro série a": "brasileiro",
        "copa joao havelange": "brasileiro",
        "torneio rio-sao paulo": "rio-sao-paulo",
        "r. central": "rosario central",
        "v. redonda": "volta redonda",
        "sel. argelia": "selecao argelia",
        "sao cristovao": "sao cristovao",
    }
    value = replacements.get(value, value)
    return " ".join(value.replace(".", " ").replace("-", " ").split())


def match_key(date: str, opponent: str, competition: str) -> tuple[str, str, str]:
    return date, norm(opponent), norm(competition)


def read_matches(db_path: Path) -> list[dict]:
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT m.id, m.date_text, t.name AS opponent, c.name AS competition,
                   m.location, m.stadium, m.match_time, m.captain_name,
                   m.paid_attendance, m.total_attendance, m.match_revenue,
                   m.arbitration_json, m.lineup_json,
                   ch.name AS coach,
                   m.vasco_goals, m.opponent_goals
            FROM matches m
            LEFT JOIN teams t ON t.id = m.opponent_team_id
            LEFT JOIN competitions c ON c.id = m.competition_id
            LEFT JOIN coaches ch ON ch.id = m.coach_id
            WHERE (m.date_iso >= '2000-01-01' AND m.date_iso < '2001-01-01')
               OR m.date_iso = '2001-01-18'
            ORDER BY m.date_iso, m.id
            """
        ).fetchall()
        goals = defaultdict(list)
        for row in conn.execute(
            """
            SELECT match_id, player_name, goals
            FROM match_goals
            WHERE side = 'vasco' AND is_disallowed = 0
            ORDER BY id
            """
        ):
            goals[int(row["match_id"])].append(f"{row['player_name']}:{int(row['goals'])}")
    finally:
        conn.close()

    return [
        {
            "id": int(row["id"]),
            "date": row["date_text"] or "",
            "opponent": row["opponent"] or "",
            "competition": row["competition"] or "",
            "location": row["location"] or "",
            "stadium": row["stadium"] or "",
            "match_time": row["match_time"] or "",
            "captain": row["captain_name"] or "",
            "paid_attendance": row["paid_attendance"],
            "total_attendance": row["total_attendance"],
            "match_revenue": row["match_revenue"],
            "arbitration_json": row["arbitration_json"] or "{}",
            "lineup_json": row["lineup_json"] or "{}",
            "coach": row["coach"] or "",
            "vasco_goals": int(row["vasco_goals"] or 0),
            "opponent_goals": int(row["opponent_goals"] or 0),
            "vasco_scorers_db": "; ".join(goals[int(row["id"])]),
        }
        for row in rows
    ]


def totals(matches: list[dict]) -> dict[str, int]:
    out = Counter()
    for match in matches:
        vg = match["vasco_goals"]
        og = match["opponent_goals"]
        out["jogos"] += 1
        out["gols_pro"] += vg
        out["gols_contra"] += og
        if vg > og:
            out["vitorias"] += 1
        elif vg == og:
            out["empates"] += 1
        else:
            out["derrotas"] += 1
    return dict(out)


def parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%d/%m/%Y")


def expected_coach(expected: ExpectedMatch) -> str:
    date = parse_date(expected.date)
    date_key = date.strftime("%Y-%m-%d")
    competition = norm(expected.competition)

    if date_key <= "2000-01-14":
        return "Antônio Lopes"
    if competition == norm("Torneio Rio-São Paulo"):
        if date_key <= "2000-02-13":
            return "Alcir Portela"
        return "Antônio Lopes"
    if "2000-03-05" <= date_key <= "2000-06-02":
        return "Abel Braga"
    if "2000-06-04" <= date_key <= "2000-06-11":
        return "Alcir Portela"
    if date_key in {"2000-06-17", "2000-06-30"}:
        return "Tita"
    if "2000-07-01" <= date_key <= "2000-12-17":
        return "Oswaldo de Oliveira"
    if date_key >= "2000-12-18":
        return "Joel Santana"
    return ""


def expected_time(expected: ExpectedMatch) -> str:
    return EXPECTED_TIME_BY_RAW.get((expected.date, expected.opponent, expected.competition), "")


def known_rich_details(expected: ExpectedMatch) -> dict[str, str]:
    return KNOWN_RICH_DETAILS.get((expected.date, expected.opponent, expected.competition), {})


def field_coverage(matches: list[dict]) -> dict[str, int]:
    return {
        "estadio": sum(1 for m in matches if m["stadium"]),
        "horario": sum(1 for m in matches if m["match_time"]),
        "capitao": sum(1 for m in matches if m["captain"]),
        "publico_pagante": sum(1 for m in matches if m["paid_attendance"] is not None),
        "publico_presente": sum(1 for m in matches if m["total_attendance"] is not None),
        "renda": sum(1 for m in matches if m["match_revenue"] is not None),
        "arbitragem": sum(1 for m in matches if m["arbitration_json"] != "{}"),
        "escalacao": sum(1 for m in matches if m["lineup_json"] != "{}"),
    }


def compare(db_matches: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    db_by_key = {match_key(m["date"], m["opponent"], m["competition"]): m for m in db_matches}
    expected_by_key = {match_key(m.date, m.opponent, m.competition): m for m in EXPECTED_MATCHES}

    confirmed = []
    manual_review = []
    ok = []

    for expected in EXPECTED_MATCHES:
        key = match_key(expected.date, expected.opponent, expected.competition)
        actual = db_by_key.get(key)
        if actual is None:
            manual_review.append({"tipo": "faltando_no_banco", "expected": expected, "actual": None})
            continue

        diffs = []
        if norm(actual["opponent"]) != norm(expected.opponent):
            diffs.append(f"adversário banco={actual['opponent']} fonte={expected.opponent}")
        if norm(actual["competition"]) != norm(expected.competition):
            diffs.append(f"competição banco={actual['competition']} fonte={expected.competition}")
        if actual["location"] != expected.location:
            diffs.append(f"local banco={actual['location']} fonte={expected.location}")
        if (actual["vasco_goals"], actual["opponent_goals"]) != (expected.vasco_goals, expected.opponent_goals):
            diffs.append(
                "placar banco="
                f"{actual['vasco_goals']}x{actual['opponent_goals']} "
                f"fonte={expected.vasco_goals}x{expected.opponent_goals}"
            )
        coach = expected_coach(expected)
        if coach and norm(actual["coach"]) != norm(coach):
            diffs.append(f"técnico banco={actual['coach']} fonte={coach}")

        item = {"expected": expected, "actual": actual, "diffs": diffs}
        if diffs:
            if (
                expected.date in {"19/02/2000", "23/02/2000", "26/02/2000", "01/03/2000", "04/06/2000", "07/06/2000", "11/06/2000"}
                or (expected.date == "20/12/2000" and norm(expected.opponent) == norm("Palmeiras-SP"))
            ):
                confirmed.append(item)
            else:
                manual_review.append(item)
        else:
            ok.append(item)

    for actual in db_matches:
        key = match_key(actual["date"], actual["opponent"], actual["competition"])
        if key not in expected_by_key:
            manual_review.append({"tipo": "sobrando_no_banco", "expected": None, "actual": actual, "diffs": []})

    return confirmed, manual_review, ok


def competition_totals(matches: list[dict]) -> dict[str, tuple[int, int, int, int, int, int]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for match in matches:
        grouped[match["competition"]].append(match)

    out = {}
    for competition, rows in grouped.items():
        t = totals(rows)
        out[competition] = (
            t.get("jogos", 0),
            t.get("vitorias", 0),
            t.get("empates", 0),
            t.get("derrotas", 0),
            t.get("gols_pro", 0),
            t.get("gols_contra", 0),
        )
    return out


def render_report(db_path: Path, db_matches: list[dict]) -> str:
    confirmed, manual_review, ok = compare(db_matches)
    db_totals = totals(db_matches)
    comp_totals = competition_totals(db_matches)
    coverage = field_coverage(db_matches)

    lines = [
        "# Auditoria Dos Jogos Do Vasco - Temporada 2000",
        "",
        f"- Banco auditado: `{db_path}`",
        "- Modo de leitura: SQLite `mode=ro`",
        "- Recorte: temporada NetVasco 2000, incluindo `18/01/2001` como jogo válido por 2000",
        "",
        "## Fontes",
    ]
    for name, url in SOURCE_URLS.items():
        lines.append(f"- {name}: {url}")

    lines.extend(
        [
            "",
            "## Totais",
            "",
            "| Métrica | Banco atual | Referência externa | Status |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for metric, expected in EXPECTED_TOTALS.items():
        actual = db_totals.get(metric, 0)
        lines.append(f"| {metric} | {actual} | {expected} | {'OK' if actual == expected else 'DIVERGE'} |")

    lines.extend(
        [
            "",
            "## Cobertura De Campos Ricos No Banco",
            "",
            "| Campo salvo | Preenchidos em PRD | Observação |",
            "| --- | ---: | --- |",
        ]
    )
    observations = {
        "estadio": "buscar em fichas de jogo e páginas oficiais",
        "horario": "NetVasco cobre quase toda a tabela, conferir divergências com outras fontes",
        "capitao": "normalmente só em súmula/ficha detalhada",
        "publico_pagante": "buscar em borderôs/súmulas, oGol/Zerozero e imprensa",
        "publico_presente": "buscar em borderôs/súmulas, oGol/Zerozero e imprensa",
        "renda": "buscar em borderôs/súmulas, oGol/Zerozero e imprensa",
        "arbitragem": "fichas detalhadas, Soccerzz/Zerozero/Playmaker e fontes oficiais",
        "escalacao": "fichas detalhadas, Soccerzz/Zerozero/Playmaker, Football-Lineups e imprensa",
    }
    for field, count in coverage.items():
        lines.append(f"| {field} | {count}/{len(db_matches)} | {observations[field]} |")

    lines.extend(
        [
            "",
            "## Totais Por Competição",
            "",
            "| Competição | Banco atual | Referência externa | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for competition, expected in EXPECTED_COMPETITION_TOTALS.items():
        actual = comp_totals.get(competition, (0, 0, 0, 0, 0, 0))
        lines.append(f"| {competition} | {format_total(actual)} | {format_total(expected)} | {'OK' if actual == expected else 'DIVERGE'} |")

    lines.extend(
        [
            "",
            "## Fontes Complementares Mapeadas",
            "",
            "| Jogo/Grupo | Campos aproveitáveis | Fonte | Status |",
            "| --- | --- | --- | --- |",
        ]
    )
    for candidate in DETAIL_SOURCE_CANDIDATES:
        lines.append(f"| {candidate['jogo']} | {candidate['campos']} | {candidate['fonte']} | {candidate['status']} |")

    lines.extend(
        [
            "",
            "## Enriquecimento Global Preparado",
            "",
            "- Horários: referência externa mapeada para os 89 jogos a partir das páginas de competição do NetVasco.",
            "- Técnicos: regra temporal mapeada para os 89 jogos usando Vaskipédia, Folha de Londrina, SuperVasco, NetVasco/Mauro Prais e fontes das finais.",
            "- Campos ricos restantes: `estadio`, `arbitragem`, `escalacao`, `cartoes`, `publico`, `renda` ficam marcados por jogo no CSV, com fonte candidata e status.",
            "- Arquivos gerados para aplicação/repetição: `docs/auditoria_temporada_2000_mapa.csv` e `docs/sql_enriquecer_temporada_2000_horarios_tecnicos.sql`.",
        ]
    )

    lines.extend(["", "## Confirmado Para Corrigir", ""])
    if confirmed:
        for item in confirmed:
            lines.extend(render_item(item))
    else:
        lines.append("- Nenhuma divergência confirmada.")

    lines.extend(["", "## Precisa Revisão Manual", ""])
    if manual_review:
        for item in manual_review:
            lines.extend(render_item(item))
    else:
        lines.append("- Nenhum caso pendente.")

    lines.extend(["", "## Sem Divergência", ""])
    for item in ok:
        expected = item["expected"]
        actual = item["actual"]
        lines.append(
            f"- {expected.date} | {expected.competition} | {expected.opponent} | "
            f"banco `{actual['vasco_goals']}x{actual['opponent_goals']}` = "
            f"fonte `{expected.vasco_goals}x{expected.opponent_goals}` | "
            f"local `{actual['location']}` | técnico `{actual['coach'] or '-'}` | "
            f"gols banco: {actual['vasco_scorers_db'] or '-'} | "
            f"gols fonte: {expected.vasco_scorers}"
        )

    return "\n".join(lines) + "\n"


def format_total(values: tuple[int, int, int, int, int, int]) -> str:
    jogos, vitorias, empates, derrotas, gols_pro, gols_contra = values
    return f"{jogos}J {vitorias}V {empates}E {derrotas}D {gols_pro}GP {gols_contra}GC"


def render_item(item: dict) -> list[str]:
    expected = item.get("expected")
    actual = item.get("actual")
    diffs = item.get("diffs", [])
    lines = []
    if expected and actual:
        lines.append(
            f"- `{actual['id']}` {expected.date} | {expected.competition} | {expected.opponent}: "
            f"banco `{actual['vasco_goals']}x{actual['opponent_goals']}` vs fonte "
            f"`{expected.vasco_goals}x{expected.opponent_goals}`"
        )
        if diffs:
            lines.append(f"  - Divergências: {'; '.join(diffs)}")
        lines.append(f"  - Gols Vasco no banco: {actual['vasco_scorers_db'] or '-'}")
        lines.append(f"  - Gols Vasco na fonte: {expected.vasco_scorers}")
        coach = expected_coach(expected)
        if coach:
            lines.append(f"  - Técnico esperado: {coach}; técnico no banco: {actual['coach'] or '-'}")
        lines.append(f"  - Fonte: {expected.source}")
    elif expected:
        lines.append(f"- Faltando no banco: {expected.date} | {expected.competition} | {expected.opponent}")
    elif actual:
        lines.append(
            f"- Sobrando no banco: `{actual['id']}` {actual['date']} | {actual['competition']} | "
            f"{actual['opponent']} | {actual['vasco_goals']}x{actual['opponent_goals']}"
        )
    return lines


def rows_for_export(db_matches: list[dict]) -> list[dict[str, str]]:
    db_by_key = {match_key(m["date"], m["opponent"], m["competition"]): m for m in db_matches}
    rows = []
    for expected in EXPECTED_MATCHES:
        actual = db_by_key.get(match_key(expected.date, expected.opponent, expected.competition), {})
        coach = expected_coach(expected)
        time = expected_time(expected)
        details = known_rich_details(expected)
        rows.append(
            {
                "match_id": str(actual.get("id", "")),
                "data": expected.date,
                "competicao": expected.competition,
                "adversario": expected.opponent,
                "local_ref": expected.location,
                "placar_ref": f"{expected.vasco_goals}x{expected.opponent_goals}",
                "placar_banco": (
                    f"{actual.get('vasco_goals', '')}x{actual.get('opponent_goals', '')}"
                    if actual
                    else ""
                ),
                "gols_vasco_ref": expected.vasco_scorers,
                "gols_vasco_banco": str(actual.get("vasco_scorers_db", "")),
                "tecnico_ref": coach,
                "tecnico_banco": str(actual.get("coach", "")),
                "tecnico_status": "OK" if actual and norm(str(actual.get("coach", ""))) == norm(coach) else "corrigir",
                "horario_ref": time,
                "horario_banco": str(actual.get("match_time", "")),
                "horario_status": "OK" if actual and actual.get("match_time") == time else "preencher",
                "estadio_ref": details.get("estadio", ""),
                "estadio_banco": str(actual.get("stadium", "")),
                "estadio_status": "confirmado" if details.get("estadio") else "pesquisar",
                "arbitro_ref": details.get("arbitro", ""),
                "arbitragem_banco": str(actual.get("arbitration_json", "")),
                "arbitragem_status": "confirmado" if details.get("arbitro") else "pesquisar",
                "escalacao_status": details.get("escalacao_status", "pesquisar"),
                "cartoes_status": details.get("cartoes_status", "pesquisar"),
                "publico_presente_ref": details.get("publico_presente", ""),
                "publico_banco": str(actual.get("total_attendance", "")),
                "renda_banco": str(actual.get("match_revenue", "")),
                "fonte_rica": details.get("fonte", "NetVasco núcleo + fontes complementares a pesquisar"),
            }
        )
    return rows


def write_csv_map(path: Path, db_matches: list[dict]) -> None:
    rows = rows_for_export(db_matches)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def iso_date(date_text: str) -> str:
    return datetime.strptime(date_text, "%d/%m/%Y").date().isoformat()


def render_time_coach_sql() -> str:
    lines = [
        "-- Enriquecimento revisável da temporada 2000: horários e técnicos.",
        "-- Gerado por scripts/audit_temporada_2000.py.",
        "-- Fontes: páginas NetVasco por competição, Vaskipédia, Folha de Londrina, SuperVasco e fichas de finais.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for expected in EXPECTED_MATCHES:
        time = expected_time(expected)
        coach = expected_coach(expected)
        date_iso = iso_date(expected.date)
        lines.extend(
            [
                f"-- {expected.date} | {expected.competition} | {expected.opponent}",
                "UPDATE matches",
                f"SET match_time = {sql_quote(time)},",
                f"    coach_id = (SELECT id FROM coaches WHERE name = {sql_quote(coach)} LIMIT 1)",
                "WHERE date_iso = " + sql_quote(date_iso),
                f"  AND opponent_team_id = (SELECT id FROM teams WHERE name = {sql_quote(expected.opponent)} LIMIT 1)",
                f"  AND competition_id = (SELECT id FROM competitions WHERE name = {sql_quote(expected.competition)} LIMIT 1)",
                f"  AND EXISTS (SELECT 1 FROM coaches WHERE name = {sql_quote(coach)});",
                "",
            ]
        )
    lines.extend(
        [
            "SELECT COUNT(*) AS jogos_temporada_2000_com_horario",
            "FROM matches",
            "WHERE ((date_iso >= '2000-01-01' AND date_iso < '2001-01-01') OR date_iso = '2001-01-18')",
            "  AND match_time <> '';",
            "",
            "COMMIT;",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audita os jogos do Vasco na temporada NetVasco 2000.")
    parser.add_argument("--db", type=Path, default=DEFAULT_PRD_DB, help="Caminho do SQLite a auditar em modo read-only.")
    parser.add_argument("--output", type=Path, help="Arquivo Markdown de saída. Se omitido, imprime no stdout.")
    parser.add_argument("--map-output", type=Path, help="Arquivo CSV com o mapa jogo a jogo dos campos auditáveis.")
    parser.add_argument("--sql-output", type=Path, help="Arquivo SQL para preencher horários e técnicos mapeados.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.db.exists():
        raise SystemExit(f"Banco não encontrado: {args.db}")

    db_matches = read_matches(args.db)
    report = render_report(args.db, db_matches)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    if args.map_output:
        write_csv_map(args.map_output, db_matches)
    if args.sql_output:
        args.sql_output.write_text(render_time_coach_sql(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
