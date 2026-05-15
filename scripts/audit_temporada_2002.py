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
    "indice_netvasco": "https://www.netvasco.com.br/futebol/index2002.shtml",
    "estatisticas_netvasco": "https://www.netvasco.com.br/futebol/estatisticas2002/",
    "rio_sao_paulo_netvasco": "https://www.netvasco.com.br/futebol/riosaopaulo2002/",
    "estadual_netvasco": "https://www.netvasco.com.br/futebol/estadual2002/",
    "copa_do_brasil_netvasco": "https://www.netvasco.com.br/futebol/copadobrasil2002/",
    "copa_dos_campeoes_netvasco": "https://www.netvasco.com.br/futebol/copadoscampeoes2002/",
    "brasileiro_netvasco": "https://www.netvasco.com.br/futebol/brasileiro2002/",
    "evaristo_saida_dgabc": "https://www.dgabc.com.br/Noticia/132458/evaristo-de-macedo-nao-e-mais-o-tecnico-do-vasco",
}

DETAIL_SOURCE_CANDIDATES = [
    {
        "jogo": "Torneio Rio-Sao Paulo 2002",
        "campos": "tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia",
        "fonte": "NetVasco Rio-Sao Paulo 2002",
        "status": "usado para horario e validacao de nucleo",
    },
    {
        "jogo": "Campeonato Carioca 2002",
        "campos": "tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia",
        "fonte": "NetVasco Estadual 2002",
        "status": "usado para horario e validacao de nucleo",
    },
    {
        "jogo": "Copa do Brasil 2002",
        "campos": "tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia",
        "fonte": "NetVasco Copa do Brasil 2002",
        "status": "usado para horario e validacao de nucleo",
    },
    {
        "jogo": "Copa dos Campeoes 2002",
        "campos": "tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia",
        "fonte": "NetVasco Copa dos Campeoes 2002",
        "status": "usado para horario, validacao de nucleo e tecnico Evaristo nas fichas",
    },
    {
        "jogo": "Campeonato Brasileiro 2002",
        "campos": "tabela completa com data, horario, mando, placar, gols do Vasco e links de ficha/noticia",
        "fonte": "NetVasco Brasileiro 2002",
        "status": "usado para horario, validacao de nucleo e tecnico Antonio Lopes nas fichas",
    },
    {
        "jogo": "20/01/2002 Vasco x Ponte Preta",
        "campos": "estadio, arbitragem, publico, renda, escalação, substituições, gols/minutos e cartoes",
        "fonte": "NetVasco noticia 4726",
        "status": "fonte rica mapeada, pendente SQL especifico de campos detalhados",
    },
    {
        "jogo": "10/08/2002 Vasco x Figueirense",
        "campos": "estadio, arbitragem, publico, escalação, substituições, gols/minutos, cartoes e estatisticas",
        "fonte": "NetVasco noticia 7612",
        "status": "fonte rica mapeada, pendente SQL especifico de campos detalhados",
    },
    {
        "jogo": "17/11/2002 Corinthians x Vasco",
        "campos": "estadio, arbitragem, publico, renda, escalação, substituições, gols/minutos, cartoes e gol anulado citado no texto",
        "fonte": "NetVasco noticia 8993",
        "status": "fonte rica mapeada, pendente SQL especifico de campos detalhados",
    },
]

EXPECTED_TOTALS = {
    "jogos": 76,
    "vitorias": 35,
    "empates": 17,
    "derrotas": 24,
    "gols_pro": 137,
    "gols_contra": 108,
}

EXPECTED_COMPETITION_TOTALS = {
    "Torneio Rio-São Paulo": (15, 6, 6, 3, 32, 23),
    "Copa do Brasil": (8, 4, 2, 2, 14, 12),
    "Campeonato Carioca": (25, 15, 4, 6, 50, 30),
    "Copa dos Campeões": (3, 0, 2, 1, 4, 5),
    "Campeonato Brasileiro Serie A": (25, 10, 3, 12, 37, 38),
}

