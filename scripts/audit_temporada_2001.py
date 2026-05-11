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
    "indice_netvasco": "https://www.netvasco.com.br/futebol/index2001.shtml",
    "estatisticas_netvasco": "https://www.netvasco.com.br/futebol/estatisticas2001/",
    "rio_sao_paulo_netvasco": "https://www.netvasco.com.br/futebol/riosaopaulo2001/",
    "estadual_netvasco": "https://www.netvasco.com.br/futebol/estadual2001/",
    "libertadores_netvasco": "https://www.netvasco.com.br/futebol/libertadores2001/",
    "mercosul_netvasco": "https://www.netvasco.com.br/futebol/mercosul2001/",
    "brasileiro_netvasco": "https://www.netvasco.com.br/futebol/brasileiro2001/index.html",
    "amistosos_netvasco": "https://www.netvasco.com.br/futebol/amistosos2001/",
    "leon_supervasco": "https://www.supervasco.com/noticias/ha-12-anos-vasco-vencia-amistoso-contra-o-leonmex-por-3-a-1-185670.html",
    "leon_blog_garone": "https://blogdogarone.blogspot.com/2011/07/bau-do-portuga-ha-10-anos-vasco-vencia.html",
    "bahia_netvasco_ficha": "https://www.netvasco.com.br/futebol/brasileiro2001/50vasbah.html",
    "corinthians_rsp_netvasco_ficha": "https://www.netvasco.com.br/futebol/riosaopaulo2001/05vascor.html",
}

DETAIL_SOURCE_CANDIDATES = [
    {
        "jogo": "08/07/2001 León x Vasco",
        "campos": "estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações",
        "fonte": "NetVasco Amistosos 2001 + SuperVasco + Blog do Garone",
        "status": "confirmado para SQL de correção/enriquecimento; ficha NetVasco traz ano 2000 por provável erro de template",
    },
    {
        "jogo": "10/07/2001 Tigres x Vasco",
        "campos": "estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações",
        "fonte": "NetVasco Amistosos 2001",
        "status": "confirmado para SQL de correção/enriquecimento; ficha NetVasco traz ano 2000 por provável erro de template",
    },
    {
        "jogo": "31/01/2001 Vasco x Corinthians",
        "campos": "estádio, arbitragem, público, escalação, substituições, gols/minutos, cartões e observações",
        "fonte": "NetVasco Rio-São Paulo 2001, ficha 05vascor",
        "status": "fonte detalhada encontrada, pendente de SQL específico",
    },
    {
        "jogo": "16/09/2001 Vasco x Bahia",
        "campos": "estádio, arbitragem completa, público pagante, escalação, reservas, substituições, gols/minutos, cartões e observações",
        "fonte": "NetVasco Brasileiro 2001, ficha 50vasbah",
        "status": "fonte detalhada encontrada, pendente de SQL específico",
    },
    {
        "jogo": "Brasileiro 2001",
        "campos": "24 fichas detalhadas linkadas pela página da competição, mais tabela completa de 27 jogos",
        "fonte": "NetVasco Brasileiro 2001",
        "status": "fonte complementar mapeada",
    },
    {
        "jogo": "Estadual/Rio-SP/Libertadores/Mercosul 2001",
        "campos": "fichas detalhadas parciais e tabelas completas por competição",
        "fonte": "NetVasco por competição",
        "status": "fonte complementar mapeada",
    },
    {
        "jogo": "Jogos de Brasileiro e Libertadores",
        "campos": "validação cruzada de placar, mando e ficha quando disponível",
        "fonte": "oGol/Zerozero/PlaymakerStats/Soccerzz/Football-Lineups e páginas de adversários",
        "status": "candidato para próximas levas de enriquecimento fino",
    },
]

EXPECTED_TOTALS = {
    "jogos": 68,
    "vitorias": 35,
    "empates": 16,
    "derrotas": 17,
    "gols_pro": 136,
    "gols_contra": 83,
}