COACH_CORRECTION_KEYS = {
    ("02/06/2002", "Bangu-RJ", "Campeonato Carioca"),
    ("05/06/2002", "Americano-RJ", "Campeonato Carioca"),
    ("08/06/2002", "Botafogo", "Campeonato Carioca"),
    ("03/07/2002", "Atlético-MG", "Copa dos Campeões"),
    ("10/07/2002", "Palmeiras-SP", "Copa dos Campeões"),
    ("14/07/2002", "Bahia-BA", "Copa dos Campeões"),
    ("16/10/2002", "Flamengo-RJ", "Campeonato Brasileiro Serie A"),
    ("19/10/2002", "Paraná-PR", "Campeonato Brasileiro Serie A"),
    ("23/10/2002", "Bahia-BA", "Campeonato Brasileiro Serie A"),
    ("31/10/2002", "Fluminense-RJ", "Campeonato Brasileiro Serie A"),
    ("03/11/2002", "Palmeiras-SP", "Campeonato Brasileiro Serie A"),
    ("06/11/2002", "São Paulo-SP", "Campeonato Brasileiro Serie A"),
    ("09/11/2002", "Vitória-BA", "Campeonato Brasileiro Serie A"),
    ("13/11/2002", "Ponte Preta-SP", "Campeonato Brasileiro Serie A"),
    ("17/11/2002", "Corinthians", "Campeonato Brasileiro Serie A"),
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
    detail_url: str


EXPECTED_MATCHES = [
    ExpectedMatch("20/01/2002", "Ponte Preta-SP", "Torneio Rio-São Paulo", "casa", 3, 3, "Geder, Ely Thadeu, Romário", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias02/4726.shtml"),
    ExpectedMatch("26/01/2002", "Bangu-RJ", "Campeonato Carioca", "casa", 3, 0, "Ely Thadeu, André Leone, Souza", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias02/4825.shtml"),
    ExpectedMatch("27/01/2002", "São Paulo-SP", "Torneio Rio-São Paulo", "fora", 3, 2, "Romário (2), Euller", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias02/4836.shtml"),
    ExpectedMatch("30/01/2002", "América", "Torneio Rio-São Paulo", "fora", 2, 0, "Leonardo, Souza", "20:30", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias02/4888.shtml"),
    ExpectedMatch("02/02/2002", "Madureira-RJ", "Campeonato Carioca", "fora", 2, 1, "Ely Thadeu, André Ladaga", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias02/4934.shtml"),
    ExpectedMatch("03/02/2002", "Palmeiras-SP", "Torneio Rio-São Paulo", "casa", 2, 2, "Romário (2)", "17:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias02/4950.shtml"),
    ExpectedMatch("06/02/2002", "Entrerriense-RJ", "Campeonato Carioca", "fora", 3, 0, "Souza, Ely Thadeu, Alex Oliveira", "19:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias02/4993.shtml"),
    ExpectedMatch("09/02/2002", "Jundiaí", "Torneio Rio-São Paulo", "fora", 2, 2, "Léo Lima, Ely Thadeu", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5031.shtml"),
    ExpectedMatch("13/02/2002", "Sergipe", "Copa do Brasil", "fora", 1, 1, "Felipe", "21:45", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5081.shtml"),
    ExpectedMatch("17/02/2002", "Americano-RJ", "Torneio Rio-São Paulo", "casa", 3, 0, "Romário (2), André Silva", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5136.shtml"),
    ExpectedMatch("18/02/2002", "Botafogo", "Campeonato Carioca", "casa", 1, 0, "Cadu", "20:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5146.shtml"),
    ExpectedMatch("20/02/2002", "Sergipe", "Copa do Brasil", "casa", 2, 1, "Euller, Felipe", "20:30", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5184.shtml"),
    ExpectedMatch("21/02/2002", "Olaria-RJ", "Campeonato Carioca", "casa", 3, 0, "Souza (2), Cadu", "20:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5208.shtml"),
    ExpectedMatch("24/02/2002", "São Caetano-SP", "Torneio Rio-São Paulo", "fora", 0, 3, "-", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5250.shtml"),
    ExpectedMatch("25/02/2002", "América", "Campeonato Carioca", "fora", 2, 1, "Cadu, Geovani", "20:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5265.shtml"),
    ExpectedMatch("27/02/2002", "Santa Cruz-PE", "Copa do Brasil", "fora", 2, 1, "Romário, Leonardo", "21:45", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5302.shtml"),
    ExpectedMatch("28/02/2002", "Friburguense", "Campeonato Carioca", "casa", 1, 0, "Souza", "20:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5314.shtml"),
    ExpectedMatch("02/03/2002", "Portuguesa", "Torneio Rio-São Paulo", "casa", 4, 1, "Romário (2), Alex Oliveira, Euller", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5343.shtml"),
    ExpectedMatch("06/03/2002", "Santa Cruz-PE", "Copa do Brasil", "casa", 3, 3, "Euller, Léo Lima, Romário", "20:30", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5390.shtml"),
    ExpectedMatch("07/03/2002", "Fluminense-RJ", "Campeonato Carioca", "fora", 2, 2, "Haroldo, Cadu", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5401.shtml"),
    ExpectedMatch("10/03/2002", "Flamengo-RJ", "Torneio Rio-São Paulo", "casa", 3, 1, "Euller, André Leone, Souza", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5451.shtml"),
    ExpectedMatch("11/03/2002", "V. Redonda", "Campeonato Carioca", "casa", 2, 0, "Cadu, Ely Thadeu", "16:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5463.shtml"),
    ExpectedMatch("17/03/2002", "Guarani-SP", "Torneio Rio-São Paulo", "fora", 1, 1, "Felipe", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5540.shtml"),
    ExpectedMatch("21/03/2002", "Botafogo", "Torneio Rio-São Paulo", "fora", 2, 2, "Léo Lima, Romário", "20:30", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5609.shtml"),
    ExpectedMatch("24/03/2002", "Fluminense-RJ", "Torneio Rio-São Paulo", "casa", 1, 3, "João Carlos", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5656.shtml"),
    ExpectedMatch("25/03/2002", "Flamengo-RJ", "Campeonato Carioca", "fora", 1, 0, "Léo Macaé", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/5674.shtml"),
    ExpectedMatch("27/03/2002", "CSA", "Copa do Brasil", "fora", 1, 2, "Felipe", "19:00", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5705.shtml"),
    ExpectedMatch("30/03/2002", "Santos", "Torneio Rio-São Paulo", "casa", 1, 1, "Romário", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5751.shtml"),
    ExpectedMatch("03/04/2002", "CSA", "Copa do Brasil", "casa", 4, 0, "Romário (2), Euller, Léo Lima", "20:30", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5804.shtml"),
    ExpectedMatch("07/04/2002", "Bangu-RJ", "Torneio Rio-São Paulo", "casa", 5, 1, "Romário (2), Leonardo, Léo Lima, Felipe", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/5883.shtml"),
    ExpectedMatch("10/04/2002", "São Paulo-SP", "Copa do Brasil", "casa", 1, 0, "Romário", "21:45", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/5931.shtml"),
    ExpectedMatch("14/04/2002", "Corinthians", "Torneio Rio-São Paulo", "fora", 0, 1, "-", "16:00", "Evaristo de Macedo", "NetVasco Rio-São Paulo 2002", "https://www.netvasco.com.br/news/noticias03/6010.shtml"),
    ExpectedMatch("17/04/2002", "São Paulo-SP", "Copa do Brasil", "fora", 0, 4, "-", "21:45", "Evaristo de Macedo", "NetVasco Copa do Brasil 2002", "https://www.netvasco.com.br/news/noticias03/6069.shtml"),
    ExpectedMatch("21/04/2002", "Madureira-RJ", "Campeonato Carioca", "casa", 3, 1, "Romário (2), Leonardo", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/6119.shtml"),
    ExpectedMatch("24/04/2002", "Entrerriense-RJ", "Campeonato Carioca", "casa", 6, 1, "Romário (4), Edinho, Souza", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/6172.shtml"),
    ExpectedMatch("28/04/2002", "Americano-RJ", "Campeonato Carioca", "fora", 1, 2, "Romário", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/6232.shtml"),
    ExpectedMatch("01/05/2002", "Olaria-RJ", "Campeonato Carioca", "fora", 1, 1, "Alex Oliveira", "15:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias03/6291.shtml"),
    ExpectedMatch("05/05/2002", "América", "Campeonato Carioca", "casa", 2, 1, "Romário, Felipe", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6356.shtml"),
    ExpectedMatch("08/05/2002", "Friburguense", "Campeonato Carioca", "fora", 2, 3, "Léo Macaé, Leonardo", "20:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6410.shtml"),
    ExpectedMatch("11/05/2002", "Americano-RJ", "Campeonato Carioca", "casa", 2, 1, "Jailson, Leonardo", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6449.shtml"),
    ExpectedMatch("15/05/2002", "Fluminense-RJ", "Campeonato Carioca", "casa", 1, 0, "Souza", "20:30", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6499.shtml"),
    ExpectedMatch("19/05/2002", "V. Redonda", "Campeonato Carioca", "fora", 3, 4, "Jorginho, Ramon, Euller", "15:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6551.shtml"),
    ExpectedMatch("23/05/2002", "Bangu-RJ", "Campeonato Carioca", "fora", 3, 1, "Ramon (2), Euller", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6601.shtml"),
    ExpectedMatch("26/05/2002", "Flamengo-RJ", "Campeonato Carioca", "casa", 0, 0, "-", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6653.shtml"),
    ExpectedMatch("29/05/2002", "Botafogo", "Campeonato Carioca", "fora", 2, 2, "Léo Lima, Haroldo", "15:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6696.shtml"),
    ExpectedMatch("02/06/2002", "Bangu-RJ", "Campeonato Carioca", "casa", 1, 4, "Souza", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6743.shtml"),
    ExpectedMatch("05/06/2002", "Americano-RJ", "Campeonato Carioca", "casa", 3, 4, "Ramon, Souza, Cadu", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6781.shtml"),
    ExpectedMatch("08/06/2002", "Botafogo", "Campeonato Carioca", "casa", 0, 1, "-", "16:00", "Evaristo de Macedo", "NetVasco Estadual 2002", "https://www.netvasco.com.br/news/noticias04/6814.shtml"),
    ExpectedMatch("03/07/2002", "Atlético-MG", "Copa dos Campeões", "fora", 3, 3, "Ramon (2), Souza", "21:45", "Evaristo de Macedo", "NetVasco Copa dos Campeões 2002", "https://www.netvasco.com.br/news/noticias05/7033.shtml"),
    ExpectedMatch("10/07/2002", "Palmeiras-SP", "Copa dos Campeões", "fora", 1, 1, "Alexandre (contra)", "21:45", "Evaristo de Macedo", "NetVasco Copa dos Campeões 2002", "https://www.netvasco.com.br/news/noticias05/7135.shtml"),
    ExpectedMatch("14/07/2002", "Bahia-BA", "Copa dos Campeões", "fora", 0, 1, "-", "16:00", "Evaristo de Macedo", "NetVasco Copa dos Campeões 2002", "https://www.netvasco.com.br/news/noticias05/7196.shtml"),
    ExpectedMatch("10/08/2002", "Figueirense-SC", "Campeonato Brasileiro Serie A", "casa", 2, 0, "Ramon (2)", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7612.shtml"),
    ExpectedMatch("14/08/2002", "Grêmio-RS", "Campeonato Brasileiro Serie A", "fora", 2, 3, "Ramon (2)", "21:40", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7673.shtml"),
    ExpectedMatch("17/08/2002", "Atlético-PR", "Campeonato Brasileiro Serie A", "fora", 1, 2, "Siston", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7722.shtml"),
    ExpectedMatch("22/08/2002", "Gama-DF", "Campeonato Brasileiro Serie A", "casa", 0, 1, "-", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7791.shtml"),
    ExpectedMatch("25/08/2002", "Goiás-GO", "Campeonato Brasileiro Serie A", "fora", 4, 2, "Souza, Rodrigo Souto, Washington, Cadu", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7842.shtml"),
    ExpectedMatch("01/09/2002", "Juventude-RS", "Campeonato Brasileiro Serie A", "fora", 0, 1, "-", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7958.shtml"),
    ExpectedMatch("04/09/2002", "Atlético-MG", "Campeonato Brasileiro Serie A", "casa", 1, 2, "Cadu", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/7995.shtml"),
    ExpectedMatch("07/09/2002", "Coritiba-PR", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Petkovic", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/8034.shtml"),
    ExpectedMatch("11/09/2002", "Paysandu-PA", "Campeonato Brasileiro Serie A", "fora", 0, 2, "-", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/8081.shtml"),
    ExpectedMatch("15/09/2002", "Botafogo", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Cadu", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias05/8137.shtml"),
    ExpectedMatch("18/09/2002", "Santos", "Campeonato Brasileiro Serie A", "casa", 1, 2, "Souza", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8182.shtml"),
    ExpectedMatch("22/09/2002", "Internacional-RS", "Campeonato Brasileiro Serie A", "casa", 1, 1, "Ely Thadeu", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8229.shtml"),
    ExpectedMatch("25/09/2002", "Cruzeiro-MG", "Campeonato Brasileiro Serie A", "fora", 0, 4, "-", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8275.shtml"),
    ExpectedMatch("29/09/2002", "Portuguesa", "Campeonato Brasileiro Serie A", "casa", 4, 0, "Valdir (2), Geder, Léo Lima", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8325.shtml"),
    ExpectedMatch("05/10/2002", "Guarani-SP", "Campeonato Brasileiro Serie A", "fora", 2, 1, "Rodrigo Souto, Ramon", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8410.shtml"),
    ExpectedMatch("12/10/2002", "São Caetano-SP", "Campeonato Brasileiro Serie A", "fora", 0, 2, "-", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8503.shtml"),
    ExpectedMatch("16/10/2002", "Flamengo-RJ", "Campeonato Brasileiro Serie A", "casa", 2, 1, "Ramon (2)", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8567.shtml"),
    ExpectedMatch("19/10/2002", "Paraná-PR", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Ramon", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8613.shtml"),
    ExpectedMatch("23/10/2002", "Bahia-BA", "Campeonato Brasileiro Serie A", "fora", 2, 4, "Ramon (2)", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8676.shtml"),
    ExpectedMatch("31/10/2002", "Fluminense-RJ", "Campeonato Brasileiro Serie A", "fora", 1, 2, "Valdir", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8778.shtml"),
    ExpectedMatch("03/11/2002", "Palmeiras-SP", "Campeonato Brasileiro Serie A", "casa", 1, 0, "Léo Lima", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8813.shtml"),
    ExpectedMatch("06/11/2002", "São Paulo-SP", "Campeonato Brasileiro Serie A", "fora", 3, 5, "Ramon (2), Zé Carlos", "21:40", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8862.shtml"),
    ExpectedMatch("09/11/2002", "Vitória-BA", "Campeonato Brasileiro Serie A", "casa", 4, 1, "Russo, Ramon, Petkovic, Valdir", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8894.shtml"),
    ExpectedMatch("13/11/2002", "Ponte Preta-SP", "Campeonato Brasileiro Serie A", "casa", 2, 0, "Valdir, Ramon", "20:30", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8949.shtml"),
    ExpectedMatch("17/11/2002", "Corinthians", "Campeonato Brasileiro Serie A", "fora", 1, 1, "Ramon", "16:00", "Antônio Lopes", "NetVasco Brasileiro 2002", "https://www.netvasco.com.br/news/noticias06/8993.shtml"),
]


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def norm(value: str) -> str:
    value = strip_accents(value or "").casefold().strip()
    for token in ("-rj", "-sp", "-mg", "-pr", "-pe", "-pa", "-ba", "-rs", "-sc", "-df", "-go"):
        value = value.replace(token, "")
    replacements = {
        "campeonato brasileiro serie a": "brasileiro",
        "campeonato brasileiro série a": "brasileiro",
        "torneio rio sao paulo": "rio sao paulo",
        "v redonda": "volta redonda",
        "atletico pr": "athletico pr",
        "internacional": "internacional",
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
            WHERE m.date_iso >= '2002-01-01' AND m.date_iso < '2003-01-01'
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
            manual_review.append({"tipo": "sobrando_no_banco", "expected": None, "actual": actual, "diffs": ["jogo fora do recorte NetVasco 2002"]})

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
        lines.append(f"  - Fonte: {expected.source}; ficha: {expected.detail_url}")
    elif expected:
        lines.append(f"- Faltando no banco: {expected.date} | {expected.competition} | {expected.opponent} | {expected.vasco_goals}x{expected.opponent_goals}")
        lines.append(f"  - Gols Vasco na fonte: {expected.vasco_scorers}")
        lines.append(f"  - Fonte: {expected.source}; ficha: {expected.detail_url}")
    elif actual:
        lines.append(
            f"- Sobrando no recorte 2002: `{actual['id']}` {actual['date']} | {actual['competition']} | "
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
        "# Auditoria Dos Jogos Do Vasco - Temporada 2002",
        "",
        f"- Banco auditado: `{db_path}`",
        "- Modo de leitura: SQLite `mode=ro`",
        "- Recorte: temporada NetVasco 2002, com 76 jogos e sem amistosos listados nas estatísticas.",
        "- Nota de técnico: fichas de junho/julho ainda trazem `Evaristo de Macedo`; fichas do Brasileiro trazem `Antônio Lopes` até o fim da temporada.",
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
            "| Métrica | Banco atual ano civil 2002 | Referência NetVasco 2002 | Status |",
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
            "| Campo salvo | Preenchidos no banco auditado | Observação |",
            "| --- | ---: | --- |",
        ]
    )
    observations = {
        "estadio": "fichas NetVasco detalhadas trazem estádio em parte relevante; ainda não aplicado no SQL global",
        "horario": "tabelas NetVasco por competição trazem horário para os 76 jogos",
        "capitao": "aparece em várias fichas detalhadas; pendente extração e SQL específico",
        "publico_pagante": "fichas detalhadas trazem público em parte dos jogos; pendente SQL específico",
        "publico_presente": "fichas detalhadas trazem público em parte dos jogos; pendente SQL específico",
        "renda": "fichas detalhadas trazem renda em parte dos jogos; várias como não divulgada",
        "arbitragem": "fichas detalhadas trazem árbitro e auxiliares em parte dos jogos; pendente SQL específico",
        "escalacao": "fichas detalhadas trazem escalações e substituições em parte dos jogos; pendente SQL específico",
    }
    for field, count in coverage.items():
        lines.append(f"| {field} | {count}/{len(db_matches)} | {observations[field]} |")

    lines.extend(
        [
            "",
            "## Totais Por Competição",
            "",
            "| Competição | Banco atual ano civil 2002 | Referência NetVasco 2002 | Status |",
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
            "- Horários: referência externa mapeada para os 76 jogos a partir das páginas NetVasco por competição.",
            "- Técnicos: `Evaristo de Macedo` até a Copa dos Campeões; `Antônio Lopes` em todo o Brasileiro 2002.",
            "- Correção de núcleo preparada: 15 jogos com técnico divergente no banco auditado.",
            "- Campos ricos de fichas detalhadas foram mapeados no CSV, mas estádio/arbitragem/escalação/público/renda ficam para SQLs específicos por jogo/bloco.",
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


def rows_for_export(db_matches: list[dict]) -> list[dict[str, str]]:
    db_by_key = {match_key(m["date"], m["opponent"], m["competition"]): m for m in db_matches}
    rows = []
    for expected in EXPECTED_MATCHES:
        actual = db_by_key.get(match_key(expected.date, expected.opponent, expected.competition), {})
        key = (expected.date, expected.opponent, expected.competition)
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
                "tecnico_status": "OK" if actual and norm(str(actual.get("coach", ""))) == norm(expected.coach) else "corrigir",
                "horario_ref": expected.match_time,
                "horario_banco": str(actual.get("match_time", "")),
                "horario_status": "OK" if actual and actual.get("match_time") == expected.match_time else "preencher",
                "estadio_ref": "",
                "estadio_banco": str(actual.get("stadium", "")),
                "estadio_status": "pendente - fonte indicada",
                "arbitro_ref": "",
                "arbitragem_banco": str(actual.get("arbitration_json", "")),
                "arbitragem_status": "pendente - fonte indicada",
                "titulares_status": "pendente - fonte indicada",
                "reservas_status": "pendente - fonte indicada",
                "substituicoes_status": "pendente - fonte indicada",
                "relacionados_status": "pendente - fonte indicada",
                "minutos_status": "pendente - fonte indicada",
                "cartoes_status": "pendente - fonte indicada",
                "publico_presente_ref": "",
                "publico_banco": str(actual.get("total_attendance", "")),
                "renda_banco": str(actual.get("match_revenue", "")),
                "fonte_rica": expected.detail_url,
                "correcao_nucleo": "tecnico" if key in COACH_CORRECTION_KEYS else "",
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


def render_update_sql(expected: ExpectedMatch, include_time: bool) -> list[str]:
    date_iso = iso_date(expected.date)
    set_lines = [f"    coach_id = (SELECT id FROM coaches WHERE name = {sql_quote(expected.coach)} LIMIT 1)"]
    if include_time:
        set_lines.insert(0, f"    match_time = {sql_quote(expected.match_time)}")
    return [
        f"-- {expected.date} | {expected.competition} | {expected.opponent}",
        "UPDATE matches",
        "SET " + ",\n".join(set_lines),
        "WHERE date_iso = " + sql_quote(date_iso),
        f"  AND opponent_team_id = (SELECT id FROM teams WHERE name = {sql_quote(expected.opponent)} LIMIT 1)",
        f"  AND competition_id = (SELECT id FROM competitions WHERE name = {sql_quote(expected.competition)} LIMIT 1)",
        f"  AND EXISTS (SELECT 1 FROM coaches WHERE name = {sql_quote(expected.coach)});",
        "",
    ]


def render_time_coach_sql() -> str:
    lines = [
        "-- Enriquecimento revisável da temporada 2002: horários e técnicos.",
        "-- Gerado por scripts/audit_temporada_2002.py.",
        "-- Fontes: páginas NetVasco por competição e fichas detalhadas linkadas.",
        "",
        "BEGIN TRANSACTION;",
        "",
        "INSERT OR IGNORE INTO coaches(name) VALUES ('Evaristo de Macedo');",
        "INSERT OR IGNORE INTO coaches(name) VALUES ('Antônio Lopes');",
        "INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Evaristo de Macedo');",
        "INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Antônio Lopes');",
        "",
    ]
    for expected in EXPECTED_MATCHES:
        lines.extend(render_update_sql(expected, include_time=True))
    lines.extend(
        [
            "SELECT COUNT(*) AS jogos_temporada_2002_com_horario",
            "FROM matches",
            "WHERE date_iso >= '2002-01-01' AND date_iso < '2003-01-01'",
            "  AND match_time <> '';",
            "",
            "COMMIT;",
            "",
        ]
    )
    return "\n".join(lines)


def render_correction_sql() -> str:
    lines = [
        "-- Correções revisáveis de núcleo da temporada 2002.",
        "-- Corrige técnicos confirmados nas fichas NetVasco.",
        "-- Não aplique direto em PRD sem testar numa cópia.",
        "",
        "BEGIN TRANSACTION;",
        "",
        "INSERT OR IGNORE INTO coaches(name) VALUES ('Evaristo de Macedo');",
        "INSERT OR IGNORE INTO coaches(name) VALUES ('Antônio Lopes');",
        "INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Evaristo de Macedo');",
        "INSERT OR IGNORE INTO list_entries(list_type, value) VALUES ('tecnicos', 'Antônio Lopes');",
        "",
    ]
    for expected in EXPECTED_MATCHES:
        if (expected.date, expected.opponent, expected.competition) in COACH_CORRECTION_KEYS:
            lines.extend(render_update_sql(expected, include_time=False))
    lines.extend(
        [
            "SELECT m.date_text, c.name AS competicao, t.name AS adversario, ch.name AS tecnico",
            "FROM matches m",
            "JOIN teams t ON t.id = m.opponent_team_id",
            "JOIN competitions c ON c.id = m.competition_id",
            "LEFT JOIN coaches ch ON ch.id = m.coach_id",
            "WHERE m.date_iso >= '2002-06-01' AND m.date_iso < '2002-12-01'",
            "  AND (m.date_iso <= '2002-07-14' OR m.date_iso >= '2002-10-16')",
            "ORDER BY m.date_iso;",
            "",
            "COMMIT;",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audita os jogos do Vasco na temporada NetVasco 2002.")
    parser.add_argument("--db", type=Path, default=DEFAULT_PRD_DB, help="Caminho do SQLite a auditar em modo read-only.")
    parser.add_argument("--output", type=Path, help="Arquivo Markdown de saída. Se omitido, imprime no stdout.")
    parser.add_argument("--map-output", type=Path, help="Arquivo CSV com o mapa jogo a jogo dos campos auditáveis.")
    parser.add_argument("--sql-output", type=Path, help="Arquivo SQL para preencher horários e técnicos mapeados.")
    parser.add_argument("--correction-sql-output", type=Path, help="Arquivo SQL com correções de núcleo confirmadas.")
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
    if args.correction_sql_output:
        args.correction_sql_output.write_text(render_correction_sql(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