EXPECTED_COMPETITION_TOTALS = {
    "Amistoso": (2, 1, 1, 0, 5, 3),
    "Campeonato Brasileiro Serie A": (27, 10, 9, 8, 57, 36),
    "Campeonato Carioca": (19, 13, 3, 3, 42, 18),
    "Copa Libertadores": (10, 8, 0, 2, 20, 10),
    "Copa Mercosul": (6, 2, 2, 2, 11, 11),
    "Torneio Rio-São Paulo": (4, 1, 1, 2, 1, 5),
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
    match_time: str
    coach: str
    source: str


EXPECTED_MATCHES = [
    ExpectedMatch("17/01/2001", "São Paulo-SP", "Torneio Rio-São Paulo", "fora", 0, 2, "-", "20:30", "Joel Santana", "NetVasco Rio-São Paulo 2001"),
    ExpectedMatch("21/01/2001", "Madureira-RJ", "Campeonato Carioca", "casa", 1, 2, "Pedrinho", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("24/01/2001", "Palmeiras-SP", "Torneio Rio-São Paulo", "casa", 0, 0, "-", "21:40", "Joel Santana", "NetVasco Rio-São Paulo 2001"),
    ExpectedMatch("27/01/2001", "Friburguense", "Campeonato Carioca", "fora", 2, 1, "Ely Thadeu, Zada", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("31/01/2001", "Corinthians", "Torneio Rio-São Paulo", "casa", 1, 0, "Alex Oliveira", "21:40", "Joel Santana", "NetVasco Rio-São Paulo 2001"),
    ExpectedMatch("03/02/2001", "América", "Campeonato Carioca", "fora", 1, 0, "Maricá", "16:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("07/02/2001", "Santos", "Torneio Rio-São Paulo", "fora", 0, 3, "-", "21:40", "Joel Santana", "NetVasco Rio-São Paulo 2001"),
    ExpectedMatch("11/02/2001", "Fluminense-RJ", "Campeonato Carioca", "casa", 2, 0, "Pedrinho, Euller", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("17/02/2001", "Cabofriense-RJ", "Campeonato Carioca", "casa", 3, 1, "Romário (2), Juninho Paulista", "16:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("22/02/2001", "Flamengo-RJ", "Campeonato Carioca", "fora", 0, 1, "-", "20:30", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("11/03/2001", "Cabofriense-RJ", "Campeonato Carioca", "casa", 3, 1, "Geder, Romário (2)", "16:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("14/03/2001", "América Cáli", "Copa Libertadores", "fora", 3, 0, "Juninho Paulista, Clébson, Euller", "21:40", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("17/03/2001", "Olaria-RJ", "Campeonato Carioca", "fora", 1, 0, "Romário", "18:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("21/03/2001", "Dep. Táchira", "Copa Libertadores", "fora", 1, 0, "Euller", "21:40", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("30/03/2001", "Madureira-RJ", "Campeonato Carioca", "casa", 3, 1, "Torres, Viola, Juninho Paulista", "20:30", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("02/04/2001", "V. Redonda", "Campeonato Carioca", "casa", 2, 1, "Romário, Jorginho Paulista", "20:30", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("05/04/2001", "Peñarol", "Copa Libertadores", "casa", 2, 1, "Viola (2)", "20:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("08/04/2001", "Americano-RJ", "Campeonato Carioca", "fora", 1, 1, "Juninho Paulista", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("12/04/2001", "América Cáli", "Copa Libertadores", "casa", 4, 1, "Viáfara (contra), Clébson, Romário, Jorginho Paulista", "21:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("15/04/2001", "Fluminense-RJ", "Campeonato Carioca", "fora", 3, 3, "Viola, Pedrinho, Dedé", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("18/04/2001", "Friburguense", "Campeonato Carioca", "fora", 2, 0, "Dedé, Pedrinho", "20:30", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("21/04/2001", "Dep. Táchira", "Copa Libertadores", "casa", 3, 2, "Romário (2), Dedé", "18:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("26/04/2001", "Bangu-RJ", "Campeonato Carioca", "casa", 3, 2, "Romário (2), Viola", "20:30", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("29/04/2001", "Botafogo", "Campeonato Carioca", "casa", 7, 0, "Romário (2), Juninho Paulista (3), Pedrinho, Euller", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("02/05/2001", "Peñarol", "Copa Libertadores", "fora", 3, 1, "Dedé (2), Viola", "21:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("05/05/2001", "América", "Campeonato Carioca", "fora", 5, 0, "Romário (3), Jorginho Paulista, Euller", "16:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("09/05/2001", "Dep. Concepción", "Copa Libertadores", "fora", 3, 1, "Juninho Paulista (2), Romário", "19:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("13/05/2001", "Flamengo-RJ", "Campeonato Carioca", "fora", 0, 0, "-", "17:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("16/05/2001", "Dep. Concepción", "Copa Libertadores", "casa", 1, 0, "Juninho Paulista", "21:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("20/05/2001", "Flamengo-RJ", "Campeonato Carioca", "fora", 2, 1, "Viola, Juninho Paulista", "15:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("23/05/2001", "Boca Juniors", "Copa Libertadores", "casa", 0, 1, "-", "15:00", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("27/05/2001", "Flamengo-RJ", "Campeonato Carioca", "casa", 1, 3, "Juninho Paulista", "15:00", "Joel Santana", "NetVasco Estadual 2001"),
    ExpectedMatch("30/05/2001", "Boca Juniors", "Copa Libertadores", "fora", 0, 3, "-", "21:40", "Joel Santana", "NetVasco Libertadores 2001"),
    ExpectedMatch("08/07/2001", "León", "Amistoso", "fora", 3, 1, "Pedrinho, Romário, Paulo César", "18:00", "Joel Santana", "NetVasco Amistosos 2001 + SuperVasco"),
    ExpectedMatch("10/07/2001", "Tigres", "Amistoso", "fora", 2, 2, "Romário, Gilberto", "22:45", "Joel Santana", "NetVasco Amistosos 2001"),
    ExpectedMatch("24/07/2001", "U. Católica", "Copa Mercosul", "fora", 1, 2, "Euller", "19:00", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("29/07/2001", "Boca Juniors", "Copa Mercosul", "casa", 2, 2, "Pedrinho, Patrício", "15:10", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("01/08/2001", "Gama-DF", "Campeonato Brasileiro Serie A", "fora", 0, 0, "-", "20:30", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("05/08/2001", "Guarani-SP", "Campeonato Brasileiro Serie A", "casa", 7, 1, "Romário (4), Juninho Paulista, Jorginho, Botti", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("08/08/2001", "Coritiba-PR", "Campeonato Brasileiro Serie A", "fora", 0, 1, "-", "21:45", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("11/08/2001", "Juventude-RS", "Campeonato Brasileiro Serie A", "casa", 1, 1, "Dedé", "14:30", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("15/08/2001", "Vitória-BA", "Campeonato Brasileiro Serie A", "fora", 0, 1, "-", "18:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("18/08/2001", "Santa Cruz-PE", "Campeonato Brasileiro Serie A", "casa", 1, 1, "Euller", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("21/08/2001", "C. Porteño", "Copa Mercosul", "fora", 1, 2, "Juninho Paulista", "22:10", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("26/08/2001", "Atlético-PR", "Campeonato Brasileiro Serie A", "casa", 4, 0, "Euller (2), Juninho Paulista, Fabiano Eller", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("29/08/2001", "América-MG", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Euller", "20:30", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("02/09/2001", "Botafogo-SP", "Campeonato Brasileiro Serie A", "casa", 2, 2, "Ricardo Bóvio, Bebeto", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("09/09/2001", "Sport-PE", "Campeonato Brasileiro Serie A", "fora", 3, 3, "Ricardo Bóvio, Bebeto, Euller", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("13/09/2001", "U. Católica", "Copa Mercosul", "casa", 2, 1, "Romário, Juninho Paulista", "15:00", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("16/09/2001", "Bahia-BA", "Campeonato Brasileiro Serie A", "casa", 0, 1, "-", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("19/09/2001", "Paraná-PR", "Campeonato Brasileiro Serie A", "fora", 0, 2, "-", "21:45", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("22/09/2001", "Goiás-GO", "Campeonato Brasileiro Serie A", "casa", 2, 1, "Paulo César, Juninho Paulista", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("25/09/2001", "Boca Juniors", "Copa Mercosul", "fora", 2, 2, "Odvan, Euller", "21:10", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("30/09/2001", "Ponte Preta-SP", "Campeonato Brasileiro Serie A", "fora", 2, 2, "Fabiano Eller (2)", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("03/10/2001", "Cruzeiro-MG", "Campeonato Brasileiro Serie A", "casa", 3, 0, "Romário (3)", "15:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("06/10/2001", "Flamengo-RJ", "Campeonato Brasileiro Serie A", "casa", 5, 1, "Romário (3), Gilberto, Euller", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("10/10/2001", "Inter-RS", "Campeonato Brasileiro Serie A", "fora", 0, 2, "-", "21:45", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("13/10/2001", "Botafogo-RJ", "Campeonato Brasileiro Serie A", "casa", 3, 1, "Romário, Tiago (contra), Rafael", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("17/10/2001", "C. Porteño", "Copa Mercosul", "casa", 3, 2, "Léo Lima, Paulo César, Ely Thadeu", "16:00", "Hélio dos Anjos", "NetVasco Mercosul 2001"),
    ExpectedMatch("20/10/2001", "São Caetano-SP", "Campeonato Brasileiro Serie A", "casa", 1, 2, "Juninho Paulista", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("28/10/2001", "Fluminense-RJ", "Campeonato Brasileiro Serie A", "casa", 2, 2, "Romário (2)", "17:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("04/11/2001", "Portuguesa", "Campeonato Brasileiro Serie A", "fora", 4, 5, "Romário (2), Gilberto, Tiago Silva (contra)", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("08/11/2001", "Corinthians", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Jamir", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("11/11/2001", "Atlético-MG", "Campeonato Brasileiro Serie A", "fora", 1, 2, "Ely Thadeu", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("15/11/2001", "Grêmio-RS", "Campeonato Brasileiro Serie A", "casa", 2, 0, "Romário, Léo Lima", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("18/11/2001", "Palmeiras-SP", "Campeonato Brasileiro Serie A", "fora", 3, 1, "Romário (2), Ely Thadeu", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("25/11/2001", "São Paulo-SP", "Campeonato Brasileiro Serie A", "casa", 7, 1, "Romário (3), Gilberto, Euller, Léo Lima, Dedé", "16:00", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
    ExpectedMatch("02/12/2001", "Santos", "Campeonato Brasileiro Serie A", "fora", 2, 2, "Gilberto, Dedé", "15:30", "Hélio dos Anjos", "NetVasco Brasileiro 2001"),
]

KNOWN_RICH_DETAILS = {
    ("08/07/2001", "León", "Amistoso"): {
        "estadio": "Nou Camp",
        "arbitro": "Germán Arredondo",
        "publico_presente": "25000",
        "arbitragem_status": "confirmado",
        "escalacao_status": "confirmado",
        "reservas_status": "confirmado",
        "substituicoes_status": "confirmado",
        "relacionados_status": "parcial",
        "minutos_status": "parcial",
        "cartoes_status": "confirmado",
        "fonte": "NetVasco Amistosos 2001 + SuperVasco + Blog do Garone",
    },
    ("10/07/2001", "Tigres", "Amistoso"): {
        "estadio": "Universitário",
        "arbitro": "Eduardo Brizio Carter",
        "publico_presente": "25000",
        "arbitragem_status": "parcial",
        "escalacao_status": "confirmado",
        "reservas_status": "confirmado",
        "substituicoes_status": "confirmado",
        "relacionados_status": "parcial",
        "minutos_status": "parcial",
        "cartoes_status": "confirmado",
        "fonte": "NetVasco Amistosos 2001",
    },
    ("31/01/2001", "Corinthians", "Torneio Rio-São Paulo"): {
        "estadio": "São Januário",
        "arbitro": "Edílson Pereira de Carvalho",
        "publico_presente": "500",
        "arbitragem_status": "confirmado",
        "escalacao_status": "confirmado, pendente SQL",
        "reservas_status": "parcial",
        "substituicoes_status": "confirmado",
        "relacionados_status": "parcial",
        "minutos_status": "parcial",
        "cartoes_status": "confirmado adversário; Vasco sem cartões na ficha",
        "fonte": "NetVasco Rio-São Paulo 2001 ficha 05vascor",
    },
    ("16/09/2001", "Bahia-BA", "Campeonato Brasileiro Serie A"): {
        "estadio": "São Januário",
        "arbitro": "Márcio Rezende de Freitas",
        "publico_presente": "7750",
        "arbitragem_status": "confirmado",
        "escalacao_status": "confirmado, pendente SQL",
        "reservas_status": "confirmado",
        "substituicoes_status": "confirmado",
        "relacionados_status": "parcial",
        "minutos_status": "parcial",
        "cartoes_status": "confirmado",
        "fonte": "NetVasco Brasileiro 2001 ficha 50vasbah",
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
        "torneio rio-sao paulo": "rio-sao-paulo",
        "v redonda": "volta redonda",
        "u catolica": "universidad catolica",
        "c porteno": "cerro porteno",
        "dep tachira": "deportivo tachira",
        "dep concepcion": "deportes concepcion",
        "america cali": "america de cali",
        "inter": "internacional",
        "inter rs": "internacional",
    }
    value = " ".join(value.replace(".", " ").replace("-", " ").split())
    return replacements.get(value, value)


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
            WHERE m.date_iso >= '2001-01-01' AND m.date_iso < '2002-01-01'
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
            confirmed.append({"tipo": "faltando_no_banco", "expected": expected, "actual": None, "diffs": ["jogo ausente em PRD"]})
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
        if norm(actual["coach"]) != norm(expected.coach):
            diffs.append(f"técnico banco={actual['coach']} fonte={expected.coach}")

        item = {"expected": expected, "actual": actual, "diffs": diffs}
        if diffs:
            confirmed.append(item)
        else:
            ok.append(item)

    for actual in db_matches:
        key = match_key(actual["date"], actual["opponent"], actual["competition"])
        if key not in expected_by_key:
            manual_review.append({"tipo": "sobrando_no_banco", "expected": None, "actual": actual, "diffs": ["fora do recorte NetVasco 2001; pertence à temporada 2000 se for a final contra o São Caetano"]})

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
        lines.append(f"  - Técnico esperado: {expected.coach}; técnico no banco: {actual['coach'] or '-'}")
        lines.append(f"  - Fonte: {expected.source}")
    elif expected:
        lines.append(f"- Faltando no banco: {expected.date} | {expected.competition} | {expected.opponent} | {expected.vasco_goals}x{expected.opponent_goals}")
        lines.append(f"  - Gols Vasco na fonte: {expected.vasco_scorers}")
        lines.append(f"  - Fonte: {expected.source}")
    elif actual:
        lines.append(
            f"- Sobrando no recorte 2001: `{actual['id']}` {actual['date']} | {actual['competition']} | "
            f"{actual['opponent']} | {actual['vasco_goals']}x{actual['opponent_goals']}"
        )
        if diffs:
            lines.append(f"  - Observação: {'; '.join(diffs)}")
    return lines


def render_report(db_path: Path, db_matches: list[dict]) -> str:
    confirmed, manual_review, ok = compare(db_matches)
    db_totals = totals(db_matches)
    comp_totals = competition_totals(db_matches)
    coverage = field_coverage(db_matches)

    lines = [
        "# Auditoria Dos Jogos Do Vasco - Temporada 2001",
        "",
        f"- Banco auditado: `{db_path}`",
        "- Modo de leitura: SQLite `mode=ro`",
        "- Recorte: temporada NetVasco 2001, com 68 jogos, incluindo 2 amistosos no México.",
        "- Nota de recorte: `18/01/2001 Vasco 3 x 1 São Caetano` é jogo válido pelo Brasileiro 2000 e fica como sobra no ano civil.",
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
            "| Métrica | Banco atual ano civil 2001 | Referência NetVasco 2001 | Status |",
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
        "estadio": "fichas NetVasco detalhadas cobrem parte relevante; PRD está vazio",
        "horario": "tabelas NetVasco por competição trazem horário para os 68 jogos",
        "capitao": "buscar em súmula/ficha detalhada; encontrado em algumas fichas",
        "publico_pagante": "NetVasco detalha público em fichas específicas; PRD está vazio",
        "publico_presente": "NetVasco detalha público em fichas específicas; PRD está vazio",
        "renda": "renda muitas vezes não divulgada",
        "arbitragem": "fichas NetVasco detalhadas trazem árbitros e auxiliares em parte dos jogos",
        "escalacao": "fichas NetVasco detalhadas trazem titulares e substituições em parte dos jogos",
    }
    for field, count in coverage.items():
        lines.append(f"| {field} | {count}/{len(db_matches)} | {observations[field]} |")

    lines.extend(
        [
            "",
            "## Totais Por Competição",
            "",
            "| Competição | Banco atual ano civil 2001 | Referência NetVasco 2001 | Status |",
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
            "- Horários: referência externa mapeada para os 68 jogos a partir das páginas NetVasco por competição.",
            "- Técnicos: `Joel Santana` até os amistosos de julho; `Hélio dos Anjos` a partir da Copa Mercosul/Brasileiro.",
            "- Correção de núcleo preparada: inclusão revisável dos amistosos `León 1 x 3 Vasco` e `Tigres 2 x 2 Vasco`.",
            "- Campos ricos preparados em SQL específico para os dois amistosos mexicanos.",
            "- Jogadores históricos ausentes detectados para revisar antes de aplicar escalações: `Valdo` e `William`.",
        ]
    )

    lines.extend(["", "## Confirmado Para Corrigir/Enriquecer", ""])
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

    lines.extend(["", "## Sem Divergência De Núcleo", ""])
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


def known_rich_details(expected: ExpectedMatch) -> dict[str, str]:
    return KNOWN_RICH_DETAILS.get((expected.date, expected.opponent, expected.competition), {})


def rows_for_export(db_matches: list[dict]) -> list[dict[str, str]]:
    db_by_key = {match_key(m["date"], m["opponent"], m["competition"]): m for m in db_matches}
    rows = []
    for expected in EXPECTED_MATCHES:
        actual = db_by_key.get(match_key(expected.date, expected.opponent, expected.competition), {})
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
                "tecnico_ref": expected.coach,
                "tecnico_banco": str(actual.get("coach", "")),
                "tecnico_status": "OK" if actual and norm(str(actual.get("coach", ""))) == norm(expected.coach) else "preencher" if not actual else "corrigir",
                "horario_ref": expected.match_time,
                "horario_banco": str(actual.get("match_time", "")),
                "horario_status": "OK" if actual and actual.get("match_time") == expected.match_time else "preencher",
                "estadio_ref": details.get("estadio", ""),
                "estadio_banco": str(actual.get("stadium", "")),
                "estadio_status": "confirmado" if details.get("estadio") else "pesquisar",
                "arbitro_ref": details.get("arbitro", ""),
                "arbitragem_banco": str(actual.get("arbitration_json", "")),
                "arbitragem_status": details.get("arbitragem_status", "pesquisar"),
                "titulares_status": details.get("escalacao_status", "pesquisar"),
                "reservas_status": details.get("reservas_status", "pesquisar"),
                "substituicoes_status": details.get("substituicoes_status", "pesquisar"),
                "relacionados_status": details.get("relacionados_status", "pesquisar"),
                "minutos_status": details.get("minutos_status", "pesquisar"),
                "cartoes_status": details.get("cartoes_status", "pesquisar"),
                "publico_presente_ref": details.get("publico_presente", ""),
                "publico_banco": str(actual.get("total_attendance", "")),
                "renda_banco": str(actual.get("match_revenue", "")),
                "fonte_rica": details.get("fonte", expected.source + " + fontes complementares a pesquisar"),
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
        "-- Enriquecimento revisável da temporada 2001: horários e técnicos.",
        "-- Gerado por scripts/audit_temporada_2001.py.",
        "-- Fontes: páginas NetVasco por competição e fichas detalhadas dos amistosos.",
        "-- Não aplique direto em PRD sem testar numa cópia.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for expected in EXPECTED_MATCHES:
        date_iso = iso_date(expected.date)
        lines.extend(
            [
                f"-- {expected.date} | {expected.competition} | {expected.opponent}",
                "UPDATE matches",
                f"SET match_time = {sql_quote(expected.match_time)},",
                f"    coach_id = (SELECT id FROM coaches WHERE name = {sql_quote(expected.coach)} LIMIT 1)",
                "WHERE date_iso = " + sql_quote(date_iso),
                f"  AND opponent_team_id = (SELECT id FROM teams WHERE name = {sql_quote(expected.opponent)} LIMIT 1)",
                f"  AND competition_id = (SELECT id FROM competitions WHERE name = {sql_quote(expected.competition)} LIMIT 1)",
                f"  AND EXISTS (SELECT 1 FROM coaches WHERE name = {sql_quote(expected.coach)});",
                "",
            ]
        )
    lines.extend(
        [
            "SELECT COUNT(*) AS jogos_temporada_2001_com_horario",
            "FROM matches",
            "WHERE date_iso >= '2001-01-01' AND date_iso < '2002-01-01'",
            "  AND date_iso <> '2001-01-18'",
            "  AND match_time <> '';",
            "",
            "COMMIT;",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audita os jogos do Vasco na temporada NetVasco 2001.")
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
