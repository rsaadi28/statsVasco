import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import defaultdict, Counter
import copy
import json
import math
import os
import sys
import ast
import shutil
from difflib import SequenceMatcher
try:
    from tkcalendar import Calendar
    TKCALENDAR_OK = True
except Exception:
    Calendar = None
    TKCALENDAR_OK = False
import tkinter.font as tkFont
import re
import unicodedata
from datetime import datetime
from storage_sqlite import (
    backup_database_snapshot,
    bootstrap_database,
    db_path_for,
    delete_external_opponent_probability_data as db_delete_external_opponent_probability_data,
    load_external_opponent_probability_data as db_load_external_opponent_probability_data,
    load_team_stadium as db_load_team_stadium,
    load_team_stadiums as db_load_team_stadiums,
    load_current_squad as db_load_current_squad,
    load_future_matches as db_load_future_matches,
    load_historic_players as db_load_historic_players,
    load_listas as db_load_listas,
    load_matches as db_load_matches,
    load_titles as db_load_titles,
    save_current_squad as db_save_current_squad,
    save_external_opponent_probability_data as db_save_external_opponent_probability_data,
    save_future_matches as db_save_future_matches,
    save_historic_players as db_save_historic_players,
    save_listas as db_save_listas,
    save_matches as db_save_matches,
    save_titles as db_save_titles,
)
from web_sync import schedule_sync_after_change, set_status_callback, sync_config

# --- Matplotlib (gráficos) ---
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False

# Diretórios e arquivos (robusto ao diretório atual de execução)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = "StatsVasco"
ESTADIOS_BRASIL_PADRAO = [
    "São Januário",
    "Maracanã",
    "Nilton Santos",
    "Mineirão",
    "Arena MRV",
    "Morumbi",
    "Neo Química Arena",
    "Allianz Parque",
    "Vila Belmiro",
    "Arena Barueri",
    "Mané Garrincha",
    "Arena BRB",
    "Beira-Rio",
    "Arena do Grêmio",
    "Ligga Arena",
    "Arena da Baixada",
    "Couto Pereira",
    "Arena Condá",
    "Ressacada",
    "Heriberto Hülse",
    "Arena Fonte Nova",
    "Barradão",
    "Arena Castelão",
    "Presidente Vargas",
    "Ilha do Retiro",
    "Aflitos",
    "Arena de Pernambuco",
    "Castelão de São Luís",
    "Mangueirão",
    "Arena da Amazônia",
    "Albertão",
    "Serra Dourada",
    "Antônio Accioly",
    "Serrinha",
    "Onésio Brasileiro Alvarenga",
    "Kléber Andrade",
    "Brinco de Ouro",
    "Moisés Lucarelli",
    "Nabi Abi Chedid",
    "Arena Pantanal",
    "Alfredo Jaconi",
    "José Maria de Campos Maia",
]


def _diretorio_dados_por_plataforma():
    """Retorna a pasta de dados do usuário conforme o sistema operacional."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return os.path.join(base, APP_NAME)


def _definir_diretorio_dados():
    """Usa pasta de dados do usuário quando empacotado (PyInstaller)."""
    if getattr(sys, "frozen", False):
        app_support_dir = _diretorio_dados_por_plataforma()
        os.makedirs(app_support_dir, exist_ok=True)
        return app_support_dir
    return PROJECT_ROOT


DATA_DIR = _definir_diretorio_dados()
ARQUIVO_JOGOS = os.path.join(DATA_DIR, "jogos_vasco.json")
ARQUIVO_LISTAS = os.path.join(DATA_DIR, "listas_auxiliares.json")
ARQUIVO_FUTUROS = os.path.join(DATA_DIR, "jogos_futuros.json")
ARQUIVO_ELENCO_ATUAL = os.path.join(DATA_DIR, "elenco_atual.json")
ARQUIVO_JOGADORES_HISTORICO = os.path.join(DATA_DIR, "jogadores_historico.json")
DB_PATH = db_path_for(DATA_DIR)
_DATA_CACHE = {}


def _json_origem_inicial(nome_arquivo: str) -> str:
    preferido = os.path.join(DATA_DIR, nome_arquivo)
    if os.path.exists(preferido):
        return preferido
    return os.path.join(PROJECT_ROOT, nome_arquivo)


def _cache_get(key, loader):
    if key not in _DATA_CACHE:
        _DATA_CACHE[key] = loader()
    return _DATA_CACHE[key]


def _cache_set(key, value):
    _DATA_CACHE[key] = value


def _cache_clear(*keys):
    if not keys:
        _DATA_CACHE.clear()
        return
    for key in keys:
        _DATA_CACHE.pop(key, None)


def _copiar_db_inicial_se_necessario():
    if os.path.exists(DB_PATH):
        return
    origem = os.path.join(PROJECT_ROOT, "stats_vasco.sqlite3")
    if not os.path.exists(origem):
        return
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        shutil.copy2(origem, DB_PATH)
    except Exception:
        pass


_copiar_db_inicial_se_necessario()
bootstrap_database(
    DB_PATH,
    json_paths={
        "jogos": _json_origem_inicial("jogos_vasco.json"),
        "listas": _json_origem_inicial("listas_auxiliares.json"),
        "futuros": _json_origem_inicial("jogos_futuros.json"),
        "elenco": _json_origem_inicial("elenco_atual.json"),
        "historico": _json_origem_inicial("jogadores_historico.json"),
        "titulos": _json_origem_inicial("titulos_vasco.json"),
    },
)
COMPETICOES_COM_POSICAO_TABELA = {
    "Campeonato Brasileiro Serie A",
    "Campeonato Brasileiro Série A",
    "Campeonato Brasileiro Serie B",
    "Campeonato Brasileiro Série B",
}
COMPETICOES_COM_GRAFICO_POSICAO = {
    "Campeonato Brasileiro Serie A",
    "Campeonato Brasileiro Série A",
}
TITULOS_VASCO_PADRAO = [
    {"campeonato": "Campeonato Brasileiro Serie A", "ano": 2000},
    {"campeonato": "Copa Mercosul", "ano": 2000},
    {"campeonato": "Campeonato Carioca", "ano": 2003},
    {"campeonato": "Campeonato Brasileiro Serie B", "ano": 2009},
    {"campeonato": "Copa do Brasil", "ano": 2011},
    {"campeonato": "Campeonato Carioca", "ano": 2015},
    {"campeonato": "Campeonato Carioca", "ano": 2016},
    {"campeonato": "Campeonato Brasileiro Serie B", "ano": 2016},
]
POSICOES_ELENCO = [
    "Goleiro",
    "Lateral-Direito",
    "Zagueiro",
    "Lateral-Esquerdo",
    "Volante",
    "Meio-Campista",
    "Atacante",
]
CONDICOES_ELENCO = ["Titular", "Reserva", "Não Relacionado", "Lesionado", "Suspenso", "Servindo a seleção", "Emprestado"]
CATEGORIAS_ESCALACAO_EXTRAS = (
    ("reservas", "Reservas"),
    ("nao_relacionados", "Não Relacionados"),
    ("lesionados", "Lesionados"),
    ("suspensos", "Suspensos"),
    ("servindo_selecao", "Servindo a seleção"),
)
ESTATISTICAS_VASCO_ALIASES = {
    "assistencias": "assistencias",
    "chutes": "finalizacoes",
    "chutes_bloqueados": "finalizacoes_bloqueadas",
    "chutes_fora": "finalizacoes_fora",
    "chutes_no_gol": "finalizacoes_no_gol",
    "cruzamentos_certos": "cruzamentos_certos",
    "cruzamentos_errados": "cruzamentos_errados",
    "cruzamentos_tentados": "cruzamentos_tentados",
    "desarmes": "desarmes",
    "duelos_aereos_ganhos": "duelos_aereos_ganhos",
    "duelos_ganhos": "duelos_ganhos",
    "escanteios": "escanteios",
    "faltas_cometidas": "faltas_cometidas",
    "faltas_recebidas": "faltas_recebidas",
    "finalizacoes": "finalizacoes",
    "finalizacoes_bloqueadas": "finalizacoes_bloqueadas",
    "finalizacoes_fora": "finalizacoes_fora",
    "finalizacoes_no_gol": "finalizacoes_no_gol",
    "impedimentos": "impedimentos",
    "interceptacoes": "interceptacoes",
    "lancamentos_certos": "lancamentos_certos",
    "lancamentos_errados": "lancamentos_errados",
    "lancamentos_tentados": "lancamentos_tentados",
    "nota": "nota",
    "nota_sofascore": "nota_sofascore",
    "passes": "passes_tentados",
    "passes_certo": "passes_certos",
    "passes_certos": "passes_certos",
    "passes_completos": "passes_certos",
    "passes_errado": "passes_errados",
    "passes_errados": "passes_errados",
    "passes_incompletos": "passes_errados",
    "passes_precisao": "precisao_passes",
    "passes_precisao_pct": "precisao_passes",
    "passes_totais": "passes_tentados",
    "passes_total": "passes_tentados",
    "passes_tentados": "passes_tentados",
    "posse": "posse_bola",
    "posse_bola": "posse_bola",
    "posse_bola_pct": "posse_bola",
    "posse_de_bola": "posse_bola",
    "posse_de_bola_pct": "posse_bola",
    "precisao_passe": "precisao_passes",
    "precisao_de_passes": "precisao_passes",
    "precisao_de_passes_pct": "precisao_passes",
    "precisao_passes": "precisao_passes",
    "precisao_passes_pct": "precisao_passes",
    "sofridas": "faltas_recebidas",
    "xg": "xg",
}
ESTATISTICAS_PERCENTUAIS = {
    "posse_bola",
    "precisao_cruzamentos",
    "precisao_lancamentos",
    "precisao_passes",
}
ELENCO_POSICAO_PLACEHOLDER = "Selecione..."
ELENCO_CONDICAO_PLACEHOLDER = "Selecione..."

def _gerar_backup_jsons_inicio():
    """Gera backup snapshot do banco SQLite ao abrir o app."""
    backup_database_snapshot(DATA_DIR, DB_PATH)


def _limpar_nome_arbitragem_bruto(nome: str) -> str:
    nome_limpo = re.sub(r"\s+", " ", str(nome or "").strip())
    if not nome_limpo:
        return ""
    nome_limpo = re.sub(r"\s*\([A-Z]{2,4}\s*$", "", nome_limpo).strip()
    nome_limpo = re.sub(r"\s*\([^)]+?\)\s*$", "", nome_limpo).strip()
    return re.sub(r"\s+", " ", nome_limpo)


def _chave_nome_arbitragem(nome: str) -> str:
    nome_limpo = _limpar_nome_arbitragem_bruto(nome)
    nome_sem_acentos = "".join(
        ch for ch in unicodedata.normalize("NFKD", nome_limpo)
        if not unicodedata.combining(ch)
    )
    nome_sem_acentos = re.sub(r"[^\w\s]", " ", nome_sem_acentos, flags=re.UNICODE)
    return re.sub(r"\s+", " ", nome_sem_acentos).strip().casefold()


_NOMES_ARBITRAGEM_CANONICOS = {
    _chave_nome_arbitragem("Bruno Arleu de Araujo"): "Bruno Arleu de Araújo",
    _chave_nome_arbitragem("Carlos Bentancur"): "Carlos Bentancur",
    _chave_nome_arbitragem("Jhon Ospina"): "Jhon Ospina",
    _chave_nome_arbitragem("Joao Vitor Gobi"): "João Vitor Gobi",
    _chave_nome_arbitragem("Rodrigo Jose Pereira de Lima"): "Rodrigo José Pereira de Lima",
    _chave_nome_arbitragem("Rodrigo José Pereira De Lima"): "Rodrigo José Pereira de Lima",
    _chave_nome_arbitragem("Savio Pereira Sampaio"): "Sávio Pereira Sampaio",
    _chave_nome_arbitragem("Wagner do Nascimento Magalhaes"): "Wagner do Nascimento Magalhães",
    _chave_nome_arbitragem("Alessandro Alvaro Rocha de Matos"): "Alessandro Álvaro Rocha de Matos",
    _chave_nome_arbitragem("Alexander Guzman"): "Alexander Guzman",
    _chave_nome_arbitragem("Andres Nievas"): "Andrés Nievas",
    _chave_nome_arbitragem("Bruno Muller"): "Bruno Müller",
    _chave_nome_arbitragem("David Fuentes"): "David Fuentes",
    _chave_nome_arbitragem("Jhon Gallego"): "Jhon Gallego",
    _chave_nome_arbitragem("Luanderson Lima Dos Santos"): "Luanderson Lima dos Santos",
    _chave_nome_arbitragem("Maira Mastella Moreira"): "Maíra Mastella Moreira",
    _chave_nome_arbitragem("Rodrigo Figueiredo Henrique Correa"): "Rodrigo Figueiredo Henrique Corrêa",
    _chave_nome_arbitragem("Thiago Henrique Neto Correa Farinha"): "Thiago Henrique Neto Corrêa Farinha",
    _chave_nome_arbitragem("Wallace Muller Barros Santos"): "Wallace Müller Barros Santos",
    _chave_nome_arbitragem("Claudio Rocha Filho"): "José Cláudio Rocha Filho",
    _chave_nome_arbitragem("Jose Claudio Rocha Filho"): "José Cláudio Rocha Filho",
    _chave_nome_arbitragem("Leonard Mosquera"): "Leonard Mosquera",
    _chave_nome_arbitragem("Marco Aurelio Augusto Fazekas Ferreira"): "Marco Aurélio Augusto Fazekas Ferreira",
    _chave_nome_arbitragem("Pablo Ramon Goncalves Pinheiro"): "Pablo Ramon Gonçalves Pinheiro",
    _chave_nome_arbitragem("Ricardo Garcia"): "Ricardo Garcia",
    _chave_nome_arbitragem("Rodrigo Carvalhaes de Miranda"): "Rodrigo Carvalhães de Miranda",
}


def _normalizar_nome_arbitragem(nome: str) -> str:
    nome_limpo = _limpar_nome_arbitragem_bruto(nome)
    if not nome_limpo:
        return ""
    return _NOMES_ARBITRAGEM_CANONICOS.get(_chave_nome_arbitragem(nome_limpo), nome_limpo)


def _normalizar_lista_arbitragem_nomes(nomes) -> list:
    normalizados = []
    vistos = set()
    for nome in nomes or []:
        nome_limpo = _normalizar_nome_arbitragem(nome)
        if not nome_limpo:
            continue
        chave = _chave_nome_arbitragem(nome_limpo)
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(nome_limpo)
    return sorted(normalizados, key=lambda s: s.casefold())


def _ordenar_listas(dados: dict) -> dict:
    """Ordena, alfabeticamente (case-insensitive), as listas auxiliares."""
    if not isinstance(dados, dict):
        return dados
    chaves = (
        "clubes_adversarios",
        "jogadores_vasco",
        "jogadores_contra",
        "competicoes",
        "tecnicos",
        "estadios",
        "arbitros",
        "auxiliares",
        "vars",
    )
    for k in chaves:
        lista = dados.get(k)
        if isinstance(lista, list):
            if k == "estadios":
                dados[k] = sorted(
                    lista,
                    key=lambda s: (0 if str(s).casefold() == "são januário".casefold() else 1, str(s).casefold()),
                )
            elif k in {"arbitros", "auxiliares", "vars"}:
                dados[k] = _normalizar_lista_arbitragem_nomes(lista)
            else:
                dados[k] = sorted(lista, key=lambda s: s.casefold())
    return dados


def carregar_dados_jogos():
    return _cache_get("matches", lambda: db_load_matches(DB_PATH))


def carregar_jogos_futuros():
    return _cache_get("future_matches", lambda: db_load_future_matches(DB_PATH))


def carregar_listas():
    if "listas" in _DATA_CACHE:
        return _DATA_CACHE["listas"]

    dados = db_load_listas(DB_PATH)
    dados_original = copy.deepcopy(dados)
    dados = _ordenar_listas(dados)
    alterou = dados != dados_original
    if not dados.get("tecnicos"):
        dados["tecnicos"] = ["Fernando Diniz"]
        alterou = True
    if not dados.get("estadios"):
        dados["estadios"] = list(ESTADIOS_BRASIL_PADRAO)
        alterou = True
    if not dados.get("tecnico_atual"):
        dados["tecnico_atual"] = dados["tecnicos"][0]
        alterou = True
    elif dados["tecnico_atual"] not in dados["tecnicos"]:
        dados["tecnicos"].append(dados["tecnico_atual"])
        dados = _ordenar_listas(dados)
        alterou = True

    tecnicos_jogos = set()
    arbitros_jogos = set()
    auxiliares_jogos = set()
    vars_jogos = set()
    for jogo in carregar_dados_jogos():
        tecnico = str(jogo.get("tecnico", "") or "").strip()
        if tecnico:
            tecnicos_jogos.add(tecnico)
        arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
        arbitro = arbitragem.get("arbitro", "")
        if arbitro:
            arbitros_jogos.add(arbitro)
        for auxiliar in arbitragem.get("auxiliares", []):
            if auxiliar:
                auxiliares_jogos.add(auxiliar)
        var_nome = arbitragem.get("var", "")
        if var_nome:
            vars_jogos.add(var_nome)

    if tecnicos_jogos:
        base = list(dados.get("tecnicos", []))
        base_cf = {str(nome).casefold() for nome in base}
        for nome in sorted(tecnicos_jogos, key=str.casefold):
            if nome.casefold() not in base_cf:
                base.append(nome)
                base_cf.add(nome.casefold())
                alterou = True
        dados["tecnicos"] = sorted(base, key=lambda s: s.casefold())

    for chave_lista, nomes in (
        ("arbitros", arbitros_jogos),
        ("auxiliares", auxiliares_jogos),
        ("vars", vars_jogos),
    ):
        if nomes:
            base = _normalizar_lista_arbitragem_nomes(dados.get(chave_lista, []))
            base_chaves = {_chave_nome_arbitragem(nome) for nome in base}
            for nome in sorted(nomes, key=str.casefold):
                nome_limpo = _normalizar_nome_arbitragem(nome)
                chave_nome = _chave_nome_arbitragem(nome_limpo)
                if nome_limpo and chave_nome not in base_chaves:
                    base.append(nome_limpo)
                    base_chaves.add(chave_nome)
                    alterou = True
            dados[chave_lista] = _normalizar_lista_arbitragem_nomes(base)

    if alterou:
        db_save_listas(DB_PATH, dados)
    _cache_set("listas", dados)
    return dados


def salvar_listas(data):
    data = _ordenar_listas(data)
    db_save_listas(DB_PATH, data)
    _cache_set("listas", data)


def salvar_jogo(jogo):
    dados = carregar_dados_jogos()
    dados.append(jogo)
    salvar_lista_jogos(dados)


def salvar_lista_jogos(dados):
    db_save_matches(DB_PATH, dados)
    _cache_set("matches", dados if isinstance(dados, list) else [])
    schedule_sync_after_change(DB_PATH, reason="matches-updated")


def salvar_lista_futuros(dados):
    db_save_future_matches(DB_PATH, dados)
    _cache_set("future_matches", dados if isinstance(dados, list) else [])
    schedule_sync_after_change(DB_PATH, reason="future-matches-updated")


def carregar_estadio_adversario(nome_time: str) -> str:
    return db_load_team_stadium(DB_PATH, nome_time)


def carregar_estadios_adversario(nome_time: str) -> list[str]:
    return db_load_team_stadiums(DB_PATH, nome_time)


def _ordenar_titulos_vasco(titulos):
    return sorted(
        titulos,
        key=lambda t: (
            int(t.get("ano", 0)),
            str(t.get("campeonato", "")).casefold(),
        ),
    )


def _normalizar_titulo_vasco_item(item):
    if not isinstance(item, dict):
        return None
    campeonato = str(item.get("campeonato", "")).strip()
    if not campeonato:
        return None
    try:
        ano = int(item.get("ano", 0))
    except Exception:
        return None
    if ano < 1900 or ano > 2100:
        return None
    return {"campeonato": campeonato, "ano": ano}


def carregar_titulos_vasco():
    dados = _cache_get("titles", lambda: db_load_titles(DB_PATH))
    if not isinstance(dados, list):
        dados = []
    if not dados:
        dados = list(TITULOS_VASCO_PADRAO)
        db_save_titles(DB_PATH, dados)
        _cache_set("titles", dados)

    normalizados = []
    vistos = set()
    for item in dados:
        titulo = _normalizar_titulo_vasco_item(item)
        if not titulo:
            continue
        chave = (titulo["campeonato"].casefold(), titulo["ano"])
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(titulo)
    return _ordenar_titulos_vasco(normalizados)


def salvar_titulos_vasco(titulos):
    normalizados = []
    vistos = set()
    for item in titulos if isinstance(titulos, list) else []:
        titulo = _normalizar_titulo_vasco_item(item)
        if not titulo:
            continue
        chave = (titulo["campeonato"].casefold(), titulo["ano"])
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(titulo)
    normalizados = _ordenar_titulos_vasco(normalizados)
    db_save_titles(DB_PATH, normalizados)
    _cache_set("titles", normalizados)


def carregar_dados_externos_adversario_probabilidade(adversario: str):
    return db_load_external_opponent_probability_data(DB_PATH, adversario)


def salvar_dados_externos_adversario_probabilidade(adversario: str, dados: dict):
    db_save_external_opponent_probability_data(DB_PATH, adversario, dados)


def excluir_dados_externos_adversario_probabilidade(adversario: str):
    db_delete_external_opponent_probability_data(DB_PATH, adversario)


def _normalizar_posicao_elenco(posicao: str) -> str:
    posicao_txt = str(posicao or "").strip()
    if posicao_txt.casefold() == "goleiros":
        posicao_txt = "Goleiro"
    return posicao_txt if posicao_txt in POSICOES_ELENCO else "Meio-Campista"


def _normalizar_condicao_elenco(condicao: str) -> str:
    condicao_txt = str(condicao or "").strip()
    return condicao_txt if condicao_txt in CONDICOES_ELENCO else "Reserva"


def _normalizar_flag_capitao(valor) -> bool:
    if isinstance(valor, bool):
        return valor
    txt = str(valor or "").strip().casefold()
    return txt in {"1", "true", "sim", "s", "yes"}


def _nome_exibicao_capitao(nome: str, eh_capitao: bool) -> str:
    nome_limpo = str(nome or "").strip()
    if not nome_limpo:
        return ""
    return f"{nome_limpo} (C)" if eh_capitao else nome_limpo


def _nome_sem_marcador_capitao(nome: str) -> str:
    nome_limpo = str(nome or "").strip()
    if nome_limpo.endswith(" (C)"):
        return nome_limpo[:-4].rstrip()
    return nome_limpo


def _normalizar_jogador_elenco(item):
    if isinstance(item, str):
        nome = item.strip()
        if not nome:
            return None
        return {
            "nome": nome,
            "posicao": "Meio-Campista",
            "condicao": "Reserva",
            "capitao": False,
        }
    if not isinstance(item, dict):
        return None
    nome = str(item.get("nome", "")).strip()
    if not nome:
        return None
    return {
        "nome": nome,
        "posicao": _normalizar_posicao_elenco(item.get("posicao")),
        "condicao": _normalizar_condicao_elenco(item.get("condicao")),
        "capitao": _normalizar_flag_capitao(item.get("capitao")),
    }


def _ordenar_jogadores_elenco(jogadores):
    ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
    ordem_condicao = {cond: idx for idx, cond in enumerate(CONDICOES_ELENCO)}
    return sorted(
        jogadores,
        key=lambda j: (
            ordem_condicao.get(j.get("condicao", ""), len(CONDICOES_ELENCO)),
            ordem_posicao.get(j.get("posicao", ""), len(POSICOES_ELENCO))
        )
    )


def _ordenar_jogadores_por_posicao(jogadores):
    ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
    ordem_condicao = {cond: idx for idx, cond in enumerate(CONDICOES_ELENCO)}
    return sorted(
        jogadores,
        key=lambda j: (
            ordem_posicao.get(j.get("posicao", ""), len(POSICOES_ELENCO)),
            ordem_condicao.get(_normalizar_condicao_elenco(j.get("condicao")), len(CONDICOES_ELENCO))
        )
    )


def carregar_elenco_atual():
    dados = _cache_get("current_squad", lambda: db_load_current_squad(DB_PATH))
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": [], "tecnico": ""}
    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []
    tecnico = str(dados.get("tecnico", "") or "").strip()

    normalizados = []
    vistos = set()
    capitao_definido = False
    for item in jogadores:
        jogador = _normalizar_jogador_elenco(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        if jogador.get("capitao"):
            if capitao_definido:
                jogador["capitao"] = False
            else:
                capitao_definido = True
        normalizados.append(jogador)

    normalizados = _ordenar_jogadores_elenco(normalizados)
    return {"jogadores": normalizados, "tecnico": tecnico}


def salvar_elenco_atual(dados):
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": [], "tecnico": ""}
    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []
    tecnico = str(dados.get("tecnico", "") or "").strip()

    normalizados = []
    vistos = set()
    capitao_definido = False
    for item in jogadores:
        jogador = _normalizar_jogador_elenco(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        if jogador.get("capitao"):
            if capitao_definido:
                jogador["capitao"] = False
            else:
                capitao_definido = True
        normalizados.append(jogador)

    jogadores_limpos = _ordenar_jogadores_elenco(normalizados)
    dados_limpos = {"jogadores": jogadores_limpos, "tecnico": tecnico}
    db_save_current_squad(DB_PATH, dados_limpos)
    _cache_set("current_squad", dados_limpos)
    schedule_sync_after_change(DB_PATH, reason="current-squad-updated")


def _normalizar_jogador_historico(item):
    if isinstance(item, str):
        nome = item.strip()
        if not nome:
            return None
        return {
            "nome": nome,
            "posicao": "Meio-Campista",
            "data_registro": "",
            "data_entrada": "",
            "data_saida": "",
            "passagens": [],
            "jogos_pelo_vasco": None,
        }
    if not isinstance(item, dict):
        return None
    nome = str(item.get("nome", "")).strip()
    if not nome:
        return None
    data_registro = str(item.get("data_registro", "")).strip()
    if data_registro and not _parse_data_ptbr_safe(data_registro):
        data_registro = ""
    data_entrada = str(item.get("data_entrada", "")).strip()
    if data_entrada and not _parse_data_ptbr_safe(data_entrada):
        data_entrada = ""
    data_saida = str(item.get("data_saida", "")).strip()
    if data_saida and not _parse_data_ptbr_safe(data_saida):
        data_saida = ""
    passagens = []
    bruto_passagens = item.get("passagens", [])
    if isinstance(bruto_passagens, list):
        for passagem in bruto_passagens:
            if not isinstance(passagem, dict):
                continue
            entrada = str(passagem.get("data_entrada", "")).strip()
            saida = str(passagem.get("data_saida", "")).strip()
            if entrada and not _parse_data_ptbr_safe(entrada):
                entrada = ""
            if saida and not _parse_data_ptbr_safe(saida):
                saida = ""
            if not entrada and not saida:
                continue
            passagens.append({
                "data_entrada": entrada,
                "data_saida": saida,
            })
    if not passagens and (data_entrada or data_saida):
        passagens.append({
            "data_entrada": data_entrada,
            "data_saida": data_saida,
        })
    passagens = sorted(
        passagens,
        key=lambda p: _parse_data_ptbr_safe(p.get("data_entrada", "")) or datetime.max,
    )
    jogos_pelo_vasco = item.get("jogos_pelo_vasco")
    try:
        jogos_pelo_vasco = int(jogos_pelo_vasco)
        if jogos_pelo_vasco < 0:
            jogos_pelo_vasco = None
    except (TypeError, ValueError):
        jogos_pelo_vasco = None
    return {
        "nome": nome,
        "posicao": _normalizar_posicao_elenco(item.get("posicao")),
        "data_registro": data_registro,
        "data_entrada": data_entrada,
        "data_saida": data_saida,
        "passagens": passagens,
        "jogos_pelo_vasco": jogos_pelo_vasco,
    }


def _ordenar_jogadores_historico(jogadores):
    ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
    return sorted(
        jogadores,
        key=lambda j: (
            ordem_posicao.get(j.get("posicao", ""), len(POSICOES_ELENCO)),
            str(j.get("nome", "")).casefold(),
        ),
    )


def carregar_jogadores_historico():
    dados = _cache_get("historic_players", lambda: db_load_historic_players(DB_PATH))
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": []}
    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []

    normalizados = []
    vistos = set()
    for item in jogadores:
        jogador = _normalizar_jogador_historico(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(jogador)

    return {"jogadores": _ordenar_jogadores_historico(normalizados)}


def salvar_jogadores_historico(dados):
    if isinstance(dados, list):
        dados = {"jogadores": dados}
    if not isinstance(dados, dict):
        dados = {"jogadores": []}
    jogadores = dados.get("jogadores", [])
    if not isinstance(jogadores, list):
        jogadores = []

    normalizados = []
    vistos = set()
    for item in jogadores:
        jogador = _normalizar_jogador_historico(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(jogador)

    dados_limpos = {"jogadores": _ordenar_jogadores_historico(normalizados)}
    db_save_historic_players(DB_PATH, dados_limpos)
    _cache_set("historic_players", dados_limpos)
    schedule_sync_after_change(DB_PATH, reason="historic-players-updated")


def _chave_nome_jogador(nome):
    nome_limpo = re.sub(r"\s+", " ", str(nome or "").strip())
    nome_sem_acentos = "".join(
        ch for ch in unicodedata.normalize("NFKD", nome_limpo)
        if not unicodedata.combining(ch)
    )
    return nome_sem_acentos.casefold()


def _jogadores_que_participaram_do_jogo(jogo):
    esc = jogo.get("escalacao_partida", jogo.get("escalacao"))
    if not isinstance(esc, dict):
        return set()
    participantes = set()
    tit_por_pos = esc.get("titulares_por_posicao", {})
    if isinstance(tit_por_pos, dict):
        for pos in POSICOES_ELENCO:
            for nome in tit_por_pos.get(pos, []):
                chave = _chave_nome_jogador(nome)
                if chave:
                    participantes.add(chave)
    reservas_que_entraram = esc.get("reservas_que_entraram")
    if not isinstance(reservas_que_entraram, list):
        reservas_que_entraram = esc.get("reservas", [])
    for nome in reservas_que_entraram:
        chave = _chave_nome_jogador(nome)
        if chave:
            participantes.add(chave)
    return participantes


def _parse_data_ptbr(s: str) -> datetime:
    # dd/mm/aaaa
    return datetime.strptime(s, "%d/%m/%Y")


def _parse_data_ptbr_safe(s: str):
    try:
        return _parse_data_ptbr(s)
    except Exception:
        return None


def _hoje_ptbr() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def _normalizar_nome_tecnico(nome: str) -> str:
    tecnico = str(nome or "").strip()
    return tecnico or "(Sem Técnico)"


def _normalizar_arbitragem(dados):
    if not isinstance(dados, dict):
        dados = {}
    arbitro = _normalizar_nome_arbitragem(dados.get("arbitro", ""))
    var = _normalizar_nome_arbitragem(dados.get("var", ""))
    auxiliares_brutos = dados.get("auxiliares", [])
    if not isinstance(auxiliares_brutos, list):
        auxiliares_brutos = []
    auxiliares = []
    vistos = set()
    for nome in auxiliares_brutos:
        nome_limpo = _normalizar_nome_arbitragem(nome)
        if not nome_limpo:
            continue
        chave = _chave_nome_arbitragem(nome_limpo)
        if chave in vistos:
            continue
        vistos.add(chave)
        auxiliares.append(nome_limpo)
    return {
        "arbitro": arbitro,
        "auxiliares": auxiliares,
        "var": var,
    }


def _normalizar_inteiro_positivo(valor):
    txt = str(valor or "").strip()
    if not txt:
        return None
    txt = re.sub(r"[^\d]", "", txt)
    if not txt:
        return None
    try:
        numero = int(txt)
    except Exception:
        return None
    return numero if numero >= 0 else None


def _normalizar_renda_brl(valor):
    txt = str(valor or "").strip()
    if not txt:
        return None
    txt = txt.replace("R$", "").replace(" ", "")
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    else:
        txt = txt.replace(",", "")
    try:
        numero = float(txt)
    except Exception:
        return None
    return numero if numero >= 0 else None


def _formatar_publico(valor):
    if valor in (None, ""):
        return "—"
    try:
        return f"{int(valor):,}".replace(",", ".")
    except Exception:
        return "—"


def _formatar_renda_brl(valor):
    if valor in (None, ""):
        return "—"
    try:
        numero = float(valor)
    except Exception:
        return "—"
    inteiro, decimal = f"{numero:.2f}".split(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    return f"R$ {inteiro},{decimal}"


def _criar_stats_tecnico():
    return {
        "jogos": 0,
        "casa": 0,
        "fora": 0,
        "vitorias": 0,
        "empates": 0,
        "derrotas": 0,
        "gols_pro": 0,
        "gols_contra": 0,
        "artilheiros": Counter(),
    }


def _acumular_stats_tecnico(info: dict, jogo: dict):
    info["jogos"] += 1
    local = jogo.get("local", "casa")
    if local == "fora":
        info["fora"] += 1
    else:
        info["casa"] += 1

    placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    info["gols_pro"] += gols_vasco
    info["gols_contra"] += gols_adv

    for g in jogo.get("gols_vasco", []):
        if isinstance(g, dict):
            nome = str(g.get("nome", "Desconhecido")).strip() or "Desconhecido"
            info["artilheiros"][nome] += int(g.get("gols", 0) or 0)
        elif isinstance(g, str):
            nome = g.strip()
            if nome:
                info["artilheiros"][nome] += 1

    if gols_vasco > gols_adv:
        info["vitorias"] += 1
    elif gols_vasco < gols_adv:
        info["derrotas"] += 1
    else:
        info["empates"] += 1


def _texto_artilheiro_counter(artilheiros: Counter) -> str:
    top = artilheiros.most_common(1)
    if not top:
        return "—"
    nome, gols = top[0]
    return f"{nome} ({gols})"


def _calcular_aproveitamento_stats(info: dict) -> float:
    jogos = int(info.get("jogos", 0) or 0)
    if jogos <= 0:
        return 0.0
    pontos = int(info.get("vitorias", 0) or 0) * 3 + int(info.get("empates", 0) or 0)
    return round((pontos / (jogos * 3)) * 100, 1)


def _criar_stats_arbitro():
    return {
        "jogos": 0,
        "vitorias": 0,
        "empates": 0,
        "derrotas": 0,
        "gols_pro": 0,
        "gols_contra": 0,
        "primeiro_jogo_data": None,
        "primeiro_jogo_txt": "—",
        "ultimo_jogo_data": None,
        "ultimo_jogo_txt": "—",
    }


def _resumo_partida_arbitro(jogo: dict) -> str:
    placar = jogo.get("placar", {}) if isinstance(jogo.get("placar"), dict) else {}
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    adversario = str(jogo.get("adversario", "") or "").strip() or "Adversário não informado"
    data = str(jogo.get("data", "") or "").strip()
    return f"{data} - Vasco {gols_vasco} x {gols_adv} {adversario}" if data else f"Vasco {gols_vasco} x {gols_adv} {adversario}"


def _acumular_stats_arbitro(info: dict, jogo: dict):
    info["jogos"] += 1
    placar = jogo.get("placar", {}) if isinstance(jogo.get("placar"), dict) else {}
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    info["gols_pro"] += gols_vasco
    info["gols_contra"] += gols_adv

    if gols_vasco > gols_adv:
        info["vitorias"] += 1
    elif gols_vasco < gols_adv:
        info["derrotas"] += 1
    else:
        info["empates"] += 1

    data_jogo = _parse_data_ptbr_safe(str(jogo.get("data", "")).strip())
    if data_jogo is None:
        return

    resumo = _resumo_partida_arbitro(jogo)
    primeiro = info.get("primeiro_jogo_data")
    if primeiro is None or data_jogo < primeiro:
        info["primeiro_jogo_data"] = data_jogo
        info["primeiro_jogo_txt"] = resumo

    ultimo = info.get("ultimo_jogo_data")
    if ultimo is None or data_jogo > ultimo:
        info["ultimo_jogo_data"] = data_jogo
        info["ultimo_jogo_txt"] = resumo


def _ordenar_jogos_por_data(jogos):
    return sorted(
        jogos,
        key=lambda j: (
            _parse_data_ptbr_safe(str(j.get("data", "")).strip()) or datetime.min,
            str(j.get("adversario", "")).casefold(),
        ),
    )


def _normalizar_minuto_partida(valor):
    txt = "" if valor is None else str(valor).strip().replace("'", "")
    if not txt:
        return None
    try:
        minuto = int(txt)
    except Exception:
        return None
    return minuto if 0 <= minuto <= 120 else None


PERIODOS_EVENTO = (
    ("1T", "1º tempo"),
    ("2T", "2º tempo"),
    ("1P", "1º tempo da prorrogação"),
    ("2P", "2º tempo da prorrogação"),
)
PERIODOS_SUBSTITUICAO = (
    ("1T", "1º tempo"),
    ("INT", "Intervalo"),
    ("2T", "2º tempo"),
    ("1P", "1º tempo da prorrogação"),
    ("INTP", "Intervalo da prorrogação"),
    ("2P", "2º tempo da prorrogação"),
)
PERIODOS_INTERVALO_SUBSTITUICAO = {"INT", "INTP"}


def _normalizar_periodo_partida(periodo: str, *, substituicao=False) -> str:
    periodo_txt = str(periodo or "").strip()
    if not periodo_txt:
        return ""
    direto = {codigo: codigo for codigo, _label in (PERIODOS_SUBSTITUICAO if substituicao else PERIODOS_EVENTO)}
    if periodo_txt in direto:
        return periodo_txt
    chave = unicodedata.normalize("NFKD", periodo_txt)
    chave = "".join(ch for ch in chave if not unicodedata.combining(ch))
    chave = re.sub(r"[^a-zA-Z0-9]+", "", chave).casefold()
    aliases = {
        "1t": "1T",
        "1tempo": "1T",
        "1otempo": "1T",
        "primeirotempo": "1T",
        "2t": "2T",
        "2tempo": "2T",
        "2otempo": "2T",
        "segundotempo": "2T",
        "1p": "1P",
        "1prorrogacao": "1P",
        "1tempodaprorrogacao": "1P",
        "1otempodaprorrogacao": "1P",
        "primeirotempodaprorrogacao": "1P",
        "2p": "2P",
        "2prorrogacao": "2P",
        "2tempodaprorrogacao": "2P",
        "2otempodaprorrogacao": "2P",
        "segundotempodaprorrogacao": "2P",
    }
    if substituicao:
        aliases.update({
            "int": "INT",
            "intervalo": "INT",
            "intervalodojogo": "INT",
            "intervalonormal": "INT",
            "ht": "INT",
            "intp": "INTP",
            "intervaloprorrogacao": "INTP",
            "intervalodaprorrogacao": "INTP",
            "intervalodaprorr": "INTP",
            "intervaloentreprorrogacoes": "INTP",
        })
    return aliases.get(chave, "")


def _limite_minuto_por_periodo(periodo: str) -> int:
    periodo_norm = _normalizar_periodo_partida(periodo, substituicao=True)
    if periodo_norm in PERIODOS_INTERVALO_SUBSTITUICAO:
        return 0
    return 15 if periodo_norm in {"1P", "2P"} else 45


def _limite_minuto_evento_por_periodo(periodo: str) -> int:
    periodo_norm = _normalizar_periodo_partida(periodo, substituicao=False)
    limites = {
        "1T": 60,
        "2T": 60,
        "1P": 30,
        "2P": 30,
    }
    return limites.get(periodo_norm, 0)


def _minuto_absoluto_substituicao(minuto: int | None, periodo: str) -> int | None:
    if minuto is None:
        return None
    periodo_norm = _normalizar_periodo_partida(periodo, substituicao=True)
    offsets = {
        "1T": 0,
        "INT": 45,
        "2T": 45,
        "1P": 90,
        "INTP": 105,
        "2P": 105,
    }
    if periodo_norm not in offsets:
        return None
    limite = _limite_minuto_por_periodo(periodo_norm)
    if minuto < 0 or minuto > limite:
        return None
    return offsets[periodo_norm] + minuto


def _formatar_minuto_periodo(minuto: int | None, periodo: str) -> str:
    minuto_ok = _normalizar_minuto_partida(minuto)
    if minuto_ok is None:
        return "—"
    periodo_norm = _normalizar_periodo_partida(periodo, substituicao=True) or str(periodo or "").strip()
    if periodo_norm in PERIODOS_INTERVALO_SUBSTITUICAO:
        labels = {codigo: label for codigo, label in PERIODOS_SUBSTITUICAO}
        return labels.get(periodo_norm, periodo_norm)
    return f"{minuto_ok}' {periodo_norm}" if periodo_norm else f"{minuto_ok}'"


def _minuto_absoluto_evento(minuto: int | None, periodo: str) -> int | None:
    minuto_ok = _normalizar_minuto_partida(minuto)
    periodo_norm = _normalizar_periodo_partida(periodo, substituicao=False)
    if periodo_norm:
        offsets = {
            "1T": 0,
            "2T": 45,
            "1P": 90,
            "2P": 105,
        }
        limite = _limite_minuto_evento_por_periodo(periodo_norm)
        if minuto_ok is None or minuto_ok > limite:
            return None
        return offsets.get(periodo_norm, 0) + minuto_ok
    return minuto_ok


def _chave_ordenacao_tempo_evento(minuto: int | None, periodo: str) -> int:
    minuto_abs = _minuto_absoluto_evento(minuto, periodo)
    if minuto_abs is not None:
        return minuto_abs
    minuto_ok = _normalizar_minuto_partida(minuto)
    return minuto_ok if minuto_ok is not None else 999


def _normalizar_substituicao_partida(item):
    if not isinstance(item, dict):
        return None
    jogador_entrou = str(item.get("jogador_entrou", "")).strip()
    jogador_saiu = str(item.get("jogador_saiu", "")).strip()
    periodo = _normalizar_periodo_partida(item.get("periodo"), substituicao=True)
    minuto = _normalizar_minuto_partida(item.get("minuto"))
    if periodo in PERIODOS_INTERVALO_SUBSTITUICAO and minuto is None:
        minuto = 0
    minuto_absoluto = _minuto_absoluto_substituicao(minuto, periodo)
    if not jogador_entrou or not jogador_saiu or minuto_absoluto is None:
        return None
    return {
        "jogador_entrou": jogador_entrou,
        "jogador_saiu": jogador_saiu,
        "minuto": minuto,
        "periodo": periodo,
        "minuto_absoluto": minuto_absoluto,
    }


def _duracao_partida_jogo(jogo, esc=None):
    esc = esc if isinstance(esc, dict) else jogo.get("escalacao_partida", jogo.get("escalacao"))
    if isinstance(esc, dict):
        for sub in esc.get("substituicoes", []):
            sub_norm = _normalizar_substituicao_partida(sub)
            if sub_norm and sub_norm["minuto_absoluto"] > 90:
                return 120
    for chave in ("gols_vasco", "gols_adversario"):
        for item in jogo.get(chave, []) if isinstance(jogo.get(chave, []), list) else []:
            if not isinstance(item, dict):
                continue
            minutos = _normalizar_lista_minutos(item.get("minutos", []))
            if any(minuto > 90 for minuto in minutos):
                return 120
    return 90


def _normalizar_lista_minutos(minutos):
    if not isinstance(minutos, list):
        return []
    out = []
    for minuto in minutos:
        minuto_ok = _normalizar_minuto_partida(minuto)
        if minuto_ok is not None:
            out.append(minuto_ok)
    return out


def _expandir_eventos_gol(dados):
    eventos = []
    if not isinstance(dados, list):
        return eventos
    for item in dados:
        if isinstance(item, dict):
            nome = str(item.get("nome", "")).strip()
            clube = str(item.get("clube", "")).strip()
            saiu_do_banco = bool(item.get("saiu_do_banco", False))
            try:
                qtd = int(item.get("gols", 1))
            except Exception:
                qtd = 1
            qtd = max(1, qtd)
            minutos = _normalizar_lista_minutos(item.get("minutos", []))
            periodos = [str(periodo).strip() for periodo in item.get("periodos", []) if str(periodo).strip()]
            if not minutos:
                minuto_unico = _normalizar_minuto_partida(item.get("minuto"))
                if minuto_unico is not None:
                    minutos = [minuto_unico]
            if not periodos:
                periodo_unico = str(item.get("periodo", "")).strip()
                if periodo_unico:
                    periodos = [periodo_unico]
            assistencias_raw = item.get("assistencias")
            if isinstance(assistencias_raw, list):
                assistencias = [str(nome or "").strip() for nome in assistencias_raw]
                while assistencias and not assistencias[-1]:
                    assistencias.pop()
            else:
                assistencia_unica = str(item.get("assistencia", "") or "").strip()
                assistencias = [assistencia_unica] if assistencia_unica else []
            for idx in range(qtd):
                eventos.append({
                    "nome": nome,
                    "clube": clube,
                    "minuto": minutos[idx] if idx < len(minutos) else None,
                    "periodo": periodos[idx] if idx < len(periodos) else "",
                    "assistencia": assistencias[idx] if idx < len(assistencias) else "",
                    "saiu_do_banco": saiu_do_banco,
                })
        else:
            nome = str(item or "").strip()
            if nome:
                eventos.append({"nome": nome, "clube": "", "minuto": None, "periodo": "", "assistencia": "", "saiu_do_banco": False})
    return [evento for evento in eventos if str(evento.get("nome", "")).strip()]


def _agrupar_eventos_gol(eventos):
    agrupado = {}
    ordem = []
    for evento in eventos if isinstance(eventos, list) else []:
        nome = str(evento.get("nome", "")).strip()
        if not nome:
            continue
        clube = str(evento.get("clube", "")).strip()
        saiu_do_banco = bool(evento.get("saiu_do_banco", False))
        chave = (nome.casefold(), clube.casefold(), saiu_do_banco)
        if chave not in agrupado:
            agrupado[chave] = {
                "nome": nome,
                "gols": 0,
                "minutos": [],
                "periodos": [],
                "assistencias": [],
                "saiu_do_banco": saiu_do_banco,
            }
            if clube:
                agrupado[chave]["clube"] = clube
            ordem.append(chave)
        agrupado[chave]["gols"] += 1
        minuto = _normalizar_minuto_partida(evento.get("minuto"))
        periodo = str(evento.get("periodo", "")).strip()
        assistencia = str(evento.get("assistencia", "") or "").strip()
        if minuto is not None:
            agrupado[chave]["minutos"].append(minuto)
            agrupado[chave]["periodos"].append(periodo)
        agrupado[chave]["assistencias"].append(assistencia)

    saida = []
    for chave in ordem:
        item = agrupado[chave]
        assistencias = list(item.get("assistencias", []))
        momentos = sorted(
            zip(item["minutos"], item["periodos"], assistencias),
            key=lambda par: (
                _chave_ordenacao_tempo_evento(par[0], par[1]),
                par[0],
                par[1],
            ),
        )
        if momentos:
            item["minutos"] = [minuto for minuto, _periodo, _assistencia in momentos]
            item["periodos"] = [periodo for _minuto, periodo, _assistencia in momentos]
            item["assistencias"] = [assistencia for _minuto, _periodo, assistencia in momentos]
        if not item["minutos"]:
            item.pop("minutos", None)
            item.pop("periodos", None)
        assistencias = [str(assistencia or "").strip() for assistencia in item.get("assistencias", [])]
        while assistencias and not assistencias[-1]:
            assistencias.pop()
        item["assistencias"] = assistencias
        if any(item["assistencias"]):
            if len(item["assistencias"]) == 1 and item["assistencias"][0]:
                item["assistencia"] = item["assistencias"][0]
            else:
                item.pop("assistencia", None)
        else:
            item.pop("assistencias", None)
        saida.append(item)
    return saida


def _expandir_eventos_cartao(dados):
    eventos = []
    if not isinstance(dados, list):
        return eventos
    for item in dados:
        if isinstance(item, dict):
            nome = str(item.get("nome", "")).strip()
            try:
                qtd = int(item.get("cartoes", item.get("qtd", 1)))
            except Exception:
                qtd = 1
            for _ in range(max(1, qtd)):
                if nome:
                    eventos.append({"nome": nome})
        else:
            nome = str(item or "").strip()
            if nome:
                eventos.append({"nome": nome})
    return eventos


def _agrupar_eventos_cartao(eventos):
    contagem = Counter()
    nomes = {}
    for evento in eventos if isinstance(eventos, list) else []:
        nome = str(evento.get("nome", "")).strip()
        if not nome:
            continue
        chave = nome.casefold()
        contagem[chave] += 1
        nomes.setdefault(chave, nome)
    return [
        {"nome": nomes[chave], "cartoes": qtd}
        for chave, qtd in contagem.items()
    ]


def _formatar_evento_gol(evento):
    nome = str(evento.get("nome", "")).strip() or "Jogador"
    minuto = _normalizar_minuto_partida(evento.get("minuto"))
    periodo = str(evento.get("periodo", "")).strip()
    prefixo = "🪑 " if bool(evento.get("saiu_do_banco", False)) else ""
    assistencia = str(evento.get("assistencia", "") or "").strip()
    sufixo = f" · ass. {assistencia}" if assistencia else ""
    if minuto is not None:
        return f"{prefixo}{nome} - {_formatar_minuto_periodo(minuto, periodo)}{sufixo}"
    return f"{prefixo}{nome}{sufixo}"


def _formatar_evento_cartao(evento):
    return str(evento.get("nome", "")).strip() or "Jogador"


JOGADORES_HIST_RANKING_OPCOES = [
    "Nenhum",
    "Passagens pelo Vasco",
    "Jogos com participação",
    "Minutos jogados",
    "Jogos como titular",
    "Jogos como reserva",
    "Foi para o jogo e não entrou",
    "Jogos como não relacionado",
    "Jogos como lesionado",
    "Jogos como suspenso",
    "Jogos servindo a seleção",
    "Gols pelo Vasco",
    "Assistências",
    "Participações em gol",
    "Jogos como capitão",
    "Partidas em que marcou",
    "Partidas com assistência",
    "Gols como titular",
    "Gols saindo do banco",
    "Média de minutos jogados",
    "Média de gols por jogo",
    "Cartões amarelos",
    "Cartões vermelhos",
    "Média de minutos entre gols",
]


def _resumo_partida_tecnico(jogo: dict) -> str:
    adversario = str(jogo.get("adversario", "Adversário não informado")).strip() or "Adversário não informado"
    placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    competicao = str(jogo.get("competicao", "")).strip()
    resumo = f"Vasco {gols_vasco} x {gols_adv} {adversario}"
    if competicao:
        resumo = f"{resumo} | {competicao}"
    return resumo


def _resultado_jogo_tecnico(jogo: dict) -> str:
    placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    if gols_vasco > gols_adv:
        return "Vitória"
    if gols_vasco < gols_adv:
        return "Derrota"
    return "Empate"


def _placar_jogo_tecnico(jogo: dict) -> str:
    placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
    gols_vasco = int(placar.get("vasco", 0) or 0)
    gols_adv = int(placar.get("adversario", 0) or 0)
    return f"Vasco {gols_vasco} x {gols_adv} {str(jogo.get('adversario', '')).strip() or 'Adversário não informado'}"


def _gerar_passagens_tecnico(jogos, tecnico_nome: str):
    jogos_ordenados = _ordenar_jogos_por_data(jogos)
    tecnico_alvo = _normalizar_nome_tecnico(tecnico_nome)
    passagens = []
    passagem_atual = None

    for jogo in jogos_ordenados:
        tecnico_jogo = _normalizar_nome_tecnico(jogo.get("tecnico"))
        if tecnico_jogo != tecnico_alvo:
            passagem_atual = None
            continue

        if passagem_atual is None:
            passagem_atual = {
                "tecnico": tecnico_alvo,
                "jogos_lista": [],
                "stats": _criar_stats_tecnico(),
            }
            passagens.append(passagem_atual)

        passagem_atual["jogos_lista"].append(jogo)
        _acumular_stats_tecnico(passagem_atual["stats"], jogo)

    rows = []
    for idx, passagem in enumerate(passagens, start=1):
        jogos_passagem = passagem["jogos_lista"]
        inicio = jogos_passagem[0]
        fim = jogos_passagem[-1]
        info = passagem["stats"]
        rows.append({
            "passagem": idx,
            "periodo": f"{str(inicio.get('data', '—')).strip() or '—'} a {str(fim.get('data', '—')).strip() or '—'}",
            "inicio_data": str(inicio.get("data", "—")).strip() or "—",
            "primeiro_jogo": _resumo_partida_tecnico(inicio),
            "fim_data": str(fim.get("data", "—")).strip() or "—",
            "ultimo_jogo": _resumo_partida_tecnico(fim),
            "jogos_lista": jogos_passagem,
            "jogos": info["jogos"],
            "casa": info["casa"],
            "fora": info["fora"],
            "vitorias": info["vitorias"],
            "empates": info["empates"],
            "derrotas": info["derrotas"],
            "gols_pro": info["gols_pro"],
            "gols_contra": info["gols_contra"],
            "saldo": info["gols_pro"] - info["gols_contra"],
            "aproveitamento": _calcular_aproveitamento_stats(info),
            "artilheiro": _texto_artilheiro_counter(info["artilheiros"]),
        })
    return rows


def _extrair_adversario_de_jogo(jogo_txt: str) -> str:
    if not jogo_txt:
        return ""
    jogo_clean = re.sub(r"\s*×\s*", " x ", jogo_txt)
    partes = re.split(r"\s+(?:x|vs\.?)\s+", jogo_clean, maxsplit=1, flags=re.IGNORECASE)
    if len(partes) == 2:
        p1, p2 = partes[0].strip(), partes[1].strip()
        if "vasco" in p1.casefold():
            return p2
        if "vasco" in p2.casefold():
            return p1
        return p2
    return jogo_txt.strip()


def _normalizar_em_casa(valor):
    if isinstance(valor, bool):
        return valor
    if valor is None:
        return None
    txt = str(valor).strip().lower()
    if txt in ("sim", "s", "casa", "em casa", "emcasa", "true", "1", "yes", "y"):
        return True
    if txt in ("nao", "não", "n", "fora", "false", "0", "no"):
        return False
    return None


def _normalizar_futuro_item(item):
    if not isinstance(item, dict):
        return None
    jogo = (item.get("jogo") or "").strip()
    data = (item.get("data") or "").strip()
    em_casa = _normalizar_em_casa(
        item.get("emCasa", item.get("em_casa", item.get("emcasa")))
    )
    campeonato = (item.get("campeonato") or item.get("competicao") or "").strip()
    hora = (item.get("hora") or item.get("horario") or item.get("match_time") or "").strip()
    local = (item.get("local") or item.get("estadio") or item.get("stadium") or "").strip()
    adversario = (item.get("adversario") or "").strip()
    if not adversario and jogo:
        extraido = _extrair_adversario_de_jogo(jogo)
        adversario = re.sub(r"\bvasco\b", "", extraido, flags=re.IGNORECASE).strip()

    if em_casa is True and adversario:
        jogo = f"Vasco x {adversario}"
    elif em_casa is False and adversario:
        jogo = f"{adversario} x Vasco"

    if not jogo:
        if adversario:
            jogo = f"Vasco x {adversario}" if em_casa is not False else f"{adversario} x Vasco"
    if not jogo or not data:
        return None
    return {
        "jogo": jogo,
        "data": data,
        "em_casa": em_casa,
        "hora": hora,
        "local": local,
        "campeonato": campeonato,
    }


def _escalacao_partida_vazia(escalacao):
    if not isinstance(escalacao, dict):
        return True
    titulares_por_posicao = escalacao.get("titulares_por_posicao")
    if isinstance(titulares_por_posicao, dict):
        for nomes in titulares_por_posicao.values():
            if isinstance(nomes, list) and any(str(nome).strip() for nome in nomes):
                return False
    for chave, _label in CATEGORIAS_ESCALACAO_EXTRAS:
        nomes = escalacao.get(chave)
        if isinstance(nomes, list) and any(str(nome).strip() for nome in nomes):
            return False
    return True


def _nomes_reservas_que_entraram_escalacao(escalacao):
    if not isinstance(escalacao, dict):
        return []
    reservas = [
        str(nome).strip()
        for nome in escalacao.get("reservas", [])
        if str(nome).strip()
    ]
    reservas_cf = {nome.casefold() for nome in reservas}
    substituicoes = escalacao.get("substituicoes")
    if isinstance(substituicoes, list) and substituicoes:
        vistos = set()
        filtrados = []
        for item in substituicoes:
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            chave = sub["jogador_entrou"].casefold()
            if chave in vistos or chave not in reservas_cf:
                continue
            vistos.add(chave)
            filtrados.append(sub["jogador_entrou"])
        return filtrados
    if "reservas_que_entraram" not in escalacao:
        return list(reservas)
    bruto = escalacao.get("reservas_que_entraram")
    if not isinstance(bruto, list):
        return []
    filtrados = []
    vistos = set()
    for nome in bruto:
        nome_limpo = str(nome).strip()
        chave = nome_limpo.casefold()
        if not nome_limpo or chave in vistos or chave not in reservas_cf:
            continue
        vistos.add(chave)
        filtrados.append(nome_limpo)
    return filtrados


def _chave_nome_consulta(nome: str) -> str:
    txt = ''.join(c for c in unicodedata.normalize('NFD', str(nome or '').strip()) if unicodedata.category(c) != 'Mn')
    txt = re.sub(r'\s+', ' ', txt)
    return txt.casefold()


# --------------------- Tooltip simples ---------------------
class Tooltip:
    def __init__(self, master, delay=400):
        self.master = master
        self.tip = None
        self.delay = delay
        self._after_id = None

    def schedule(self, func):
        self.cancel()
        self._after_id = self.master.after(self.delay, func)

    def cancel(self):
        if self._after_id:
            self.master.after_cancel(self._after_id)
            self._after_id = None
        self.hide()

    def show(self, text, x_root, y_root):
        self.hide()
        if not text:
            return
        tw = tk.Toplevel(self.master)
        tw.wm_overrideredirect(True)
        try:
            tw.attributes("-topmost", True)
        except tk.TclError:
            pass
        tw.wm_geometry(f"+{x_root + 18}+{y_root + 16}")
        ttk.Label(tw, text=text, justify="left",
                  relief="solid", borderwidth=1, padding=(8, 6)).pack()
        self.tip = tw

    def hide(self):
        if self.tip is not None:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


# ===================== APP =====================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Estatísticas do Vasco")
        self.root.minsize(1000, 700)
        self._ajustar_geometria_inicial()
        
        # Fontes maiores
        default_font = tkFont.nametofont("TkDefaultFont")
        text_font = tkFont.nametofont("TkTextFont")
        fixed_font = tkFont.nametofont("TkFixedFont")
        for f in (default_font, text_font, fixed_font):
            f.configure(size=11)

        # Estilo TTK
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Card.TLabelframe", padding=8)
        style.configure("CardValue.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        # Paleta clara inspirada no macOS (mais suave ao olhar)
        self.colors = {
            "bg": "#f2f3f5",           # fundo principal
            "bg2": "#e1e3e8",          # fundo secundário
            "fg": "#1f1f1f",           # texto
            "accent": "#0a84ff",       # destaque azul macOS
            "row_alt_bg": "#e8edf8",   # zebra discreta
            "tree_bg": "#ffffff",
            "tree_fg": "#1c1c1e",
            "tree_head_bg": "#edf0f7",
            "tree_head_fg": "#2f2f30",
            "entry_bg": "#ffffff",
            "entry_fg": "#111111",
            "select_bg": "#0a84ff",
            "select_fg": "#ffffff",
        }

        self.editing_index = None
        self._elenco_edicao_partida_cf = None
        # Aplicar às principais classes ttk/tk
        self.root.configure(bg=self.colors["bg"])  # fundo da janela
        # garante cursor de digitação visível nas entradas
        self.root.option_add("*insertWidth", 2)
        self.root.option_add("*Entry.insertBackground", self.colors["accent"])
        self.root.option_add("*TEntry.insertBackground", self.colors["accent"])
        self.root.option_add("*TCombobox*insertBackground", self.colors["accent"])
        self.root.option_add("*Text.insertBackground", self.colors["accent"])
        style.configure(".", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TFrame", background=self.colors["bg"]) 
        style.configure("TLabelframe", background=self.colors["bg"]) 
        style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"]) 
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"]) 
        style.configure("TNotebook", background=self.colors["bg"]) 
        style.configure("TNotebook.Tab", background=self.colors["bg"], foreground=self.colors["fg"]) 
        style.map("TNotebook.Tab", background=[("selected", self.colors["bg2"])])
        style.configure("TButton", background=self.colors["bg2"], foreground=self.colors["fg"]) 
        style.map("TButton", background=[("active", self.colors["tree_head_bg"])])
        style.configure("TEntry", fieldbackground=self.colors["entry_bg"], foreground=self.colors["entry_fg"]) 
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], foreground=self.colors["entry_fg"], background=self.colors["entry_bg"]) 
        style.configure("Treeview", background=self.colors["tree_bg"], fieldbackground=self.colors["tree_bg"], foreground=self.colors["tree_fg"], bordercolor=self.colors["bg"], lightcolor=self.colors["bg"], darkcolor=self.colors["bg"]) 
        style.configure("Treeview.Heading", background=self.colors["tree_head_bg"], foreground=self.colors["tree_head_fg"]) 

        try:
            style.configure("TEntry", insertcolor=self.colors["accent"])
            style.configure("TCombobox", insertcolor=self.colors["accent"])
        except tk.TclError:
            pass

        self.listas = carregar_listas()
        self.titulos_vasco = carregar_titulos_vasco()
        self.elenco_atual = carregar_elenco_atual()
        self.jogadores_historico = carregar_jogadores_historico()
        jogadores_elenco = [j.get("nome", "") for j in self.elenco_atual.get("jogadores", []) if j.get("nome")]
        jogadores_vasco = list(self.listas.get("jogadores_vasco", []))
        if jogadores_elenco:
            self.listas["jogadores_vasco"] = jogadores_elenco
            salvar_listas(self.listas)
        elif jogadores_vasco:
            self.elenco_atual = {
                "tecnico": self.listas.get("tecnico_atual", "Fernando Diniz"),
                "jogadores": [
                    {"nome": nome, "posicao": "Meio-Campista", "condicao": "Reserva"}
                    for nome in jogadores_vasco
                ]
            }
            salvar_elenco_atual(self.elenco_atual)
        self._evolucao_subtab_index = 0
        self._evolucao_geral_art_page = 0
        self._evolucao_geral_art_page_size = 20
        self._calendar_popup = None
        self._elenco_info_por_nome_cf = {}
        self._tabs_sujas: set[str] = set()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.web_sync_status_var = tk.StringVar(
            value="Web: sincronização automática ativa"
            if sync_config(DB_PATH)["enabled"]
            else "Web: sincronização automática desativada"
        )
        self.web_sync_status_label = ttk.Label(
            root,
            textvariable=self.web_sync_status_var,
            anchor="w",
            padding=(8, 4),
        )
        self.web_sync_status_label.pack(fill="x", side="bottom")
        set_status_callback(self._receber_status_sync_web)

        self.frame_futuros = ttk.Frame(self.notebook, padding=10)
        self.frame_retro = ttk.Frame(self.notebook, padding=10)
        self.frame_elenco_atual = ttk.Frame(self.notebook, padding=10)
        self.frame_registro = ttk.Frame(self.notebook, padding=10)
        self.frame_temporadas = ttk.Frame(self.notebook, padding=10)
        self.frame_geral = ttk.Frame(self.notebook, padding=10)
        self.frame_estadios = ttk.Frame(self.notebook, padding=10)
        self.frame_comparativo = ttk.Frame(self.notebook, padding=10)
        self.frame_tecnicos = ttk.Frame(self.notebook, padding=10)
        self.frame_arbitros = ttk.Frame(self.notebook, padding=10)
        self.frame_titulos = ttk.Frame(self.notebook, padding=10)
        self.frame_graficos = ttk.Frame(self.notebook, padding=10)
        self.frame_jogadores_historico = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.frame_futuros, text="Jogos Futuros")
        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_retro, text="Retrospecto")
        self.notebook.add(self.frame_geral, text="Geral")
        self.notebook.add(self.frame_temporadas, text="Temporadas")
        self.notebook.add(self.frame_comparativo, text="Comparativo")
        self.notebook.add(self.frame_graficos, text="Evolução")
        self.notebook.add(self.frame_elenco_atual, text="Elenco Atual")
        self.notebook.add(self.frame_tecnicos, text="Técnicos")
        self.notebook.add(self.frame_arbitros, text="Árbitros")
        self.notebook.add(self.frame_jogadores_historico, text="Jogadores")
        self.notebook.add(self.frame_estadios, text="Estádios")
        self.notebook.add(self.frame_titulos, text="Títulos")

        self._criar_aba_futuros(self.frame_futuros)
        self._criar_aba_elenco_atual(self.frame_elenco_atual)
        self._criar_aba_jogadores_historico(self.frame_jogadores_historico)
        self._criar_formulario(self.frame_registro)
        self._sincronizar_jogadores_historico()
        self._criar_aba_retro(self.frame_retro)
        # Abas estatísticas carregadas sob demanda (lazy) na primeira visita
        self._tabs_sujas = {
            "frame_temporadas",
            "frame_geral",
            "frame_estadios",
            "frame_comparativo",
            "frame_graficos",
            "frame_tecnicos",
            "frame_arbitros",
            "frame_titulos",
        }
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed, add="+")
        self.notebook.select(self.frame_registro)

    def _receber_status_sync_web(self, payload):
        def apply():
            state = str(payload.get("state") or "")
            result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
            if state == "queued":
                self.web_sync_status_var.set("Web: sincronização agendada...")
            elif state == "syncing":
                self.web_sync_status_var.set("Web: sincronizando com Railway...")
            elif state == "success":
                matches = result.get("matches", "—")
                futuros = result.get("future_matches", "—")
                agora = datetime.now().strftime("%H:%M:%S")
                self.web_sync_status_var.set(f"Web: sincronizado às {agora} ({matches} jogos, {futuros} futuros)")
            elif state == "error":
                erro = result.get("error") or result.get("status") or "erro desconhecido"
                self.web_sync_status_var.set(f"Web: falha ao sincronizar ({erro})")
            elif state == "disabled":
                self.web_sync_status_var.set("Web: sincronização automática desativada")

        try:
            self.root.after(0, apply)
        except Exception:
            pass

    # --------------------- Jogos Futuros ---------------------
    def _criar_aba_futuros(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        frame.rowconfigure(6, weight=1)

        header = ttk.Label(frame, text="Importar jogos futuros (JSON):")
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        json_wrap = ttk.Frame(frame)
        json_wrap.grid(row=1, column=0, sticky="nsew", pady=(0, 10), padx=(0, 6))
        json_wrap.columnconfigure(0, weight=1)

        self.futuros_json_text = tk.Text(
            json_wrap, height=10, wrap="none",
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            insertbackground=self.colors["accent"]
        )
        self.futuros_json_text.grid(row=0, column=0, sticky="ew")
        self.futuros_json_text.bind("<Button-3>", self._abrir_menu_contexto_json_futuros)
        self.futuros_json_text.bind("<Control-Button-1>", self._abrir_menu_contexto_json_futuros)

        btns = ttk.Frame(json_wrap)
        btns.grid(row=0, column=1, sticky="ns", padx=(8, 0))
        ttk.Button(btns, text="Importar JSON", command=self._importar_jogos_futuros).pack(fill="x", pady=(0, 6))
        ttk.Button(btns, text="Limpar", command=self._limpar_campos_futuros).pack(fill="x", pady=(0, 6))
        ttk.Button(btns, text="Copiar Exemplo JSON", command=self._copiar_exemplo_json_futuros).pack(fill="x")

        manual_frame = ttk.Labelframe(frame, text="Adicionar jogo manualmente", padding=8)
        manual_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 10), padx=(6, 0))
        manual_frame.columnconfigure(1, weight=1)
        manual_frame.columnconfigure(3, weight=1)

        self.fut_manual_adversario_var = tk.StringVar()
        self.fut_manual_data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.fut_manual_mando_var = tk.StringVar(value="casa")
        self.fut_manual_campeonato_var = tk.StringVar()
        self.fut_manual_hora_h_var = tk.StringVar()
        self.fut_manual_hora_m_var = tk.StringVar()
        self.fut_manual_local_var = tk.StringVar()

        ttk.Label(manual_frame, text="Adversário:").grid(row=0, column=0, sticky="w", pady=3)
        _jogos_futuros_manual = carregar_dados_jogos()
        adversarios_disputados = sorted({
            str(j.get("adversario", "")).strip()
            for j in _jogos_futuros_manual
            if str(j.get("adversario", "")).strip()
        }, key=lambda s: s.casefold())
        opcoes_adversario = sorted(set(self.listas.get("clubes_adversarios", []) + adversarios_disputados), key=lambda s: s.casefold())
        self.fut_manual_adversario_entry = ttk.Combobox(
            manual_frame,
            textvariable=self.fut_manual_adversario_var,
            values=opcoes_adversario
        )
        self.fut_manual_adversario_entry.grid(
            row=0, column=1, columnspan=3, sticky="ew", pady=3, padx=(6, 0)
        )
        self._forcar_cursor_visivel(self.fut_manual_adversario_entry)

        ttk.Label(manual_frame, text="Campeonato:").grid(row=1, column=0, sticky="w", pady=3)
        competicoes_disputadas = sorted({
            str(j.get("competicao", "")).strip()
            for j in _jogos_futuros_manual
            if str(j.get("competicao", "")).strip()
        }, key=lambda s: s.casefold())
        opcoes_campeonato = sorted(set(self.listas.get("competicoes", []) + competicoes_disputadas), key=lambda s: s.casefold())
        self.fut_manual_campeonato_entry = ttk.Combobox(
            manual_frame,
            textvariable=self.fut_manual_campeonato_var,
            values=opcoes_campeonato
        )
        self.fut_manual_campeonato_entry.grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=3, padx=(6, 0)
        )
        self._forcar_cursor_visivel(self.fut_manual_campeonato_entry)

        ttk.Label(manual_frame, text="Data (dd/mm/aaaa):").grid(row=2, column=0, sticky="w", pady=3)
        data_fut_wrap = ttk.Frame(manual_frame)
        data_fut_wrap.grid(row=2, column=1, sticky="w", pady=3, padx=(6, 0))
        ttk.Entry(data_fut_wrap, width=14, textvariable=self.fut_manual_data_var).pack(side="left")
        ttk.Button(data_fut_wrap, text="Calendário", command=lambda: self._abrir_calendario_popup(self.fut_manual_data_var)).pack(
            side="left", padx=(8, 0)
        )
        mando_wrap = ttk.Frame(manual_frame)
        mando_wrap.grid(row=2, column=2, columnspan=2, sticky="w", pady=3, padx=(10, 0))
        ttk.Label(mando_wrap, text="Mando:").pack(side="left")
        ttk.Radiobutton(mando_wrap, text="Casa", variable=self.fut_manual_mando_var, value="casa").pack(side="left", padx=(8, 6))
        ttk.Radiobutton(mando_wrap, text="Fora", variable=self.fut_manual_mando_var, value="fora").pack(side="left")

        def _valores_estadio_futuro_manual(adversario: str) -> list[str]:
            base = list(self.listas.get("estadios", []))
            relacionados = carregar_estadios_adversario(adversario or "")
            return self._ordenar_opcoes_estadios(base, relacionados)

        def _formatar_horario_futuro_manual(var: tk.StringVar, proximo_widget=None):
            atual_txt = var.get()
            formatado = re.sub(r"\D", "", atual_txt)[:2]
            if atual_txt != formatado:
                var.set(formatado)
                return
            if len(formatado) == 2 and proximo_widget is not None:
                proximo_widget.focus_set()

        def _aplicar_estadio_futuro_manual(*_args):
            adversario = self._resolver_nome_clube_canonico(self.fut_manual_adversario_var.get().strip())
            if hasattr(self, "fut_manual_local_entry"):
                self.fut_manual_local_entry.configure(values=_valores_estadio_futuro_manual(adversario))
            sugerido = self._sugerir_estadio_por_adversario(adversario, self.fut_manual_mando_var.get())
            self.fut_manual_local_var.set(sugerido or "")

        ttk.Label(manual_frame, text="Hora:").grid(row=3, column=0, sticky="w", pady=3)
        hora_wrap = ttk.Frame(manual_frame)
        hora_wrap.grid(row=3, column=1, sticky="w", pady=3, padx=(6, 10))
        fut_hora_h_entry = ttk.Entry(hora_wrap, width=3, textvariable=self.fut_manual_hora_h_var, justify="center")
        fut_hora_h_entry.pack(side="left")
        ttk.Label(hora_wrap, text=":").pack(side="left", padx=2)
        fut_hora_m_entry = ttk.Entry(hora_wrap, width=3, textvariable=self.fut_manual_hora_m_var, justify="center")
        fut_hora_m_entry.pack(side="left")
        self.fut_manual_hora_h_var.trace_add("write", lambda *_: _formatar_horario_futuro_manual(self.fut_manual_hora_h_var, fut_hora_m_entry))
        self.fut_manual_hora_m_var.trace_add("write", lambda *_: _formatar_horario_futuro_manual(self.fut_manual_hora_m_var))
        ttk.Label(manual_frame, text="Local:").grid(row=3, column=2, sticky="w", pady=3)
        self.fut_manual_local_entry = ttk.Combobox(
            manual_frame,
            textvariable=self.fut_manual_local_var,
            values=_valores_estadio_futuro_manual(self.fut_manual_adversario_var.get().strip()),
        )
        self.fut_manual_local_entry.grid(
            row=3, column=3, sticky="ew", pady=3, padx=(6, 0)
        )
        self.fut_manual_adversario_var.trace_add("write", _aplicar_estadio_futuro_manual)
        self.fut_manual_mando_var.trace_add("write", _aplicar_estadio_futuro_manual)
        _aplicar_estadio_futuro_manual()

        ttk.Button(manual_frame, text="Adicionar Jogo", command=self._adicionar_jogo_futuro_manual).grid(
            row=4, column=0, columnspan=4, sticky="e", pady=(6, 0)
        )

        filtros_futuros = ttk.Frame(frame)
        filtros_futuros.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        filtros_futuros.columnconfigure(3, weight=1)
        ttk.Label(filtros_futuros, text="Jogos futuros cadastrados:").grid(row=0, column=0, sticky="w")
        ttk.Label(filtros_futuros, text="Competição:").grid(row=0, column=1, sticky="e", padx=(12, 0))
        self.filtro_futuros_competicao_var = tk.StringVar(value="Todas")
        self.filtro_futuros_competicao_combo = ttk.Combobox(
            filtros_futuros,
            textvariable=self.filtro_futuros_competicao_var,
            values=["Todas"],
            state="readonly",
            width=26,
        )
        self.filtro_futuros_competicao_combo.grid(row=0, column=2, sticky="w", padx=(6, 6))
        ttk.Button(
            filtros_futuros,
            text="Limpar",
            command=lambda: self.filtro_futuros_competicao_var.set("Todas"),
        ).grid(row=0, column=4, sticky="e")
        self.filtro_futuros_competicao_var.trace_add("write", lambda *_: self._render_lista_futuros())

        list_wrap = ttk.Frame(frame)
        list_wrap.grid(row=4, column=0, columnspan=2, sticky="nsew")
        list_wrap.rowconfigure(0, weight=1)
        list_wrap.columnconfigure(0, weight=1)

        cols = ("data", "hora", "jogo", "mando", "local", "campeonato")
        self.tv_futuros = ttk.Treeview(list_wrap, columns=cols, show="headings", height=10)
        self.tv_futuros.heading("data", text="Data")
        self.tv_futuros.heading("hora", text="Hora")
        self.tv_futuros.heading("jogo", text="Jogo")
        self.tv_futuros.heading("mando", text="Em casa?")
        self.tv_futuros.heading("local", text="Local")
        self.tv_futuros.heading("campeonato", text="Campeonato")
        self.tv_futuros.column("data", width=100, anchor="center")
        self.tv_futuros.column("hora", width=80, anchor="center")
        self.tv_futuros.column("jogo", width=320, anchor="w")
        self.tv_futuros.column("mando", width=90, anchor="center")
        self.tv_futuros.column("local", width=220, anchor="w")
        self.tv_futuros.column("campeonato", width=220, anchor="w")
        self.tv_futuros.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_futuros.tag_configure("past", foreground="#7a7a7a")
        self.tv_futuros.grid(row=0, column=0, sticky="nsew")

        sy = ttk.Scrollbar(list_wrap, orient="vertical", command=self.tv_futuros.yview)
        sy.grid(row=0, column=1, sticky="ns")
        self.tv_futuros.configure(yscrollcommand=sy.set)
        self.tv_futuros.bind("<<TreeviewSelect>>", self._atualizar_retro_futuro_selecionado)
        self.tv_futuros.bind("<Double-1>", self._importar_futuro_para_registro)
        self.tv_futuros.bind("<Button-3>", self._abrir_menu_contexto_futuros)
        self.tv_futuros.bind("<Control-Button-1>", self._abrir_menu_contexto_futuros)

        retro_frame = ttk.Labelframe(frame, text="Retrospecto do adversário selecionado", padding=8)
        retro_frame.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
        retro_frame.columnconfigure(0, weight=1)
        retro_frame.rowconfigure(1, weight=1)

        self.retro_resumo_var = tk.StringVar(value="Selecione um jogo para ver o retrospecto contra o adversário.")
        ttk.Label(retro_frame, textvariable=self.retro_resumo_var).grid(row=0, column=0, sticky="w", pady=(0, 8))

        retro_table_wrap = ttk.Frame(retro_frame)
        retro_table_wrap.grid(row=1, column=0, sticky="nsew")
        retro_table_wrap.columnconfigure(0, weight=1)
        retro_table_wrap.rowconfigure(0, weight=1)

        retro_cols = ("data", "competicao", "local", "placar", "resultado", "gols_vasco", "gols_adversario")
        self.tv_retro_futuros = ttk.Treeview(retro_table_wrap, columns=retro_cols, show="headings", height=8)
        self.tv_retro_futuros.heading("data", text="Data", command=lambda c="data": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("competicao", text="Competição", command=lambda c="competicao": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("local", text="Local", command=lambda c="local": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("placar", text="Placar", command=lambda c="placar": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("resultado", text="Resultado", command=lambda c="resultado": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("gols_vasco", text="Gols do Vasco", command=lambda c="gols_vasco": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.heading("gols_adversario", text="Gols do Adversário", command=lambda c="gols_adversario": self._ordenar_coluna_retro(c))
        self.tv_retro_futuros.column("data", width=90, anchor="center")
        self.tv_retro_futuros.column("competicao", width=170, anchor="w")
        self.tv_retro_futuros.column("local", width=70, anchor="center")
        self.tv_retro_futuros.column("placar", width=90, anchor="center")
        self.tv_retro_futuros.column("resultado", width=110, anchor="w")
        self.tv_retro_futuros.column("gols_vasco", width=280, anchor="w")
        self.tv_retro_futuros.column("gols_adversario", width=280, anchor="w")
        self.tv_retro_futuros.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_retro_futuros.grid(row=0, column=0, sticky="nsew")

        sy_retro = ttk.Scrollbar(retro_table_wrap, orient="vertical", command=self.tv_retro_futuros.yview)
        sy_retro.grid(row=0, column=1, sticky="ns")
        self.tv_retro_futuros.configure(yscrollcommand=sy_retro.set)
        self._retro_partidas_atual = []
        self._retro_sort_col = "data"
        self._retro_sort_reverse = True

        self._render_lista_futuros()
        self._atualizar_retro_futuro_selecionado()

    def _importar_jogos_futuros(self):
        raw = self.futuros_json_text.get("1.0", "end").strip()
        if not raw:
            messagebox.showerror("Erro", "Cole o JSON dos jogos futuros antes de importar.")
            return
        try:
            data = json.loads(raw)
        except Exception:
            try:
                data = ast.literal_eval(raw)
            except Exception:
                messagebox.showerror(
                    "Erro",
                    "JSON inválido. Use aspas duplas para as chaves e valores."
                )
                return
        if not isinstance(data, list):
            messagebox.showerror("Erro", "O JSON deve ser uma lista de jogos.")
            return

        validos = []
        invalidos = 0
        for item in data:
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                invalidos += 1
                continue
            data_obj = _parse_data_ptbr_safe(normalizado["data"])
            if not data_obj:
                invalidos += 1
                continue
            validos.append(normalizado)

        if not validos:
            messagebox.showerror("Erro", "Nenhum jogo válido encontrado no JSON.")
            return

        existentes = carregar_jogos_futuros()
        base = list(existentes)

        def chave_futuro(item):
            return (
                str(item.get("data", "")).strip(),
                str(item.get("hora", "")).strip(),
                str(item.get("jogo", "")).strip(),
                item.get("em_casa"),
                str(item.get("local", "")).strip(),
                str(item.get("campeonato", "")).strip(),
            )

        chaves_existentes = set()
        for item in existentes:
            normalizado = _normalizar_futuro_item(item)
            if normalizado:
                chaves_existentes.add(chave_futuro(normalizado))

        adicionados = 0
        duplicados = 0
        for item in validos:
            chave = chave_futuro(item)
            if chave in chaves_existentes:
                duplicados += 1
                continue
            base.append(item)
            chaves_existentes.add(chave)
            adicionados += 1

        salvar_lista_futuros(base)
        self._render_lista_futuros()
        message = f"Novos adicionados: {adicionados}"
        if duplicados:
            message += f" | Já existiam: {duplicados}"
        if invalidos:
            message += f" | Inválidos: {invalidos}"
        message += f" | Total cadastrado: {len(base)}"
        messagebox.showinfo("Importação concluída", message)

    def _criar_aba_retro(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        topo = ttk.Frame(frame)
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        topo.columnconfigure(1, weight=1)

        ttk.Label(topo, text="Adversário:").grid(row=0, column=0, sticky="w")
        self.retro_adversario_var = tk.StringVar()
        self.retro_adversario_combo = ttk.Combobox(
            topo,
            textvariable=self.retro_adversario_var,
            state="readonly",
            values=[],
        )
        self.retro_adversario_combo.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.retro_adversario_combo.bind("<<ComboboxSelected>>", self._atualizar_retro_aba_adversario)

        ttk.Button(topo, text="Atualizar", command=self._atualizar_retro_aba_adversario).grid(row=0, column=2, sticky="e")

        content = ttk.Frame(frame)
        content.grid(row=1, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        table_wrap = ttk.Frame(content)
        table_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        retro_cols = ("data", "competicao", "local", "placar", "resultado", "gols_vasco", "gols_adversario")
        self.tv_retro_aba = ttk.Treeview(table_wrap, columns=retro_cols, show="headings", height=16)
        self.tv_retro_aba.heading("data", text="Data", command=lambda c="data": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("competicao", text="Competição", command=lambda c="competicao": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("local", text="Local", command=lambda c="local": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("placar", text="Placar", command=lambda c="placar": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("resultado", text="Resultado", command=lambda c="resultado": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("gols_vasco", text="Gols do Vasco", command=lambda c="gols_vasco": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.heading("gols_adversario", text="Gols do Adversário", command=lambda c="gols_adversario": self._ordenar_coluna_retro_aba(c))
        self.tv_retro_aba.column("data", width=90, anchor="center")
        self.tv_retro_aba.column("competicao", width=170, anchor="w")
        self.tv_retro_aba.column("local", width=70, anchor="center")
        self.tv_retro_aba.column("placar", width=90, anchor="center")
        self.tv_retro_aba.column("resultado", width=110, anchor="w")
        self.tv_retro_aba.column("gols_vasco", width=280, anchor="w")
        self.tv_retro_aba.column("gols_adversario", width=280, anchor="w")
        self.tv_retro_aba.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_retro_aba.grid(row=0, column=0, sticky="nsew")

        sy = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tv_retro_aba.yview)
        sy.grid(row=0, column=1, sticky="ns")
        self.tv_retro_aba.configure(yscrollcommand=sy.set)

        info_wrap = ttk.Labelframe(content, text="Informações do retrospecto", padding=10)
        info_wrap.grid(row=0, column=1, sticky="nsew")
        info_wrap.columnconfigure(0, weight=1)
        info_wrap.rowconfigure(13, weight=1)

        self.retro_aba_art_vasco_var = tk.StringVar(value="—")
        self.retro_aba_art_adv_var = tk.StringVar(value="—")
        self.retro_aba_total_var = tk.StringVar(value="0")
        self.retro_aba_aproveitamento_var = tk.StringVar(value="0%")
        self.retro_aba_vitorias_var = tk.StringVar(value="0")
        self.retro_aba_empates_var = tk.StringVar(value="0")
        self.retro_aba_derrotas_var = tk.StringVar(value="0")
        self.retro_aba_saldo_var = tk.StringVar(value="0")
        self.retro_aba_gols_somados_var = tk.StringVar(value="Vasco 0 x 0 Adversário")
        self.retro_aba_elastico_vasco_var = tk.StringVar(value="—")
        self.retro_aba_elastico_adv_var = tk.StringVar(value="—")
        self.retro_aba_jejum_adv_var = tk.StringVar(value="—")
        self.retro_aba_jejum_vasco_var = tk.StringVar(value="—")
        self.retro_aba_art_adv_titulo_var = tk.StringVar(value="Artilheiros do adversário")
        self.retro_aba_elastico_adv_titulo_var = tk.StringVar(value="Para o adversário")
        self.retro_aba_jejum_adv_titulo_var = tk.StringVar(value="Adversário sem vencer")
        self.retro_aba_jejum_vasco_titulo_var = tk.StringVar(value="Vasco sem vencer")

        cards_wrap = tk.Frame(info_wrap, bg=self.colors["bg"], highlightthickness=0)
        cards_wrap.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for col in range(3):
            cards_wrap.grid_columnconfigure(col, weight=1, uniform="retrocards")

        def _card(parent, row, col, titulo, var, bg, fg="#111111"):
            card = tk.Frame(
                parent,
                bg=bg,
                bd=1,
                relief="solid",
                padx=8,
                pady=6,
                highlightthickness=0,
            )
            card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            tk.Label(card, text=titulo, bg=bg, fg=fg, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(card, textvariable=var, bg=bg, fg=fg, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(2, 0))
            return card

        def _card_texto(parent, row, col, titulo=None, var=None, bg="#ffffff", fg="#111111", titulo_var=None, valor_font=None, valor_wraplength=180):
            card = tk.Frame(parent, bg=bg, bd=1, relief="solid", padx=8, pady=6, highlightthickness=0)
            card.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            titulo_kwargs = dict(bg=bg, fg=fg, font=("Segoe UI", 9, "bold"), wraplength=180, justify="center")
            if titulo_var is not None:
                tk.Label(card, textvariable=titulo_var, **titulo_kwargs).pack(fill="x")
            else:
                tk.Label(card, text=titulo or "", **titulo_kwargs).pack(fill="x")
            tk.Label(
                card,
                textvariable=var,
                bg=bg,
                fg=fg,
                font=valor_font or ("Segoe UI", 10),
                wraplength=valor_wraplength,
                justify="center"
            ).pack(fill="x", pady=(4, 0))
            return card

        _card(cards_wrap, 0, 0, "Jogos", self.retro_aba_total_var, "#eef2f7").grid_configure(columnspan=2, sticky="ew")
        _card(cards_wrap, 0, 2, "Aproveitamento", self.retro_aba_aproveitamento_var, "#eef7ff", "#0f4d73")
        _card(cards_wrap, 1, 0, "Vitórias", self.retro_aba_vitorias_var, "#d9f4dd", "#14532d")
        _card(cards_wrap, 1, 1, "Empates", self.retro_aba_empates_var, "#fff3bf", "#7a5a00")
        _card(cards_wrap, 1, 2, "Derrotas", self.retro_aba_derrotas_var, "#ffd9d6", "#8a1c16")

        ttk.Label(info_wrap, text="Gols somados:", font=("TkDefaultFont", 10, "bold")).grid(row=1, column=0, sticky="w")
        gols_card_wrap = tk.Frame(info_wrap, bg=self.colors["bg"], highlightthickness=0)
        gols_card_wrap.grid(row=2, column=0, sticky="ew", pady=(2, 10))
        gols_card_wrap.grid_columnconfigure(0, weight=1)
        gols_card = _card_texto(
            gols_card_wrap,
            0,
            0,
            titulo="Gols somados",
            var=self.retro_aba_gols_somados_var,
            bg="#eef7ff",
            fg="#0f4d73",
            valor_font=("Segoe UI", 14, "bold"),
            valor_wraplength=420,
        )
        gols_card.grid_configure(padx=0, pady=0)
        for child in gols_card.winfo_children():
            try:
                child.pack_configure(anchor="center")
            except Exception:
                pass

        ttk.Label(info_wrap, text="Placares mais elásticos:", font=("TkDefaultFont", 10, "bold")).grid(row=4, column=0, sticky="w")
        placares_wrap = tk.Frame(info_wrap, bg=self.colors["bg"], highlightthickness=0)
        placares_wrap.grid(row=5, column=0, sticky="ew", pady=(2, 10))
        placares_wrap.grid_columnconfigure(0, weight=1, uniform="retroelastic")
        placares_wrap.grid_columnconfigure(1, weight=1, uniform="retroelastic")
        _card_texto(placares_wrap, 0, 0, titulo="Para o Vasco", var=self.retro_aba_elastico_vasco_var, bg="#e8f0ff", fg="#163c7a")
        _card_texto(placares_wrap, 0, 1, var=self.retro_aba_elastico_adv_var, bg="#fbe9e7", fg="#8a1c16", titulo_var=self.retro_aba_elastico_adv_titulo_var)

        ttk.Label(info_wrap, text="Maiores Jejuns:", font=("TkDefaultFont", 10, "bold")).grid(row=6, column=0, sticky="w")
        jejuns_wrap = tk.Frame(info_wrap, bg=self.colors["bg"], highlightthickness=0)
        jejuns_wrap.grid(row=7, column=0, sticky="ew", pady=(2, 10))
        jejuns_wrap.grid_columnconfigure(0, weight=1, uniform="retrojejuns")
        jejuns_wrap.grid_columnconfigure(1, weight=1, uniform="retrojejuns")
        _card_texto(jejuns_wrap, 0, 0, var=self.retro_aba_jejum_adv_var, bg="#eef7ff", fg="#0f4d73", titulo_var=self.retro_aba_jejum_adv_titulo_var)
        _card_texto(jejuns_wrap, 0, 1, var=self.retro_aba_jejum_vasco_var, bg="#f2efff", fg="#4a2f8a", titulo_var=self.retro_aba_jejum_vasco_titulo_var)

        ttk.Label(info_wrap, text="Artilheiros do Vasco", font=("TkDefaultFont", 10, "bold")).grid(row=8, column=0, sticky="w")
        ttk.Label(
            info_wrap,
            textvariable=self.retro_aba_art_vasco_var,
            justify="left",
            wraplength=420,
        ).grid(row=9, column=0, sticky="nw", pady=(2, 10))

        ttk.Label(
            info_wrap,
            textvariable=self.retro_aba_art_adv_titulo_var,
            font=("TkDefaultFont", 10, "bold")
        ).grid(row=10, column=0, sticky="w")
        ttk.Label(
            info_wrap,
            textvariable=self.retro_aba_art_adv_var,
            justify="left",
            wraplength=420,
        ).grid(row=11, column=0, sticky="nw")

        self._retro_aba_partidas_atual = []
        self._retro_aba_sort_col = "data"
        self._retro_aba_sort_reverse = True
        self._atualizar_opcoes_aba_retro()

    def _listar_adversarios_com_historico(self):
        return sorted(
            {
                str(j.get("adversario", "")).strip()
                for j in carregar_dados_jogos()
                if str(j.get("adversario", "")).strip()
            },
            key=lambda s: s.casefold()
        )

    def _atualizar_opcoes_aba_retro(self):
        if not hasattr(self, "retro_adversario_combo"):
            return
        atual = self.retro_adversario_var.get().strip() if hasattr(self, "retro_adversario_var") else ""
        opcoes = self._listar_adversarios_com_historico()
        self.retro_adversario_combo["values"] = opcoes
        if atual and atual in opcoes:
            self.retro_adversario_var.set(atual)
        elif atual and opcoes:
            self.retro_adversario_var.set("")
            self._limpar_retro_aba("Selecione um adversário para ver o retrospecto.")
        elif not opcoes:
            self.retro_adversario_var.set("")
            self._limpar_retro_aba("Nenhum jogo registrado para montar retrospecto.")

    def _limpar_retro_aba(self, mensagem):
        self._retro_aba_partidas_atual = []
        if hasattr(self, "retro_aba_total_var"):
            self.retro_aba_total_var.set("0")
        if hasattr(self, "retro_aba_aproveitamento_var"):
            self.retro_aba_aproveitamento_var.set("0%")
        if hasattr(self, "retro_aba_vitorias_var"):
            self.retro_aba_vitorias_var.set("0")
        if hasattr(self, "retro_aba_empates_var"):
            self.retro_aba_empates_var.set("0")
        if hasattr(self, "retro_aba_derrotas_var"):
            self.retro_aba_derrotas_var.set("0")
        if hasattr(self, "retro_aba_saldo_var"):
            self.retro_aba_saldo_var.set("0")
        if hasattr(self, "retro_aba_gols_somados_var"):
            self.retro_aba_gols_somados_var.set(mensagem if mensagem else "Vasco 0 x 0 Adversário")
        if hasattr(self, "retro_aba_elastico_vasco_var"):
            self.retro_aba_elastico_vasco_var.set("—")
        if hasattr(self, "retro_aba_elastico_adv_var"):
            self.retro_aba_elastico_adv_var.set("—")
        if hasattr(self, "retro_aba_jejum_adv_var"):
            self.retro_aba_jejum_adv_var.set("—")
        if hasattr(self, "retro_aba_jejum_vasco_var"):
            self.retro_aba_jejum_vasco_var.set("—")
        if hasattr(self, "retro_aba_elastico_adv_titulo_var"):
            self.retro_aba_elastico_adv_titulo_var.set("Para o adversário")
        if hasattr(self, "retro_aba_jejum_adv_titulo_var"):
            self.retro_aba_jejum_adv_titulo_var.set("Adversário sem vencer")
        if hasattr(self, "retro_aba_jejum_vasco_titulo_var"):
            self.retro_aba_jejum_vasco_titulo_var.set("Vasco sem vencer")
        if hasattr(self, "retro_aba_art_vasco_var"):
            self.retro_aba_art_vasco_var.set("—")
        if hasattr(self, "retro_aba_art_adv_var"):
            self.retro_aba_art_adv_var.set("—")
        if hasattr(self, "retro_aba_art_adv_titulo_var"):
            self.retro_aba_art_adv_titulo_var.set("Artilheiros do adversário")
        if hasattr(self, "tv_retro_aba"):
            for iid in self.tv_retro_aba.get_children():
                self.tv_retro_aba.delete(iid)

    def _atualizar_retro_aba_adversario(self, _event=None):
        if not hasattr(self, "tv_retro_aba"):
            return
        adversario = self.retro_adversario_var.get().strip() if hasattr(self, "retro_adversario_var") else ""
        if not adversario:
            self._limpar_retro_aba("Selecione um adversário para ver o retrospecto.")
            return

        retro = self._coletar_retro_por_adversario(adversario)
        total = len(retro["partidas"])
        if total == 0:
            self._limpar_retro_aba(f"{adversario}: sem partidas registradas contra o Vasco.")
            return

        artilheiros_vasco = self._formatar_goleadores(retro["artilheiros_vasco"])
        artilheiros_adv = self._formatar_goleadores(retro["artilheiros_adversario"])

        def _parse_placar_nums(placar_txt):
            m = re.match(r"^\s*(\d+)\s*x\s*(\d+)\s*$", str(placar_txt or "").strip())
            if not m:
                return 0, 0
            return int(m.group(1)), int(m.group(2))

        def _fmt_partida_card(partida):
            data = str(partida.get("data", "—")).strip() or "—"
            placar = str(partida.get("placar", "—")).strip() or "—"
            return f"{placar}\nData: {data}"

        def _maior_elastico(partidas, lado="vasco"):
            melhor = None
            melhor_diff = -1
            for p in partidas:
                gv, ga = _parse_placar_nums(p.get("placar"))
                diff = (gv - ga) if lado == "vasco" else (ga - gv)
                if diff <= 0:
                    continue
                if diff > melhor_diff:
                    melhor_diff = diff
                    melhor = p
            return "—" if melhor is None else _fmt_partida_card(melhor)

        def _maior_jejum(partidas, sem_vencer_resultados):
            max_len = 0
            cur_len = 0
            inicio = fim = None
            cur_inicio = None
            streak_atual = False
            for p in partidas:  # cronológico (mais antigo -> mais novo)
                res = str(p.get("resultado", "")).strip()
                if res in sem_vencer_resultados:
                    cur_len += 1
                    if cur_inicio is None:
                        cur_inicio = p
                    cur_fim = p
                    if cur_len > max_len:
                        max_len = cur_len
                        inicio, fim = cur_inicio, cur_fim
                        streak_atual = False
                else:
                    cur_len = 0
                    cur_inicio = None
            if partidas:
                ultimo = partidas[-1]
                if str(ultimo.get("resultado", "")).strip() in sem_vencer_resultados and inicio is not None and fim is not None:
                    # Se o maior jejum termina no último jogo, considera em andamento.
                    streak_atual = str(fim.get("data", "")) == str(ultimo.get("data", ""))
            return {"qtd": max_len, "inicio": inicio, "fim": fim, "em_andamento": streak_atual}

        def _fmt_jejum_card(info):
            qtd = int(info.get("qtd", 0) or 0)
            if qtd <= 0:
                return "0 jogo(s)\nPeríodo: —"
            inicio = info.get("inicio") or {}
            fim = info.get("fim") or {}
            data_ini = str(inicio.get("data", "—")).strip() or "—"
            data_fim = "hoje" if info.get("em_andamento") else (str(fim.get("data", "—")).strip() or "—")
            return f"{qtd} jogo(s)\n{data_ini} até {data_fim}"

        aproveitamento = ((retro["vitorias"] * 3 + retro["empates"]) / (total * 3)) * 100 if total else 0.0
        self.retro_aba_total_var.set(str(total))
        self.retro_aba_aproveitamento_var.set(f"{aproveitamento:.0f}%")
        self.retro_aba_vitorias_var.set(str(retro["vitorias"]))
        self.retro_aba_empates_var.set(str(retro["empates"]))
        self.retro_aba_derrotas_var.set(str(retro["derrotas"]))
        self.retro_aba_saldo_var.set(str(retro["gols_vasco"] - retro["gols_adversario"]))
        self.retro_aba_gols_somados_var.set(
            f"Vasco {retro['gols_vasco']} x {retro['gols_adversario']} {adversario}"
        )
        self.retro_aba_elastico_vasco_var.set(_maior_elastico(retro["partidas"], "vasco"))
        self.retro_aba_elastico_adv_var.set(_maior_elastico(retro["partidas"], "adversario"))
        self.retro_aba_elastico_adv_titulo_var.set(f"Para o {adversario}")
        self.retro_aba_jejum_adv_titulo_var.set(f"{adversario} sem vencer")
        self.retro_aba_jejum_vasco_titulo_var.set("Vasco sem vencer")
        self.retro_aba_jejum_adv_var.set(_fmt_jejum_card(_maior_jejum(retro["partidas"], {"Vitória", "Empate"})))
        self.retro_aba_jejum_vasco_var.set(_fmt_jejum_card(_maior_jejum(retro["partidas"], {"Derrota", "Empate"})))
        self.retro_aba_art_vasco_var.set(artilheiros_vasco)
        self.retro_aba_art_adv_titulo_var.set(f"Artilheiros do {adversario}")
        self.retro_aba_art_adv_var.set(artilheiros_adv)
        self._retro_aba_partidas_atual = list(retro["partidas"])
        self._retro_aba_sort_col = "data"
        self._retro_aba_sort_reverse = True
        self._render_retro_partidas_aba_ordenado()

    def _render_retro_partidas_aba_ordenado(self):
        if not hasattr(self, "tv_retro_aba"):
            return
        for iid in self.tv_retro_aba.get_children():
            self.tv_retro_aba.delete(iid)
        partidas = sorted(
            self._retro_aba_partidas_atual,
            key=lambda p: self._chave_ordenacao_retro(p, self._retro_aba_sort_col),
            reverse=self._retro_aba_sort_reverse
        )
        for i, partida in enumerate(partidas, start=1):
            self.tv_retro_aba.insert(
                "",
                "end",
                values=(
                    partida["data"],
                    partida["competicao"],
                    partida["local"],
                    partida["placar"],
                    self._formatar_resultado_com_bolinha(partida["resultado"]),
                    partida["gols_vasco"],
                    partida["gols_adversario"],
                ),
                tags=("odd",) if i % 2 else ()
            )

    def _ordenar_coluna_retro_aba(self, coluna):
        if not getattr(self, "_retro_aba_partidas_atual", None):
            return
        if self._retro_aba_sort_col == coluna:
            self._retro_aba_sort_reverse = not self._retro_aba_sort_reverse
        else:
            self._retro_aba_sort_col = coluna
            self._retro_aba_sort_reverse = False
        self._render_retro_partidas_aba_ordenado()

    def _copiar_exemplo_json_futuros(self):
        exemplo = [
            {
                "jogo": "Vasco x Time adversario",
                "data": "18/02/2026",
                "hora": "21:30",
                "local": "São Januário",
                "em_casa": True,
                "campeonato": "Campeonato Carioca"
            },
            {
                "jogo": "Time adversario x Vasco",
                "data": "22/02/2026",
                "hora": "",
                "local": "",
                "em_casa": False,
                "campeonato": "Brasileirão Série A"
            }
        ]
        texto = json.dumps(exemplo, ensure_ascii=False, indent=2)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update()

    def _limpar_campos_futuros(self):
        self.futuros_json_text.delete("1.0", "end")
        self.fut_manual_adversario_var.set("")
        self.fut_manual_campeonato_var.set("")
        self.fut_manual_data_var.set(datetime.now().strftime("%d/%m/%Y"))
        self.fut_manual_mando_var.set("casa")
        self.fut_manual_hora_h_var.set("")
        self.fut_manual_hora_m_var.set("")
        self.fut_manual_local_var.set("")

    def _abrir_menu_contexto_json_futuros(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Colar do clipboard", command=self._colar_json_futuros_clipboard)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _colar_json_futuros_clipboard(self):
        try:
            texto = self.root.clipboard_get()
        except tk.TclError:
            messagebox.showwarning("Clipboard", "O clipboard está vazio ou indisponível.")
            return
        if not texto:
            messagebox.showwarning("Clipboard", "O clipboard está vazio.")
            return
        self.futuros_json_text.insert("insert", texto)

    def _adicionar_jogo_futuro_manual(self):
        adversario = self._resolver_nome_clube_canonico(self.fut_manual_adversario_var.get().strip())
        data_txt = self.fut_manual_data_var.get().strip()
        campeonato = self.fut_manual_campeonato_var.get().strip()
        em_casa = self.fut_manual_mando_var.get() != "fora"
        hora = ""
        if self.fut_manual_hora_h_var.get().strip() or self.fut_manual_hora_m_var.get().strip():
            hora = f"{self.fut_manual_hora_h_var.get().strip()}:{self.fut_manual_hora_m_var.get().strip()}"
        local = self.fut_manual_local_var.get().strip()

        if not adversario or not data_txt:
            messagebox.showerror("Erro", "Preencha pelo menos os campos Adversário e Data.")
            return

        jogo = f"Vasco x {adversario}" if em_casa else f"{adversario} x Vasco"
        item = {
            "jogo": jogo,
            "data": data_txt,
            "em_casa": em_casa,
            "hora": hora,
            "local": local,
            "campeonato": campeonato,
        }
        normalizado = _normalizar_futuro_item(item)
        if not normalizado:
            messagebox.showerror("Erro", "Não foi possível normalizar o jogo informado.")
            return
        if not _parse_data_ptbr_safe(normalizado["data"]):
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.")
            return
        if hora and not re.match(r"^\d{2}:\d{2}$", hora):
            messagebox.showerror("Erro", "Informe a hora no formato HH:MM.")
            return
        if hora:
            horas, minutos = [int(parte) for parte in hora.split(":", 1)]
            if horas > 23 or minutos > 59:
                messagebox.showerror("Erro", "Informe um horário válido entre 00:00 e 23:59.")
                return

        jogos = carregar_jogos_futuros()
        jogos.append(normalizado)
        salvar_lista_futuros(jogos)
        adversario = self._registrar_clube_adversario(adversario)
        self.fut_manual_adversario_var.set(adversario)
        salvar_listas(self.listas)
        self._render_lista_futuros()
        self.fut_manual_adversario_var.set("")
        self.fut_manual_campeonato_var.set("")
        self.fut_manual_hora_h_var.set("")
        self.fut_manual_hora_m_var.set("")
        self.fut_manual_local_var.set("")
        messagebox.showinfo("Sucesso", "Jogo futuro adicionado.")

    def _render_lista_futuros(self):
        for iid in self.tv_futuros.get_children():
            self.tv_futuros.delete(iid)

        jogos = carregar_jogos_futuros()
        competicoes = sorted({
            str(item.get("campeonato", "")).strip()
            for item in jogos
            if str(item.get("campeonato", "")).strip()
        }, key=lambda s: s.casefold())
        if hasattr(self, "filtro_futuros_competicao_combo"):
            atual = self.filtro_futuros_competicao_var.get().strip() or "Todas"
            opcoes = ["Todas"] + competicoes
            self.filtro_futuros_competicao_combo.configure(values=opcoes)
            if atual not in opcoes:
                atual = "Todas"
                self.filtro_futuros_competicao_var.set(atual)
        competicao_sel = ""
        if hasattr(self, "filtro_futuros_competicao_var"):
            competicao_sel = self.filtro_futuros_competicao_var.get().strip()

        jogos_validos = []
        for item in jogos:
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                continue
            data_obj = _parse_data_ptbr_safe(normalizado["data"])
            if not data_obj:
                continue
            if competicao_sel and competicao_sel != "Todas":
                if str(normalizado.get("campeonato", "")).strip().casefold() != competicao_sel.casefold():
                    continue
            jogos_validos.append((data_obj, normalizado))

        today = datetime.now().date()
        for i, (data_obj, jogo) in enumerate(sorted(jogos_validos, key=lambda j: j[0])):
            em_casa = jogo.get("em_casa")
            if em_casa is True:
                local = "Sim"
            elif em_casa is False:
                local = "Não"
            else:
                local = "-"
            tags = []
            if i % 2 == 1:
                tags.append("odd")
            if data_obj.date() < today:
                tags.append("past")
            self.tv_futuros.insert(
                "",
                "end",
                values=(
                    jogo.get("data"),
                    jogo.get("hora") or "-",
                    jogo.get("jogo"),
                    local,
                    jogo.get("local") or "-",
                    jogo.get("campeonato") or "-",
                ),
                tags=tuple(tags)
            )
        self._atualizar_retro_futuro_selecionado()

    def _contagem_goleadores(self, gols_lista):
        contagem = Counter()
        for item in gols_lista or []:
            if isinstance(item, dict):
                nome = str(item.get("nome", "")).strip() or "Desconhecido"
                try:
                    qtd = int(item.get("gols", 1))
                except (ValueError, TypeError):
                    qtd = 1
                contagem[nome] += max(1, qtd)
            elif isinstance(item, str):
                nome = item.strip()
                if nome:
                    contagem[nome] += 1
        return contagem

    def _formatar_goleadores(self, contagem):
        if not contagem:
            return "—"
        partes = []
        for nome, qtd in contagem.most_common():
            partes.append(f"{nome} x{qtd}" if qtd > 1 else nome)
        return ", ".join(partes)

    def _formatar_resultado_com_bolinha(self, resultado):
        resultado_txt = str(resultado or "").strip()
        resultado_norm = _chave_nome_jogador(resultado_txt)
        bolinha = ""
        if resultado_norm == "vitoria":
            bolinha = "🟢"
        elif resultado_norm == "empate":
            bolinha = "🟡"
        elif resultado_norm == "derrota":
            bolinha = "🔴"
        return f"{bolinha} {resultado_txt}".strip()

    def _coletar_retro_por_adversario(self, adversario):
        retrospecto = {
            "partidas": [],
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_vasco": 0,
            "gols_adversario": 0,
            "artilheiros_vasco": Counter(),
            "artilheiros_adversario": Counter(),
        }
        if not adversario:
            return retrospecto

        jogos = carregar_dados_jogos()
        alvo = _chave_nome_consulta(adversario)
        for jogo in jogos:
            adv_jogo = str(jogo.get("adversario", "")).strip()
            if not adv_jogo or _chave_nome_consulta(adv_jogo) != alvo:
                continue

            placar = jogo.get("placar", {})
            try:
                gols_vasco = int(placar.get("vasco", 0))
            except (ValueError, TypeError):
                gols_vasco = 0
            try:
                gols_adv = int(placar.get("adversario", 0))
            except (ValueError, TypeError):
                gols_adv = 0

            if gols_vasco > gols_adv:
                resultado = "Vitória"
                retrospecto["vitorias"] += 1
            elif gols_vasco < gols_adv:
                resultado = "Derrota"
                retrospecto["derrotas"] += 1
            else:
                resultado = "Empate"
                retrospecto["empates"] += 1

            retrospecto["gols_vasco"] += gols_vasco
            retrospecto["gols_adversario"] += gols_adv

            goleadores_vasco = self._contagem_goleadores(jogo.get("gols_vasco", []))
            goleadores_adv = self._contagem_goleadores(jogo.get("gols_adversario", []))
            retrospecto["artilheiros_vasco"].update(goleadores_vasco)
            retrospecto["artilheiros_adversario"].update(goleadores_adv)

            local = "Casa" if jogo.get("local", "casa") == "casa" else "Fora"
            data_txt = str(jogo.get("data", "")).strip()
            data_ord = _parse_data_ptbr_safe(data_txt) or datetime.min

            retrospecto["partidas"].append({
                "data": data_txt or "—",
                "data_ord": data_ord,
                "competicao": str(jogo.get("competicao", "")).strip() or "—",
                "local": local,
                "placar": f"{gols_vasco} x {gols_adv}",
                "resultado": resultado,
                "gols_vasco": self._formatar_goleadores(goleadores_vasco),
                "gols_adversario": self._formatar_goleadores(goleadores_adv),
            })

        retrospecto["partidas"].sort(key=lambda p: p["data_ord"])
        return retrospecto

    def _atualizar_retro_futuro_selecionado(self, _event=None):
        if not hasattr(self, "tv_retro_futuros"):
            return

        for iid in self.tv_retro_futuros.get_children():
            self.tv_retro_futuros.delete(iid)

        sel = self.tv_futuros.selection()
        if not sel:
            self._retro_partidas_atual = []
            self.retro_resumo_var.set("Selecione um jogo para ver o retrospecto contra o adversário.")
            return

        values = self.tv_futuros.item(sel[0], "values")
        if len(values) < 3:
            self._retro_partidas_atual = []
            self.retro_resumo_var.set("Não foi possível identificar o adversário.")
            return

        jogo_txt = str(values[2]).strip()
        adversario = self._resolver_nome_clube_canonico(
            _extrair_adversario_de_jogo(jogo_txt).replace("Vasco", "").strip()
        )
        if not adversario:
            self._retro_partidas_atual = []
            self.retro_resumo_var.set("Não foi possível identificar o adversário.")
            return

        retro = self._coletar_retro_por_adversario(adversario)
        total = len(retro["partidas"])
        if total == 0:
            self._retro_partidas_atual = []
            self.retro_resumo_var.set(f"{adversario}: sem partidas registradas contra o Vasco.")
            return

        resumo = (
            f"{adversario} | Jogos: {total} | V/E/D: "
            f"{retro['vitorias']}/{retro['empates']}/{retro['derrotas']} | "
            f"Gols totais: Vasco {retro['gols_vasco']} x {retro['gols_adversario']} {adversario}"
        )
        artilheiros_vasco = self._formatar_goleadores(retro["artilheiros_vasco"])
        artilheiros_adv = self._formatar_goleadores(retro["artilheiros_adversario"])
        self.retro_resumo_var.set(
            f"{resumo} | Artilheiros do Vasco: {artilheiros_vasco} | Artilheiros do {adversario}: {artilheiros_adv}"
        )
        self._retro_partidas_atual = list(retro["partidas"])
        self._retro_sort_col = "data"
        self._retro_sort_reverse = True
        self._render_retro_partidas_ordenado()

    def _chave_ordenacao_retro(self, partida, coluna):
        if coluna == "data":
            return partida.get("data_ord") or datetime.min
        if coluna == "placar":
            placar_txt = str(partida.get("placar", "0 x 0")).strip()
            m = re.match(r"^\s*(\d+)\s*x\s*(\d+)\s*$", placar_txt)
            if m:
                return int(m.group(1)), int(m.group(2))
            return -1, -1
        return str(partida.get(coluna, "")).casefold()

    def _render_retro_partidas_ordenado(self):
        for iid in self.tv_retro_futuros.get_children():
            self.tv_retro_futuros.delete(iid)
        partidas = sorted(
            self._retro_partidas_atual,
            key=lambda p: self._chave_ordenacao_retro(p, self._retro_sort_col),
            reverse=self._retro_sort_reverse
        )
        for i, partida in enumerate(partidas, start=1):
            self.tv_retro_futuros.insert(
                "",
                "end",
                values=(
                    partida["data"],
                    partida["competicao"],
                    partida["local"],
                    partida["placar"],
                    self._formatar_resultado_com_bolinha(partida["resultado"]),
                    partida["gols_vasco"],
                    partida["gols_adversario"],
                ),
                tags=("odd",) if i % 2 else ()
            )

    def _ordenar_coluna_retro(self, coluna):
        if not getattr(self, "_retro_partidas_atual", None):
            return
        if self._retro_sort_col == coluna:
            self._retro_sort_reverse = not self._retro_sort_reverse
        else:
            self._retro_sort_col = coluna
            self._retro_sort_reverse = False
        self._render_retro_partidas_ordenado()

    def _local_futuro_txt(self, em_casa):
        if em_casa is True:
            return "Sim"
        if em_casa is False:
            return "Não"
        return "-"

    def _opcoes_clubes_adversarios(self):
        base = list(self.listas.get("clubes_adversarios", []))
        extras = []
        for jogo in carregar_dados_jogos():
            nome = str(jogo.get("adversario", "")).strip()
            if nome:
                extras.append(nome)
        for futuro in carregar_jogos_futuros():
            nome = _extrair_adversario_de_jogo(str(futuro.get("jogo", "")).strip()).replace("Vasco", "").strip()
            if nome:
                extras.append(nome)
        vistos = set()
        ordenados = []
        for nome in sorted(base + extras, key=lambda s: s.casefold()):
            chave = _chave_nome_consulta(nome)
            if not chave or chave in vistos:
                continue
            vistos.add(chave)
            ordenados.append(nome)
        return ordenados

    def _atualizar_combos_clubes_adversarios(self):
        opcoes = self._opcoes_clubes_adversarios()
        if hasattr(self, "adversario_entry"):
            self.adversario_entry["values"] = opcoes
        if hasattr(self, "fut_manual_adversario_entry"):
            self.fut_manual_adversario_entry["values"] = opcoes
        return opcoes

    def _resolver_nome_clube_canonico(self, nome: str) -> str:
        nome_limpo = str(nome or "").strip()
        if not nome_limpo:
            return ""
        alvo = _chave_nome_consulta(nome_limpo)
        for candidato in self._opcoes_clubes_adversarios():
            if _chave_nome_consulta(candidato) == alvo:
                return candidato
        return nome_limpo

    def _registrar_clube_adversario(self, nome: str) -> str:
        canonico = self._resolver_nome_clube_canonico(nome)
        if not canonico:
            return ""
        lista = self.listas.setdefault("clubes_adversarios", [])
        if not any(_chave_nome_consulta(item) == _chave_nome_consulta(canonico) for item in lista):
            lista.append(canonico)
            self.listas["clubes_adversarios"] = sorted(lista, key=lambda s: s.casefold())
        self._atualizar_combos_clubes_adversarios()
        return canonico

    def _dados_futuro_selecionado(self):
        sel = self.tv_futuros.selection()
        if not sel:
            return None
        values = self.tv_futuros.item(sel[0], "values")
        if len(values) < 6:
            return None
        data_txt, hora_txt, jogo_txt, mando_txt, local_txt, campeonato_txt = values
        return {
            "data": str(data_txt),
            "hora": "" if str(hora_txt) == "-" else str(hora_txt),
            "jogo": str(jogo_txt),
            "mando": str(mando_txt),
            "local": "" if str(local_txt) == "-" else str(local_txt),
            "campeonato": "" if str(campeonato_txt) == "-" else str(campeonato_txt),
        }

    def _localizar_indice_futuro(self, alvo: dict):
        futuros = carregar_jogos_futuros()
        for idx, item in enumerate(futuros):
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                continue
            mesmo_jogo = (
                str(normalizado.get("data", "")) == str(alvo.get("data", ""))
                and str(normalizado.get("hora", "")) == str(alvo.get("hora", ""))
                and str(normalizado.get("jogo", "")) == str(alvo.get("jogo", ""))
                and self._local_futuro_txt(normalizado.get("em_casa")) == str(alvo.get("mando", ""))
                and str(normalizado.get("local", "")) == str(alvo.get("local", ""))
                and str(normalizado.get("campeonato", "")) == str(alvo.get("campeonato", ""))
            )
            if mesmo_jogo:
                return futuros, idx, normalizado
        return futuros, None, None

    def _inferir_em_casa_futuro(self, futuro: dict):
        em_casa = futuro.get("em_casa")
        if em_casa is True or em_casa is False:
            return em_casa
        jogo_txt = str(futuro.get("jogo", "") or "").strip()
        jogo_clean = re.sub(r"\s*×\s*", " x ", jogo_txt)
        partes = re.split(r"\s+(?:x|vs\.?)\s+", jogo_clean, maxsplit=1, flags=re.IGNORECASE)
        if len(partes) != 2:
            return None
        p1, p2 = partes[0].strip().casefold(), partes[1].strip().casefold()
        if "vasco" in p1:
            return True
        if "vasco" in p2:
            return False
        return None

    def _partidas_base_probabilidade(self, limite_data=None):
        partidas = []
        for jogo in carregar_dados_jogos():
            data_txt = str(jogo.get("data", "") or "").strip()
            data_obj = _parse_data_ptbr_safe(data_txt)
            if not data_obj:
                continue
            if limite_data and data_obj.date() >= limite_data.date():
                continue

            placar = jogo.get("placar", {}) if isinstance(jogo.get("placar"), dict) else {}
            try:
                gols_vasco = int(placar.get("vasco", 0) or 0)
                gols_adv = int(placar.get("adversario", 0) or 0)
            except (TypeError, ValueError):
                continue
            if gols_vasco < 0 or gols_adv < 0:
                continue

            if gols_vasco > gols_adv:
                resultado = "vitoria"
            elif gols_vasco < gols_adv:
                resultado = "derrota"
            else:
                resultado = "empate"

            local_txt = str(jogo.get("local", "casa") or "casa").strip().casefold()
            if local_txt == "fora":
                em_casa = False
            elif local_txt == "casa":
                em_casa = True
            else:
                em_casa = None

            adversario = str(jogo.get("adversario", "") or "").strip()
            partidas.append({
                "data": data_obj,
                "data_txt": data_txt,
                "adversario": adversario,
                "adversario_chave": _chave_nome_consulta(adversario),
                "competicao": str(jogo.get("competicao", "") or "").strip(),
                "competicao_chave": _chave_nome_consulta(jogo.get("competicao", "")),
                "em_casa": em_casa,
                "gols_vasco": gols_vasco,
                "gols_adversario": gols_adv,
                "resultado": resultado,
            })
        return sorted(partidas, key=lambda p: p["data"])

    def _resumir_partidas_probabilidade(self, partidas):
        resumo = {
            "jogos": len(partidas),
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_vasco": 0,
            "gols_adversario": 0,
            "media_gols_vasco": 0.0,
            "media_gols_adversario": 0.0,
            "aproveitamento": 0.0,
        }
        for partida in partidas:
            if partida["resultado"] == "vitoria":
                resumo["vitorias"] += 1
            elif partida["resultado"] == "derrota":
                resumo["derrotas"] += 1
            else:
                resumo["empates"] += 1
            resumo["gols_vasco"] += partida["gols_vasco"]
            resumo["gols_adversario"] += partida["gols_adversario"]

        jogos = resumo["jogos"]
        if jogos:
            resumo["media_gols_vasco"] = resumo["gols_vasco"] / jogos
            resumo["media_gols_adversario"] = resumo["gols_adversario"] / jogos
            pontos = resumo["vitorias"] * 3 + resumo["empates"]
            resumo["aproveitamento"] = (pontos / (jogos * 3)) * 100
        return resumo

    def _distribuicao_partidas_probabilidade(self, partidas, pesos=None, suavizacao=0.0):
        chaves = ("vitoria", "empate", "derrota")
        contagem = {chave: float(suavizacao) for chave in chaves}
        if pesos is None:
            pesos = [1.0] * len(partidas)
        for partida, peso in zip(partidas, pesos):
            chave = partida.get("resultado")
            if chave in contagem:
                contagem[chave] += max(float(peso), 0.0)
        total = sum(contagem.values())
        if total <= 0:
            return {chave: 1 / 3 for chave in chaves}
        return {chave: contagem[chave] / total for chave in chaves}

    def _distribuicao_poisson_probabilidade(self, gols_vasco_esp, gols_adv_esp):
        gols_vasco_esp = max(0.05, min(float(gols_vasco_esp), 5.0))
        gols_adv_esp = max(0.05, min(float(gols_adv_esp), 5.0))

        def pmf(media, gols):
            return math.exp(-media) * (media ** gols) / math.factorial(gols)

        probs = {"vitoria": 0.0, "empate": 0.0, "derrota": 0.0}
        total = 0.0
        for gols_vasco in range(9):
            prob_v = pmf(gols_vasco_esp, gols_vasco)
            for gols_adv in range(9):
                prob = prob_v * pmf(gols_adv_esp, gols_adv)
                total += prob
                if gols_vasco > gols_adv:
                    probs["vitoria"] += prob
                elif gols_vasco < gols_adv:
                    probs["derrota"] += prob
                else:
                    probs["empate"] += prob
        if total > 0:
            probs = {chave: valor / total for chave, valor in probs.items()}
        return probs

    def _calcular_gols_esperados_probabilidade(self, grupos):
        numerador_vasco = 0.0
        numerador_adv = 0.0
        peso_total = 0.0
        fontes = []
        for nome, partidas, peso_base, minimo_ref in grupos:
            if not partidas:
                continue
            resumo = self._resumir_partidas_probabilidade(partidas)
            fator_amostra = min(1.0, resumo["jogos"] / max(1, minimo_ref))
            peso = peso_base * fator_amostra
            if peso <= 0:
                continue
            numerador_vasco += resumo["media_gols_vasco"] * peso
            numerador_adv += resumo["media_gols_adversario"] * peso
            peso_total += peso
            fontes.append((nome, resumo["jogos"], peso))
        if peso_total <= 0:
            return None
        return {
            "gols_vasco": numerador_vasco / peso_total,
            "gols_adversario": numerador_adv / peso_total,
            "fontes": fontes,
        }

    def _adicionar_componente_probabilidade(self, componentes, nome, partidas, peso, suavizacao=0.0, pesos_partidas=None):
        if not partidas or peso <= 0:
            return
        resumo = self._resumir_partidas_probabilidade(partidas)
        componentes.append({
            "nome": nome,
            "peso": peso,
            "partidas": partidas,
            "resumo": resumo,
            "distribuicao": self._distribuicao_partidas_probabilidade(
                partidas,
                pesos=pesos_partidas,
                suavizacao=suavizacao,
            ),
        })

    def _calcular_probabilidade_futuro(self, futuro: dict, adversario_externo=None):
        futuro = _normalizar_futuro_item(futuro) or futuro
        adversario = self._resolver_nome_clube_canonico(
            _extrair_adversario_de_jogo(str(futuro.get("jogo", "") or "")).replace("Vasco", "").strip()
        )
        adversario_chave = _chave_nome_consulta(adversario)
        competicao = str(futuro.get("campeonato", "") or "").strip()
        competicao_chave = _chave_nome_consulta(competicao)
        em_casa = self._inferir_em_casa_futuro(futuro)
        data_futuro = _parse_data_ptbr_safe(str(futuro.get("data", "") or "").strip())

        partidas = self._partidas_base_probabilidade(limite_data=data_futuro)
        if not partidas:
            return {
                "erro": "Não há partidas anteriores suficientes na base para calcular probabilidade.",
                "adversario": adversario,
            }

        partidas_desc = sorted(partidas, key=lambda p: p["data"], reverse=True)
        recentes = partidas_desc[:10]
        ultimos_cinco = partidas_desc[:5]
        mesmo_mando = [p for p in partidas if em_casa is None or p["em_casa"] == em_casa]
        h2h = [p for p in partidas if adversario_chave and p["adversario_chave"] == adversario_chave]
        mesma_competicao = [p for p in partidas if competicao_chave and p["competicao_chave"] == competicao_chave]

        componentes = []
        self._adicionar_componente_probabilidade(
            componentes,
            "Histórico geral",
            partidas,
            peso=1.8,
            suavizacao=1.0,
        )

        if recentes:
            n = len(recentes)
            pesos_recentes = [1.0 + ((n - idx - 1) * 0.08) for idx in range(n)]
            self._adicionar_componente_probabilidade(
                componentes,
                "Momento recente (10 jogos)",
                recentes,
                peso=2.6 * min(1.0, n / 10),
                pesos_partidas=pesos_recentes,
            )

        if ultimos_cinco:
            self._adicionar_componente_probabilidade(
                componentes,
                "Recorte curto (5 jogos)",
                ultimos_cinco,
                peso=0.9 * min(1.0, len(ultimos_cinco) / 5),
            )

        if em_casa is not None and mesmo_mando:
            nome_mando = "Mando: Vasco em casa" if em_casa else "Mando: Vasco fora"
            self._adicionar_componente_probabilidade(
                componentes,
                nome_mando,
                mesmo_mando,
                peso=1.4 * min(1.0, len(mesmo_mando) / 20),
            )

        if h2h:
            self._adicionar_componente_probabilidade(
                componentes,
                f"Retrospecto vs {adversario}",
                h2h,
                peso=1.2 * min(1.0, len(h2h) / 8),
            )

        if mesma_competicao:
            self._adicionar_componente_probabilidade(
                componentes,
                "Mesma competição",
                mesma_competicao,
                peso=0.9 * min(1.0, len(mesma_competicao) / 12),
            )

        resumo_adversario = None
        resumo_adversario_mando = None
        resumo_adversario_tabela = None
        partidas_adversario_recentes = []
        partidas_adversario_mando = []
        if adversario_externo:
            partidas_adv = list(adversario_externo.get("partidas", []))
            if data_futuro:
                partidas_adv = [
                    p for p in partidas_adv
                    if p.get("data") == datetime.min or p.get("data").date() < data_futuro.date()
                ]
            partidas_adv = sorted(partidas_adv, key=lambda p: p.get("data") or datetime.min, reverse=True)
            recentes_adv = partidas_adv[:10]
            nivel_fator = float(adversario_externo.get("nivel_fator", 0.80) or 0.80)
            if recentes_adv:
                partidas_adversario_recentes = list(recentes_adv)
                resumo_adversario = self._resumir_partidas_adversario_probabilidade(recentes_adv)
                n = len(recentes_adv)
                pesos_adv = [1.0 + ((n - idx - 1) * 0.08) for idx in range(n)]
                componentes.append({
                    "nome": f"Momento do adversário ({adversario_externo.get('time', adversario)})",
                    "peso": 1.3 * min(1.0, n / 8) * nivel_fator,
                    "partidas": [],
                    "resumo": resumo_adversario,
                    "resumo_tipo": "adversario",
                    "distribuicao": self._distribuicao_adversario_para_vasco(
                        recentes_adv,
                        pesos=pesos_adv,
                    ),
                })

            if em_casa is not None and partidas_adv:
                mando_adv = not em_casa
                partidas_adv_mando = [p for p in partidas_adv if p.get("em_casa") == mando_adv]
                if partidas_adv_mando:
                    partidas_adversario_mando = list(partidas_adv_mando)
                    resumo_adversario_mando = self._resumir_partidas_adversario_probabilidade(partidas_adv_mando)
                    nome_mando_adv = "adversário fora" if mando_adv is False else "adversário em casa"
                    componentes.append({
                        "nome": f"Momento do {nome_mando_adv}",
                        "peso": 0.7 * min(1.0, len(partidas_adv_mando) / 5) * nivel_fator,
                        "partidas": [],
                        "resumo": resumo_adversario_mando,
                        "resumo_tipo": "adversario",
                        "distribuicao": self._distribuicao_adversario_para_vasco(partidas_adv_mando),
                    })

            resumo_adversario_tabela = self._resumo_tabela_adversario_probabilidade(
                adversario_externo.get("tabela", {})
            )
            if resumo_adversario_tabela:
                componentes.append({
                    "nome": f"Campanha do adversário ({adversario_externo.get('nivel', 'nível não informado')})",
                    "peso": 0.6 * min(1.0, resumo_adversario_tabela["jogos"] / 10) * nivel_fator,
                    "partidas": [],
                    "resumo": resumo_adversario_tabela,
                    "resumo_tipo": "adversario",
                    "distribuicao": self._distribuicao_tabela_adversario_para_vasco(resumo_adversario_tabela),
                })

        grupos_gols = [
            ("histórico geral", partidas, 1.1, 30),
            ("momento recente", recentes, 1.8, 10),
            ("mando", mesmo_mando, 1.0, 18),
            ("retrospecto direto", h2h, 0.9, 8),
            ("competição", mesma_competicao, 0.6, 12),
        ]
        gols_esperados = self._calcular_gols_esperados_probabilidade(grupos_gols)
        if gols_esperados:
            componentes.append({
                "nome": "Modelo de gols estimados",
                "peso": 1.2,
                "partidas": [],
                "resumo": None,
                "distribuicao": self._distribuicao_poisson_probabilidade(
                    gols_esperados["gols_vasco"],
                    gols_esperados["gols_adversario"],
                ),
            })

        placar_prob = {"vitoria": 0.0, "empate": 0.0, "derrota": 0.0}
        peso_total = 0.0
        for componente in componentes:
            peso = componente["peso"]
            peso_total += peso
            for chave in placar_prob:
                placar_prob[chave] += componente["distribuicao"][chave] * peso
        if peso_total <= 0:
            prob_final = {chave: 1 / 3 for chave in placar_prob}
        else:
            prob_final = {chave: valor / peso_total for chave, valor in placar_prob.items()}

        resumo_geral = self._resumir_partidas_probabilidade(partidas)
        resumo_recente = self._resumir_partidas_probabilidade(recentes)
        resumo_h2h = self._resumir_partidas_probabilidade(h2h)
        resumo_mando = self._resumir_partidas_probabilidade(mesmo_mando)
        resumo_comp = self._resumir_partidas_probabilidade(mesma_competicao)
        indice_base = (
            min(1.0, resumo_geral["jogos"] / 80) * 0.35
            + min(1.0, resumo_recente["jogos"] / 10) * 0.25
            + min(1.0, resumo_mando["jogos"] / 20) * 0.20
            + min(1.0, resumo_h2h["jogos"] / 8) * 0.15
            + min(1.0, resumo_comp["jogos"] / 12) * 0.05
        )
        if resumo_adversario:
            indice_base = min(1.0, indice_base + min(1.0, resumo_adversario["jogos"] / 8) * 0.12)
        if indice_base >= 0.75:
            confianca = "Alta base de dados"
        elif indice_base >= 0.45:
            confianca = "Base de dados média"
        else:
            confianca = "Base de dados baixa"

        return {
            "adversario": adversario,
            "competicao": competicao,
            "em_casa": em_casa,
            "probabilidades": prob_final,
            "componentes": componentes,
            "gols_esperados": gols_esperados,
            "resumo_geral": resumo_geral,
            "resumo_recente": resumo_recente,
            "resumo_h2h": resumo_h2h,
            "resumo_mando": resumo_mando,
            "resumo_competicao": resumo_comp,
            "partidas_recentes": recentes,
            "partidas_h2h": h2h,
            "partidas_mando": mesmo_mando,
            "adversario_externo": adversario_externo,
            "resumo_adversario": resumo_adversario,
            "resumo_adversario_mando": resumo_adversario_mando,
            "resumo_adversario_tabela": resumo_adversario_tabela,
            "partidas_adversario_recentes": partidas_adversario_recentes,
            "partidas_adversario_mando": partidas_adversario_mando,
            "confianca": confianca,
            "indice_base": indice_base,
            "data_limite": data_futuro,
        }

    def _formatar_percentual_probabilidade(self, valor):
        return f"{valor * 100:.1f}%"

    def _formatar_ved_probabilidade(self, resumo):
        if not resumo or resumo.get("jogos", 0) == 0:
            return "—"
        return f"{resumo['vitorias']}/{resumo['empates']}/{resumo['derrotas']}"

    def _normalizar_resultado_probabilidade(self, valor):
        chave = _chave_nome_consulta(valor)
        if chave in {"v", "vitoria", "vitória", "win", "w"}:
            return "vitoria"
        if chave in {"e", "empate", "draw"}:
            return "empate"
        if chave in {"d", "derrota", "loss", "l"}:
            return "derrota"
        return ""

    def _nivel_adversario_probabilidade(self, dados: dict):
        bruto = ""
        if isinstance(dados, dict):
            bruto = (
                dados.get("nivel")
                or dados.get("divisao")
                or dados.get("serie")
                or dados.get("categoria")
                or ""
            )
            tabela = dados.get("tabela")
            if isinstance(tabela, dict):
                bruto = bruto or tabela.get("divisao") or tabela.get("serie") or tabela.get("nivel") or ""
        chave = _chave_nome_consulta(bruto)
        if "serie a" in chave or "série a" in chave or chave in {"a", "1", "primeira divisao"}:
            return str(bruto or "Série A").strip(), 1.0
        if "serie b" in chave or "série b" in chave or chave in {"b", "2", "segunda divisao"}:
            return str(bruto or "Série B").strip(), 0.86
        if "serie c" in chave or "série c" in chave or chave in {"c", "3", "terceira divisao"}:
            return str(bruto or "Série C").strip(), 0.72
        if "serie d" in chave or "série d" in chave or chave in {"d", "4", "quarta divisao"}:
            return str(bruto or "Série D").strip(), 0.58
        if "estadual" in chave or "regional" in chave or "copa verde" in chave or "paraense" in chave:
            return str(bruto or "Regional/Estadual").strip(), 0.62
        return str(bruto or "Não informado").strip(), 0.80

    def _extrair_gols_adversario_json(self, item: dict, time_chave: str):
        placar = item.get("placar")
        gols_time = None
        gols_contra = None

        def _int_placar(valor):
            try:
                numero = int(valor)
            except (TypeError, ValueError):
                return None
            return numero if numero >= 0 else None

        if isinstance(placar, dict):
            diretos_time = ("time", "pro", "favor", "gols_time", "gols_pro", "gols_marcados")
            diretos_contra = ("adversario", "contra", "gols_adversario", "gols_contra", "gols_sofridos")
            for chave in diretos_time:
                gols_time = _int_placar(placar.get(chave))
                if gols_time is not None:
                    break
            for chave in diretos_contra:
                gols_contra = _int_placar(placar.get(chave))
                if gols_contra is not None:
                    break

            if gols_time is None or gols_contra is None:
                casa = _int_placar(placar.get("mandante", placar.get("casa", placar.get("home"))))
                fora = _int_placar(placar.get("visitante", placar.get("fora", placar.get("away"))))
                if casa is not None and fora is not None:
                    mandante = _chave_nome_consulta(item.get("mandante", item.get("casa", item.get("home_team", ""))))
                    visitante = _chave_nome_consulta(item.get("visitante", item.get("fora", item.get("away_team", ""))))
                    em_casa = _normalizar_em_casa(item.get("em_casa", item.get("local", item.get("mando"))))
                    if mandante and mandante == time_chave:
                        gols_time, gols_contra = casa, fora
                    elif visitante and visitante == time_chave:
                        gols_time, gols_contra = fora, casa
                    elif em_casa is True:
                        gols_time, gols_contra = casa, fora
                    elif em_casa is False:
                        gols_time, gols_contra = fora, casa

        if gols_time is None:
            for chave in ("gols_time", "gols_pro", "gols_marcados", "pro"):
                gols_time = _int_placar(item.get(chave))
                if gols_time is not None:
                    break
        if gols_contra is None:
            for chave in ("gols_adversario", "gols_contra", "gols_sofridos", "contra"):
                gols_contra = _int_placar(item.get(chave))
                if gols_contra is not None:
                    break

        if (gols_time is None or gols_contra is None) and isinstance(placar, str):
            m = re.match(r"^\s*(\d+)\s*[xX-]\s*(\d+)\s*$", placar.strip())
            if m:
                primeiro, segundo = int(m.group(1)), int(m.group(2))
                em_casa = _normalizar_em_casa(item.get("em_casa", item.get("local", item.get("mando"))))
                gols_time, gols_contra = (primeiro, segundo) if em_casa is not False else (segundo, primeiro)

        if gols_time is None or gols_contra is None:
            return None, None
        return gols_time, gols_contra

    def _normalizar_jogo_adversario_probabilidade(self, item, time_nome: str):
        if not isinstance(item, dict):
            return None, "Jogo ignorado: item não é objeto."
        time_chave = _chave_nome_consulta(time_nome)
        data_txt = str(item.get("data", item.get("date", "")) or "").strip()
        data_obj = _parse_data_ptbr_safe(data_txt)
        adversario = str(item.get("adversario", item.get("oponente", item.get("opponent", ""))) or "").strip()
        if not adversario:
            mandante = str(item.get("mandante", item.get("casa", item.get("home_team", ""))) or "").strip()
            visitante = str(item.get("visitante", item.get("fora", item.get("away_team", ""))) or "").strip()
            if _chave_nome_consulta(mandante) == time_chave:
                adversario = visitante
            elif _chave_nome_consulta(visitante) == time_chave:
                adversario = mandante
        em_casa = _normalizar_em_casa(item.get("em_casa", item.get("local", item.get("mando"))))
        if em_casa is None:
            mandante = _chave_nome_consulta(item.get("mandante", item.get("casa", item.get("home_team", ""))))
            visitante = _chave_nome_consulta(item.get("visitante", item.get("fora", item.get("away_team", ""))))
            if mandante and mandante == time_chave:
                em_casa = True
            elif visitante and visitante == time_chave:
                em_casa = False

        gols_time, gols_contra = self._extrair_gols_adversario_json(item, time_chave)
        resultado = self._normalizar_resultado_probabilidade(item.get("resultado", item.get("result", "")))
        if gols_time is not None and gols_contra is not None:
            if gols_time > gols_contra:
                resultado = "vitoria"
            elif gols_time < gols_contra:
                resultado = "derrota"
            else:
                resultado = "empate"
        if not resultado:
            return None, f"Jogo ignorado: faltou placar/resultado em {data_txt or 'data não informada'}."
        if gols_time is None or gols_contra is None:
            return None, f"Jogo ignorado: informe placar do adversário em {data_txt or 'data não informada'}."

        return {
            "data": data_obj or datetime.min,
            "data_txt": data_txt or "—",
            "adversario": adversario or "Adversário não informado",
            "competicao": str(item.get("competicao", item.get("campeonato", "")) or "").strip(),
            "em_casa": em_casa,
            "gols_time": gols_time,
            "gols_adversario": gols_contra,
            "resultado": resultado,
        }, None

    def _normalizar_adversario_externo_probabilidade(self, dados, adversario_padrao: str):
        if isinstance(dados, list):
            dados = {"time": adversario_padrao, "jogos": dados}
        if not isinstance(dados, dict):
            raise ValueError("O JSON deve ser um objeto ou uma lista de jogos.")
        time_nome = str(
            dados.get("time")
            or dados.get("clube")
            or dados.get("nome")
            or dados.get("adversario")
            or adversario_padrao
            or ""
        ).strip()
        if not time_nome:
            raise ValueError("Informe o nome do time adversário no campo 'time'.")
        jogos_raw = None
        for chave in ("jogos", "partidas", "ultimos_jogos", "matches"):
            if isinstance(dados.get(chave), list):
                jogos_raw = dados.get(chave)
                break
        if jogos_raw is None:
            raise ValueError("Informe uma lista de jogos em 'jogos', 'partidas' ou 'ultimos_jogos'.")

        partidas = []
        avisos = []
        for item in jogos_raw:
            partida, aviso = self._normalizar_jogo_adversario_probabilidade(item, time_nome)
            if partida:
                partidas.append(partida)
            elif aviso:
                avisos.append(aviso)
        if not partidas:
            raise ValueError("Nenhum jogo válido foi encontrado. Inclua data, mando/local e placar do adversário.")

        partidas.sort(key=lambda p: p["data"])
        nivel_nome, nivel_fator = self._nivel_adversario_probabilidade(dados)
        tabela = dados.get("tabela") if isinstance(dados.get("tabela"), dict) else {}
        dados_salvos = dados.get("_dados_salvos") if isinstance(dados.get("_dados_salvos"), dict) else None
        return {
            "time": time_nome,
            "nivel": nivel_nome,
            "nivel_fator": nivel_fator,
            "partidas": partidas,
            "resumo": self._resumir_partidas_adversario_probabilidade(partidas),
            "tabela": tabela,
            "avisos": avisos,
            "dados_salvos": dados_salvos,
        }

    def _resumir_partidas_adversario_probabilidade(self, partidas):
        resumo = {
            "jogos": len(partidas),
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_pro": 0,
            "gols_contra": 0,
            "media_gols_pro": 0.0,
            "media_gols_contra": 0.0,
            "aproveitamento": 0.0,
        }
        for partida in partidas:
            if partida["resultado"] == "vitoria":
                resumo["vitorias"] += 1
            elif partida["resultado"] == "derrota":
                resumo["derrotas"] += 1
            else:
                resumo["empates"] += 1
            resumo["gols_pro"] += partida["gols_time"]
            resumo["gols_contra"] += partida["gols_adversario"]
        if resumo["jogos"]:
            resumo["media_gols_pro"] = resumo["gols_pro"] / resumo["jogos"]
            resumo["media_gols_contra"] = resumo["gols_contra"] / resumo["jogos"]
            pontos = resumo["vitorias"] * 3 + resumo["empates"]
            resumo["aproveitamento"] = (pontos / (resumo["jogos"] * 3)) * 100
        return resumo

    def _distribuicao_adversario_para_vasco(self, partidas, pesos=None, suavizacao=0.0):
        dist_adv = self._distribuicao_partidas_probabilidade(
            [{"resultado": p["resultado"]} for p in partidas],
            pesos=pesos,
            suavizacao=suavizacao,
        )
        return {
            "vitoria": dist_adv["derrota"],
            "empate": dist_adv["empate"],
            "derrota": dist_adv["vitoria"],
        }

    def _resumo_tabela_adversario_probabilidade(self, tabela: dict):
        if not isinstance(tabela, dict):
            return None

        def _int(valor):
            try:
                numero = int(valor)
            except (TypeError, ValueError):
                return None
            return numero if numero >= 0 else None

        jogos = _int(tabela.get("jogos", tabela.get("partidas")))
        vitorias = _int(tabela.get("vitorias", tabela.get("vitórias")))
        empates = _int(tabela.get("empates"))
        derrotas = _int(tabela.get("derrotas"))
        gols_pro = _int(tabela.get("gols_pro", tabela.get("gp")))
        gols_contra = _int(tabela.get("gols_contra", tabela.get("gc")))
        if jogos is None and None not in (vitorias, empates, derrotas):
            jogos = vitorias + empates + derrotas
        if None in (jogos, vitorias, empates, derrotas) or jogos <= 0:
            return None
        return {
            "jogos": jogos,
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "gols_pro": gols_pro or 0,
            "gols_contra": gols_contra or 0,
            "media_gols_pro": (gols_pro or 0) / jogos if gols_pro is not None else 0.0,
            "media_gols_contra": (gols_contra or 0) / jogos if gols_contra is not None else 0.0,
            "aproveitamento": ((vitorias * 3 + empates) / (jogos * 3)) * 100,
        }

    def _distribuicao_tabela_adversario_para_vasco(self, resumo_tabela):
        total = resumo_tabela["jogos"]
        dist_adv = {
            "vitoria": resumo_tabela["vitorias"] / total,
            "empate": resumo_tabela["empates"] / total,
            "derrota": resumo_tabela["derrotas"] / total,
        }
        return {
            "vitoria": dist_adv["derrota"],
            "empate": dist_adv["empate"],
            "derrota": dist_adv["vitoria"],
        }

    def _exemplo_json_adversario_probabilidade(self, adversario: str):
        nome = adversario or "Paysandu-PA"
        return json.dumps(
            {
                "time": nome,
                "divisao": "Serie C",
                "tabela": {
                    "competicao": "Campeonato Brasileiro Serie C",
                    "posicao": 1,
                    "jogos": 6,
                    "vitorias": 4,
                    "empates": 2,
                    "derrotas": 0,
                    "gols_pro": 13,
                    "gols_contra": 6,
                },
                "jogos": [
                    {
                        "data": "09/05/2026",
                        "competicao": "Campeonato Brasileiro Serie C",
                        "adversario": "Anapolis-GO",
                        "local": "casa",
                        "placar": {"time": 2, "adversario": 1},
                    },
                    {
                        "data": "06/05/2026",
                        "competicao": "Copa Verde",
                        "adversario": "Aguia de Maraba",
                        "local": "fora",
                        "placar": {"time": 5, "adversario": 1},
                    },
                ],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _modelo_json_adversario_probabilidade(self, adversario: str):
        nome = adversario or "Nome do adversário"
        return json.dumps(
            {
                "time": nome,
                "divisao": "Serie A|Serie B|Serie C|Serie D|Estadual/Regional",
                "tabela": {
                    "competicao": "",
                    "posicao": 0,
                    "jogos": 0,
                    "vitorias": 0,
                    "empates": 0,
                    "derrotas": 0,
                    "gols_pro": 0,
                    "gols_contra": 0,
                },
                "jogos": [
                    {
                        "data": "dd/mm/aaaa",
                        "competicao": "",
                        "adversario": "",
                        "local": "casa|fora",
                        "placar": {
                            "time": 0,
                            "adversario": 0,
                        },
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )

    def _copiar_modelo_json_adversario_probabilidade(self, adversario: str):
        texto = self._modelo_json_adversario_probabilidade(adversario)
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Modelo copiado", "Modelo JSON do adversário copiado para a área de transferência.")
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível copiar o modelo.\n\n{exc}")

    def _prompt_json_adversario_probabilidade(self, adversario: str, futuro: dict):
        adversario = adversario or "adversário"
        jogo = str(futuro.get("jogo", "") or "").strip() or f"Vasco x {adversario}"
        data = str(futuro.get("data", "") or "").strip() or "data não informada"
        hora = str(futuro.get("hora", "") or "").strip()
        campeonato = str(futuro.get("campeonato", "") or "").strip()
        local = str(futuro.get("local", "") or "").strip()
        detalhes = [f"jogo: {jogo}", f"data: {data}"]
        if hora:
            detalhes.append(f"hora: {hora}")
        if campeonato:
            detalhes.append(f"competição: {campeonato}")
        if local:
            detalhes.append(f"local: {local}")

        modelo = self._modelo_json_adversario_probabilidade(adversario)
        return (
            f"Pesquise o momento atual do {adversario} para refinar uma análise estatística do Vasco.\n"
            f"Contexto do jogo futuro: {'; '.join(detalhes)}.\n\n"
            "Preciso que você retorne somente um JSON válido, sem Markdown, sem comentários e sem texto fora do JSON. "
            "Use dados anteriores à data do jogo quando possível. Inclua os últimos 8 a 10 jogos oficiais mais recentes "
            "do adversário, a campanha/tabela atual se existir, gols pró/contra e a divisão ou nível competitivo do time.\n\n"
            "Regras do JSON:\n"
            "- `time`: nome do adversário.\n"
            "- `divisao`: use Serie A, Serie B, Serie C, Serie D ou Estadual/Regional.\n"
            "- `tabela`: campanha atual na competição principal mais relevante.\n"
            "- `jogos`: lista dos últimos jogos, em ordem do mais recente para o mais antigo.\n"
            "- Em cada jogo, `local` deve ser `casa` ou `fora` do ponto de vista do adversário pesquisado.\n"
            "- Em cada `placar`, `time` são os gols do adversário pesquisado e `adversario` são os gols do oponente dele.\n"
            "- Se algum campo não existir em fonte confiável, use string vazia ou 0, mas não invente resultado.\n\n"
            "Formato obrigatório:\n"
            f"{modelo}"
        )

    def _copiar_prompt_json_adversario_probabilidade(self, adversario: str, futuro: dict):
        texto = self._prompt_json_adversario_probabilidade(adversario, futuro)
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Prompt copiado", "Prompt para pedir o JSON do adversário copiado para a área de transferência.")
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível copiar o prompt.\n\n{exc}")

    def _resultado_exibicao_probabilidade(self, resultado: str):
        chave = _chave_nome_consulta(resultado)
        if chave == "vitoria":
            return "Vitória"
        if chave == "derrota":
            return "Derrota"
        return "Empate"

    def _sequencia_probabilidade(self, partidas):
        if not partidas:
            return "—"
        mapa = {"vitoria": "V", "empate": "E", "derrota": "D"}
        return " ".join(mapa.get(p.get("resultado"), "?") for p in partidas[:8])

    def _resumo_vasco_comum_probabilidade(self, resumo):
        if not resumo:
            return None
        return {
            "jogos": resumo.get("jogos", 0),
            "vitorias": resumo.get("vitorias", 0),
            "empates": resumo.get("empates", 0),
            "derrotas": resumo.get("derrotas", 0),
            "gols_pro": resumo.get("gols_vasco", 0),
            "gols_contra": resumo.get("gols_adversario", 0),
            "media_gols_pro": resumo.get("media_gols_vasco", 0.0),
            "media_gols_contra": resumo.get("media_gols_adversario", 0.0),
            "aproveitamento": resumo.get("aproveitamento", 0.0),
        }

    def _resumo_adversario_comum_probabilidade(self, resumo):
        if not resumo:
            return None
        return {
            "jogos": resumo.get("jogos", 0),
            "vitorias": resumo.get("vitorias", 0),
            "empates": resumo.get("empates", 0),
            "derrotas": resumo.get("derrotas", 0),
            "gols_pro": resumo.get("gols_pro", 0),
            "gols_contra": resumo.get("gols_contra", 0),
            "media_gols_pro": resumo.get("media_gols_pro", 0.0),
            "media_gols_contra": resumo.get("media_gols_contra", 0.0),
            "aproveitamento": resumo.get("aproveitamento", 0.0),
        }

    def _formatar_resumo_comum_probabilidade(self, resumo):
        if not resumo or not resumo.get("jogos"):
            return "Sem amostra"
        saldo = resumo["gols_pro"] - resumo["gols_contra"]
        sinal = "+" if saldo > 0 else ""
        return (
            f"{resumo['jogos']} jogos | V/E/D {resumo['vitorias']}/{resumo['empates']}/{resumo['derrotas']} | "
            f"gols {resumo['gols_pro']} x {resumo['gols_contra']} | saldo {sinal}{saldo} | "
            f"aproveitamento {resumo['aproveitamento']:.1f}%"
        )

    def _formatar_partida_vasco_probabilidade(self, partida):
        adversario = partida.get("adversario") or "Adversário"
        gols_vasco = int(partida.get("gols_vasco", 0) or 0)
        gols_adv = int(partida.get("gols_adversario", 0) or 0)
        em_casa = partida.get("em_casa")
        if em_casa is False:
            local = "Fora"
            placar = f"{adversario} {gols_adv} x {gols_vasco} Vasco"
        else:
            local = "Casa" if em_casa is True else "—"
            placar = f"Vasco {gols_vasco} x {gols_adv} {adversario}"
        return (
            partida.get("data_txt", "—"),
            partida.get("competicao") or "—",
            local,
            placar,
            self._resultado_exibicao_probabilidade(partida.get("resultado")),
        )

    def _formatar_partida_adversario_probabilidade(self, partida, time_nome):
        time_nome = time_nome or "Adversário"
        adversario = partida.get("adversario") or "Adversário"
        gols_time = int(partida.get("gols_time", 0) or 0)
        gols_adv = int(partida.get("gols_adversario", 0) or 0)
        em_casa = partida.get("em_casa")
        if em_casa is False:
            local = "Fora"
            placar = f"{adversario} {gols_adv} x {gols_time} {time_nome}"
        else:
            local = "Casa" if em_casa is True else "—"
            placar = f"{time_nome} {gols_time} x {gols_adv} {adversario}"
        return (
            partida.get("data_txt", "—"),
            partida.get("competicao") or "—",
            local,
            placar,
            self._resultado_exibicao_probabilidade(partida.get("resultado")),
        )

    def _render_tabela_jogos_momento_probabilidade(self, container, titulo, partidas, formatter, vazio):
        frame = ttk.Labelframe(container, text=titulo, padding=8)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        cols = ("data", "competicao", "local", "placar", "resultado")
        tv = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        cabecalhos = {
            "data": "Data",
            "competicao": "Competição",
            "local": "Local",
            "placar": "Placar",
            "resultado": "Resultado",
        }
        larguras = {"data": 85, "competicao": 160, "local": 60, "placar": 250, "resultado": 85}
        for col in cols:
            tv.heading(col, text=cabecalhos[col])
            tv.column(col, width=larguras[col], anchor="w" if col in {"competicao", "placar"} else "center")
        tv.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        tv.configure(yscrollcommand=scroll.set)
        for partida in partidas:
            tv.insert("", "end", values=formatter(partida))
        if not partidas:
            tv.insert("", "end", values=("—", "—", "—", vazio, "—"))
        return tv

    def _render_comparativo_probabilidade(self, container, analise, adversario):
        for child in container.winfo_children():
            child.destroy()
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(2, weight=1)

        partidas_vasco = list(analise.get("partidas_recentes", []))
        partidas_adv = list(analise.get("partidas_adversario_recentes", []))
        adversario_externo = analise.get("adversario_externo") or {}
        nome_adv = adversario_externo.get("time") or adversario
        resumo_vasco = self._resumo_vasco_comum_probabilidade(analise.get("resumo_recente"))
        resumo_adv = self._resumo_adversario_comum_probabilidade(analise.get("resumo_adversario"))

        topo = ttk.Frame(container)
        topo.grid(row=0, column=0, columnspan=2, sticky="ew")
        topo.columnconfigure(0, weight=1)
        topo.columnconfigure(1, weight=1)

        card_vasco = ttk.Labelframe(topo, text="Momento do Vasco", padding=8)
        card_vasco.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Label(card_vasco, text=self._formatar_resumo_comum_probabilidade(resumo_vasco), wraplength=420).pack(anchor="w")
        ttk.Label(card_vasco, text=f"Sequência: {self._sequencia_probabilidade(partidas_vasco)}").pack(anchor="w", pady=(3, 0))

        card_adv = ttk.Labelframe(topo, text=f"Momento do {nome_adv}", padding=8)
        card_adv.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        if resumo_adv:
            nivel = adversario_externo.get("nivel", "nível não informado")
            ttk.Label(card_adv, text=self._formatar_resumo_comum_probabilidade(resumo_adv), wraplength=420).pack(anchor="w")
            ttk.Label(card_adv, text=f"Sequência: {self._sequencia_probabilidade(partidas_adv)} | Nível: {nivel}").pack(anchor="w", pady=(3, 0))
        else:
            ttk.Label(
                card_adv,
                text="Importe um JSON do adversário para comparar forma recente, ataque, defesa e sequência.",
                wraplength=420,
            ).pack(anchor="w")

        metricas = ttk.Labelframe(container, text="Comparativo numérico", padding=8)
        metricas.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 8))
        metricas.columnconfigure(0, weight=1)
        cols = ("metrica", "vasco", "adversario")
        tv_metricas = ttk.Treeview(metricas, columns=cols, show="headings", height=7)
        tv_metricas.heading("metrica", text="Métrica")
        tv_metricas.heading("vasco", text="Vasco")
        tv_metricas.heading("adversario", text=nome_adv)
        tv_metricas.column("metrica", width=180, anchor="w")
        tv_metricas.column("vasco", width=180, anchor="center")
        tv_metricas.column("adversario", width=180, anchor="center")
        tv_metricas.pack(fill="x")

        def valor(resumo, chave, tipo="num"):
            if not resumo or not resumo.get("jogos"):
                return "—"
            if tipo == "pct":
                return f"{resumo.get(chave, 0.0):.1f}%"
            if tipo == "media":
                return f"{resumo.get(chave, 0.0):.2f}"
            if tipo == "saldo":
                saldo = resumo["gols_pro"] - resumo["gols_contra"]
                return f"{'+' if saldo > 0 else ''}{saldo}"
            return str(resumo.get(chave, "—"))

        linhas = [
            ("Jogos considerados", valor(resumo_vasco, "jogos"), valor(resumo_adv, "jogos")),
            ("V/E/D", f"{resumo_vasco['vitorias']}/{resumo_vasco['empates']}/{resumo_vasco['derrotas']}" if resumo_vasco else "—", f"{resumo_adv['vitorias']}/{resumo_adv['empates']}/{resumo_adv['derrotas']}" if resumo_adv else "—"),
            ("Aproveitamento", valor(resumo_vasco, "aproveitamento", "pct"), valor(resumo_adv, "aproveitamento", "pct")),
            ("Gols pró", valor(resumo_vasco, "gols_pro"), valor(resumo_adv, "gols_pro")),
            ("Gols sofridos", valor(resumo_vasco, "gols_contra"), valor(resumo_adv, "gols_contra")),
            ("Média gols pró", valor(resumo_vasco, "media_gols_pro", "media"), valor(resumo_adv, "media_gols_pro", "media")),
            ("Média gols sofridos", valor(resumo_vasco, "media_gols_contra", "media"), valor(resumo_adv, "media_gols_contra", "media")),
            ("Saldo", valor(resumo_vasco, "saldo", "saldo"), valor(resumo_adv, "saldo", "saldo")),
        ]
        for linha in linhas:
            tv_metricas.insert("", "end", values=linha)

        listas = ttk.Frame(container)
        listas.grid(row=2, column=0, columnspan=2, sticky="nsew")
        listas.columnconfigure(0, weight=1)
        listas.columnconfigure(1, weight=1)
        listas.rowconfigure(0, weight=1)

        wrap_vasco = ttk.Frame(listas)
        wrap_vasco.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        wrap_vasco.rowconfigure(0, weight=1)
        wrap_vasco.columnconfigure(0, weight=1)
        self._render_tabela_jogos_momento_probabilidade(
            wrap_vasco,
            "Últimos jogos do Vasco usados no momento",
            partidas_vasco,
            self._formatar_partida_vasco_probabilidade,
            "Sem jogos recentes do Vasco",
        )

        wrap_adv = ttk.Frame(listas)
        wrap_adv.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        wrap_adv.rowconfigure(0, weight=1)
        wrap_adv.columnconfigure(0, weight=1)
        self._render_tabela_jogos_momento_probabilidade(
            wrap_adv,
            f"Últimos jogos do {nome_adv}",
            partidas_adv,
            lambda partida: self._formatar_partida_adversario_probabilidade(partida, nome_adv),
            "Importe JSON do adversário para preencher",
        )

    def _abrir_modal_probabilidade_futuro(self, adversario_externo=None, carregar_salvo=True):
        selecionado = self._dados_futuro_selecionado()
        if not selecionado:
            return
        _futuros, idx, futuro = self._localizar_indice_futuro(selecionado)
        if idx is None or futuro is None:
            messagebox.showwarning("Não encontrado", "Não foi possível localizar o jogo futuro para análise.")
            return

        futuro = _normalizar_futuro_item(futuro) or futuro
        adversario_modal = self._resolver_nome_clube_canonico(
            _extrair_adversario_de_jogo(str(futuro.get("jogo", "") or "")).replace("Vasco", "").strip()
        )
        dados_salvos_aplicados = False
        if adversario_externo is None and carregar_salvo:
            dados_salvos = carregar_dados_externos_adversario_probabilidade(adversario_modal)
            if dados_salvos:
                try:
                    adversario_externo = self._normalizar_adversario_externo_probabilidade(dados_salvos, adversario_modal)
                    dados_salvos_aplicados = True
                except Exception:
                    adversario_externo = None

        analise = self._calcular_probabilidade_futuro(futuro, adversario_externo=adversario_externo)
        if analise.get("erro"):
            messagebox.showwarning("Probabilidade indisponível", analise["erro"])
            return

        adversario = analise.get("adversario") or "Adversário"
        probs = analise["probabilidades"]
        top = tk.Toplevel(self.root)
        top.title(f"Probabilidade - Vasco x {adversario}")
        top.transient(self.root)
        top.grab_set()
        top.resizable(True, True)
        top.minsize(980, 720)

        container = ttk.Frame(top, padding=14)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        jogo_txt = str(futuro.get("jogo", "") or "").strip()
        data_txt = str(futuro.get("data", "") or "").strip()
        hora_txt = str(futuro.get("hora", "") or "").strip()
        comp_txt = str(futuro.get("campeonato", "") or "").strip()
        detalhe = data_txt
        if hora_txt:
            detalhe = f"{detalhe} às {hora_txt}" if detalhe else hora_txt
        if comp_txt:
            detalhe = f"{detalhe} | {comp_txt}" if detalhe else comp_txt
        ttk.Label(container, text=jogo_txt or f"Vasco x {adversario}", font=("TkDefaultFont", 14, "bold")).grid(
            row=0,
            column=0,
            sticky="w",
        )
        detalhe_wrap = ttk.Frame(container)
        detalhe_wrap.grid(row=1, column=0, sticky="ew", pady=(2, 10))
        detalhe_wrap.columnconfigure(0, weight=1)
        ttk.Label(detalhe_wrap, text=detalhe or "Jogo futuro").grid(row=0, column=0, sticky="w")
        if adversario_externo:
            salvo = adversario_externo.get("dados_salvos") if isinstance(adversario_externo, dict) else None
            origem_dados = "dados salvos" if dados_salvos_aplicados or salvo else "JSON colado"
            atualizado_em = f" | atualizado em {salvo.get('atualizado_em')}" if isinstance(salvo, dict) and salvo.get("atualizado_em") else ""
            ext_txt = (
                f"Refinado com {origem_dados}: {adversario_externo.get('time', adversario)} | "
                f"{adversario_externo.get('nivel', 'nível não informado')} | "
                f"{len(adversario_externo.get('partidas', []))} jogos importados"
                f"{atualizado_em}"
            )
            ttk.Label(detalhe_wrap, text=ext_txt).grid(row=0, column=1, sticky="e", padx=(12, 0))

        probs_frame = ttk.Labelframe(container, text="Probabilidades estimadas", padding=10)
        probs_frame.grid(row=2, column=0, sticky="ew")
        probs_frame.columnconfigure(1, weight=1)
        ordem = [
            ("vitoria", "Vitória do Vasco"),
            ("empate", "Empate"),
            ("derrota", "Derrota do Vasco"),
        ]
        for row, (chave, label) in enumerate(ordem):
            valor = probs.get(chave, 0.0)
            ttk.Label(probs_frame, text=label, width=20).grid(row=row, column=0, sticky="w", pady=3)
            barra = ttk.Progressbar(probs_frame, maximum=100, value=valor * 100)
            barra.grid(row=row, column=1, sticky="ew", padx=(8, 8), pady=3)
            ttk.Label(probs_frame, text=self._formatar_percentual_probabilidade(valor), width=8, anchor="e").grid(
                row=row,
                column=2,
                sticky="e",
                pady=3,
            )

        resumo = ttk.Frame(container)
        resumo.grid(row=3, column=0, sticky="ew", pady=(10, 8))
        resumo.columnconfigure(0, weight=1)
        resumo.columnconfigure(1, weight=1)
        resumo.columnconfigure(2, weight=1)

        def _card_resumo(col, titulo, resumo_partidas):
            texto = "Sem amostra"
            if resumo_partidas and resumo_partidas.get("jogos", 0):
                texto = (
                    f"{resumo_partidas['jogos']} jogos | V/E/D "
                    f"{self._formatar_ved_probabilidade(resumo_partidas)} | "
                    f"gols {resumo_partidas['gols_vasco']} x {resumo_partidas['gols_adversario']}"
                )
            frame = ttk.Labelframe(resumo, text=titulo, padding=8)
            frame.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0))
            ttk.Label(frame, text=texto, wraplength=240).pack(anchor="w")

        _card_resumo(0, "Momento recente", analise["resumo_recente"])
        _card_resumo(1, f"Retrospecto vs {adversario}", analise["resumo_h2h"])
        _card_resumo(2, "Mando", analise["resumo_mando"])
        if analise.get("resumo_adversario"):
            resumo_adv = analise["resumo_adversario"]
            frame_adv = ttk.Labelframe(resumo, text="Momento do adversário importado", padding=8)
            frame_adv.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 0))
            texto_adv = (
                f"{resumo_adv['jogos']} jogos | V/E/D do adversário "
                f"{resumo_adv['vitorias']}/{resumo_adv['empates']}/{resumo_adv['derrotas']} | "
                f"gols {resumo_adv['gols_pro']} x {resumo_adv['gols_contra']} | "
                f"aproveitamento {resumo_adv['aproveitamento']:.1f}%"
            )
            ttk.Label(frame_adv, text=texto_adv, wraplength=720).pack(anchor="w")

        abas_detalhe = ttk.Notebook(container)
        abas_detalhe.grid(row=4, column=0, sticky="nsew")

        tab_fatores = ttk.Frame(abas_detalhe, padding=8)
        tab_comparativo = ttk.Frame(abas_detalhe, padding=8)
        abas_detalhe.add(tab_fatores, text="Fatores do modelo")
        abas_detalhe.add(tab_comparativo, text="Comparativo de momento")

        tab_fatores.rowconfigure(0, weight=1)
        tab_fatores.columnconfigure(0, weight=1)
        cols = ("fator", "peso", "jogos", "ved", "prob", "gols")
        tv = ttk.Treeview(tab_fatores, columns=cols, show="headings", height=8)
        cabecalhos = {
            "fator": "Fator",
            "peso": "Peso",
            "jogos": "Jogos",
            "ved": "V/E/D",
            "prob": "Prob. V/E/D",
            "gols": "Médias gols",
        }
        larguras = {"fator": 220, "peso": 70, "jogos": 70, "ved": 90, "prob": 160, "gols": 130}
        for col in cols:
            tv.heading(col, text=cabecalhos[col])
            tv.column(col, width=larguras[col], anchor="w" if col == "fator" else "center")
        tv.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(tab_fatores, orient="vertical", command=tv.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        tv.configure(yscrollcommand=scroll.set)

        for componente in analise["componentes"]:
            resumo_comp = componente.get("resumo")
            dist = componente["distribuicao"]
            if resumo_comp:
                jogos_txt = str(resumo_comp["jogos"])
                if componente.get("resumo_tipo") == "adversario":
                    ved_txt = f"{resumo_comp['vitorias']}/{resumo_comp['empates']}/{resumo_comp['derrotas']}"
                    gols_txt = f"{resumo_comp['media_gols_pro']:.2f} x {resumo_comp['media_gols_contra']:.2f}"
                else:
                    ved_txt = self._formatar_ved_probabilidade(resumo_comp)
                    gols_txt = f"{resumo_comp['media_gols_vasco']:.2f} x {resumo_comp['media_gols_adversario']:.2f}"
            else:
                jogos_txt = "—"
                ved_txt = "—"
                gols = analise.get("gols_esperados") or {}
                gols_txt = f"{gols.get('gols_vasco', 0):.2f} x {gols.get('gols_adversario', 0):.2f}"
            prob_txt = (
                f"{self._formatar_percentual_probabilidade(dist['vitoria'])} / "
                f"{self._formatar_percentual_probabilidade(dist['empate'])} / "
                f"{self._formatar_percentual_probabilidade(dist['derrota'])}"
            )
            tv.insert(
                "",
                "end",
                values=(
                    componente["nome"],
                    f"{componente['peso']:.2f}",
                    jogos_txt,
                    ved_txt,
                    prob_txt,
                    gols_txt,
                ),
            )

        self._render_comparativo_probabilidade(tab_comparativo, analise, adversario)

        rodape = ttk.Frame(container)
        rodape.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        rodape.columnconfigure(0, weight=1)
        gols_esperados = analise.get("gols_esperados")
        if gols_esperados:
            gols_txt = (
                f"Gols estimados: Vasco {gols_esperados['gols_vasco']:.2f} x "
                f"{gols_esperados['gols_adversario']:.2f} {adversario}."
            )
        else:
            gols_txt = "Gols estimados indisponíveis."
        nota = (
            f"{analise['confianca']} ({analise['indice_base'] * 100:.0f}%). {gols_txt} "
            "Modelo heurístico, sem odds externas; use como leitura estatística e calibre com jogos antigos antes de confiar."
        )
        ttk.Label(rodape, text=nota, wraplength=720, justify="left").grid(row=0, column=0, sticky="w")

        def importar_json_adversario():
            popup = tk.Toplevel(top)
            popup.title("Colar JSON do adversário")
            popup.transient(top)
            popup.grab_set()
            popup.resizable(True, True)
            popup.minsize(720, 520)

            frame_json = ttk.Frame(popup, padding=12)
            frame_json.pack(fill="both", expand=True)
            frame_json.rowconfigure(1, weight=1)
            frame_json.columnconfigure(0, weight=1)

            ttk.Label(
                frame_json,
                text=(
                    f"Cole o JSON com o momento atual do {adversario}. "
                    "Ao aplicar, os dados salvos desse adversário serão substituídos."
                ),
            ).grid(row=0, column=0, sticky="w", pady=(0, 8))

            text_wrap = ttk.Frame(frame_json)
            text_wrap.grid(row=1, column=0, sticky="nsew")
            text_wrap.rowconfigure(0, weight=1)
            text_wrap.columnconfigure(0, weight=1)
            json_text = tk.Text(
                text_wrap,
                wrap="none",
                bg=self.colors["entry_bg"],
                fg=self.colors["entry_fg"],
                insertbackground=self.colors["accent"],
                undo=True,
            )
            json_text.grid(row=0, column=0, sticky="nsew")
            sy = ttk.Scrollbar(text_wrap, orient="vertical", command=json_text.yview)
            sy.grid(row=0, column=1, sticky="ns")
            sx = ttk.Scrollbar(text_wrap, orient="horizontal", command=json_text.xview)
            sx.grid(row=1, column=0, sticky="ew")
            json_text.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

            botoes_json = ttk.Frame(frame_json)
            botoes_json.grid(row=2, column=0, sticky="ew", pady=(10, 0))
            botoes_json.columnconfigure(0, weight=1)

            def colar_clipboard():
                try:
                    texto_clip = self.root.clipboard_get()
                except Exception:
                    texto_clip = ""
                if texto_clip:
                    json_text.insert("insert", texto_clip)

            def inserir_modelo():
                if json_text.get("1.0", "end").strip():
                    if not messagebox.askyesno(
                        "Substituir conteúdo",
                        "Substituir o JSON atual pelo modelo?",
                        parent=popup,
                    ):
                        return
                    json_text.delete("1.0", "end")
                json_text.insert("1.0", self._modelo_json_adversario_probabilidade(adversario))

            def aplicar_json():
                raw = json_text.get("1.0", "end").strip()
                if not raw:
                    messagebox.showwarning("JSON obrigatório", "Cole o JSON do adversário antes de aplicar.", parent=popup)
                    return
                try:
                    dados = json.loads(raw)
                    externo = self._normalizar_adversario_externo_probabilidade(dados, adversario)
                    salvar_dados_externos_adversario_probabilidade(adversario, dados)
                    dados_salvos = carregar_dados_externos_adversario_probabilidade(adversario)
                    if dados_salvos:
                        externo = self._normalizar_adversario_externo_probabilidade(dados_salvos, adversario)
                except Exception as exc:
                    messagebox.showerror("Erro ao importar JSON", f"Não foi possível usar esse JSON.\n\n{exc}", parent=popup)
                    return
                popup.destroy()
                top.destroy()
                self._abrir_modal_probabilidade_futuro(adversario_externo=externo, carregar_salvo=False)

            ttk.Button(botoes_json, text="Colar", command=colar_clipboard).pack(side="left")
            ttk.Button(botoes_json, text="Inserir modelo", command=inserir_modelo).pack(side="left", padx=(8, 0))
            ttk.Button(botoes_json, text="Cancelar", command=popup.destroy).pack(side="right")
            ttk.Button(botoes_json, text="Aplicar JSON", command=aplicar_json).pack(side="right", padx=(0, 8))

            popup.protocol("WM_DELETE_WINDOW", popup.destroy)
            popup.update_idletasks()
            self._centralizar_modal_no_app(popup)
            popup.lift(top)
            popup.focus_force()
            json_text.focus_set()

        botoes_modal = ttk.Frame(rodape)
        botoes_modal.grid(row=0, column=1, sticky="e", padx=(10, 0))
        ttk.Button(
            botoes_modal,
            text="Reimportar JSON do adversário" if adversario_externo else "Colar JSON do adversário",
            command=importar_json_adversario,
        ).pack(side="right")
        ttk.Button(
            botoes_modal,
            text="Copiar prompt IA",
            command=lambda: self._copiar_prompt_json_adversario_probabilidade(adversario, futuro),
        ).pack(side="right", padx=(0, 8))
        ttk.Button(
            botoes_modal,
            text="Copiar modelo JSON",
            command=lambda: self._copiar_modelo_json_adversario_probabilidade(adversario),
        ).pack(side="right", padx=(0, 8))
        if adversario_externo:
            ttk.Button(
                botoes_modal,
                text="Ignorar refinamento",
                command=lambda: (top.destroy(), self._abrir_modal_probabilidade_futuro(carregar_salvo=False)),
            ).pack(side="right", padx=(0, 8))
        ttk.Button(botoes_modal, text="Fechar", command=top.destroy).pack(side="right", padx=(0, 8))

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        self._centralizar_modal_no_app(top)
        top.lift(self.root)
        top.focus_force()

    def _abrir_menu_contexto_futuros(self, event):
        iid = self.tv_futuros.identify_row(event.y)
        if not iid:
            return
        self.tv_futuros.selection_set(iid)
        self.tv_futuros.focus(iid)

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Ver probabilidade", command=self._abrir_modal_probabilidade_futuro)
        menu.add_separator()
        menu.add_command(label="Editar jogo futuro", command=self._editar_jogo_futuro_selecionado)
        menu.add_command(label="Excluir jogo futuro", command=self._excluir_jogo_futuro_selecionado)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _editar_jogo_futuro_selecionado(self):
        selecionado = self._dados_futuro_selecionado()
        if not selecionado:
            return
        futuros, idx, atual = self._localizar_indice_futuro(selecionado)
        if idx is None or atual is None:
            messagebox.showwarning("Não encontrado", "Não foi possível localizar o jogo futuro para edição.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Editar jogo futuro")
        popup.transient(self.root)
        popup.grab_set()
        popup.resizable(False, False)

        frame = ttk.Frame(popup, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        data_var = tk.StringVar(value=atual.get("data", ""))
        hora_atual = str(atual.get("hora", "") or "").strip()
        hora_h_var = tk.StringVar(value=hora_atual[:2] if len(hora_atual) >= 2 else "")
        hora_m_var = tk.StringVar(value=hora_atual[3:5] if len(hora_atual) >= 5 and ":" in hora_atual else "")
        adversario_var = tk.StringVar(value=_extrair_adversario_de_jogo(atual.get("jogo", "")).replace("Vasco", "").strip())
        campeonato_var = tk.StringVar(value=atual.get("campeonato", ""))
        mando_var = tk.StringVar(value="casa" if atual.get("em_casa") is not False else "fora")
        local_var = tk.StringVar(value=atual.get("local", ""))

        def _valores_estadio_modal(adversario: str) -> list[str]:
            base = list(self.listas.get("estadios", []))
            relacionados = carregar_estadios_adversario(adversario or "")
            return self._ordenar_opcoes_estadios(base, relacionados)

        def _formatar_horario_var(var: tk.StringVar, proximo_widget=None):
            atual_txt = var.get()
            formatado = re.sub(r"\D", "", atual_txt)[:2]
            if atual_txt != formatado:
                var.set(formatado)
                return
            if len(formatado) == 2 and proximo_widget is not None:
                proximo_widget.focus_set()

        def _aplicar_estadio_modal(*_args):
            adversario = self._resolver_nome_clube_canonico(adversario_var.get().strip())
            valores = _valores_estadio_modal(adversario)
            local_entry["values"] = valores
            sugerido = self._sugerir_estadio_por_adversario(adversario, mando_var.get())
            local_var.set(sugerido or "")

        ttk.Label(frame, text="Adversário:").grid(row=0, column=0, sticky="w", pady=4)
        opcoes_adversario = sorted({
            *self.listas.get("clubes_adversarios", []),
            *[
                str(j.get("adversario", "")).strip()
                for j in carregar_dados_jogos()
                if str(j.get("adversario", "")).strip()
            ],
        }, key=lambda s: s.casefold())
        adversario_entry = ttk.Combobox(frame, textvariable=adversario_var, values=opcoes_adversario)
        adversario_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=4, padx=(6, 0))

        ttk.Label(frame, text="Campeonato:").grid(row=1, column=0, sticky="w", pady=4)
        opcoes_campeonato = sorted({
            *self.listas.get("competicoes", []),
            *[
                str(j.get("competicao", "")).strip()
                for j in carregar_dados_jogos()
                if str(j.get("competicao", "")).strip()
            ],
        }, key=lambda s: s.casefold())
        ttk.Combobox(frame, textvariable=campeonato_var, values=opcoes_campeonato).grid(
            row=1, column=1, columnspan=3, sticky="ew", pady=4, padx=(6, 0)
        )

        ttk.Label(frame, text="Data:").grid(row=2, column=0, sticky="w", pady=4)
        data_wrap = ttk.Frame(frame)
        data_wrap.grid(row=2, column=1, sticky="w", pady=4, padx=(6, 0))
        ttk.Entry(data_wrap, width=14, textvariable=data_var).pack(side="left")
        ttk.Button(data_wrap, text="Calendário", command=lambda: self._abrir_calendario_popup(data_var)).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Hora:").grid(row=2, column=2, sticky="w", pady=4, padx=(10, 0))
        hora_wrap = ttk.Frame(frame)
        hora_wrap.grid(row=2, column=3, sticky="w", pady=4, padx=(6, 0))
        hora_h_entry = ttk.Entry(hora_wrap, width=3, textvariable=hora_h_var, justify="center")
        hora_h_entry.pack(side="left")
        ttk.Label(hora_wrap, text=":").pack(side="left", padx=2)
        hora_m_entry = ttk.Entry(hora_wrap, width=3, textvariable=hora_m_var, justify="center")
        hora_m_entry.pack(side="left")
        hora_h_var.trace_add("write", lambda *_: _formatar_horario_var(hora_h_var, hora_m_entry))
        hora_m_var.trace_add("write", lambda *_: _formatar_horario_var(hora_m_var))

        mando_wrap = ttk.Frame(frame)
        mando_wrap.grid(row=3, column=0, columnspan=4, sticky="w", pady=4)
        ttk.Label(mando_wrap, text="Mando:").pack(side="left")
        ttk.Radiobutton(mando_wrap, text="Casa", variable=mando_var, value="casa").pack(side="left", padx=(8, 6))
        ttk.Radiobutton(mando_wrap, text="Fora", variable=mando_var, value="fora").pack(side="left")

        ttk.Label(frame, text="Local:").grid(row=4, column=0, sticky="w", pady=4)
        local_entry = ttk.Combobox(frame, textvariable=local_var, values=_valores_estadio_modal(adversario_var.get().strip()))
        local_entry.grid(row=4, column=1, columnspan=3, sticky="ew", pady=4, padx=(6, 0))

        adversario_var.trace_add("write", _aplicar_estadio_modal)
        mando_var.trace_add("write", _aplicar_estadio_modal)
        _aplicar_estadio_modal()

        botoes = ttk.Frame(frame)
        botoes.grid(row=5, column=0, columnspan=4, sticky="e", pady=(10, 0))

        def salvar():
            adversario = self._resolver_nome_clube_canonico(adversario_var.get().strip())
            data_txt = data_var.get().strip()
            hora = ""
            if hora_h_var.get().strip() or hora_m_var.get().strip():
                hora = f"{hora_h_var.get().strip()}:{hora_m_var.get().strip()}"
            item = {
                "adversario": adversario,
                "data": data_txt,
                "em_casa": mando_var.get() != "fora",
                "campeonato": campeonato_var.get().strip(),
                "hora": hora,
                "local": local_var.get().strip(),
            }
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                messagebox.showerror("Erro", "Preencha pelo menos os campos Adversário e Data.", parent=popup)
                return
            if not _parse_data_ptbr_safe(normalizado["data"]):
                messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.", parent=popup)
                return
            if hora and not re.match(r"^\d{2}:\d{2}$", hora):
                messagebox.showerror("Erro", "Informe a hora no formato HH:MM.", parent=popup)
                return
            if hora:
                horas, minutos = [int(parte) for parte in hora.split(":", 1)]
                if horas > 23 or minutos > 59:
                    messagebox.showerror("Erro", "Informe um horário válido entre 00:00 e 23:59.", parent=popup)
                    return
            futuros[idx] = normalizado
            salvar_lista_futuros(futuros)
            adversario = self._registrar_clube_adversario(adversario)
            adversario_var.set(adversario)
            salvar_listas(self.listas)
            self._render_lista_futuros()
            popup.destroy()

        ttk.Button(botoes, text="Cancelar", command=popup.destroy).pack(side="right")
        ttk.Button(botoes, text="Salvar", command=salvar).pack(side="right", padx=(0, 8))
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        popup.update_idletasks()
        try:
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()
            win_w = popup.winfo_width()
            win_h = popup.winfo_height()
            pos_x = root_x + (root_w - win_w) // 2
            pos_y = root_y + (root_h - win_h) // 2
            popup.geometry(f"+{pos_x}+{pos_y}")
        except Exception:
            pass
        popup.lift(self.root)
        popup.focus_force()
        adversario_entry.focus_set()

    def _excluir_jogo_futuro_selecionado(self):
        selecionado = self._dados_futuro_selecionado()
        if not selecionado:
            return
        data_txt = selecionado["data"]
        jogo_txt = selecionado["jogo"]
        desc = f"{data_txt} | {jogo_txt}"
        if not messagebox.askyesno("Excluir jogo futuro", f"Deseja excluir este jogo futuro?\n\n{desc}"):
            return

        futuros, idx, _ = self._localizar_indice_futuro(selecionado)
        if idx is None:
            messagebox.showwarning("Não encontrado", "Não foi possível localizar o jogo futuro para exclusão.")
            return

        novos = []
        removido = False
        for pos, item in enumerate(futuros):
            if pos == idx and not removido:
                removido = True
                continue
            novos.append(item)

        salvar_lista_futuros(novos)
        self._render_lista_futuros()

    def _importar_futuro_para_registro(self, _event=None):
        sel = self.tv_futuros.selection()
        if not sel:
            return
        values = self.tv_futuros.item(sel[0], "values")
        if len(values) < 6:
            return
        data_txt, hora_txt, jogo_txt, local_txt, local_nome_txt, campeonato_txt = values
        adversario = _extrair_adversario_de_jogo(jogo_txt).replace("Vasco", "").strip()

        if data_txt:
            self.data_var.set(data_txt)
        if adversario:
            match = next(
                (c for c in self.listas.get("clubes_adversarios", []) if c.casefold() == adversario.casefold()),
                None
            )
            valor = match or adversario
            self.adversario_var.set(valor)
            self.adversario_entry.set(valor)
        if campeonato_txt and campeonato_txt != "-":
            self.competicao_var.set(campeonato_txt)
        local_norm = local_txt.strip().lower()
        if local_norm in ("sim", "s", "casa"):
            self.local_var.set("casa")
        elif local_norm in ("nao", "não", "n", "fora"):
            self.local_var.set("fora")
        if hasattr(self, "horario_hora_var") and hasattr(self, "horario_minuto_var"):
            hora_normalizada = "" if str(hora_txt).strip() == "-" else str(hora_txt).strip()
            self.horario_hora_var.set(hora_normalizada[:2] if len(hora_normalizada) >= 2 else "")
            self.horario_minuto_var.set(hora_normalizada[3:5] if len(hora_normalizada) >= 5 and ":" in hora_normalizada else "")
        if hasattr(self, "estadio_var"):
            local_nome_normalizado = "" if str(local_nome_txt).strip() == "-" else str(local_nome_txt).strip()
            if local_nome_normalizado:
                self.estadio_var.set(local_nome_normalizado)
            else:
                self._preencher_estadio_por_adversario(adversario, self.local_var.get())

        self.notebook.select(self.frame_registro)

    # --------------------- Elenco Atual ---------------------
    def _criar_aba_elenco_atual(self, frame):
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3, minsize=620)
        frame.rowconfigure(2, weight=0)
        frame.rowconfigure(3, weight=1)

        ttk.Label(
            frame,
            text="Cadastre os jogadores que estão no Vasco atualmente."
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        entrada_wrap = ttk.Frame(frame)
        entrada_wrap.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        entrada_wrap.columnconfigure(3, weight=1)
        entrada_wrap.columnconfigure(9, weight=1)

        self.elenco_nome_var = tk.StringVar()
        self.elenco_posicao_var = tk.StringVar(value=ELENCO_POSICAO_PLACEHOLDER)
        self.elenco_condicao_var = tk.StringVar(value=ELENCO_CONDICAO_PLACEHOLDER)
        self.elenco_modo_var = tk.StringVar(value="")
        self.elenco_botao_var = tk.StringVar(value="Adicionar")
        self.elenco_resumo_var = tk.StringVar(value="")
        self.elenco_capitao_var = tk.BooleanVar(value=False)
        self._elenco_edit_nome_cf = None
        self._elenco_sort_col = None
        self._elenco_sort_reverse = False

        ttk.Label(entrada_wrap, text="Posição:").grid(row=0, column=0, sticky="w")
        self.elenco_posicao_entry = ttk.Combobox(
            entrada_wrap,
            textvariable=self.elenco_posicao_var,
            values=[ELENCO_POSICAO_PLACEHOLDER] + POSICOES_ELENCO,
            state="readonly",
            width=18
        )
        self.elenco_posicao_entry.grid(row=0, column=1, sticky="w", padx=(6, 10))

        ttk.Label(entrada_wrap, text="Jogador:").grid(row=0, column=2, sticky="w")
        self.elenco_nome_entry = ttk.Entry(entrada_wrap, textvariable=self.elenco_nome_var)
        self.elenco_nome_entry.grid(row=0, column=3, sticky="ew", padx=(6, 10))
        self.elenco_nome_entry.bind("<Return>", self._adicionar_jogador_elenco)
        self._forcar_cursor_visivel(self.elenco_nome_entry)

        ttk.Label(entrada_wrap, text="Condição:").grid(row=0, column=4, sticky="w")
        self.elenco_condicao_entry = ttk.Combobox(
            entrada_wrap,
            textvariable=self.elenco_condicao_var,
            values=[ELENCO_CONDICAO_PLACEHOLDER] + CONDICOES_ELENCO,
            state="readonly",
            width=16
        )
        self.elenco_condicao_entry.grid(row=0, column=5, sticky="w", padx=(6, 10))

        ttk.Checkbutton(
            entrada_wrap,
            text="Capitão atual",
            variable=self.elenco_capitao_var,
        ).grid(row=0, column=6, sticky="w", padx=(0, 10))

        ttk.Button(
            entrada_wrap, textvariable=self.elenco_botao_var, command=self._adicionar_jogador_elenco
        ).grid(row=0, column=7)

        self.elenco_tecnico_var = tk.StringVar(
            value=self.elenco_atual.get("tecnico", "") or self.listas.get("tecnico_atual", "Fernando Diniz")
        )
        ttk.Label(entrada_wrap, text="Técnico:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.elenco_tecnico_entry = ttk.Combobox(
            entrada_wrap,
            textvariable=self.elenco_tecnico_var,
            width=24
        )
        self.elenco_tecnico_entry["values"] = self.listas.get("tecnicos", [])
        self.elenco_tecnico_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=(6, 10), pady=(8, 0))
        self.elenco_tecnico_entry.bind("<Return>", self._salvar_tecnico_elenco_atual)
        self.elenco_tecnico_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "tecnicos"))
        self._forcar_cursor_visivel(self.elenco_tecnico_entry)
        ttk.Button(
            entrada_wrap, text="Salvar Técnico", command=self._salvar_tecnico_elenco_atual
        ).grid(row=1, column=4, sticky="w", pady=(8, 0))

        ttk.Label(frame, textvariable=self.elenco_resumo_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        list_wrap = ttk.Frame(frame)
        list_wrap.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        list_wrap.rowconfigure(0, weight=1)
        list_wrap.columnconfigure(0, weight=1)

        cols = ("posicao", "jogador", "condicao", "capitao")
        self.tv_elenco_atual = ttk.Treeview(
            list_wrap,
            columns=cols,
            show="headings",
            height=14,
            selectmode="extended",
        )
        self.tv_elenco_atual["displaycolumns"] = ("posicao", "jogador", "condicao")
        self.tv_elenco_atual.heading("posicao", text="Posição", command=lambda: self._toggle_ordenacao_elenco_atual("posicao"))
        self.tv_elenco_atual.heading("jogador", text="Jogador", command=lambda: self._toggle_ordenacao_elenco_atual("jogador"))
        self.tv_elenco_atual.heading("condicao", text="Condição", command=self._reset_ordenacao_elenco_atual)
        self.tv_elenco_atual.column("posicao", width=180, anchor="w")
        self.tv_elenco_atual.column("jogador", width=340, anchor="w")
        self.tv_elenco_atual.column("condicao", width=150, anchor="center")
        self.tv_elenco_atual.column("capitao", width=1, stretch=False)
        self.tv_elenco_atual.tag_configure("status_titulares", background="#dff5e6", foreground="#173a23")
        self.tv_elenco_atual.tag_configure("status_reservas", background="#fff4cf", foreground="#4a3a06")
        self.tv_elenco_atual.tag_configure("status_nao_relacionados", background="#ffe3c2", foreground="#4f2a09")
        self.tv_elenco_atual.tag_configure("status_lesionados", background="#ffd6d6", foreground="#5a1414")
        self.tv_elenco_atual.tag_configure("status_suspensos", background="#ffe9bf", foreground="#5c3b00")
        self.tv_elenco_atual.tag_configure("status_servindo_selecao", background="#d9ecff", foreground="#0f3d63")
        self.tv_elenco_atual.tag_configure("status_emprestados", background="#e8ebf4", foreground="#1f2f57")
        self.tv_elenco_atual.tag_configure("status_sem_lista", background="#e6e7eb", foreground="#2f3136")
        self.tv_elenco_atual.grid(row=0, column=0, sticky="nsew")
        self.tv_elenco_atual.bind("<Delete>", self._remover_jogador_elenco)
        self.tv_elenco_atual.bind("<Double-1>", self._iniciar_edicao_jogador_elenco)
        self.tv_elenco_atual.bind("<Button-3>", self._abrir_menu_contexto_elenco_atual)
        self.tv_elenco_atual.bind("<Control-Button-1>", self._abrir_menu_contexto_elenco_atual)

        sy = ttk.Scrollbar(list_wrap, orient="vertical", command=self.tv_elenco_atual.yview)
        sy.grid(row=0, column=1, sticky="ns")
        self.tv_elenco_atual.configure(yscrollcommand=sy.set)

        campinho_wrap = ttk.Labelframe(frame, text="Campinho (ordenação dos titulares)", padding=8)
        campinho_wrap.grid(row=3, column=1, sticky="nsew", padx=(6, 0))
        campinho_wrap.columnconfigure(0, weight=1)
        campinho_wrap.rowconfigure(0, weight=1)
        self.canvas_campinho_elenco = tk.Canvas(
            campinho_wrap,
            background="#0f6a35",
            highlightthickness=1,
            highlightbackground="#1a1a1a",
        )
        self.canvas_campinho_elenco.grid(row=0, column=0, sticky="nsew")
        self.canvas_campinho_elenco.bind("<Configure>", lambda _e: self._render_campinho_elenco())
        self.canvas_campinho_elenco.bind("<ButtonPress-1>", self._elenco_campinho_drag_start)
        self.canvas_campinho_elenco.bind("<ButtonRelease-1>", self._elenco_campinho_drag_end)
        self.canvas_campinho_elenco.bind("<Button-3>", self._abrir_menu_contexto_campinho_elenco)
        self.canvas_campinho_elenco.bind("<Control-Button-1>", self._abrir_menu_contexto_campinho_elenco)

        botoes = ttk.Frame(frame)
        botoes.grid(row=4, column=0, columnspan=2, sticky="e", pady=(8, 0))
        ttk.Label(botoes, textvariable=self.elenco_modo_var, foreground=self.colors["accent"]).pack(side="left", padx=(0, 10))
        self.btn_cancelar_edicao_elenco = ttk.Button(
            botoes, text="Cancelar Edição", command=self._cancelar_edicao_jogador_elenco
        )
        self.btn_cancelar_edicao_elenco.pack(side="left", padx=(0, 8))
        self.btn_cancelar_edicao_elenco.state(["disabled"])
        ttk.Button(
            botoes, text="Remover Selecionado", command=self._remover_jogador_elenco
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            botoes, text="Limpar Lista", command=self._limpar_elenco_atual
        ).pack(side="left")

        self._render_elenco_atual()

    def _render_elenco_atual(self):
        if not hasattr(self, "tv_elenco_atual"):
            return
        for iid in self.tv_elenco_atual.get_children():
            self.tv_elenco_atual.delete(iid)
        jogadores = list(self.elenco_atual.get("jogadores", []))
        jogadores = self._ordenar_jogadores_elenco_para_exibicao(jogadores)
        cont = {
            "Titular": 0,
            "Reserva": 0,
            "Não Relacionado": 0,
            "Lesionado": 0,
            "Suspenso": 0,
            "Servindo a seleção": 0,
            "Emprestado": 0,
        }
        for jogador in jogadores:
            condicao = _normalizar_condicao_elenco(jogador.get("condicao"))
            cont[condicao] = cont.get(condicao, 0) + 1
            if condicao == "Titular":
                tag = "status_titulares"
            elif condicao == "Reserva":
                tag = "status_reservas"
            elif condicao == "Não Relacionado":
                tag = "status_nao_relacionados"
            elif condicao == "Lesionado":
                tag = "status_lesionados"
            elif condicao == "Suspenso":
                tag = "status_suspensos"
            elif condicao == "Servindo a seleção":
                tag = "status_servindo_selecao"
            elif condicao == "Emprestado":
                tag = "status_emprestados"
            else:
                tag = "status_sem_lista"
            self.tv_elenco_atual.insert(
                "",
                "end",
                values=(
                    jogador.get("posicao", ""),
                    _nome_exibicao_capitao(jogador.get("nome", ""), bool(jogador.get("capitao"))),
                    jogador.get("condicao", ""),
                    "1" if jogador.get("capitao") else "",
                ),
                tags=(tag,)
            )
        if hasattr(self, "elenco_resumo_var"):
            self.elenco_resumo_var.set(
                f"Titulares: {cont['Titular']} | Reservas: {cont['Reserva']} | "
                f"Não Relacionados: {cont['Não Relacionado']} | Lesionados: {cont['Lesionado']} | "
                f"Suspensos: {cont['Suspenso']} | Seleção: {cont['Servindo a seleção']} | "
                f"Emprestados: {cont['Emprestado']}"
            )
        self._render_campinho_elenco()

    def _dados_linha_elenco(self, iid):
        valores = self.tv_elenco_atual.item(iid, "values")
        posicao = str(valores[0]).strip() if len(valores) >= 1 else ""
        nome = _nome_sem_marcador_capitao(str(valores[1]).strip()) if len(valores) >= 2 else ""
        condicao = str(valores[2]).strip() if len(valores) >= 3 else ""
        eh_capitao = _normalizar_flag_capitao(valores[3]) if len(valores) >= 4 else False
        return posicao, nome, condicao, eh_capitao

    def _ordenar_jogadores_elenco_para_exibicao(self, jogadores):
        itens = list(jogadores or [])
        col = getattr(self, "_elenco_sort_col", None)
        if col not in {"posicao", "jogador"}:
            return _ordenar_jogadores_elenco(itens)

        pos_ordem = {pos: i for i, pos in enumerate(POSICOES_ELENCO)}

        def key_pos(item):
            pos = _normalizar_posicao_elenco(item.get("posicao"))
            nome = str(item.get("nome", "")).strip()
            return (pos_ordem.get(pos, 999), _chave_nome_jogador(nome))

        def key_jog(item):
            nome = str(item.get("nome", "")).strip()
            pos = _normalizar_posicao_elenco(item.get("posicao"))
            return (_chave_nome_jogador(nome), pos_ordem.get(pos, 999))

        key_fn = key_pos if col == "posicao" else key_jog
        return sorted(itens, key=key_fn, reverse=bool(getattr(self, "_elenco_sort_reverse", False)))

    def _toggle_ordenacao_elenco_atual(self, coluna):
        if coluna not in {"posicao", "jogador"}:
            return
        if getattr(self, "_elenco_sort_col", None) == coluna:
            self._elenco_sort_reverse = not bool(getattr(self, "_elenco_sort_reverse", False))
        else:
            self._elenco_sort_col = coluna
            self._elenco_sort_reverse = False
        self._render_elenco_atual()

    def _reset_ordenacao_elenco_atual(self):
        self._elenco_sort_col = None
        self._elenco_sort_reverse = False
        self._render_elenco_atual()

    def _titulares_elenco_por_posicao(self):
        tit = {pos: [] for pos in POSICOES_ELENCO}
        for jogador in self.elenco_atual.get("jogadores", []):
            if not isinstance(jogador, dict):
                continue
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            if _normalizar_condicao_elenco(jogador.get("condicao")) != "Titular":
                continue
            pos = _normalizar_posicao_elenco(jogador.get("posicao"))
            tit.setdefault(pos, []).append(nome)
        return tit

    def _render_campinho_elenco(self):
        canvas = getattr(self, "canvas_campinho_elenco", None)
        if canvas is None:
            return
        canvas.delete("all")
        self._elenco_campinho_hits = []

        w = max(300, canvas.winfo_width())
        h = max(220, canvas.winfo_height())
        m = 14
        canvas.create_rectangle(0, 0, w, h, fill="#0f6a35", outline="")
        canvas.create_rectangle(m, m, w - m, h - m, outline="#e9f7ed", width=2)
        meio_y = h / 2
        canvas.create_line(m, meio_y, w - m, meio_y, fill="#e9f7ed", width=2)
        canvas.create_oval(w / 2 - 34, meio_y - 34, w / 2 + 34, meio_y + 34, outline="#e9f7ed", width=2)

        titulares = self._titulares_elenco_por_posicao()

        def _lista(pos):
            return [str(n).strip() for n in titulares.get(pos, []) if str(n).strip()]

        linhas = [
            ("ATA", "Atacante", _lista("Atacante"), 0.16),
            ("MEI", "Meio-Campista", _lista("Meio-Campista"), 0.34),
            ("VOL", "Volante", _lista("Volante"), 0.50),
            ("DEF", "Defesa", _lista("Lateral-Esquerdo") + _lista("Zagueiro") + _lista("Lateral-Direito"), 0.68),
            ("GOL", "Goleiro", _lista("Goleiro"), 0.84),
        ]

        for setor, chave_linha, nomes, rel_y in linhas:
            y = m + (h - 2 * m) * rel_y
            canvas.create_text(m + 16, y, text=setor, fill="#d8f0de", font=("Segoe UI", 9, "bold"))
            if not nomes:
                continue
            n = len(nomes)
            for i, nome in enumerate(nomes):
                x = m + (w - 2 * m) * ((i + 1) / (n + 1))
                r = 14
                canvas.create_oval(x - r, y - r, x + r, y + r, fill="#f5f8f6", outline="#0b3d24", width=1)
                canvas.create_text(x, y, text=str(i + 1), fill="#133b23", font=("Segoe UI", 8, "bold"))
                nome_curto = nome if len(nome) <= 21 else (nome[:20] + "…")
                canvas.create_text(x, y + 20, text=nome_curto, fill="#eef9f1", font=("Segoe UI", 11, "bold"))
                self._elenco_campinho_hits.append({
                    "linha": chave_linha,
                    "idx": i,
                    "n": n,
                    "x": x,
                    "y": y,
                    "r": r,
                    "nome": nome,
                })

    def _elenco_reordenar_linha(self, linha, origem, alvo, n):
        jogadores = list(self.elenco_atual.get("jogadores", []))
        if linha == "Defesa":
            idx_le = [i for i, j in enumerate(jogadores) if _normalizar_condicao_elenco(j.get("condicao")) == "Titular" and _normalizar_posicao_elenco(j.get("posicao")) == "Lateral-Esquerdo"]
            idx_zag = [i for i, j in enumerate(jogadores) if _normalizar_condicao_elenco(j.get("condicao")) == "Titular" and _normalizar_posicao_elenco(j.get("posicao")) == "Zagueiro"]
            idx_ld = [i for i, j in enumerate(jogadores) if _normalizar_condicao_elenco(j.get("condicao")) == "Titular" and _normalizar_posicao_elenco(j.get("posicao")) == "Lateral-Direito"]
            seq = [jogadores[i] for i in idx_le] + [jogadores[i] for i in idx_zag] + [jogadores[i] for i in idx_ld]
            if len(seq) != n:
                return
            it = seq.pop(origem)
            seq.insert(alvo, it)
            n_le = len(idx_le)
            n_zag = len(idx_zag)
            seq_le = seq[:n_le]
            seq_zag = seq[n_le:n_le + n_zag]
            seq_ld = seq[n_le + n_zag:]
            for i, item in zip(idx_le, seq_le):
                jogadores[i] = item
            for i, item in zip(idx_zag, seq_zag):
                jogadores[i] = item
            for i, item in zip(idx_ld, seq_ld):
                jogadores[i] = item
        else:
            idxs = [i for i, j in enumerate(jogadores) if _normalizar_condicao_elenco(j.get("condicao")) == "Titular" and _normalizar_posicao_elenco(j.get("posicao")) == linha]
            if len(idxs) != n:
                return
            seq = [jogadores[i] for i in idxs]
            it = seq.pop(origem)
            seq.insert(alvo, it)
            for i, item in zip(idxs, seq):
                jogadores[i] = item

        self.elenco_atual["jogadores"] = jogadores
        salvar_elenco_atual(self.elenco_atual)
        self._sincronizar_jogadores_vasco_com_elenco()

    def _elenco_campinho_drag_start(self, event):
        hit = None
        for item in getattr(self, "_elenco_campinho_hits", []):
            dx = event.x - item["x"]
            dy = event.y - item["y"]
            if (dx * dx + dy * dy) <= (item["r"] + 4) ** 2:
                hit = item
                break
        self._elenco_campinho_drag_state = hit
        if hit:
            self.canvas_campinho_elenco.configure(cursor="hand2")

    def _elenco_campinho_drag_end(self, event):
        state = getattr(self, "_elenco_campinho_drag_state", None)
        self._elenco_campinho_drag_state = None
        self.canvas_campinho_elenco.configure(cursor="")
        if not state or state["n"] < 2:
            return
        linha = state["linha"]
        origem = state["idx"]
        n = state["n"]
        mesmos = sorted(
            [p for p in getattr(self, "_elenco_campinho_hits", []) if p.get("linha") == linha],
            key=lambda p: p.get("idx", 0),
        )
        if len(mesmos) != n:
            return
        alvo = min(range(n), key=lambda i: abs(event.x - mesmos[i]["x"]))
        if alvo == origem:
            return
        self._elenco_reordenar_linha(linha, origem, alvo, n)

    def _abrir_menu_contexto_campinho_elenco(self, event):
        hit = None
        for item in getattr(self, "_elenco_campinho_hits", []):
            dx = event.x - item["x"]
            dy = event.y - item["y"]
            if (dx * dx + dy * dy) <= (item["r"] + 4) ** 2:
                hit = item
                break
        if not hit:
            return

        nome = str(hit.get("nome", "")).strip()
        if not nome:
            return

        iid_encontrado = None
        alvo_cf = nome.casefold()
        for iid in self.tv_elenco_atual.get_children():
            _pos, nome_iid, _cond, _cap = self._dados_linha_elenco(iid)
            if str(nome_iid).strip().casefold() == alvo_cf:
                iid_encontrado = iid
                break
        if not iid_encontrado:
            return

        self.tv_elenco_atual.selection_set(iid_encontrado)
        self.tv_elenco_atual.focus(iid_encontrado)

        menu = tk.Menu(self.root, tearoff=0)
        submenu_tit = tk.Menu(menu, tearoff=0)
        for pos in POSICOES_ELENCO:
            submenu_tit.add_command(
                label=f"Titular - {pos}",
                command=lambda p=pos: self._enviar_jogador_elenco_para(("titulares", p))
            )
        menu.add_cascade(label="Enviar para Titulares", menu=submenu_tit)
        menu.add_separator()
        menu.add_command(label="Enviar para Reserva", command=lambda: self._enviar_jogador_elenco_para(("extras", "reservas")))
        menu.add_command(label="Enviar para Não Relacionado", command=lambda: self._enviar_jogador_elenco_para(("extras", "nao_relacionados")))
        menu.add_command(label="Enviar para Lesionado", command=lambda: self._enviar_jogador_elenco_para(("extras", "lesionados")))
        menu.add_command(label="Enviar para Suspenso", command=lambda: self._enviar_jogador_elenco_para(("extras", "suspensos")))
        menu.add_command(label="Enviar para Servindo a seleção", command=lambda: self._enviar_jogador_elenco_para(("extras", "servindo_selecao")))
        menu.add_command(label="Enviar para Emprestado", command=lambda: self._enviar_jogador_elenco_para(("extras", "emprestados")))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _chave_ordenacao_elenco(self, jogador, coluna):
        ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
        ordem_condicao = {cond: idx for idx, cond in enumerate(CONDICOES_ELENCO)}
        nome = str(jogador.get("nome", "")).strip()
        posicao = _normalizar_posicao_elenco(jogador.get("posicao"))
        condicao = _normalizar_condicao_elenco(jogador.get("condicao"))

        if coluna == "jogador":
            return nome.casefold(), ordem_condicao.get(condicao, len(CONDICOES_ELENCO)), ordem_posicao.get(posicao, len(POSICOES_ELENCO))
        if coluna == "posicao":
            return ordem_posicao.get(posicao, len(POSICOES_ELENCO)), ordem_condicao.get(condicao, len(CONDICOES_ELENCO)), nome.casefold()
        return ordem_condicao.get(condicao, len(CONDICOES_ELENCO)), ordem_posicao.get(posicao, len(POSICOES_ELENCO)), nome.casefold()

    def _ordenar_coluna_elenco(self, coluna):
        if self._elenco_sort_col == coluna:
            self._elenco_sort_reverse = not self._elenco_sort_reverse
        else:
            self._elenco_sort_col = coluna
            self._elenco_sort_reverse = False
        self._render_elenco_atual()

    def _resetar_modo_edicao_elenco(self):
        self._elenco_edit_nome_cf = None
        self.elenco_modo_var.set("")
        self.elenco_botao_var.set("Adicionar")
        if hasattr(self, "btn_cancelar_edicao_elenco"):
            self.btn_cancelar_edicao_elenco.state(["disabled"])

    def _iniciar_edicao_jogador_elenco(self, event=None):
        iid = None
        if event is not None:
            iid = self.tv_elenco_atual.identify_row(event.y)
            if iid:
                self.tv_elenco_atual.selection_set(iid)
                self.tv_elenco_atual.focus(iid)
        selecao = self.tv_elenco_atual.selection()
        if not selecao:
            return
        posicao, nome, condicao, eh_capitao = self._dados_linha_elenco(selecao[0])
        nome = str(nome).strip()
        if not nome:
            return
        self._elenco_edit_nome_cf = nome.casefold()
        self.elenco_nome_var.set(nome)
        self.elenco_posicao_var.set(_normalizar_posicao_elenco(posicao))
        self.elenco_condicao_var.set(_normalizar_condicao_elenco(condicao))
        self.elenco_capitao_var.set(bool(eh_capitao))
        self.elenco_modo_var.set(f"Editando: {nome}")
        self.elenco_botao_var.set("Salvar Edição")
        self.btn_cancelar_edicao_elenco.state(["!disabled"])
        self.elenco_nome_entry.focus_set()
        self.elenco_nome_entry.icursor(tk.END)

    def _cancelar_edicao_jogador_elenco(self):
        self._resetar_modo_edicao_elenco()
        self.elenco_nome_var.set("")
        self.elenco_posicao_var.set(ELENCO_POSICAO_PLACEHOLDER)
        self.elenco_condicao_var.set(ELENCO_CONDICAO_PLACEHOLDER)
        self.elenco_capitao_var.set(False)

    def _salvar_elenco_da_interface(self):
        jogadores = []
        for iid in self.tv_elenco_atual.get_children():
            posicao, nome, condicao, eh_capitao = self._dados_linha_elenco(iid)
            jogadores.append(
                {
                    "nome": str(nome).strip(),
                    "posicao": str(posicao).strip(),
                    "condicao": str(condicao).strip(),
                    "capitao": bool(eh_capitao),
                }
            )
        self.elenco_atual = {
            "jogadores": jogadores,
            "tecnico": str(self.elenco_atual.get("tecnico", "")).strip(),
        }
        salvar_elenco_atual(self.elenco_atual)
        self._sincronizar_jogadores_vasco_com_elenco()

    def _salvar_tecnico_elenco_atual(self, _event=None):
        tecnico = self.elenco_tecnico_var.get().strip() if hasattr(self, "elenco_tecnico_var") else ""
        if not tecnico:
            messagebox.showwarning("Campo obrigatório", "Informe o nome do técnico.")
            return
        self.elenco_atual["tecnico"] = tecnico
        salvar_elenco_atual(self.elenco_atual)
        lista_tecnicos = self.listas.setdefault("tecnicos", [])
        if tecnico not in lista_tecnicos:
            lista_tecnicos.append(tecnico)
            self.listas["tecnicos"] = sorted(lista_tecnicos, key=lambda s: s.casefold())
        self.listas["tecnico_atual"] = tecnico
        salvar_listas(self.listas)
        if hasattr(self, "elenco_tecnico_var"):
            self.elenco_tecnico_var.set(tecnico)
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(tecnico)
        self._atualizar_combo_tecnicos()

    def _obter_tecnico_destacado(self) -> str:
        tecnico_elenco = str(self.elenco_atual.get("tecnico", "") or "").strip()
        if tecnico_elenco:
            return tecnico_elenco
        return str(self.listas.get("tecnico_atual", "") or "Fernando Diniz").strip()

    def _sincronizar_jogadores_vasco_com_elenco(self, persistir_listas=False):
        self._atualizar_opcoes_gol_vasco(persistir=persistir_listas)
        self._sincronizar_jogadores_historico()
        if hasattr(self, "_render_elenco_atual"):
            self._render_elenco_atual()
        if hasattr(self, "_render_aba_jogadores_historico"):
            self._render_aba_jogadores_historico()
        self._atualizar_elenco_disponivel_partida()
        if hasattr(self, "escalacao_partida"):
            if getattr(self, "editing_index", None) is None:
                self._inicializar_escalacao_partida()
            else:
                self._carregar_escalacao_partida(self.escalacao_partida)

    def _nome_capitao_elenco_atual(self) -> str:
        for jogador in self.elenco_atual.get("jogadores", []):
            if isinstance(jogador, dict) and jogador.get("capitao"):
                return str(jogador.get("nome", "")).strip()
        return ""

    def _jogadores_que_foram_capitaes(self) -> set[str]:
        capitaes = set()
        capitao_atual = self._nome_capitao_elenco_atual()
        if capitao_atual:
            capitaes.add(capitao_atual.casefold())
        for jogo in carregar_dados_jogos():
            nome = str(jogo.get("capitao", "")).strip()
            if nome:
                capitaes.add(nome.casefold())
        return capitaes

    def _opcoes_capitao_partida(self):
        esc = getattr(self, "escalacao_partida", self._escalacao_partida_base())
        opcoes = []
        vistos = set()

        def add_nome(nome):
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                return
            chave = nome_limpo.casefold()
            if chave in vistos:
                return
            vistos.add(chave)
            opcoes.append(nome_limpo)

        titulares_por_posicao = esc.get("titulares_por_posicao", {}) if isinstance(esc, dict) else {}
        for pos in POSICOES_ELENCO:
            for nome in titulares_por_posicao.get(pos, []):
                add_nome(nome)
        for nome in esc.get("reservas", []) if isinstance(esc, dict) else []:
            add_nome(nome)
        for info in getattr(self, "_elenco_info_por_nome_cf", {}).values():
            if info.get("condicao") != "Emprestado":
                add_nome(info.get("nome", ""))
        return opcoes

    def _atualizar_opcoes_capitao_partida(self, preservar_valor=True):
        if not hasattr(self, "capitao_partida_var") or not hasattr(self, "capitao_partida_entry"):
            return
        atual = self.capitao_partida_var.get().strip()
        opcoes = self._opcoes_capitao_partida()
        self.capitao_partida_entry["values"] = [""] + opcoes
        if preservar_valor and atual and any(atual.casefold() == nome.casefold() for nome in opcoes):
            self.capitao_partida_var.set(atual)
            return
        if not preservar_valor:
            self.capitao_partida_var.set("")
            return
        if atual:
            self.capitao_partida_var.set("")

    def _ordenar_opcoes_gol_vasco(self):
        opcoes = []
        vistos = set()

        def add_nome(nome):
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                return
            cf = nome_limpo.casefold()
            if cf in vistos:
                return
            vistos.add(cf)
            opcoes.append(nome_limpo)

        esc = getattr(self, "escalacao_partida", self._escalacao_partida_base())
        titulares_por_posicao = esc.get("titulares_por_posicao", {}) if isinstance(esc, dict) else {}
        # Ordem para lista de gols: do ataque para trás.
        ordem_titulares_gols = [
            "Atacante",
            "Meio-Campista",
            "Volante",
            "Lateral-Esquerdo",
            "Zagueiro",
            "Lateral-Direito",
            "Goleiro",
        ]
        for pos in ordem_titulares_gols:
            for nome in titulares_por_posicao.get(pos, []):
                add_nome(nome)
        # Reservas sempre no fim.
        for nome in esc.get("reservas", []) if isinstance(esc, dict) else []:
            add_nome(nome)
        return opcoes

    def _atualizar_opcoes_gol_vasco(self, persistir=False):
        opcoes = self._ordenar_opcoes_gol_vasco()
        alterou = opcoes != list(self.listas.get("jogadores_vasco", []))
        self.listas["jogadores_vasco"] = opcoes
        if hasattr(self, "entry_gol_vasco"):
            self.entry_gol_vasco["values"] = opcoes
        if hasattr(self, "entry_cartao_amarelo"):
            self.entry_cartao_amarelo["values"] = opcoes
        if hasattr(self, "entry_cartao_vermelho"):
            self.entry_cartao_vermelho["values"] = opcoes
        self._atualizar_opcoes_capitao_partida()
        if persistir and alterou:
            salvar_listas(self.listas)

    def _on_notebook_tab_changed(self, event):
        if event.widget is not self.notebook:
            return
        atual = self.notebook.select()
        # Lazy load: carrega aba estatística se estiver suja ou nunca carregada
        for frame_attr, loader in self._LAZY_TAB_LOADERS:
            frame = getattr(self, frame_attr, None)
            if frame is not None and str(atual) == str(frame):
                if frame_attr in self._tabs_sujas:
                    getattr(self, loader)()
                    self._tabs_sujas.discard(frame_attr)
                return
        if hasattr(self, "frame_retro") and str(atual) == str(self.frame_retro):
            self._atualizar_opcoes_aba_retro()
            if getattr(self, "retro_adversario_var", None) and self.retro_adversario_var.get().strip():
                self._atualizar_retro_aba_adversario()
        if str(atual) != str(self.frame_registro):
            return
        if getattr(self, "editing_index", None) is not None:
            # Em modo edição, preserva os dados do jogo carregado (inclui técnico específico da partida).
            self._sincronizar_jogadores_vasco_com_elenco()
            return
        # Sempre espelha o que estiver salvo no Elenco Atual ao entrar na aba de registro.
        self.elenco_atual = carregar_elenco_atual()
        tecnico_elenco = str(self.elenco_atual.get("tecnico", "") or "").strip()
        if tecnico_elenco:
            lista_tecnicos = self.listas.setdefault("tecnicos", [])
            if tecnico_elenco not in lista_tecnicos:
                lista_tecnicos.append(tecnico_elenco)
                self.listas["tecnicos"] = sorted(lista_tecnicos, key=lambda s: s.casefold())
            self.listas["tecnico_atual"] = tecnico_elenco
            if hasattr(self, "tecnico_var"):
                self.tecnico_var.set(tecnico_elenco)
            salvar_listas(self.listas)
            self._atualizar_combo_tecnicos()
        self._sincronizar_jogadores_vasco_com_elenco()

    def _nomes_expandidos_cartoes(self, jogo, chave):
        eventos = _expandir_eventos_cartao(jogo.get(chave, []))
        return [
            str(evento.get("nome", "")).strip()
            for evento in eventos
            if str(evento.get("nome", "")).strip()
        ]

    def _atualizar_condicoes_elenco_por_escalacao(self, escalacao_partida):
        if not isinstance(escalacao_partida, dict):
            return

        nomes_por_condicao = {}
        titulares_por_posicao = escalacao_partida.get("titulares_por_posicao", {})
        if isinstance(titulares_por_posicao, dict):
            for nomes in titulares_por_posicao.values():
                if isinstance(nomes, list):
                    for nome in nomes:
                        nome_limpo = str(nome).strip()
                        if nome_limpo:
                            nomes_por_condicao[nome_limpo.casefold()] = "Titular"

        for chave, condicao in (
            ("reservas", "Reserva"),
            ("nao_relacionados", "Não Relacionado"),
            ("lesionados", "Lesionado"),
            ("suspensos", "Suspenso"),
            ("servindo_selecao", "Servindo a seleção"),
        ):
            nomes = escalacao_partida.get(chave, [])
            if not isinstance(nomes, list):
                continue
            for nome in nomes:
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    nomes_por_condicao[nome_limpo.casefold()] = condicao

        if not nomes_por_condicao:
            return

        alterou = False
        for jogador in self.elenco_atual.get("jogadores", []):
            if not isinstance(jogador, dict):
                continue
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            nome_cf = nome.casefold()
            condicao_atual = _normalizar_condicao_elenco(jogador.get("condicao"))
            if condicao_atual == "Emprestado" and nome_cf not in nomes_por_condicao:
                continue
            nova_condicao = nomes_por_condicao.get(nome_cf, "Não Relacionado")
            if jogador.get("condicao") != nova_condicao:
                jogador["condicao"] = nova_condicao
                alterou = True

        if alterou:
            salvar_elenco_atual(self.elenco_atual)
            self._sincronizar_jogadores_vasco_com_elenco()

    def _adicionar_jogador_elenco(self, _event=None):
        nome = self.elenco_nome_var.get().strip()
        posicao_raw = self.elenco_posicao_var.get().strip()
        condicao_raw = self.elenco_condicao_var.get().strip()
        eh_capitao = bool(self.elenco_capitao_var.get())
        if not nome:
            messagebox.showwarning("Campo obrigatório", "Informe o nome do jogador.")
            return
        if posicao_raw == ELENCO_POSICAO_PLACEHOLDER or posicao_raw not in POSICOES_ELENCO:
            messagebox.showwarning("Campo obrigatório", "Selecione a posição do jogador.")
            return
        if condicao_raw == ELENCO_CONDICAO_PLACEHOLDER or condicao_raw not in CONDICOES_ELENCO:
            messagebox.showwarning("Campo obrigatório", "Selecione a condição do jogador.")
            return
        posicao = _normalizar_posicao_elenco(posicao_raw)
        condicao = _normalizar_condicao_elenco(condicao_raw)
        nomes_atuais = {}
        titulares_atuais = 0
        condicao_jogador_editando = None
        for iid in self.tv_elenco_atual.get_children():
            _pos_atual, nome_atual, cond_atual, _cap_atual = self._dados_linha_elenco(iid)
            nome_cf = str(nome_atual).casefold()
            nomes_atuais[nome_cf] = iid
            if _normalizar_condicao_elenco(cond_atual) == "Titular":
                titulares_atuais += 1
            if self._elenco_edit_nome_cf and nome_cf == self._elenco_edit_nome_cf:
                condicao_jogador_editando = _normalizar_condicao_elenco(cond_atual)

        editando = self._elenco_edit_nome_cf is not None
        # Regra: não permitir mais de 11 titulares no elenco atual.
        if condicao == "Titular":
            if editando and condicao_jogador_editando == "Titular":
                pass
            elif titulares_atuais >= 11:
                messagebox.showerror("Limite de titulares", "Não é possível ter mais de 11 titulares no elenco atual.")
                return

        if editando:
            if nome.casefold() != self._elenco_edit_nome_cf and nome.casefold() in nomes_atuais:
                messagebox.showwarning("Duplicado", f"'{nome}' já está no elenco atual.")
                return
            iid_edit = nomes_atuais.get(self._elenco_edit_nome_cf)
            if iid_edit:
                if eh_capitao:
                    for iid in self.tv_elenco_atual.get_children():
                        p, n, c, cap = self._dados_linha_elenco(iid)
                        if cap and iid != iid_edit:
                            self.tv_elenco_atual.item(iid, values=(p, _nome_exibicao_capitao(n, False), c, ""))
                self.tv_elenco_atual.item(
                    iid_edit,
                    values=(posicao, _nome_exibicao_capitao(nome, eh_capitao), condicao, "1" if eh_capitao else ""),
                )
            else:
                self.tv_elenco_atual.insert(
                    "",
                    "end",
                    values=(posicao, _nome_exibicao_capitao(nome, eh_capitao), condicao, "1" if eh_capitao else ""),
                )
        elif nome.casefold() in nomes_atuais:
            messagebox.showwarning("Duplicado", f"'{nome}' já está no elenco atual.")
            return
        else:
            if eh_capitao:
                for iid in self.tv_elenco_atual.get_children():
                    p, n, c, cap = self._dados_linha_elenco(iid)
                    if cap:
                        self.tv_elenco_atual.item(iid, values=(p, _nome_exibicao_capitao(n, False), c, ""))
            self.tv_elenco_atual.insert(
                "",
                "end",
                values=(posicao, _nome_exibicao_capitao(nome, eh_capitao), condicao, "1" if eh_capitao else ""),
            )

        self._resetar_modo_edicao_elenco()
        self.elenco_nome_var.set("")
        self.elenco_posicao_var.set(ELENCO_POSICAO_PLACEHOLDER)
        self.elenco_condicao_var.set(ELENCO_CONDICAO_PLACEHOLDER)
        self.elenco_capitao_var.set(False)
        self._salvar_elenco_da_interface()

    def _remover_jogador_elenco(self, _event=None):
        selecao = self.tv_elenco_atual.selection()
        if not selecao:
            return
        pos_removida, nome_removido, _, _cap = self._dados_linha_elenco(selecao[0])
        jogador_saida = {"nome": str(nome_removido).strip(), "posicao": str(pos_removida).strip()}
        self._adicionar_jogadores_historico([jogador_saida])
        self._registrar_saida_jogadores_historico([jogador_saida])
        self.tv_elenco_atual.delete(selecao[0])
        if self._elenco_edit_nome_cf and str(nome_removido).strip().casefold() == self._elenco_edit_nome_cf:
            self._cancelar_edicao_jogador_elenco()
        self._salvar_elenco_da_interface()

    def _limpar_elenco_atual(self):
        if not self.tv_elenco_atual.get_children():
            return
        if not messagebox.askyesno("Limpar elenco", "Deseja remover todos os jogadores da lista do elenco atual?"):
            return
        removidos = []
        for iid in self.tv_elenco_atual.get_children():
            posicao, nome, _cond, _cap = self._dados_linha_elenco(iid)
            removidos.append({"nome": str(nome).strip(), "posicao": str(posicao).strip()})
        self._adicionar_jogadores_historico(removidos)
        self._registrar_saida_jogadores_historico(removidos)
        for iid in self.tv_elenco_atual.get_children():
            self.tv_elenco_atual.delete(iid)
        self._cancelar_edicao_jogador_elenco()
        self._salvar_elenco_da_interface()

    def _adicionar_jogadores_historico(self, jogadores):
        if not isinstance(jogadores, list):
            return
        base = list(self.jogadores_historico.get("jogadores", []))
        mapa = {str(j.get("nome", "")).strip().casefold(): dict(j) for j in base if isinstance(j, dict) and str(j.get("nome", "")).strip()}
        alterou = False
        hoje = _hoje_ptbr()
        for item in jogadores:
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            chave = jogador["nome"].casefold()
            atual = mapa.get(chave)
            if not atual:
                if not jogador.get("data_registro"):
                    jogador["data_registro"] = hoje
                if not jogador.get("data_entrada"):
                    jogador["data_entrada"] = str(jogador.get("data_registro", "")).strip() or hoje
                jogador["data_saida"] = ""
                jogador["passagens"] = [{
                    "data_entrada": jogador["data_entrada"],
                    "data_saida": "",
                }]
                mapa[chave] = jogador
                alterou = True
                continue
            passagens = list(atual.get("passagens", [])) if isinstance(atual.get("passagens", []), list) else []
            pos_atual = _normalizar_posicao_elenco(atual.get("posicao"))
            pos_nova = _normalizar_posicao_elenco(jogador.get("posicao"))
            if pos_atual == "Meio-Campista" and pos_nova != "Meio-Campista":
                atual["posicao"] = pos_nova
                mapa[chave] = atual
                alterou = True
            if not str(atual.get("data_registro", "")).strip() and jogador.get("data_registro"):
                atual["data_registro"] = jogador["data_registro"]
                mapa[chave] = atual
                alterou = True
            data_entrada_atual = str(atual.get("data_entrada", "")).strip()
            if not data_entrada_atual:
                atual["data_entrada"] = (
                    str(jogador.get("data_entrada", "")).strip()
                    or str(jogador.get("data_registro", "")).strip()
                    or hoje
                )
                mapa[chave] = atual
                alterou = True
            if not passagens:
                passagens = [{
                    "data_entrada": str(atual.get("data_entrada", "")).strip() or hoje,
                    "data_saida": str(atual.get("data_saida", "")).strip(),
                }]
                atual["passagens"] = passagens
                mapa[chave] = atual
                alterou = True
            elif str(passagens[-1].get("data_saida", "")).strip():
                nova_entrada = (
                    str(jogador.get("data_entrada", "")).strip()
                    or str(jogador.get("data_registro", "")).strip()
                    or hoje
                )
                passagens.append({
                    "data_entrada": nova_entrada,
                    "data_saida": "",
                })
                atual["passagens"] = passagens
                mapa[chave] = atual
                alterou = True
            if str(atual.get("data_saida", "")).strip():
                atual["data_saida"] = ""
                mapa[chave] = atual
                alterou = True
            atual = self._sincronizar_resumo_passagens_jogador(atual)
            mapa[chave] = atual
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(list(mapa.values()))}
        salvar_jogadores_historico(self.jogadores_historico)

    def _registrar_saida_jogadores_historico(self, jogadores):
        if not isinstance(jogadores, list):
            return
        mapa = {
            str(j.get("nome", "")).strip().casefold(): dict(j)
            for j in self.jogadores_historico.get("jogadores", [])
            if isinstance(j, dict) and str(j.get("nome", "")).strip()
        }
        alterou = False
        hoje = _hoje_ptbr()
        for item in jogadores:
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            chave = jogador["nome"].casefold()
            atual = mapa.get(chave)
            if not atual:
                continue
            if not str(atual.get("data_entrada", "")).strip():
                atual["data_entrada"] = (
                    str(atual.get("data_registro", "")).strip()
                    or hoje
                )
                alterou = True
            passagens = list(atual.get("passagens", [])) if isinstance(atual.get("passagens", []), list) else []
            if not passagens:
                passagens = [{
                    "data_entrada": str(atual.get("data_entrada", "")).strip() or hoje,
                    "data_saida": hoje,
                }]
                atual["passagens"] = passagens
                alterou = True
            elif str(passagens[-1].get("data_saida", "")).strip() != hoje:
                passagens[-1]["data_saida"] = hoje
                atual["passagens"] = passagens
                alterou = True
            if str(atual.get("data_saida", "")).strip() != hoje:
                atual["data_saida"] = hoje
                alterou = True
            atual = self._sincronizar_resumo_passagens_jogador(atual)
            mapa[chave] = atual
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(list(mapa.values()))}
        salvar_jogadores_historico(self.jogadores_historico)

    def _ajustar_jogos_pelo_vasco_jogadores_historico(self, participantes_antes=None, participantes_depois=None):
        antes = set(participantes_antes or set())
        depois = set(participantes_depois or set())
        if not antes and not depois:
            return
        mapa = {}
        for item in self.jogadores_historico.get("jogadores", []):
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            mapa[_chave_nome_jogador(jogador.get("nome", ""))] = jogador
        alterou = False
        for chave in antes | depois:
            jogador = mapa.get(chave)
            if not jogador:
                continue
            valor_atual = self._obter_jogos_pelo_vasco_salvos(jogador)
            if valor_atual is None:
                valor_atual = 0
            novo_valor = valor_atual
            if chave in antes and chave not in depois:
                novo_valor = max(0, valor_atual - 1)
            elif chave in depois and chave not in antes:
                novo_valor = valor_atual + 1
            if novo_valor != self._obter_jogos_pelo_vasco_salvos(jogador):
                jogador["jogos_pelo_vasco"] = novo_valor
                mapa[chave] = jogador
                alterou = True
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(list(mapa.values()))}
        salvar_jogadores_historico(self.jogadores_historico)

    def _sincronizar_jogos_pelo_vasco_jogadores_historico(self, jogos=None):
        if jogos is None:
            jogos = carregar_dados_jogos()
        if not isinstance(jogos, list):
            jogos = []
        jogadores = self.jogadores_historico.get("jogadores", [])
        if not isinstance(jogadores, list) or not jogadores:
            return
        contagem = Counter()
        for jogo in jogos:
            contagem.update(_jogadores_que_participaram_do_jogo(jogo))
        alterou = False
        atualizados = []
        for item in jogadores:
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            chave = _chave_nome_jogador(jogador.get("nome", ""))
            if self._obter_jogos_pelo_vasco_salvos(jogador) is None and contagem.get(chave, 0) > 0:
                jogador["jogos_pelo_vasco"] = int(contagem[chave])
                alterou = True
            atualizados.append(jogador)
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(atualizados)}
        salvar_jogadores_historico(self.jogadores_historico)

    def _sincronizar_jogadores_historico(self):
        candidatos = []
        for jogador in self.elenco_atual.get("jogadores", []):
            if not isinstance(jogador, dict):
                continue
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            candidatos.append({"nome": nome, "posicao": jogador.get("posicao", "Meio-Campista")})
        self._adicionar_jogadores_historico(candidatos)
        self._atualizar_datas_estreia_jogadores_historico()
        self._sincronizar_jogos_pelo_vasco_jogadores_historico()

    def _criar_aba_jogadores_historico(self, frame):
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)
        frame.rowconfigure(1, weight=1)
        ttk.Label(
            frame,
            text="Todos os jogadores que já passaram pelo Vasco (incluindo elenco atual).",
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        esquerda = ttk.Labelframe(frame, text="Jogadores", padding=8)
        esquerda.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        esquerda.columnconfigure(0, weight=1)
        esquerda.rowconfigure(1, weight=1)

        filtros = ttk.Frame(esquerda)
        filtros.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(filtros, text="Buscar:").pack(side="left")
        self.jogadores_hist_busca_var = tk.StringVar(value="")
        self.entry_jogadores_hist_busca = ttk.Entry(filtros, textvariable=self.jogadores_hist_busca_var, width=24)
        self.entry_jogadores_hist_busca.pack(side="left", padx=(6, 6))
        ttk.Label(filtros, text="Filtro:").pack(side="left", padx=(8, 0))
        self.jogadores_hist_filtro_var = tk.StringVar(value="Todos")
        opcoes_filtro = ["Todos", "Somente Elenco Atual", "Capitães do Vasco"] + POSICOES_ELENCO + CONDICOES_ELENCO + ["Ex-jogador"]
        self.combo_jogadores_hist_filtro = ttk.Combobox(
            filtros,
            textvariable=self.jogadores_hist_filtro_var,
            values=opcoes_filtro,
            state="readonly",
            width=18,
        )
        self.combo_jogadores_hist_filtro.pack(side="left", padx=(6, 6))
        ttk.Label(filtros, text="Os mais:").pack(side="left", padx=(8, 0))
        self.jogadores_hist_ranking_var = tk.StringVar(value="Nenhum")
        self.combo_jogadores_hist_ranking = ttk.Combobox(
            filtros,
            textvariable=self.jogadores_hist_ranking_var,
            values=JOGADORES_HIST_RANKING_OPCOES,
            state="readonly",
            width=24,
        )
        self.combo_jogadores_hist_ranking.pack(side="left", padx=(6, 6))
        ttk.Button(filtros, text="Limpar", command=self._limpar_busca_jogadores_historico).pack(side="left")
        self.jogadores_hist_busca_var.trace_add("write", lambda *_: self._render_aba_jogadores_historico())
        self.jogadores_hist_filtro_var.trace_add("write", lambda *_: self._render_aba_jogadores_historico())
        self.jogadores_hist_ranking_var.trace_add("write", lambda *_: self._render_aba_jogadores_historico())

        cols = ("posicao", "jogador", "status", "minutos", "capitao")
        self.tv_jogadores_historico = ttk.Treeview(esquerda, columns=cols, show="headings", height=16)
        self._jogadores_hist_sort_col = "posicao"
        self._jogadores_hist_sort_reverse = False
        self.tv_jogadores_historico.heading("posicao", text="Posição", command=lambda: self._toggle_ordenacao_jogadores_historico("posicao"))
        self.tv_jogadores_historico.heading("jogador", text="Jogador", command=lambda: self._toggle_ordenacao_jogadores_historico("jogador"))
        self.tv_jogadores_historico.heading("status", text="Status", command=lambda: self._toggle_ordenacao_jogadores_historico("status"))
        self.tv_jogadores_historico.heading("minutos", text="Minutos", command=lambda: self._toggle_ordenacao_jogadores_historico("minutos"))
        self.tv_jogadores_historico.heading("capitao", text="Capitão", command=lambda: self._toggle_ordenacao_jogadores_historico("capitao"))
        self.tv_jogadores_historico.column("posicao", width=150, anchor="w")
        self.tv_jogadores_historico.column("jogador", width=280, anchor="w")
        self.tv_jogadores_historico.column("status", width=130, anchor="center")
        self.tv_jogadores_historico.column("minutos", width=100, anchor="e")
        self.tv_jogadores_historico.column("capitao", width=90, anchor="center")
        self.tv_jogadores_historico.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_jogadores_historico.grid(row=1, column=0, sticky="nsew")
        self.tv_jogadores_historico.bind("<<TreeviewSelect>>", self._ao_selecionar_jogador_historico)

        sy = ttk.Scrollbar(esquerda, orient="vertical", command=self.tv_jogadores_historico.yview)
        sy.grid(row=1, column=1, sticky="ns")
        self.tv_jogadores_historico.configure(yscrollcommand=sy.set)

        direita = ttk.Labelframe(frame, text="Detalhes do Jogador", padding=8)
        direita.grid(row=1, column=1, sticky="nsew", padx=(6, 0))
        direita.columnconfigure(0, weight=1)
        direita.rowconfigure(1, weight=1)

        self.jogador_hist_titulo_var = tk.StringVar(value="Selecione um jogador na lista.")
        ttk.Label(direita, textvariable=self.jogador_hist_titulo_var).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.detalhes_jogador_notebook = ttk.Notebook(direita)
        self.detalhes_jogador_notebook.grid(row=1, column=0, sticky="nsew")
        self._detalhes_jogador_abas = {}

        botoes = ttk.Frame(direita)
        botoes.grid(row=2, column=0, sticky="e", pady=(8, 0))
        ttk.Button(
            botoes,
            text="Voltar ao Elenco Atual",
            command=self._retornar_jogador_ao_elenco_atual,
        ).pack(side="left")

        self._render_aba_jogadores_historico()

    def _render_aba_jogadores_historico(self):
        if not hasattr(self, "tv_jogadores_historico"):
            return
        selecionado_cf = None
        sel = self.tv_jogadores_historico.selection()
        if sel:
            vals = self.tv_jogadores_historico.item(sel[0], "values")
            if len(vals) >= 2:
                selecionado_cf = str(vals[1]).strip().casefold()
        termo = ""
        if hasattr(self, "jogadores_hist_busca_var"):
            termo = self.jogadores_hist_busca_var.get().strip().casefold()
        filtro = "Todos"
        if hasattr(self, "jogadores_hist_filtro_var"):
            filtro = self.jogadores_hist_filtro_var.get().strip() or "Todos"
        ranking = "Nenhum"
        if hasattr(self, "jogadores_hist_ranking_var"):
            ranking = self.jogadores_hist_ranking_var.get().strip() or "Nenhum"

        atuais = {
            str(j.get("nome", "")).strip().casefold(): _normalizar_condicao_elenco(j.get("condicao"))
            for j in self.elenco_atual.get("jogadores", [])
            if isinstance(j, dict) and str(j.get("nome", "")).strip()
        }
        capitaes = self._jogadores_que_foram_capitaes()
        jogos = carregar_dados_jogos()
        self.tv_jogadores_historico.delete(*self.tv_jogadores_historico.get_children())
        jogadores_filtrados = []
        novo_sel = None
        for jogador in _ordenar_jogadores_historico(list(self.jogadores_historico.get("jogadores", []))):
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            posicao = _normalizar_posicao_elenco(jogador.get("posicao"))
            cond = atuais.get(nome.casefold())
            status = cond if cond else "Ex-jogador"
            foi_capitao = nome.casefold() in capitaes
            icone_capitao = "🎗" if foi_capitao else ""
            ranking_valor = 0
            stats = self._coletar_estatisticas_jogador_periodo(nome, jogos)
            minutos_jogados = stats.get("minutos_jogados")
            minutos_exibicao = str(int(minutos_jogados or 0))
            if stats.get("minutos_jogados_desconhecido"):
                minutos_exibicao = "Desconhecido"
            if ranking != "Nenhum":
                ranking_valor = self._obter_valor_ranking_jogador(jogador, stats, ranking)
            if termo:
                haystack = f"{posicao} {nome} {status} {'sim' if foi_capitao else 'nao'}".casefold()
                if termo not in haystack:
                    continue
            if filtro == "Somente Elenco Atual" and not cond:
                continue
            if filtro == "Capitães do Vasco" and not foi_capitao:
                continue
            if filtro not in {"Todos", "Somente Elenco Atual", "Capitães do Vasco"} and filtro not in {posicao, status}:
                continue
            jogadores_filtrados.append({
                "posicao": posicao,
                "jogador": nome,
                "status": status,
                "minutos": minutos_exibicao,
                "minutos_valor": None if stats.get("minutos_jogados_desconhecido") else int(minutos_jogados or 0),
                "capitao": icone_capitao,
                "foi_capitao": foi_capitao,
                "ranking_valor": ranking_valor,
            })

        def _sort_key(item):
            ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
            ordem_status = {status_txt: idx for idx, status_txt in enumerate(CONDICOES_ELENCO + ["Ex-jogador"])}
            if ranking != "Nenhum":
                return (
                    -(float(item.get("ranking_valor", 0) or 0)),
                    str(item.get("jogador", "")).casefold(),
                    ordem_posicao.get(item.get("posicao", ""), len(POSICOES_ELENCO)),
                )
            col = getattr(self, "_jogadores_hist_sort_col", "posicao")
            if col == "minutos":
                minutos_valor = item.get("minutos_valor")
                return (
                    1 if minutos_valor is None else 0,
                    -(minutos_valor or 0),
                    str(item.get("jogador", "")).casefold(),
                )
            if col == "posicao":
                return (
                    ordem_posicao.get(item.get("posicao", ""), len(POSICOES_ELENCO)),
                    str(item.get("jogador", "")).casefold(),
                    ordem_status.get(item.get("status", ""), len(ordem_status)),
                )
            if col == "status":
                return (
                    ordem_status.get(item.get("status", ""), len(ordem_status)),
                    ordem_posicao.get(item.get("posicao", ""), len(POSICOES_ELENCO)),
                    str(item.get("jogador", "")).casefold(),
                )
            if col == "capitao":
                return (
                    0 if item.get("foi_capitao") else 1,
                    str(item.get("jogador", "")).casefold(),
                    ordem_posicao.get(item.get("posicao", ""), len(POSICOES_ELENCO)),
                )
            return (
                str(item.get("jogador", "")).casefold(),
                ordem_posicao.get(item.get("posicao", ""), len(POSICOES_ELENCO)),
                ordem_status.get(item.get("status", ""), len(ordem_status)),
            )

        jogadores_filtrados = sorted(
            jogadores_filtrados,
            key=_sort_key,
            reverse=getattr(self, "_jogadores_hist_sort_reverse", False),
        )

        for i, item in enumerate(jogadores_filtrados, start=1):
            iid = self.tv_jogadores_historico.insert(
                "",
                "end",
                values=(item["posicao"], item["jogador"], item["status"], item["minutos"], item["capitao"]),
                tags=("odd",) if i % 2 else (),
            )
            if selecionado_cf and item["jogador"].casefold() == selecionado_cf:
                novo_sel = iid
        if novo_sel:
            self.tv_jogadores_historico.selection_set(novo_sel)
            self.tv_jogadores_historico.focus(novo_sel)
            self._ao_selecionar_jogador_historico()

    def _limpar_busca_jogadores_historico(self):
        if hasattr(self, "jogadores_hist_busca_var"):
            self.jogadores_hist_busca_var.set("")
        if hasattr(self, "jogadores_hist_filtro_var"):
            self.jogadores_hist_filtro_var.set("Todos")
        if hasattr(self, "jogadores_hist_ranking_var"):
            self.jogadores_hist_ranking_var.set("Nenhum")

    def _obter_valor_ranking_jogador(self, jogador, stats, ranking):
        mapa = {
            "Passagens pelo Vasco": len(jogador.get("passagens", [])) if isinstance(jogador.get("passagens", []), list) else 0,
            "Jogos com participação": int(stats.get("jogos_com_participacao", 0) or 0),
            "Minutos jogados": int(stats.get("minutos_jogados", 0) or 0),
            "Jogos como titular": int(stats.get("jogos_titular", 0) or 0),
            "Jogos como reserva": int(stats.get("jogos_reserva", 0) or 0),
            "Foi para o jogo e não entrou": int(stats.get("jogos_reserva_sem_entrar", 0) or 0),
            "Jogos como não relacionado": int(stats.get("jogos_nao_rel", 0) or 0),
            "Jogos como lesionado": int(stats.get("jogos_lesionado", 0) or 0),
            "Jogos como suspenso": int(stats.get("jogos_suspenso", 0) or 0),
            "Jogos servindo a seleção": int(stats.get("jogos_servindo_selecao", 0) or 0),
            "Gols pelo Vasco": int(stats.get("gols", 0) or 0),
            "Assistências": int(stats.get("assistencias", 0) or 0),
            "Participações em gol": int(stats.get("participacoes_gol", 0) or 0),
            "Jogos como capitão": int(stats.get("jogos_como_capitao", 0) or 0),
            "Partidas em que marcou": int(stats.get("partidas_com_gol", 0) or 0),
            "Partidas com assistência": int(stats.get("partidas_com_assistencia", 0) or 0),
            "Gols como titular": int(stats.get("gols_titular", 0) or 0),
            "Gols saindo do banco": int(stats.get("gols_banco", 0) or 0),
            "Média de minutos jogados": float(stats.get("media_minutos_jogados", 0.0) or 0.0),
            "Média de gols por jogo": float(stats.get("media_gols", 0.0) or 0.0),
            "Cartões amarelos": int(stats.get("cartoes_amarelos", 0) or 0),
            "Cartões vermelhos": int(stats.get("cartoes_vermelhos", 0) or 0),
            "Média de minutos entre gols": float(stats.get("media_minutos_entre_gols", 0.0) or 0.0),
        }
        return mapa.get(ranking, 0)

    def _toggle_ordenacao_jogadores_historico(self, coluna):
        if coluna not in {"posicao", "jogador", "status", "minutos", "capitao"}:
            return
        if getattr(self, "_jogadores_hist_sort_col", None) == coluna:
            self._jogadores_hist_sort_reverse = not getattr(self, "_jogadores_hist_sort_reverse", False)
        else:
            self._jogadores_hist_sort_col = coluna
            self._jogadores_hist_sort_reverse = False
        self._render_aba_jogadores_historico()

    def _ao_selecionar_jogador_historico(self, _event=None):
        if not hasattr(self, "tv_jogadores_historico") or not hasattr(self, "detalhes_jogador_notebook"):
            return
        sel = self.tv_jogadores_historico.selection()
        if not sel:
            return
        vals = self.tv_jogadores_historico.item(sel[0], "values")
        if len(vals) < 2:
            return
        nome = str(vals[1]).strip()
        if not nome:
            return

        detalhes = self._coletar_detalhes_jogador_historico(nome)
        self.jogador_hist_titulo_var.set(f"Jogador: {nome}")
        self._render_detalhes_jogador_historico(detalhes)

    def _coletar_detalhes_jogador_historico(self, nome):
        alvo = _chave_nome_jogador(nome)
        jogos = carregar_dados_jogos()
        data_registro = ""
        data_entrada = ""
        data_saida = ""
        passagens = []
        jogador_historico = None
        for item in self.jogadores_historico.get("jogadores", []):
            if not isinstance(item, dict):
                continue
            if _chave_nome_jogador(item.get("nome", "")) == alvo:
                jogador_historico = item
                data_registro = str(item.get("data_registro", "")).strip()
                data_entrada = str(item.get("data_entrada", "")).strip()
                data_saida = str(item.get("data_saida", "")).strip()
                passagens = list(item.get("passagens", [])) if isinstance(item.get("passagens", []), list) else []
                break

        if not passagens:
            estreia = data_entrada or data_registro
            if estreia or data_saida:
                passagens = [{"data_entrada": estreia, "data_saida": data_saida}]
        if passagens:
            primeira_passagem = passagens[0]
            data_entrada = str(primeira_passagem.get("data_entrada", "")).strip()
            passagem_aberta = next((p for p in reversed(passagens) if not str(p.get("data_saida", "")).strip()), None)
            data_saida = "" if passagem_aberta else str(passagens[-1].get("data_saida", "")).strip()
        if not data_entrada:
            data_entrada = data_registro
        if not data_registro:
            data_registro = data_entrada
        data_estreia = data_entrada or data_registro

        detalhes = {
            "nome": nome,
            "geral": [
                ("Data de estreia no Vasco", data_estreia or "—"),
                ("Data de saída", data_saida or "Ainda no elenco"),
                ("Passagens pelo Vasco", len(passagens) if passagens else 1 if (data_entrada or data_saida) else 0),
            ],
            "passagens": [],
            "jogos": self._coletar_jogos_presentes_jogador(nome, jogos),
        }
        estatisticas_passagens = []
        for indice, passagem in enumerate(passagens, start=1):
            entrada = str(passagem.get("data_entrada", "")).strip()
            saida = str(passagem.get("data_saida", "")).strip()
            stats_passagem = self._coletar_estatisticas_jogador_periodo(nome, jogos, entrada, saida)
            estatisticas_passagens.append(stats_passagem)
            titulo = f"{entrada or '—'} a {saida or 'Atual'}"
            itens = [
                ("Data inicial", entrada or "—"),
                ("Data final", saida or "Atual"),
            ]
            itens.extend(
                self._formatar_detalhes_estatisticas_jogador(
                    stats_passagem
                )
            )
            detalhes["passagens"].append({
                "titulo": titulo,
                "itens": itens,
                "indice": indice,
            })
        detalhes["geral"].extend(
            self._formatar_detalhes_estatisticas_jogador(
                self._coletar_estatisticas_jogador_periodo(nome, jogos, jogador_historico=jogador_historico)
            )
        )
        return detalhes

    def _obter_jogador_historico_por_nome(self, nome):
        alvo = _chave_nome_jogador(nome)
        for item in self.jogadores_historico.get("jogadores", []):
            if isinstance(item, dict) and _chave_nome_jogador(item.get("nome", "")) == alvo:
                return item
        return None

    def _obter_jogos_pelo_vasco_salvos(self, jogador_historico):
        if not isinstance(jogador_historico, dict):
            return None
        try:
            valor = int(jogador_historico.get("jogos_pelo_vasco"))
        except (TypeError, ValueError):
            return None
        return valor if valor >= 0 else None

    def _estatisticas_importadas_jogador_no_jogo(self, nome, jogo):
        alvo = _chave_nome_jogador(nome)
        for chave in (
            "estatisticas_jogadores_vasco",
            "stats_jogadores_vasco",
            "estatisticas_individuais_vasco",
            "estatisticas_individuais_jogadores_vasco",
        ):
            bruto = jogo.get(chave)
            if isinstance(bruto, dict):
                for nome_stats, stats in bruto.items():
                    if not isinstance(stats, dict):
                        continue
                    if _chave_nome_jogador(nome_stats) == alvo:
                        return {"nome": str(nome_stats).strip(), **stats}
            elif isinstance(bruto, list):
                for stats in bruto:
                    if not isinstance(stats, dict):
                        continue
                    if _chave_nome_jogador(stats.get("nome", "")) == alvo:
                        return dict(stats)
        return {}

    def _info_participacao_jogador_no_jogo(self, nome, jogo):
        alvo = _chave_nome_jogador(nome)
        if not alvo or not isinstance(jogo, dict):
            return None
        esc_raw = jogo.get("escalacao_partida", jogo.get("escalacao"))
        if not isinstance(esc_raw, dict):
            return None
        esc = self._normalizar_escalacao_partida(esc_raw)
        duracao_partida = _duracao_partida_jogo(jogo, esc)
        substituicoes = [
            sub
            for sub in (
                _normalizar_substituicao_partida(item)
                for item in esc.get("substituicoes", [])
            )
            if sub
        ]

        em_titular = False
        posicao_titular = ""
        for pos in POSICOES_ELENCO:
            for nm in esc.get("titulares_por_posicao", {}).get(pos, []):
                if _chave_nome_jogador(nm) == alvo:
                    em_titular = True
                    posicao_titular = pos
                    break
            if em_titular:
                break

        em_reserva = any(_chave_nome_jogador(nm) == alvo for nm in esc.get("reservas", []))
        if not em_titular and not em_reserva:
            return None

        sub_entrada = next(
            (sub for sub in substituicoes if _chave_nome_jogador(sub.get("jogador_entrou", "")) == alvo),
            None,
        )
        sub_saida = next(
            (sub for sub in substituicoes if _chave_nome_jogador(sub.get("jogador_saiu", "")) == alvo),
            None,
        )

        if em_titular:
            condicao = "Titular"
            situacao = "Titular"
            entrada_txt = "Desde o início"
            if sub_saida:
                saida_txt = _formatar_minuto_periodo(sub_saida.get("minuto"), sub_saida.get("periodo"))
                minutos_jogados = min(duracao_partida, int(sub_saida.get("minuto_absoluto", duracao_partida) or duracao_partida))
            else:
                saida_txt = "Fim de jogo"
                minutos_jogados = duracao_partida
        else:
            condicao = "Reserva"
            posicao_titular = ""
            if sub_entrada:
                situacao = "Reserva (entrou)"
                entrada_txt = _formatar_minuto_periodo(sub_entrada.get("minuto"), sub_entrada.get("periodo"))
                saida_txt = "Fim de jogo"
                minutos_jogados = max(0, duracao_partida - int(sub_entrada.get("minuto_absoluto", duracao_partida) or duracao_partida))
            else:
                situacao = "Reserva (não entrou)"
                entrada_txt = "Não entrou"
                saida_txt = "—"
                minutos_jogados = 0

        gols_eventos = [
            evento for evento in _expandir_eventos_gol(jogo.get("gols_vasco", []))
            if _chave_nome_jogador(evento.get("nome", "")) == alvo
        ]
        assistencias_eventos = [
            evento for evento in _expandir_eventos_gol(jogo.get("gols_vasco", []))
            if _chave_nome_jogador(evento.get("assistencia", "")) == alvo
        ]
        gols_anulados = jogo.get("gols_anulados", {}) if isinstance(jogo.get("gols_anulados"), dict) else {}
        gols_anulados_eventos = [
            evento for evento in _expandir_eventos_gol(gols_anulados.get("vasco", []))
            if _chave_nome_jogador(evento.get("nome", "")) == alvo
        ]
        gols_momentos = [
            _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo"))
            for evento in gols_eventos
            if evento.get("minuto") is not None
        ]
        gols_anulados_momentos = [
            _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo"))
            for evento in gols_anulados_eventos
            if evento.get("minuto") is not None
        ]
        assistencias_desc = []
        for evento in assistencias_eventos:
            marcador = str(evento.get("nome", "")).strip() or "Gol do Vasco"
            minuto = _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo")) if evento.get("minuto") is not None else ""
            assistencias_desc.append(f"{marcador} ({minuto})" if minuto else marcador)

        cartoes_amarelos = sum(
            1 for evento in _expandir_eventos_cartao(jogo.get("cartoes_amarelos_vasco", []))
            if _chave_nome_jogador(evento.get("nome", "")) == alvo
        )
        cartoes_vermelhos = sum(
            1 for evento in _expandir_eventos_cartao(jogo.get("cartoes_vermelhos_vasco", []))
            if _chave_nome_jogador(evento.get("nome", "")) == alvo
        )

        return {
            "condicao": condicao,
            "situacao": situacao,
            "posicao": posicao_titular,
            "minutos": max(0, int(minutos_jogados or 0)),
            "entrada": entrada_txt,
            "saida": saida_txt,
            "sub_entrada": sub_entrada,
            "sub_saida": sub_saida,
            "gols": len(gols_eventos),
            "gols_momentos": gols_momentos,
            "gols_anulados": len(gols_anulados_eventos),
            "gols_anulados_momentos": gols_anulados_momentos,
            "assistencias": len(assistencias_eventos),
            "assistencias_desc": assistencias_desc,
            "cartoes_amarelos": cartoes_amarelos,
            "cartoes_vermelhos": cartoes_vermelhos,
            "capitao": _chave_nome_jogador(jogo.get("capitao", "")) == alvo,
            "estatisticas_importadas": self._estatisticas_importadas_jogador_no_jogo(nome, jogo),
        }

    def _coletar_jogos_presentes_jogador(self, nome, jogos=None, data_entrada="", data_saida=""):
        if jogos is None:
            jogos = carregar_dados_jogos()
        data_entrada_dt = _parse_data_ptbr_safe(data_entrada) if data_entrada else None
        data_saida_dt = _parse_data_ptbr_safe(data_saida) if data_saida else None
        linhas = []
        for idx_global, jogo in enumerate(jogos if isinstance(jogos, list) else []):
            if not isinstance(jogo, dict):
                continue
            data_txt = str(jogo.get("data", "")).strip()
            data_dt = _parse_data_ptbr_safe(data_txt)
            if data_entrada_dt and data_dt and data_dt < data_entrada_dt:
                continue
            if data_saida_dt and data_dt and data_dt > data_saida_dt:
                continue
            info = self._info_participacao_jogador_no_jogo(nome, jogo)
            if not info:
                continue
            linhas.append({
                "idx": idx_global,
                "raw": jogo,
                "data_ord": data_dt or datetime.min,
                "data": data_txt,
                "local": "Fora" if str(jogo.get("local", "")).strip().casefold() == "fora" else "Casa",
                "competicao": str(jogo.get("competicao", "") or "").strip(),
                "adversario": str(jogo.get("adversario", "") or "").strip(),
                "placar": self._placar_detalhe_partida(jogo),
                "resultado": self._resultado_detalhe_partida(jogo),
                "tecnico": str(jogo.get("tecnico", "") or "").strip(),
                "condicao": info.get("condicao", ""),
                "situacao": info.get("situacao", ""),
                "minutos": info.get("minutos", 0),
                "gols": info.get("gols", 0),
                "assistencias": info.get("assistencias", 0),
            })
        return sorted(
            linhas,
            key=lambda item: (item.get("data_ord") or datetime.min, int(item.get("idx", 0) or 0)),
            reverse=True,
        )

    def _coletar_estatisticas_jogador_periodo(self, nome, jogos, data_entrada="", data_saida="", jogador_historico=None):
        alvo = _chave_nome_jogador(nome)
        if jogador_historico is None:
            jogador_historico = self._obter_jogador_historico_por_nome(nome)
        data_entrada_dt = _parse_data_ptbr_safe(data_entrada) if data_entrada else None
        data_saida_dt = _parse_data_ptbr_safe(data_saida) if data_saida else None
        jogos_filtrados = []
        for jogo in _ordenar_jogos_por_data(jogos):
            data_jogo = str(jogo.get("data", "")).strip()
            data_jogo_dt = _parse_data_ptbr_safe(data_jogo)
            if data_entrada_dt and data_jogo_dt and data_jogo_dt < data_entrada_dt:
                continue
            if data_saida_dt and data_jogo_dt and data_jogo_dt > data_saida_dt:
                continue
            jogos_filtrados.append(jogo)

        jogos_com_escalacao = 0
        jogos_com_participacao = 0
        jogos_titular = 0
        jogos_reserva = 0
        jogos_reserva_sem_entrar = 0
        minutos_jogados = 0
        jogos_nao_rel = 0
        jogos_lesionado = 0
        jogos_suspenso = 0
        jogos_servindo_selecao = 0
        gols = 0
        assistencias = 0
        partidas_com_gol = 0
        partidas_com_assistencia = 0
        gols_banco = 0
        gols_titular = 0
        jogos_como_capitao = 0
        vitorias = empates = derrotas = 0
        cartoes_amarelos = 0
        cartoes_vermelhos = 0
        marcacoes_gol = []

        for indice_jogo, jogo in enumerate(jogos_filtrados):
            participou = False
            gol_no_jogo = 0
            assistencia_no_jogo = 0
            gol_banco_jogo = 0
            esc = jogo.get("escalacao_partida", jogo.get("escalacao"))
            em_titulares = False
            em_reservas = False
            em_nao_rel = False
            em_lesionados = False
            em_suspensos = False
            em_servindo_selecao = False

            if isinstance(esc, dict):
                jogos_com_escalacao += 1
                duracao_partida = _duracao_partida_jogo(jogo, esc)
                substituicoes = [
                    sub
                    for sub in (
                        _normalizar_substituicao_partida(item)
                        for item in esc.get("substituicoes", [])
                    )
                    if sub
                ]
                tit_por_pos = esc.get("titulares_por_posicao", {})
                if isinstance(tit_por_pos, dict):
                    for pos in POSICOES_ELENCO:
                        for nm in tit_por_pos.get(pos, []):
                            if _chave_nome_jogador(nm) == alvo:
                                em_titulares = True
                                break
                        if em_titulares:
                            break
                if not em_titulares:
                    for nm in esc.get("titulares", []):
                        if _chave_nome_jogador(nm) == alvo:
                            em_titulares = True
                            break
                reservas_que_entraram = _nomes_reservas_que_entraram_escalacao(esc)
                em_reservas = any(_chave_nome_jogador(nm) == alvo for nm in reservas_que_entraram)
                em_nao_rel = any(_chave_nome_jogador(nm) == alvo for nm in esc.get("nao_relacionados", []))
                em_lesionados = any(_chave_nome_jogador(nm) == alvo for nm in esc.get("lesionados", []))
                em_suspensos = any(_chave_nome_jogador(nm) == alvo for nm in esc.get("suspensos", []))
                em_servindo_selecao = any(_chave_nome_jogador(nm) == alvo for nm in esc.get("servindo_selecao", []))

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    nome_g = str(g.get("nome", "")).strip()
                    if _chave_nome_jogador(nome_g) != alvo:
                        continue
                    try:
                        qtd = int(g.get("gols", 0))
                    except Exception:
                        qtd = 0
                    if qtd <= 0:
                        continue
                    gol_no_jogo += qtd
                    minutos = _normalizar_lista_minutos(g.get("minutos", []))
                    periodos = [str(periodo).strip() for periodo in g.get("periodos", [])] if isinstance(g.get("periodos", []), list) else []
                    for idx in range(qtd):
                        minuto_abs = _minuto_absoluto_evento(
                            minutos[idx] if idx < len(minutos) else None,
                            periodos[idx] if idx < len(periodos) else "",
                        )
                        if minuto_abs is not None:
                            marcacoes_gol.append(indice_jogo * 90 + minuto_abs)
                    saiu_do_banco = bool(g.get("saiu_do_banco", False))
                    if not saiu_do_banco and em_reservas and not em_titulares:
                        saiu_do_banco = True
                    if saiu_do_banco:
                        gol_banco_jogo += qtd
                elif isinstance(g, str):
                    nome_g = g.strip()
                    if _chave_nome_jogador(nome_g) == alvo:
                        gol_no_jogo += 1
                        if em_reservas and not em_titulares:
                            gol_banco_jogo += 1

            amarelos_jogo = sum(
                1 for nome_cartao in self._nomes_expandidos_cartoes(jogo, "cartoes_amarelos_vasco")
                if _chave_nome_jogador(nome_cartao) == alvo
            )
            vermelhos_jogo = sum(
                1 for nome_cartao in self._nomes_expandidos_cartoes(jogo, "cartoes_vermelhos_vasco")
                if _chave_nome_jogador(nome_cartao) == alvo
            )
            cartoes_amarelos += amarelos_jogo
            cartoes_vermelhos += vermelhos_jogo

            if gol_no_jogo > 0:
                participou = True
                gols += gol_no_jogo
                partidas_com_gol += 1
                gols_banco += gol_banco_jogo
                gols_titular += max(0, gol_no_jogo - gol_banco_jogo)

            for evento_gol in _expandir_eventos_gol(jogo.get("gols_vasco", [])):
                assistencia = str(evento_gol.get("assistencia", "") or "").strip()
                if assistencia and _chave_nome_jogador(assistencia) == alvo:
                    assistencia_no_jogo += 1
            if assistencia_no_jogo > 0:
                participou = True
                assistencias += assistencia_no_jogo
                partidas_com_assistencia += 1

            if _chave_nome_jogador(jogo.get("capitao", "")) == alvo:
                jogos_como_capitao += 1

            if isinstance(esc, dict):
                if em_titulares:
                    jogos_titular += 1
                    minutos_jogo = duracao_partida
                    for sub in substituicoes:
                        if _chave_nome_jogador(sub.get("jogador_saiu", "")) == alvo:
                            minutos_jogo = min(duracao_partida, int(sub.get("minuto_absoluto", duracao_partida) or duracao_partida))
                            break
                    minutos_jogados += max(0, minutos_jogo)
                    participou = True
                elif em_reservas:
                    jogos_reserva += 1
                    minutos_jogo = 0
                    for sub in substituicoes:
                        if _chave_nome_jogador(sub.get("jogador_entrou", "")) == alvo:
                            minutos_jogo = max(0, duracao_partida - int(sub.get("minuto_absoluto", duracao_partida) or duracao_partida))
                            break
                    minutos_jogados += max(0, minutos_jogo)
                    participou = True
                elif any(_chave_nome_jogador(nm) == alvo for nm in esc.get("reservas", [])):
                    jogos_reserva_sem_entrar += 1
                elif em_nao_rel:
                    jogos_nao_rel += 1
                elif em_lesionados:
                    jogos_lesionado += 1
                elif em_suspensos:
                    jogos_suspenso += 1
                elif em_servindo_selecao:
                    jogos_servindo_selecao += 1

            if participou:
                jogos_com_participacao += 1
                placar = jogo.get("placar", {})
                try:
                    vasco = int(placar.get("vasco", 0))
                    adv = int(placar.get("adversario", 0))
                except Exception:
                    vasco = adv = 0
                if vasco > adv:
                    vitorias += 1
                elif vasco == adv:
                    empates += 1
                else:
                    derrotas += 1

        media_gols = round(gols / jogos_com_participacao, 2) if jogos_com_participacao else 0.0
        media_minutos_jogados = round(minutos_jogados / jogos_com_participacao, 2) if jogos_com_participacao else 0.0
        jogos_com_participacao_desconhecido = False
        minutos_jogados_desconhecido = False
        if not data_entrada and not data_saida:
            jogos_salvos = self._obter_jogos_pelo_vasco_salvos(jogador_historico)
            if jogos_salvos is not None:
                jogos_com_participacao = jogos_salvos
                media_gols = round(gols / jogos_salvos, 2) if jogos_salvos else 0.0
                media_minutos_jogados = round(minutos_jogados / jogos_salvos, 2) if jogos_salvos else 0.0
            elif jogos_com_participacao == 0:
                jogos_com_participacao_desconhecido = True
                minutos_jogados_desconhecido = True
                media_gols = None
                media_minutos_jogados = None
        media_minutos_entre_gols = None
        if len(marcacoes_gol) >= 2:
            diferencas = [
                marcacoes_gol[i] - marcacoes_gol[i - 1]
                for i in range(1, len(marcacoes_gol))
            ]
            if diferencas:
                media_minutos_entre_gols = round(sum(diferencas) / len(diferencas), 2)
        return {
            "jogos_com_participacao": jogos_com_participacao,
            "jogos_com_participacao_desconhecido": jogos_com_participacao_desconhecido,
            "minutos_jogados": minutos_jogados,
            "minutos_jogados_desconhecido": minutos_jogados_desconhecido,
            "jogos_titular": jogos_titular,
            "jogos_reserva": jogos_reserva,
            "jogos_reserva_sem_entrar": jogos_reserva_sem_entrar,
            "jogos_nao_rel": jogos_nao_rel,
            "jogos_lesionado": jogos_lesionado,
            "jogos_suspenso": jogos_suspenso,
            "jogos_servindo_selecao": jogos_servindo_selecao,
            "gols": gols,
            "assistencias": assistencias,
            "participacoes_gol": gols + assistencias,
            "jogos_como_capitao": jogos_como_capitao,
            "partidas_com_gol": partidas_com_gol,
            "partidas_com_assistencia": partidas_com_assistencia,
            "gols_titular": gols_titular,
            "gols_banco": gols_banco,
            "media_minutos_jogados": media_minutos_jogados,
            "media_gols": media_gols,
            "cartoes_amarelos": cartoes_amarelos,
            "cartoes_vermelhos": cartoes_vermelhos,
            "media_minutos_entre_gols": media_minutos_entre_gols,
            "participacao_ved": f"{vitorias}/{empates}/{derrotas}",
        }

    def _formatar_detalhes_estatisticas_jogador(self, stats):
        jogos_participacao = (
            "Número desconhecido"
            if stats.get("jogos_com_participacao_desconhecido")
            else stats.get("jogos_com_participacao", 0)
        )
        media_gols = stats.get("media_gols", 0.0)
        minutos_jogados = (
            "Número desconhecido"
            if stats.get("minutos_jogados_desconhecido")
            else stats.get("minutos_jogados", 0)
        )
        media_minutos_jogados = stats.get("media_minutos_jogados", 0.0)
        if stats.get("jogos_com_participacao_desconhecido") and media_gols is None:
            media_gols = "Número desconhecido"
        if stats.get("minutos_jogados_desconhecido") and media_minutos_jogados is None:
            media_minutos_jogados = "Número desconhecido"
        return [
            ("Jogos com participação", jogos_participacao),
            ("Minutos jogados", minutos_jogados),
            ("Média de minutos jogados", media_minutos_jogados),
            ("Jogos como titular", stats.get("jogos_titular", 0)),
            ("Jogos como reserva", stats.get("jogos_reserva", 0)),
            ("Foi para o jogo e não entrou", stats.get("jogos_reserva_sem_entrar", 0)),
            ("Jogos como não relacionado", stats.get("jogos_nao_rel", 0)),
            ("Jogos como lesionado", stats.get("jogos_lesionado", 0)),
            ("Jogos como suspenso", stats.get("jogos_suspenso", 0)),
            ("Jogos servindo a seleção", stats.get("jogos_servindo_selecao", 0)),
            ("Gols pelo Vasco", stats.get("gols", 0)),
            ("Assistências", stats.get("assistencias", 0)),
            ("Participações em gol", stats.get("participacoes_gol", 0)),
            ("Jogos como capitão", stats.get("jogos_como_capitao", 0)),
            ("Partidas em que marcou", stats.get("partidas_com_gol", 0)),
            ("Partidas com assistência", stats.get("partidas_com_assistencia", 0)),
            ("Gols como titular", stats.get("gols_titular", 0)),
            ("Gols saindo do banco", stats.get("gols_banco", 0)),
            ("Média de gols por jogo", media_gols),
            ("Cartões amarelos", stats.get("cartoes_amarelos", 0)),
            ("Cartões vermelhos", stats.get("cartoes_vermelhos", 0)),
            (
                "Média de minutos entre gols",
                stats.get("media_minutos_entre_gols")
                if stats.get("media_minutos_entre_gols") is not None
                else "—",
            ),
            ("Participação (V/E/D)", stats.get("participacao_ved", "0/0/0")),
        ]

    def _somar_estatisticas_passagens(self, stats_passagens):
        totais = {
            "jogos_com_participacao": 0,
            "minutos_jogados": 0,
            "minutos_jogados_desconhecido": False,
            "jogos_titular": 0,
            "jogos_reserva": 0,
            "jogos_reserva_sem_entrar": 0,
            "jogos_nao_rel": 0,
            "jogos_lesionado": 0,
            "jogos_suspenso": 0,
            "jogos_servindo_selecao": 0,
            "gols": 0,
            "assistencias": 0,
            "participacoes_gol": 0,
            "jogos_como_capitao": 0,
            "partidas_com_gol": 0,
            "partidas_com_assistencia": 0,
            "gols_titular": 0,
            "gols_banco": 0,
            "media_minutos_jogados": 0.0,
            "media_gols": 0.0,
            "cartoes_amarelos": 0,
            "cartoes_vermelhos": 0,
            "media_minutos_entre_gols": None,
            "participacao_ved": "0/0/0",
        }
        vitorias = empates = derrotas = 0
        for item in stats_passagens:
            if not isinstance(item, dict):
                continue
            for chave in (
                "jogos_com_participacao",
                "minutos_jogados",
                "jogos_titular",
                "jogos_reserva",
                "jogos_reserva_sem_entrar",
                "jogos_nao_rel",
                "jogos_lesionado",
                "jogos_suspenso",
                "jogos_servindo_selecao",
                "gols",
                "assistencias",
                "participacoes_gol",
                "jogos_como_capitao",
                "partidas_com_gol",
                "partidas_com_assistencia",
                "gols_titular",
                "gols_banco",
                "cartoes_amarelos",
                "cartoes_vermelhos",
            ):
                totais[chave] += int(item.get(chave, 0) or 0)
            totais["minutos_jogados_desconhecido"] = bool(
                totais["minutos_jogados_desconhecido"] or item.get("minutos_jogados_desconhecido")
            )
            ved = str(item.get("participacao_ved", "0/0/0"))
            try:
                vit, emp, der = [int(p or 0) for p in ved.split("/", 2)]
            except Exception:
                vit = emp = der = 0
            vitorias += vit
            empates += emp
            derrotas += der
        jogos_com_participacao = int(totais.get("jogos_com_participacao", 0) or 0)
        gols = int(totais.get("gols", 0) or 0)
        minutos_jogados = int(totais.get("minutos_jogados", 0) or 0)
        totais["media_minutos_jogados"] = round(minutos_jogados / jogos_com_participacao, 2) if jogos_com_participacao else 0.0
        totais["media_gols"] = round(gols / jogos_com_participacao, 2) if jogos_com_participacao else 0.0
        totais["participacao_ved"] = f"{vitorias}/{empates}/{derrotas}"
        return totais

    def _criar_tree_detalhes_jogador_historico(self, parent):
        frame = ttk.Frame(parent, padding=(0, 4, 0, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tv = ttk.Treeview(
            frame,
            columns=("metrica", "valor"),
            show="headings",
            height=16,
        )
        tv.heading("metrica", text="Métrica")
        tv.heading("valor", text="Valor")
        tv.column("metrica", width=320, anchor="w")
        tv.column("valor", width=180, anchor="w")
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        sy.grid(row=0, column=1, sticky="ns")
        tv.configure(yscrollcommand=sy.set)
        return frame, tv

    def _criar_tree_jogos_jogador_historico(self, parent):
        frame = ttk.Frame(parent, padding=(0, 4, 0, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        cols = (
            "data",
            "local",
            "competicao",
            "adversario",
            "placar",
            "resultado",
            "tecnico",
            "condicao",
            "minutos",
            "gols",
            "assistencias",
        )
        tv = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            height=16,
        )
        headings = {
            "data": "Data",
            "local": "Local",
            "competicao": "Competição",
            "adversario": "Adversário",
            "placar": "Placar",
            "resultado": "Resultado",
            "tecnico": "Técnico",
            "condicao": "Condição",
            "minutos": "Min.",
            "gols": "Gols",
            "assistencias": "Ass.",
        }
        widths = {
            "data": 90,
            "local": 70,
            "competicao": 150,
            "adversario": 150,
            "placar": 220,
            "resultado": 110,
            "tecnico": 140,
            "condicao": 95,
            "minutos": 60,
            "gols": 55,
            "assistencias": 55,
        }
        for col in cols:
            tv.heading(col, text=headings[col])
            anchor = "e" if col in {"minutos", "gols", "assistencias"} else "w"
            tv.column(col, width=widths[col], anchor=anchor, stretch=True)
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        sy.grid(row=0, column=1, sticky="ns")
        sx = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        sx.grid(row=1, column=0, sticky="ew")
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        return frame, tv

    def _on_jogos_jogador_double_click(self, event):
        tree = event.widget
        iid = tree.identify_row(event.y)
        if not iid:
            return
        mapping = getattr(tree, "_item_to_idx", {})
        jogo_idx = mapping.get(iid)
        if jogo_idx is None:
            return
        nome = str(getattr(tree, "_jogador_nome", "") or "").strip()
        if not nome:
            return
        tree.selection_set(iid)
        self._abrir_aba_detalhe_jogo_jogador(nome, jogo_idx)

    def _formatar_nome_estatistica_jogador(self, chave):
        labels = {
            "assistencias": "Assistências",
            "cruzamentos_certos": "Cruzamentos certos",
            "cruzamentos_errados": "Cruzamentos errados",
            "cruzamentos_tentados": "Cruzamentos tentados",
            "desarmes": "Desarmes",
            "duelos_aereos_ganhos": "Duelos aéreos ganhos",
            "duelos_ganhos": "Duelos ganhos",
            "escanteios": "Escanteios",
            "faltas_cometidas": "Faltas cometidas",
            "faltas_recebidas": "Faltas recebidas",
            "finalizacoes": "Finalizações",
            "finalizacoes_bloqueadas": "Finalizações bloqueadas",
            "finalizacoes_fora": "Finalizações fora",
            "finalizacoes_no_gol": "Finalizações no gol",
            "impedimentos": "Impedimentos",
            "interceptacoes": "Interceptações",
            "lancamentos_certos": "Lançamentos certos",
            "lancamentos_errados": "Lançamentos errados",
            "lancamentos_tentados": "Lançamentos tentados",
            "minutos": "Minutos",
            "nota": "Nota",
            "nota_sofascore": "Nota SofaScore",
            "passes_certos": "Passes certos",
            "passes_errados": "Passes errados",
            "passes_tentados": "Passes tentados",
            "posse_bola": "Posse de bola",
            "precisao_cruzamentos": "Precisão de cruzamentos",
            "precisao_lancamentos": "Precisão de lançamentos",
            "precisao_passes": "Precisão de passes",
            "xg": "xG",
        }
        chave_txt = str(chave or "").strip()
        if chave_txt in labels:
            return labels[chave_txt]
        texto = chave_txt.replace("_", " ").strip()
        return texto[:1].upper() + texto[1:] if texto else "Estatística"

    def _formatar_valor_estatistica_jogador(self, chave, valor):
        if valor in (None, ""):
            return "—"
        if isinstance(valor, float) and valor.is_integer():
            valor = int(valor)
        texto = self._texto_detalhe_partida(valor)
        if chave in ESTATISTICAS_PERCENTUAIS and texto != "—" and not str(texto).strip().endswith("%"):
            texto = f"{texto}%"
        return texto

    def _valor_numerico_estatistica(self, valor):
        if valor in (None, "") or isinstance(valor, bool):
            return None
        if isinstance(valor, (int, float)):
            if isinstance(valor, float) and not math.isfinite(valor):
                return None
            return float(valor)
        if not isinstance(valor, str):
            return None
        texto = str(valor).strip()
        if not texto:
            return None
        texto = texto.replace("%", "").strip()
        texto = re.sub(r"[^0-9,\.\-]", "", texto)
        if not texto or texto in {"-", ".", ","}:
            return None
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            texto = texto.replace(",", ".")
        try:
            numero = float(texto)
        except Exception:
            return None
        return numero if math.isfinite(numero) else None

    def _estatistica_agregada_por_media(self, chave):
        chave = str(chave or "").strip()
        return chave in ESTATISTICAS_PERCENTUAIS or chave in {"nota", "nota_sofascore"}

    def _formatar_valor_estatistica_agregada(self, chave, valor):
        if valor is None:
            return "—"
        if isinstance(valor, float):
            valor = round(valor, 2)
            if valor.is_integer():
                valor = int(valor)
        return self._formatar_valor_estatistica_jogador(chave, valor)

    def _agregar_estatisticas_vasco_jogos(self, jogos):
        estatisticas_time = defaultdict(lambda: {"total": 0.0, "qtd": 0})
        estatisticas_jogadores = defaultdict(lambda: defaultdict(lambda: {"total": 0.0, "qtd": 0}))
        jogos_com_scout_time = 0
        jogos_com_scout_jogadores = 0

        for jogo in jogos:
            if not isinstance(jogo, dict):
                continue
            stats_time = jogo.get("estatisticas_vasco")
            if isinstance(stats_time, dict) and stats_time:
                tem_scout_numerico = False
                for chave, valor in stats_time.items():
                    numero = self._valor_numerico_estatistica(valor)
                    if numero is None:
                        continue
                    bucket = estatisticas_time[str(chave)]
                    bucket["total"] += numero
                    bucket["qtd"] += 1
                    tem_scout_numerico = True
                if tem_scout_numerico:
                    jogos_com_scout_time += 1

            stats_jogadores = jogo.get("estatisticas_jogadores_vasco")
            if isinstance(stats_jogadores, list) and stats_jogadores:
                tem_scout_jogador = False
                for item in stats_jogadores:
                    if not isinstance(item, dict):
                        continue
                    nome = str(item.get("nome", "") or "").strip()
                    if not nome:
                        continue
                    for chave, valor in item.items():
                        if str(chave).strip() == "nome":
                            continue
                        numero = self._valor_numerico_estatistica(valor)
                        if numero is None:
                            continue
                        bucket = estatisticas_jogadores[nome][str(chave)]
                        bucket["total"] += numero
                        bucket["qtd"] += 1
                        tem_scout_jogador = True
                if tem_scout_jogador:
                    jogos_com_scout_jogadores += 1

        chaves_time = self._ordenar_chaves_estatisticas_jogador({chave: True for chave in estatisticas_time.keys()})
        linhas_time = []
        for chave in chaves_time:
            bucket = estatisticas_time[chave]
            qtd = bucket["qtd"]
            total = bucket["total"]
            media = total / qtd if qtd else None
            total_fmt = "—" if self._estatistica_agregada_por_media(chave) else self._formatar_valor_estatistica_agregada(chave, total)
            linhas_time.append({
                "chave": chave,
                "estatistica": self._formatar_nome_estatistica_jogador(chave),
                "total": total_fmt,
                "media": self._formatar_valor_estatistica_agregada(chave, media),
                "jogos": qtd,
            })

        linhas_jogadores = []
        for nome in sorted(estatisticas_jogadores.keys(), key=lambda s: s.casefold()):
            chaves = self._ordenar_chaves_estatisticas_jogador({chave: True for chave in estatisticas_jogadores[nome].keys()})
            for chave in chaves:
                bucket = estatisticas_jogadores[nome][chave]
                qtd = bucket["qtd"]
                total = bucket["total"]
                media = total / qtd if qtd else None
                total_fmt = "—" if self._estatistica_agregada_por_media(chave) else self._formatar_valor_estatistica_agregada(chave, total)
                linhas_jogadores.append({
                    "jogador": nome,
                    "chave": chave,
                    "estatistica": self._formatar_nome_estatistica_jogador(chave),
                    "total": total_fmt,
                    "media": self._formatar_valor_estatistica_agregada(chave, media),
                    "jogos": qtd,
                })

        def media_time(chave):
            bucket = estatisticas_time.get(chave)
            if not bucket or not bucket["qtd"]:
                return None
            return bucket["total"] / bucket["qtd"]

        def total_time(chave):
            bucket = estatisticas_time.get(chave)
            return bucket["total"] if bucket and bucket["qtd"] else None

        resumo = {
            "jogos": len(jogos),
            "jogos_com_scout_time": jogos_com_scout_time,
            "jogos_com_scout_jogadores": jogos_com_scout_jogadores,
            "posse_media": media_time("posse_bola"),
            "finalizacoes_total": total_time("finalizacoes"),
            "finalizacoes_no_gol_total": total_time("finalizacoes_no_gol"),
            "escanteios_total": total_time("escanteios"),
        }
        return linhas_time, linhas_jogadores, resumo

    def _ordenar_chaves_estatisticas_jogador(self, stats):
        ordem = [
            "minutos",
            "nota",
            "nota_sofascore",
            "gols",
            "assistencias",
            "xg",
            "finalizacoes",
            "finalizacoes_no_gol",
            "finalizacoes_fora",
            "finalizacoes_bloqueadas",
            "passes_certos",
            "passes_errados",
            "passes_tentados",
            "precisao_passes",
            "cruzamentos_certos",
            "cruzamentos_errados",
            "cruzamentos_tentados",
            "lancamentos_certos",
            "lancamentos_errados",
            "lancamentos_tentados",
            "desarmes",
            "interceptacoes",
            "duelos_ganhos",
            "duelos_aereos_ganhos",
            "faltas_cometidas",
            "faltas_recebidas",
            "impedimentos",
        ]
        ordem_map = {chave: idx for idx, chave in enumerate(ordem)}
        return sorted(
            [chave for chave in stats.keys() if str(chave).strip() != "nome"],
            key=lambda chave: (ordem_map.get(chave, 999), self._formatar_nome_estatistica_jogador(chave).casefold()),
        )

    def _linhas_detalhe_jogo_jogador(self, nome, jogo, info):
        arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
        linhas = [
            ("Partida", "Dados da partida"),
            ("Data", jogo.get("data", "")),
            ("Competição", jogo.get("competicao", "")),
            ("Adversário", jogo.get("adversario", "")),
            ("Local", "Fora" if str(jogo.get("local", "")).casefold() == "fora" else "Casa"),
            ("Placar", self._placar_detalhe_partida(jogo)),
            ("Resultado", self._resultado_detalhe_partida(jogo)),
            ("Estádio", jogo.get("estadio", "")),
            ("Horário", jogo.get("horario", "")),
            ("Técnico", jogo.get("tecnico", "")),
            ("Capitão da partida", jogo.get("capitao", "")),
            ("Posição na tabela", jogo.get("posicao_tabela", "")),
            ("Público pagante", _formatar_publico(jogo.get("publico_pagante"))),
            ("Público presente", _formatar_publico(jogo.get("publico_presente"))),
            ("Renda", _formatar_renda_brl(jogo.get("renda"))),
            ("Árbitro", arbitragem.get("arbitro", "")),
            ("Auxiliares", arbitragem.get("auxiliares", [])),
            ("VAR", arbitragem.get("var", "")),
            ("ID da partida no banco", jogo.get("db_match_id", "")),
            ("Participação do jogador", "Escalação e minutos"),
            ("Jogador", nome),
            ("Condição no jogo", info.get("condicao", "")),
            ("Situação", info.get("situacao", "")),
            ("Posição", info.get("posicao", "") or "—"),
            ("Minutos jogados", info.get("minutos", 0)),
            ("Entrada", info.get("entrada", "")),
            ("Saída", info.get("saida", "")),
            ("Foi capitão", "Sim" if info.get("capitao") else "Não"),
            ("Eventos do jogador", "Gols, assistências e cartões"),
            ("Gols", info.get("gols", 0)),
            ("Minutos dos gols", info.get("gols_momentos", [])),
            ("Gols anulados", info.get("gols_anulados", 0)),
            ("Minutos dos gols anulados", info.get("gols_anulados_momentos", [])),
            ("Assistências", info.get("assistencias", 0)),
            ("Jogadas assistidas", info.get("assistencias_desc", [])),
            ("Cartões amarelos", info.get("cartoes_amarelos", 0)),
            ("Cartões vermelhos", info.get("cartoes_vermelhos", 0)),
        ]

        stats = info.get("estatisticas_importadas", {})
        linhas.append(("Estatísticas importadas", "Stats individuais do jogo"))
        if isinstance(stats, dict) and any(str(chave).strip() != "nome" for chave in stats.keys()):
            for chave in self._ordenar_chaves_estatisticas_jogador(stats):
                linhas.append((
                    self._formatar_nome_estatistica_jogador(chave),
                    self._formatar_valor_estatistica_jogador(chave, stats.get(chave)),
                ))
        else:
            linhas.append(("Stats individuais", "Sem dados importados para este jogador."))

        observacao = str(jogo.get("observacao", "") or "").strip()
        if observacao:
            linhas.append(("Observação da partida", observacao))
        return linhas

    def _abrir_aba_detalhe_jogo_jogador(self, nome, jogo_idx):
        if not hasattr(self, "detalhes_jogador_notebook"):
            return
        jogos = carregar_dados_jogos()
        if not (0 <= int(jogo_idx) < len(jogos)):
            messagebox.showerror("Jogadores", "Não foi possível carregar o jogo selecionado.")
            return
        jogo = jogos[int(jogo_idx)]
        info = self._info_participacao_jogador_no_jogo(nome, jogo)
        if not info:
            messagebox.showinfo("Jogadores", "O jogador não aparece como titular ou reserva nesse jogo.")
            return

        if not hasattr(self, "_detalhes_jogador_jogo_tabs"):
            self._detalhes_jogador_jogo_tabs = {}
        tab_key = f"jogo_{jogo_idx}"
        frame_existente = self._detalhes_jogador_jogo_tabs.get(tab_key)
        if frame_existente is not None and frame_existente.winfo_exists():
            self.detalhes_jogador_notebook.select(frame_existente)
            return

        frame = ttk.Frame(self.detalhes_jogador_notebook, padding=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        titulo = f"{self._placar_detalhe_partida(jogo)} - {info.get('situacao', info.get('condicao', ''))}"
        ttk.Label(frame, text=titulo, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        wrap, tv = self._criar_tree_detalhes_jogador_historico(frame)
        wrap.grid(row=1, column=0, sticky="nsew")
        for i, (campo, valor) in enumerate(self._linhas_detalhe_jogo_jogador(nome, jogo, info), start=1):
            tv.insert("", "end", values=(campo, self._texto_detalhe_partida(valor)), tags=("odd",) if i % 2 else ())

        data_txt = str(jogo.get("data", "") or "").strip() or "Jogo"
        adversario = str(jogo.get("adversario", "") or "").strip()
        tab_text = f"{data_txt[:5]} {adversario[:10]}".strip()
        self.detalhes_jogador_notebook.add(frame, text=tab_text or "Jogo")
        self._detalhes_jogador_jogo_tabs[tab_key] = frame
        self.detalhes_jogador_notebook.select(frame)

    def _render_detalhes_jogador_historico(self, detalhes):
        if not hasattr(self, "detalhes_jogador_notebook"):
            return
        for tab_id in self.detalhes_jogador_notebook.tabs():
            self.detalhes_jogador_notebook.forget(tab_id)
        self._detalhes_jogador_abas = {}
        self._detalhes_jogador_jogo_tabs = {}

        frame_geral, tv_geral = self._criar_tree_detalhes_jogador_historico(self.detalhes_jogador_notebook)
        self.detalhes_jogador_notebook.add(frame_geral, text="Geral")
        self._detalhes_jogador_abas["geral"] = tv_geral
        for i, (metrica, valor) in enumerate(detalhes.get("geral", []), start=1):
            tv_geral.insert("", "end", values=(metrica, valor), tags=("odd",) if i % 2 else ())

        frame_jogos, tv_jogos = self._criar_tree_jogos_jogador_historico(self.detalhes_jogador_notebook)
        self.detalhes_jogador_notebook.add(frame_jogos, text="Jogos")
        self._detalhes_jogador_abas["jogos"] = tv_jogos
        tv_jogos._item_to_idx = {}
        tv_jogos._jogador_nome = str(detalhes.get("nome", "") or "").strip()
        jogos_jogador = detalhes.get("jogos", [])
        if jogos_jogador:
            for i, row in enumerate(jogos_jogador, start=1):
                iid = tv_jogos.insert(
                    "",
                    "end",
                    values=(
                        row.get("data", ""),
                        row.get("local", ""),
                        row.get("competicao", ""),
                        row.get("adversario", ""),
                        row.get("placar", ""),
                        self._formatar_resultado_com_bolinha(row.get("resultado", "")),
                        row.get("tecnico", ""),
                        row.get("condicao", ""),
                        row.get("minutos", 0),
                        row.get("gols", 0),
                        row.get("assistencias", 0),
                    ),
                    tags=("odd",) if i % 2 else (),
                )
                tv_jogos._item_to_idx[iid] = row.get("idx")
        else:
            tv_jogos.insert("", "end", values=("—", "—", "Sem jogos com escalação registrada", "—", "—", "—", "—", "—", "—", "—", "—"))
        tv_jogos.bind("<Double-1>", self._on_jogos_jogador_double_click)

        for passagem in detalhes.get("passagens", []):
            frame_passagem, tv_passagem = self._criar_tree_detalhes_jogador_historico(self.detalhes_jogador_notebook)
            self.detalhes_jogador_notebook.add(frame_passagem, text=passagem.get("titulo", "Passagem"))
            self._detalhes_jogador_abas[f"passagem_{passagem.get('indice', 0)}"] = tv_passagem
            for i, (metrica, valor) in enumerate(passagem.get("itens", []), start=1):
                tv_passagem.insert("", "end", values=(metrica, valor), tags=("odd",) if i % 2 else ())

    def _jogador_apareceu_em_escalacao(self, esc, alvo):
        if not isinstance(esc, dict):
            return False
        tit_por_pos = esc.get("titulares_por_posicao", {})
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                if any(_chave_nome_jogador(nm) == alvo for nm in tit_por_pos.get(pos, [])):
                    return True
        for chave in ("titulares", "reservas", "nao_relacionados", "lesionados", "suspensos", "servindo_selecao"):
            if any(_chave_nome_jogador(nm) == alvo for nm in esc.get(chave, [])):
                return True
        return False

    def _atualizar_datas_estreia_jogadores_historico(self, jogos=None):
        jogadores = self.jogadores_historico.get("jogadores", [])
        if not isinstance(jogadores, list) or not jogadores:
            return
        alterou = False
        atualizados = []
        for item in jogadores:
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            passagens = list(jogador.get("passagens", [])) if isinstance(jogador.get("passagens", []), list) else []
            data_entrada_atual = str(jogador.get("data_entrada", "")).strip()
            if not data_entrada_atual:
                jogador["data_entrada"] = str(jogador.get("data_registro", "")).strip()
                alterou = True
            if not passagens and str(jogador.get("data_entrada", "")).strip():
                jogador["passagens"] = [{
                    "data_entrada": str(jogador.get("data_entrada", "")).strip(),
                    "data_saida": str(jogador.get("data_saida", "")).strip(),
                }]
                alterou = True
            if not str(jogador.get("data_registro", "")).strip() and str(jogador.get("data_entrada", "")).strip():
                jogador["data_registro"] = str(jogador.get("data_entrada", "")).strip()
                alterou = True
            jogador = self._sincronizar_resumo_passagens_jogador(jogador)
            atualizados.append(jogador)
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(atualizados)}
        salvar_jogadores_historico(self.jogadores_historico)

    def _sincronizar_resumo_passagens_jogador(self, jogador):
        if not isinstance(jogador, dict):
            return jogador
        passagens = list(jogador.get("passagens", [])) if isinstance(jogador.get("passagens", []), list) else []
        if not passagens:
            return jogador
        jogador["data_entrada"] = str(passagens[0].get("data_entrada", "")).strip()
        passagem_aberta = next((p for p in reversed(passagens) if not str(p.get("data_saida", "")).strip()), None)
        jogador["data_saida"] = "" if passagem_aberta else str(passagens[-1].get("data_saida", "")).strip()
        return jogador

    def _retornar_jogador_ao_elenco_atual(self):
        if not hasattr(self, "tv_jogadores_historico"):
            return
        sel = self.tv_jogadores_historico.selection()
        if not sel:
            messagebox.showwarning("Jogadores", "Selecione um jogador para voltar ao elenco atual.")
            return
        vals = self.tv_jogadores_historico.item(sel[0], "values")
        if len(vals) < 3:
            return
        posicao = str(vals[0]).strip()
        nome = str(vals[1]).strip()
        status = str(vals[2]).strip()
        nome = str(nome).strip()
        if not nome:
            return
        if str(status).strip() != "Ex-jogador":
            messagebox.showinfo("Jogadores", f"'{nome}' já está no elenco atual.")
            return

        nomes_atuais_cf = {
            str(j.get("nome", "")).strip().casefold()
            for j in self.elenco_atual.get("jogadores", [])
            if isinstance(j, dict) and str(j.get("nome", "")).strip()
        }
        if nome.casefold() in nomes_atuais_cf:
            messagebox.showinfo("Jogadores", f"'{nome}' já está no elenco atual.")
            return

        self.elenco_atual.setdefault("jogadores", []).append(
            {
                "nome": nome,
                "posicao": _normalizar_posicao_elenco(posicao),
                "condicao": "Reserva",
                "capitao": False,
            }
        )
        salvar_elenco_atual(self.elenco_atual)
        self._sincronizar_jogadores_vasco_com_elenco()
        self._render_aba_jogadores_historico()

    def _abrir_menu_contexto_elenco_atual(self, event):
        iid = self.tv_elenco_atual.identify_row(event.y)
        if not iid:
            return
        selecionados = set(self.tv_elenco_atual.selection())
        if iid not in selecionados:
            self.tv_elenco_atual.selection_set(iid)
            selecionados = {iid}
        self.tv_elenco_atual.focus(iid)
        selecionados = list(self.tv_elenco_atual.selection())
        _pos, nome, _cond, eh_capitao = self._dados_linha_elenco(iid)
        selecao_unica = len(selecionados) == 1

        menu = tk.Menu(self.root, tearoff=0)
        submenu_tit = tk.Menu(menu, tearoff=0)
        for pos in POSICOES_ELENCO:
            submenu_tit.add_command(
                label=f"Titular - {pos}",
                command=lambda p=pos: self._enviar_jogador_elenco_para(("titulares", p))
            )
        menu.add_cascade(label="Enviar para Titulares", menu=submenu_tit)
        menu.add_separator()
        menu.add_command(label="Enviar para Reserva", command=lambda: self._enviar_jogador_elenco_para(("extras", "reservas")))
        menu.add_command(label="Enviar para Não Relacionado", command=lambda: self._enviar_jogador_elenco_para(("extras", "nao_relacionados")))
        menu.add_command(label="Enviar para Lesionado", command=lambda: self._enviar_jogador_elenco_para(("extras", "lesionados")))
        menu.add_command(label="Enviar para Suspenso", command=lambda: self._enviar_jogador_elenco_para(("extras", "suspensos")))
        menu.add_command(label="Enviar para Servindo a seleção", command=lambda: self._enviar_jogador_elenco_para(("extras", "servindo_selecao")))
        menu.add_command(label="Enviar para Emprestado", command=lambda: self._enviar_jogador_elenco_para(("extras", "emprestados")))
        menu.add_separator()
        menu.add_command(
            label="Remover Capitão" if eh_capitao else f"Tornar Capitão: {nome}",
            command=self._alternar_capitao_elenco_selecionado,
            state=("normal" if selecao_unica else "disabled"),
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _alternar_capitao_elenco_selecionado(self):
        sel = self.tv_elenco_atual.selection()
        if not sel:
            return
        iid_alvo = sel[0]
        posicao_alvo, nome_alvo, condicao_alvo, eh_capitao_alvo = self._dados_linha_elenco(iid_alvo)
        if not nome_alvo:
            return

        for iid in self.tv_elenco_atual.get_children():
            posicao, nome, condicao, eh_capitao = self._dados_linha_elenco(iid)
            novo_capitao = False if eh_capitao_alvo else (iid == iid_alvo)
            if eh_capitao != novo_capitao:
                self.tv_elenco_atual.item(
                    iid,
                    values=(
                        posicao,
                        _nome_exibicao_capitao(nome, novo_capitao),
                        condicao,
                        "1" if novo_capitao else "",
                    ),
                )

        if eh_capitao_alvo:
            self.tv_elenco_atual.item(
                iid_alvo,
                values=(posicao_alvo, _nome_exibicao_capitao(nome_alvo, False), condicao_alvo, ""),
            )
        else:
            self.tv_elenco_atual.item(
                iid_alvo,
                values=(posicao_alvo, _nome_exibicao_capitao(nome_alvo, True), condicao_alvo, "1"),
            )

        self._salvar_elenco_da_interface()

    def _enviar_jogador_elenco_para(self, destino):
        sel = self.tv_elenco_atual.selection()
        if not sel:
            return

        tipo, chave = destino
        if tipo == "titulares":
            nova_posicao_titular = _normalizar_posicao_elenco(chave)
            selecionados_cf = set()
            for iid in sel:
                _pos, nome, _cond, _cap = self._dados_linha_elenco(iid)
                nome = str(nome).strip()
                if nome:
                    selecionados_cf.add(nome.casefold())
            titulares_atuais = 0
            for row_iid in self.tv_elenco_atual.get_children():
                _p, row_nome, row_cond, _row_cap = self._dados_linha_elenco(row_iid)
                if (
                    _normalizar_condicao_elenco(row_cond) == "Titular"
                    and str(row_nome).strip().casefold() not in selecionados_cf
                ):
                    titulares_atuais += 1
            if titulares_atuais + len(selecionados_cf) > 11:
                messagebox.showerror("Limite de titulares", "Não é possível ter mais de 11 titulares no elenco atual.")
                return

        for iid in sel:
            posicao_atual, nome, condicao_atual, eh_capitao = self._dados_linha_elenco(iid)
            nome = str(nome).strip()
            if not nome:
                continue

            nova_posicao = str(posicao_atual).strip()
            nova_condicao = _normalizar_condicao_elenco(condicao_atual)
            if tipo == "titulares":
                nova_posicao = nova_posicao_titular
                nova_condicao = "Titular"
            else:
                if chave == "reservas":
                    nova_condicao = "Reserva"
                elif chave == "nao_relacionados":
                    nova_condicao = "Não Relacionado"
                elif chave == "lesionados":
                    nova_condicao = "Lesionado"
                elif chave == "suspensos":
                    nova_condicao = "Suspenso"
                elif chave == "servindo_selecao":
                    nova_condicao = "Servindo a seleção"
                elif chave == "emprestados":
                    nova_condicao = "Emprestado"

            self.tv_elenco_atual.item(
                iid,
                values=(nova_posicao, _nome_exibicao_capitao(nome, eh_capitao), nova_condicao, "1" if eh_capitao else ""),
            )
        self._salvar_elenco_da_interface()

    def _grupo_reordenacao_elenco(self, values):
        if len(values) < 3:
            return None
        posicao, _nome, condicao = values
        cond_norm = _normalizar_condicao_elenco(condicao)
        if cond_norm == "Titular":
            return (cond_norm, _normalizar_posicao_elenco(posicao))
        return (cond_norm, None)

    def _drag_elenco_start(self, event):
        iid = self.tv_elenco_atual.identify_row(event.y)
        if not iid:
            self._drag_elenco_state = None
            return
        grupo = self._grupo_reordenacao_elenco(self.tv_elenco_atual.item(iid, "values"))
        if not grupo:
            self._drag_elenco_state = None
            return
        self._drag_elenco_state = {"iid": iid, "grupo": grupo}

    def _drag_elenco_motion(self, event):
        st = getattr(self, "_drag_elenco_state", None)
        if not st:
            return
        origem = st.get("iid")
        alvo = self.tv_elenco_atual.identify_row(event.y)
        if not origem or not alvo or origem == alvo:
            return
        grupo_origem = st.get("grupo")
        grupo_alvo = self._grupo_reordenacao_elenco(self.tv_elenco_atual.item(alvo, "values"))
        if grupo_origem != grupo_alvo:
            return
        filhos = list(self.tv_elenco_atual.get_children(""))
        if origem not in filhos or alvo not in filhos:
            return
        idx_alvo = filhos.index(alvo)
        self.tv_elenco_atual.move(origem, "", idx_alvo)
        self.tv_elenco_atual.selection_set(origem)
        self.tv_elenco_atual.focus(origem)

    def _drag_elenco_end(self, _event):
        if getattr(self, "_drag_elenco_state", None):
            self._drag_elenco_state = None
            self._salvar_elenco_da_interface()

    # --------------------- Formulário ---------------------
    def _criar_formulario(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        frame.rowconfigure(4, weight=0)

        # Card superior: dados principais da partida
        topo = ttk.Labelframe(frame, text="Dados da Partida", padding=10)
        topo.grid(row=0, column=0, sticky="ew")
        for i in range(8):
            topo.columnconfigure(i, weight=1 if i in (1, 4) else 0)

        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.tecnico_var = tk.StringVar(value=self.listas.get("tecnico_atual", "Fernando Diniz"))
        self.adversario_var = tk.StringVar()
        self.local_var = tk.StringVar(value="casa")
        self.competicao_var = tk.StringVar()
        self.posicao_var = tk.StringVar()
        self.estadio_var = tk.StringVar()
        self.horario_hora_var = tk.StringVar()
        self.horario_minuto_var = tk.StringVar()
        self.capitao_partida_var = tk.StringVar()
        self.arbitro_var = tk.StringVar()
        self.auxiliar_1_var = tk.StringVar()
        self.auxiliar_2_var = tk.StringVar()
        self.var_arbitragem_var = tk.StringVar()
        self.publico_pagante_var = tk.StringVar()
        self.publico_presente_var = tk.StringVar()
        self.renda_var = tk.StringVar()
        self.local_var.trace_add("write", self._ao_mudar_local_registro)
        self.adversario_var.trace_add("write", self._ao_mudar_adversario_registro)

        ttk.Label(topo, text="Data:").grid(row=0, column=0, sticky="w", pady=3)
        data_wrap = ttk.Frame(topo)
        data_wrap.grid(row=0, column=1, sticky="w", pady=3)
        self.data_entry = ttk.Entry(data_wrap, width=12, textvariable=self.data_var)
        self.data_entry.pack(side="left")
        self._forcar_cursor_visivel(self.data_entry)
        ttk.Button(data_wrap, text="Calendário", command=self._abrir_calendario_popup).pack(side="left", padx=(8, 0))

        ttk.Label(topo, text="Horário:").grid(row=0, column=2, sticky="w", padx=(12, 4), pady=3)
        horario_wrap = ttk.Frame(topo)
        horario_wrap.grid(row=0, column=3, sticky="w", pady=3)
        self.horario_hora_entry = ttk.Entry(horario_wrap, width=3, textvariable=self.horario_hora_var, justify="center")
        self.horario_hora_entry.pack(side="left")
        ttk.Label(horario_wrap, text=":").pack(side="left", padx=2)
        self.horario_minuto_entry = ttk.Entry(horario_wrap, width=3, textvariable=self.horario_minuto_var, justify="center")
        self.horario_minuto_entry.pack(side="left")
        self._forcar_cursor_visivel(self.horario_hora_entry)
        self._forcar_cursor_visivel(self.horario_minuto_entry)
        self.horario_hora_var.trace_add(
            "write",
            lambda *_: self._mascara_campo_horario("horario_hora_var", self.horario_minuto_entry),
        )
        self.horario_minuto_var.trace_add("write", lambda *_: self._mascara_campo_horario("horario_minuto_var"))

        ttk.Label(topo, text="Técnico:").grid(row=2, column=4, sticky="w", padx=(12, 4), pady=3)
        self.tecnico_entry = ttk.Combobox(topo, textvariable=self.tecnico_var, width=24)
        self.tecnico_entry["values"] = self.listas.get("tecnicos", [])
        self.tecnico_entry.grid(row=2, column=5, sticky="ew", pady=3)
        self.tecnico_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "tecnicos"))
        self._forcar_cursor_visivel(self.tecnico_entry)

        ttk.Label(topo, text="Adversário:").grid(row=0, column=4, sticky="w", padx=(12, 4), pady=3)
        self.adversario_entry = ttk.Combobox(topo, textvariable=self.adversario_var)
        self.adversario_entry["values"] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=0, column=5, sticky="ew", pady=3)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))
        self.adversario_entry.bind("<<ComboboxSelected>>", lambda _e: self._ao_mudar_adversario_registro())
        self._forcar_cursor_visivel(self.adversario_entry)

        ttk.Label(topo, text="Local:").grid(row=0, column=6, sticky="w", padx=(12, 4), pady=3)
        local_wrap = ttk.Frame(topo)
        local_wrap.grid(row=0, column=7, sticky="w", pady=3)
        ttk.Radiobutton(local_wrap, text="Casa", variable=self.local_var, value="casa").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(local_wrap, text="Fora", variable=self.local_var, value="fora").pack(side="left")

        ttk.Label(topo, text="Competição:").grid(row=1, column=0, sticky="w", pady=3)
        self.competicao_entry = ttk.Combobox(topo, textvariable=self.competicao_var)
        self.competicao_entry["values"] = self.listas.get("competicoes", [])
        self.competicao_entry.grid(row=1, column=1, columnspan=5, sticky="ew", pady=3)
        self.competicao_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "competicoes"))
        self._forcar_cursor_visivel(self.competicao_entry)
        ttk.Label(topo, text="Posição na tabela:").grid(row=1, column=6, sticky="w", padx=(12, 4), pady=3)
        self.posicao_entry = ttk.Entry(topo, width=8, textvariable=self.posicao_var)
        self.posicao_entry.grid(row=1, column=7, sticky="w", pady=3)
        self._forcar_cursor_visivel(self.posicao_entry)
        self.competicao_var.trace_add("write", lambda *_: self._atualizar_estado_posicao())
        self._atualizar_estado_posicao()

        ttk.Label(topo, text="Estádio:").grid(row=2, column=0, sticky="w", pady=3)
        self.estadio_entry = ttk.Combobox(topo, textvariable=self.estadio_var)
        self.estadio_entry["values"] = self.listas.get("estadios", [])
        self.estadio_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=3)
        self._forcar_cursor_visivel(self.estadio_entry)

        ttk.Label(topo, text="Capitão:").grid(row=2, column=6, sticky="w", padx=(12, 4), pady=3)
        self.capitao_partida_entry = ttk.Combobox(topo, textvariable=self.capitao_partida_var, width=22, state="readonly")
        self.capitao_partida_entry.grid(row=2, column=7, sticky="ew", pady=3)

        arbitragem_card = ttk.Labelframe(frame, text="Arbitragem", padding=10)
        arbitragem_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        for i in range(8):
            arbitragem_card.columnconfigure(i, weight=1 if i in (1, 3, 5, 7) else 0)

        ttk.Label(arbitragem_card, text="Árbitro:").grid(row=0, column=0, sticky="w", pady=3)
        self.arbitro_entry = ttk.Combobox(arbitragem_card, textvariable=self.arbitro_var)
        self.arbitro_entry["values"] = self.listas.get("arbitros", [])
        self.arbitro_entry.grid(row=0, column=1, sticky="ew", pady=3, padx=(0, 10))
        self.arbitro_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "arbitros"))
        self._forcar_cursor_visivel(self.arbitro_entry)

        ttk.Label(arbitragem_card, text="Auxiliar 1:").grid(row=0, column=2, sticky="w", pady=3)
        self.auxiliar_1_entry = ttk.Combobox(arbitragem_card, textvariable=self.auxiliar_1_var)
        self.auxiliar_1_entry["values"] = self.listas.get("auxiliares", [])
        self.auxiliar_1_entry.grid(row=0, column=3, sticky="ew", pady=3, padx=(0, 10))
        self.auxiliar_1_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "auxiliares"))
        self._forcar_cursor_visivel(self.auxiliar_1_entry)

        ttk.Label(arbitragem_card, text="Auxiliar 2:").grid(row=0, column=4, sticky="w", pady=3)
        self.auxiliar_2_entry = ttk.Combobox(arbitragem_card, textvariable=self.auxiliar_2_var)
        self.auxiliar_2_entry["values"] = self.listas.get("auxiliares", [])
        self.auxiliar_2_entry.grid(row=0, column=5, sticky="ew", pady=3, padx=(0, 10))
        self.auxiliar_2_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "auxiliares"))
        self._forcar_cursor_visivel(self.auxiliar_2_entry)

        ttk.Label(arbitragem_card, text="VAR:").grid(row=0, column=6, sticky="w", pady=3)
        self.var_arbitragem_entry = ttk.Combobox(arbitragem_card, textvariable=self.var_arbitragem_var)
        self.var_arbitragem_entry["values"] = self.listas.get("vars", [])
        self.var_arbitragem_entry.grid(row=0, column=7, sticky="ew", pady=3)
        self.var_arbitragem_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vars"))
        self._forcar_cursor_visivel(self.var_arbitragem_entry)

        ttk.Label(arbitragem_card, text="Público pagante:").grid(row=1, column=0, sticky="w", pady=3)
        self.publico_pagante_entry = ttk.Entry(arbitragem_card, textvariable=self.publico_pagante_var)
        self.publico_pagante_entry.grid(row=1, column=1, sticky="ew", pady=3, padx=(0, 10))
        self._forcar_cursor_visivel(self.publico_pagante_entry)

        ttk.Label(arbitragem_card, text="Público presente:").grid(row=1, column=2, sticky="w", pady=3)
        self.publico_presente_entry = ttk.Entry(arbitragem_card, textvariable=self.publico_presente_var)
        self.publico_presente_entry.grid(row=1, column=3, sticky="ew", pady=3, padx=(0, 10))
        self._forcar_cursor_visivel(self.publico_presente_entry)

        ttk.Label(arbitragem_card, text="Renda:").grid(row=1, column=4, sticky="w", pady=3)
        self.renda_entry = ttk.Entry(arbitragem_card, textvariable=self.renda_var)
        self.renda_entry.grid(row=1, column=5, columnspan=3, sticky="ew", pady=3)
        self._forcar_cursor_visivel(self.renda_entry)

        placar_card = ttk.Labelframe(frame, text="Placar", padding=10)
        placar_card.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        placar_card.columnconfigure(0, weight=1)
        placar_card.columnconfigure(6, weight=1)
        ttk.Label(placar_card, text="Vasco").grid(row=0, column=1, sticky="e")
        self.placar_vasco = ttk.Entry(placar_card, width=6)
        self.placar_vasco.grid(row=0, column=2, padx=(8, 6))
        self._forcar_cursor_visivel(self.placar_vasco)
        ttk.Label(placar_card, text="x").grid(row=0, column=3, padx=4)
        self.placar_adversario = ttk.Entry(placar_card, width=6)
        self.placar_adversario.grid(row=0, column=4, padx=(6, 8), sticky="w")
        self._forcar_cursor_visivel(self.placar_adversario)
        ttk.Label(placar_card, textvariable=self.adversario_var).grid(row=0, column=5, sticky="w", padx=(2, 0))

        meio = ttk.Frame(frame)
        meio.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        meio.columnconfigure(0, weight=1)
        meio.columnconfigure(1, weight=1)
        meio.rowconfigure(0, weight=1)

        # Coluna esquerda: gols
        gols_card = ttk.Labelframe(meio, text="Gols da Partida", padding=10)
        gols_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        gols_card.columnconfigure(0, weight=1)
        gols_card.rowconfigure(1, weight=1)
        gols_card.rowconfigure(3, weight=1)
        gols_card.rowconfigure(5, weight=1)
        gols_card.rowconfigure(7, weight=1)

        ttk.Label(gols_card, text="Gols do Vasco (Enter para adicionar):").grid(row=0, column=0, sticky="w")
        col_vasco = ttk.Frame(gols_card)
        col_vasco.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        col_vasco.columnconfigure(0, weight=1)
        col_vasco.rowconfigure(1, weight=1)
        input_vasco = ttk.Frame(col_vasco)
        input_vasco.grid(row=0, column=0, sticky="ew")
        input_vasco.columnconfigure(0, weight=1)
        self.entry_gol_vasco = ttk.Combobox(input_vasco)
        self.entry_gol_vasco["values"] = self.listas["jogadores_vasco"]
        self.entry_gol_vasco.bind("<Return>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.bind("<<ComboboxSelected>>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vasco"))
        self.entry_gol_vasco.grid(row=0, column=0, sticky="ew")
        self._forcar_cursor_visivel(self.entry_gol_vasco)
        self.lista_gols_vasco = tk.Listbox(
            col_vasco,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_gols_vasco.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.lista_gols_vasco.bind("<Delete>", self.remover_gol_vasco)
        ttk.Button(col_vasco, text="Remover Selecionado", command=self.remover_gol_vasco).grid(
            row=2, column=0, sticky="e", pady=(6, 0)
        )

        ttk.Label(gols_card, text="Gols do Adversário (Enter para adicionar):").grid(row=2, column=0, sticky="w")
        col_contra = ttk.Frame(gols_card)
        col_contra.grid(row=3, column=0, sticky="nsew", pady=(4, 0))
        col_contra.columnconfigure(0, weight=1)
        col_contra.rowconfigure(1, weight=1)
        input_contra = ttk.Frame(col_contra)
        input_contra.grid(row=0, column=0, sticky="ew")
        input_contra.columnconfigure(0, weight=1)
        self.entry_gol_contra = ttk.Combobox(input_contra)
        self.entry_gol_contra["values"] = self.listas["jogadores_contra"]
        self.entry_gol_contra.bind("<Return>", self.adicionar_gol_contra)
        self.entry_gol_contra.bind("<<ComboboxSelected>>", self.adicionar_gol_contra)
        self.entry_gol_contra.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "contra"))
        self.entry_gol_contra.grid(row=0, column=0, sticky="ew")
        self._forcar_cursor_visivel(self.entry_gol_contra)
        self.lista_gols_contra = tk.Listbox(
            col_contra,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_gols_contra.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.lista_gols_contra.bind("<Delete>", self.remover_gol_contra)
        ttk.Button(col_contra, text="Remover Selecionado", command=self.remover_gol_contra).grid(
            row=2, column=0, sticky="e", pady=(6, 0)
        )

        ttk.Label(gols_card, text="Cartões Amarelos do Vasco:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        col_amarelos = ttk.Frame(gols_card)
        col_amarelos.grid(row=5, column=0, sticky="nsew", pady=(4, 8))
        col_amarelos.columnconfigure(0, weight=1)
        col_amarelos.rowconfigure(1, weight=1)
        self.entry_cartao_amarelo = ttk.Combobox(col_amarelos)
        self.entry_cartao_amarelo["values"] = self.listas["jogadores_vasco"]
        self.entry_cartao_amarelo.bind("<Return>", self.adicionar_cartao_amarelo)
        self.entry_cartao_amarelo.bind("<<ComboboxSelected>>", self.adicionar_cartao_amarelo)
        self.entry_cartao_amarelo.grid(row=0, column=0, sticky="ew")
        self._forcar_cursor_visivel(self.entry_cartao_amarelo)
        self.lista_cartoes_amarelos = tk.Listbox(
            col_amarelos,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_cartoes_amarelos.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.lista_cartoes_amarelos.bind("<Delete>", self.remover_cartao_amarelo)
        ttk.Button(col_amarelos, text="Remover Selecionado", command=self.remover_cartao_amarelo).grid(
            row=2, column=0, sticky="e", pady=(6, 0)
        )

        ttk.Label(gols_card, text="Cartões Vermelhos do Vasco:").grid(row=6, column=0, sticky="w")
        col_vermelhos = ttk.Frame(gols_card)
        col_vermelhos.grid(row=7, column=0, sticky="nsew", pady=(4, 0))
        col_vermelhos.columnconfigure(0, weight=1)
        col_vermelhos.rowconfigure(1, weight=1)
        self.entry_cartao_vermelho = ttk.Combobox(col_vermelhos)
        self.entry_cartao_vermelho["values"] = self.listas["jogadores_vasco"]
        self.entry_cartao_vermelho.bind("<Return>", self.adicionar_cartao_vermelho)
        self.entry_cartao_vermelho.bind("<<ComboboxSelected>>", self.adicionar_cartao_vermelho)
        self.entry_cartao_vermelho.grid(row=0, column=0, sticky="ew")
        self._forcar_cursor_visivel(self.entry_cartao_vermelho)
        self.lista_cartoes_vermelhos = tk.Listbox(
            col_vermelhos,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_cartoes_vermelhos.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.lista_cartoes_vermelhos.bind("<Delete>", self.remover_cartao_vermelho)
        ttk.Button(col_vermelhos, text="Remover Selecionado", command=self.remover_cartao_vermelho).grid(
            row=2, column=0, sticky="e", pady=(6, 0)
        )

        # Coluna direita: preview de escalação
        escalacao_card = ttk.Labelframe(meio, text="Escalação da Partida", padding=10)
        escalacao_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        escalacao_card.columnconfigure(0, weight=1)
        escalacao_card.rowconfigure(2, weight=1)

        ttk.Label(
            escalacao_card,
            text="Escalação montada automaticamente com base no Elenco Atual."
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.escalacao_resumo_var = tk.StringVar(value="")
        ttk.Label(escalacao_card, textvariable=self.escalacao_resumo_var).grid(row=1, column=0, sticky="w")

        preview_wrap = ttk.Frame(escalacao_card)
        preview_wrap.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        preview_wrap.columnconfigure(0, weight=3, minsize=640)
        preview_wrap.columnconfigure(1, weight=2, minsize=360)
        preview_wrap.rowconfigure(0, weight=1)

        self.canvas_campinho_preview = tk.Canvas(
            preview_wrap,
            width=700,
            height=340,
            background="#0f6a35",
            highlightthickness=1,
            highlightbackground="#1a1a1a"
        )
        self.canvas_campinho_preview.grid(row=0, column=0, sticky="nsew")
        self.canvas_campinho_preview.bind("<Configure>", lambda _e: self._render_preview_escalacao())
        self.canvas_campinho_preview.bind("<Button-3>", self._abrir_menu_contexto_titulares_preview)
        self.canvas_campinho_preview.bind("<Control-Button-1>", self._abrir_menu_contexto_titulares_preview)

        reservas_wrap = ttk.Labelframe(preview_wrap, text="Reservas", padding=6)
        reservas_wrap.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        reservas_wrap.columnconfigure(0, weight=1)
        reservas_wrap.rowconfigure(0, weight=1)
        self.lista_reservas_preview = tk.Listbox(
            reservas_wrap,
            width=42,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_reservas_preview.grid(row=0, column=0, sticky="nsew")
        self.lista_reservas_preview.bind("<Button-3>", self._abrir_menu_contexto_reservas_preview)
        self.lista_reservas_preview.bind("<Control-Button-1>", self._abrir_menu_contexto_reservas_preview)

        # Observações
        obs_card = ttk.Labelframe(frame, text="Observações da Partida", padding=10)
        obs_card.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        obs_card.columnconfigure(0, weight=1)
        obs_card.rowconfigure(0, weight=1)
        self.obs_text = tk.Text(
            obs_card, height=5, wrap="word",
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            insertbackground=self.colors["fg"]
        )
        self.obs_text.grid(row=0, column=0, sticky="nsew")
        self._forcar_cursor_visivel(self.obs_text)

        # Botões e status de edição
        self.salvar_btn_label = tk.StringVar(value="Salvar Partida")
        self.modo_edicao_var = tk.StringVar(value="")
        botoes = ttk.Frame(frame)
        botoes.grid(row=5, column=0, pady=12, sticky="ew")
        ttk.Label(botoes, textvariable=self.modo_edicao_var, foreground=self.colors["accent"]).pack(side="left", padx=(0, 12))
        self.btn_salvar = ttk.Button(botoes, textvariable=self.salvar_btn_label, command=self.salvar_partida)
        self.btn_salvar.pack(side="left", padx=6)
        ttk.Button(botoes, text="Importar JSON", command=self._abrir_importador_jogo_json).pack(side="left", padx=6)
        ttk.Button(botoes, text="Limpar Campos", command=self._limpar_formulario).pack(side="left", padx=6)
        self.btn_cancelar_edicao = ttk.Button(botoes, text="Cancelar Edição", command=self._cancelar_edicao)
        self.btn_cancelar_edicao.pack(side="left", padx=6)
        self.btn_cancelar_edicao.state(["disabled"])
        ttk.Button(botoes, text="Atualizar Abas", command=self._atualizar_abas).pack(side="left", padx=6)

        self.gols_vasco_eventos = []
        self.gols_contra_eventos = []
        self.cartoes_amarelos_eventos = []
        self.cartoes_vermelhos_eventos = []
        self._inicializar_escalacao_partida()
        self._atualizar_opcoes_capitao_partida(preservar_valor=False)

    def _render_preview_escalacao(self):
        if not hasattr(self, "canvas_campinho_preview"):
            return
        canvas = self.canvas_campinho_preview
        canvas.delete("all")
        self._preview_hit_players = []
        capitao_cf = ""
        if hasattr(self, "capitao_partida_var"):
            capitao_cf = self.capitao_partida_var.get().strip().casefold()

        w = max(300, canvas.winfo_width())
        h = max(220, canvas.winfo_height())
        m = 14

        # Campo
        canvas.create_rectangle(0, 0, w, h, fill="#0f6a35", outline="")
        canvas.create_rectangle(m, m, w - m, h - m, outline="#e9f7ed", width=2)
        meio_y = h / 2
        canvas.create_line(m, meio_y, w - m, meio_y, fill="#e9f7ed", width=2)
        canvas.create_oval(w / 2 - 34, meio_y - 34, w / 2 + 34, meio_y + 34, outline="#e9f7ed", width=2)

        esc = getattr(self, "escalacao_partida", self._escalacao_partida_base())
        titulares_por_posicao = esc.get("titulares_por_posicao", {})

        def _lista(pos):
            return [str(n).strip() for n in titulares_por_posicao.get(pos, []) if str(n).strip()]

        linha_ataque = _lista("Atacante")
        linha_meio = _lista("Meio-Campista")
        linha_vol = _lista("Volante")
        defesa_le = _lista("Lateral-Esquerdo")
        defesa_zag = _lista("Zagueiro")
        defesa_ld = _lista("Lateral-Direito")
        linha_def = defesa_le + defesa_zag + defesa_ld
        linha_gol = _lista("Goleiro")

        linhas = [
            ("ATA", "Atacante", linha_ataque, 0.16),
            ("MEI", "Meio-Campista", linha_meio, 0.34),
            ("VOL", "Volante", linha_vol, 0.50),
            ("DEF", "Defesa", linha_def, 0.68),
            ("GOL", "Goleiro", linha_gol, 0.84),
        ]

        for setor, chave_linha, nomes, rel_y in linhas:
            y = m + (h - 2 * m) * rel_y
            canvas.create_text(m + 16, y, text=setor, fill="#d8f0de", font=("Segoe UI", 9, "bold"))
            if not nomes:
                continue
            n = len(nomes)
            for i, nome in enumerate(nomes):
                x = m + (w - 2 * m) * ((i + 1) / (n + 1))
                r = 14
                canvas.create_oval(x - r, y - r, x + r, y + r, fill="#f5f8f6", outline="#0b3d24", width=1)
                canvas.create_text(x, y, text=str(i + 1), fill="#133b23", font=("Segoe UI", 8, "bold"))
                nome_exibicao = f"{nome} (C)" if capitao_cf and nome.casefold() == capitao_cf else nome
                nome_curto = nome_exibicao if len(nome_exibicao) <= 21 else (nome_exibicao[:20] + "…")
                canvas.create_text(x, y + 20, text=nome_curto, fill="#eef9f1", font=("Segoe UI", 11, "bold"))
                self._preview_hit_players.append({
                    "linha": chave_linha,
                    "idx": i,
                    "n": n,
                    "x": x,
                    "y": y,
                    "r": r,
                    "m": m,
                    "w": w,
                    "nome": nome,
                })

        if hasattr(self, "lista_reservas_preview"):
            self.lista_reservas_preview.delete(0, tk.END)
            substituicoes_por_reserva = {}
            for item in esc.get("substituicoes", []):
                sub = _normalizar_substituicao_partida(item)
                if not sub:
                    continue
                substituicoes_por_reserva[sub["jogador_entrou"].casefold()] = sub
            reservas_que_entraram_cf = {
                str(nome).strip().casefold()
                for nome in _nomes_reservas_que_entraram_escalacao(esc)
                if str(nome).strip()
            }
            for nome in esc.get("reservas", []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    sub = substituicoes_por_reserva.get(nome_limpo.casefold())
                    if sub:
                        sufixo = (
                            f" [{_formatar_minuto_periodo(sub.get('minuto'), sub.get('periodo'))}"
                            f" <- {sub.get('jogador_saiu', '')}]"
                        )
                    else:
                        sufixo = " [entrou]" if nome_limpo.casefold() in reservas_que_entraram_cf else ""
                    self.lista_reservas_preview.insert(tk.END, f"{nome_limpo}{sufixo}")

    def _preview_drag_start(self, event):
        hit = None
        for item in getattr(self, "_preview_hit_players", []):
            dx = event.x - item["x"]
            dy = event.y - item["y"]
            if (dx * dx + dy * dy) <= (item["r"] + 4) ** 2:
                hit = item
                break
        self._preview_drag_state = hit
        if hit:
            self.canvas_campinho_preview.configure(cursor="hand2")

    def _preview_drag_end(self, event):
        state = getattr(self, "_preview_drag_state", None)
        self._preview_drag_state = None
        self.canvas_campinho_preview.configure(cursor="")
        if not state:
            return
        if state["n"] < 2:
            return

        # Calcula o alvo pelo jogador mais próximo no eixo X da mesma linha.
        linha = state["linha"]
        origem = state["idx"]
        n = state["n"]
        mesmos = sorted(
            [p for p in getattr(self, "_preview_hit_players", []) if p.get("linha") == linha],
            key=lambda p: p.get("idx", 0)
        )
        if len(mesmos) != n:
            return
        alvo = min(range(n), key=lambda i: abs(event.x - mesmos[i]["x"]))
        origem = state["idx"]
        if alvo == origem:
            return

        esc = self._coletar_escalacao_partida()
        if linha == "Defesa":
            le = list(esc["titulares_por_posicao"].get("Lateral-Esquerdo", []))
            zag = list(esc["titulares_por_posicao"].get("Zagueiro", []))
            ld = list(esc["titulares_por_posicao"].get("Lateral-Direito", []))
            combinado = le + zag + ld
            if len(combinado) != n:
                return
            jogador = combinado.pop(origem)
            combinado.insert(alvo, jogador)
            n_le = len(le)
            n_zag = len(zag)
            esc["titulares_por_posicao"]["Lateral-Esquerdo"] = combinado[:n_le]
            esc["titulares_por_posicao"]["Zagueiro"] = combinado[n_le:n_le + n_zag]
            esc["titulares_por_posicao"]["Lateral-Direito"] = combinado[n_le + n_zag:]
        else:
            lista = list(esc["titulares_por_posicao"].get(linha, []))
            if len(lista) != n:
                return
            jogador = lista.pop(origem)
            lista.insert(alvo, jogador)
            esc["titulares_por_posicao"][linha] = lista

        self._carregar_escalacao_partida(esc)

    def _indice_reserva_preview_por_evento(self, event):
        lista = getattr(self, "lista_reservas_preview", None)
        esc = getattr(self, "escalacao_partida", None)
        if lista is None or not isinstance(esc, dict):
            return None
        total = len(esc.get("reservas", []))
        if total <= 0:
            return None
        try:
            idx = int(lista.nearest(event.y))
        except Exception:
            return None
        if not (0 <= idx < total):
            return None
        bbox = lista.bbox(idx)
        if bbox:
            _x, y, _w, h = bbox
            if not (y <= event.y <= y + h):
                return None
        return idx

    def _titular_preview_por_evento(self, event):
        for item in getattr(self, "_preview_hit_players", []):
            dx = event.x - item["x"]
            dy = event.y - item["y"]
            if (dx * dx + dy * dy) <= (item["r"] + 8) ** 2:
                return item
        return None

    def _calcular_resumo_minutos_substituicao(self, minuto, periodo):
        minuto_abs = _minuto_absoluto_substituicao(minuto, periodo)
        if minuto_abs is None:
            return ("—", "—")
        duracao = 120 if minuto_abs > 90 else 90
        titular = max(0, min(duracao, minuto_abs))
        reserva = max(0, duracao - titular)
        return (str(titular), str(reserva))

    def _alternar_entrada_reserva_partida(self, idx_reserva):
        esc = self._coletar_escalacao_partida()
        reservas = list(esc.get("reservas", []))
        if not (0 <= idx_reserva < len(reservas)):
            return
        nome = str(reservas[idx_reserva]).strip()
        if not nome:
            return
        entraram = [
            str(item).strip()
            for item in esc.get("reservas_que_entraram", [])
            if str(item).strip()
        ]
        nome_cf = nome.casefold()
        if any(item.casefold() == nome_cf for item in entraram):
            entraram = [item for item in entraram if item.casefold() != nome_cf]
        else:
            entraram.append(nome)
        esc["reservas_que_entraram"] = entraram
        self._carregar_escalacao_partida(esc)

    def _titulares_partida_ordenados(self, esc):
        titulares = []
        tit_por_pos = esc.get("titulares_por_posicao", {}) if isinstance(esc, dict) else {}
        for pos in POSICOES_ELENCO:
            for nome in tit_por_pos.get(pos, []) if isinstance(tit_por_pos, dict) else []:
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    titulares.append(nome_limpo)
        return titulares

    def _registrar_substituicao_reserva_partida(self, idx_reserva, substituicao):
        esc = self._coletar_escalacao_partida()
        reservas = list(esc.get("reservas", []))
        if not (0 <= idx_reserva < len(reservas)):
            return
        reserva_nome = str(reservas[idx_reserva]).strip()
        sub = _normalizar_substituicao_partida({
            **(substituicao or {}),
            "jogador_entrou": reserva_nome,
        })
        if not sub:
            return
        substituicoes = []
        for item in esc.get("substituicoes", []):
            sub_existente = _normalizar_substituicao_partida(item)
            if not sub_existente:
                continue
            if sub_existente["jogador_entrou"].casefold() == reserva_nome.casefold():
                continue
            substituicoes.append(sub_existente)
        substituicoes.append(sub)
        esc["substituicoes"] = substituicoes
        esc["reservas_que_entraram"] = [item["jogador_entrou"] for item in substituicoes]
        self._carregar_escalacao_partida(esc)

    def _registrar_substituicao_titular_partida(self, nome_titular, substituicao):
        esc = self._coletar_escalacao_partida()
        titular_nome = str(nome_titular or "").strip()
        if not titular_nome:
            return
        sub = _normalizar_substituicao_partida({
            **(substituicao or {}),
            "jogador_saiu": titular_nome,
        })
        if not sub:
            return
        substituicoes = []
        for item in esc.get("substituicoes", []):
            sub_existente = _normalizar_substituicao_partida(item)
            if not sub_existente:
                continue
            if sub_existente["jogador_saiu"].casefold() == titular_nome.casefold():
                continue
            substituicoes.append(sub_existente)
        substituicoes.append(sub)
        esc["substituicoes"] = substituicoes
        esc["reservas_que_entraram"] = [item["jogador_entrou"] for item in substituicoes]
        self._carregar_escalacao_partida(esc)

    def _remover_substituicao_titular_partida(self, nome_titular):
        esc = self._coletar_escalacao_partida()
        titular_nome = str(nome_titular or "").strip()
        if not titular_nome:
            return
        substituicoes = []
        alterou = False
        for item in esc.get("substituicoes", []):
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            if sub["jogador_saiu"].casefold() == titular_nome.casefold():
                alterou = True
                continue
            substituicoes.append(sub)
        if not alterou:
            return
        esc["substituicoes"] = substituicoes
        esc["reservas_que_entraram"] = [item["jogador_entrou"] for item in substituicoes]
        self._carregar_escalacao_partida(esc)

    def _remover_substituicao_reserva_partida(self, idx_reserva):
        esc = self._coletar_escalacao_partida()
        reservas = list(esc.get("reservas", []))
        if not (0 <= idx_reserva < len(reservas)):
            return
        reserva_nome = str(reservas[idx_reserva]).strip()
        substituicoes = []
        alterou = False
        for item in esc.get("substituicoes", []):
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            if sub["jogador_entrou"].casefold() == reserva_nome.casefold():
                alterou = True
                continue
            substituicoes.append(sub)
        if not alterou:
            return
        esc["substituicoes"] = substituicoes
        esc["reservas_que_entraram"] = [item["jogador_entrou"] for item in substituicoes]
        self._carregar_escalacao_partida(esc)

    def _abrir_modal_substituicao(self, *, titulo, linha_principal, label_selecao, opcoes, valor_inicial, minuto_inicial="", periodo_inicial="", ao_salvar):
        if not opcoes:
            messagebox.showwarning("Substituição", "Não há jogadores disponíveis para essa substituição.")
            return

        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.focus_force()
        top.resizable(False, False)
        top.configure(bg=self.colors["bg"])
        top.minsize(620, 0)
        try:
            top.attributes("-topmost", True)
        except tk.TclError:
            pass

        card = tk.Frame(
            top,
            bg=self.colors["bg"],
            highlightthickness=1,
            highlightbackground=self.colors["bg2"],
            bd=0,
            padx=16,
            pady=14,
        )
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=0)
        card.columnconfigure(1, weight=1)

        selecao_var = tk.StringVar(value=valor_inicial if valor_inicial else opcoes[0])
        minuto_var = tk.StringVar(value=str(minuto_inicial) if minuto_inicial not in ("", None) else "")
        periodo_map = {label: codigo for codigo, label in PERIODOS_SUBSTITUICAO}
        periodo_map_inv = {codigo: label for codigo, label in PERIODOS_SUBSTITUICAO}
        periodo_var = tk.StringVar(value=periodo_map_inv.get(periodo_inicial, "") if periodo_inicial else "")
        resumo_var = tk.StringVar(value="Titular: — min | Reserva: — min")

        tk.Label(
            card,
            text="Registrar substituição",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        tk.Label(
            card,
            text=linha_principal,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        tk.Label(card, text=label_selecao, bg=self.colors["bg"], fg=self.colors["tree_head_fg"]).grid(row=2, column=0, sticky="w", pady=4, padx=(0, 10))
        combo_selecao = ttk.Combobox(card, textvariable=selecao_var, values=opcoes, state="readonly", width=30)
        combo_selecao.grid(row=2, column=1, sticky="ew", pady=4)

        linha_tempo = tk.Frame(card, bg=self.colors["bg"])
        linha_tempo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 4))
        linha_tempo.columnconfigure(0, weight=0)
        linha_tempo.columnconfigure(1, weight=0)
        linha_tempo.columnconfigure(2, weight=0)
        linha_tempo.columnconfigure(3, weight=1)
        tk.Label(linha_tempo, text="Minuto", bg=self.colors["bg"], fg=self.colors["tree_head_fg"]).grid(row=0, column=0, sticky="w", padx=(0, 10))
        vcmd = (self.root.register(self._validar_input_inteiro), "%P")
        entry_minuto = ttk.Entry(
            linha_tempo,
            textvariable=minuto_var,
            width=8,
            justify="center",
            validate="key",
            validatecommand=vcmd,
        )
        entry_minuto.grid(row=0, column=1, sticky="w")
        tk.Label(linha_tempo, text="Período", bg=self.colors["bg"], fg=self.colors["tree_head_fg"]).grid(row=0, column=2, sticky="w", padx=(18, 10))
        combo_periodo = ttk.Combobox(
            linha_tempo,
            textvariable=periodo_var,
            values=[label for _codigo, label in PERIODOS_SUBSTITUICAO],
            state="readonly",
            width=28,
        )
        combo_periodo.grid(row=0, column=3, sticky="w")

        tk.Label(
            card,
            textvariable=resumo_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 10, "bold"),
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 12))

        def atualizar_resumo(*_args):
            periodo = periodo_map.get(periodo_var.get().strip(), "")
            if periodo in PERIODOS_INTERVALO_SUBSTITUICAO and minuto_var.get().strip() != "0":
                minuto_var.set("0")
                return
            minuto = _normalizar_minuto_partida(minuto_var.get())
            titular, reserva = self._calcular_resumo_minutos_substituicao(minuto, periodo)
            resumo_var.set(f"Titular: {titular} min | Reserva: {reserva} min")

        minuto_var.trace_add("write", atualizar_resumo)
        periodo_var.trace_add("write", atualizar_resumo)
        atualizar_resumo()

        botoes = tk.Frame(card, bg=self.colors["bg"])
        botoes.grid(row=5, column=0, columnspan=2, sticky="e")

        def salvar():
            nome_escolhido = selecao_var.get().strip()
            periodo = periodo_map.get(periodo_var.get().strip(), "")
            minuto = _normalizar_minuto_partida(minuto_var.get())
            if not nome_escolhido:
                messagebox.showerror("Substituição", "Selecione o jogador da substituição.", parent=top)
                return
            if periodo not in {codigo for codigo, _ in PERIODOS_SUBSTITUICAO}:
                messagebox.showerror("Substituição", "Selecione o período da substituição.", parent=top)
                return
            if periodo in PERIODOS_INTERVALO_SUBSTITUICAO and minuto is None:
                minuto = 0
            if minuto is None:
                messagebox.showerror("Substituição", "Informe um minuto válido.", parent=top)
                return
            if minuto > _limite_minuto_por_periodo(periodo):
                messagebox.showerror(
                    "Substituição",
                    f"O {periodo} permite no máximo {_limite_minuto_por_periodo(periodo)} minuto(s).",
                    parent=top,
                )
                return
            ao_salvar(nome_escolhido, minuto, periodo)
            top.destroy()

        ttk.Button(botoes, text="Cancelar", command=top.destroy).pack(side="right")
        ttk.Button(botoes, text="Salvar", command=salvar).pack(side="right", padx=(0, 8))
        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.update_idletasks()
        self._centralizar_modal_no_app(top)
        entry_minuto.focus_set()
        top.bind("<Return>", lambda _e: salvar())

    def _abrir_modal_substituicao_reserva(self, idx_reserva):
        esc = self._coletar_escalacao_partida()
        reservas = list(esc.get("reservas", []))
        if not (0 <= idx_reserva < len(reservas)):
            return
        reserva_nome = str(reservas[idx_reserva]).strip()
        if not reserva_nome:
            return
        sub_atual = None
        substituidos_cf = set()
        for item in esc.get("substituicoes", []):
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            if sub["jogador_entrou"].casefold() == reserva_nome.casefold():
                sub_atual = sub
            else:
                substituidos_cf.add(sub["jogador_saiu"].casefold())
        titulares = [
            nome for nome in self._titulares_partida_ordenados(esc)
            if nome.casefold() not in substituidos_cf or (sub_atual and nome.casefold() == sub_atual["jogador_saiu"].casefold())
        ]
        self._abrir_modal_substituicao(
            titulo=f"Substituição: {reserva_nome}",
            linha_principal=f"Reserva que entrou: {reserva_nome}",
            label_selecao="Saiu no lugar de",
            opcoes=titulares,
            valor_inicial=sub_atual["jogador_saiu"] if sub_atual else (titulares[0] if titulares else ""),
            minuto_inicial=sub_atual["minuto"] if sub_atual else "",
            periodo_inicial=sub_atual["periodo"] if sub_atual else "",
            ao_salvar=lambda jogador_saiu, minuto, periodo: self._registrar_substituicao_reserva_partida(
                idx_reserva,
                {"jogador_saiu": jogador_saiu, "minuto": minuto, "periodo": periodo},
            ),
        )

    def _abrir_modal_substituicao_titular(self, nome_titular):
        esc = self._coletar_escalacao_partida()
        titular_nome = str(nome_titular or "").strip()
        if not titular_nome:
            return
        sub_atual = None
        reservas_utilizadas_cf = set()
        for item in esc.get("substituicoes", []):
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            if sub["jogador_saiu"].casefold() == titular_nome.casefold():
                sub_atual = sub
            else:
                reservas_utilizadas_cf.add(sub["jogador_entrou"].casefold())
        reservas = [
            nome for nome in esc.get("reservas", [])
            if str(nome).strip() and (str(nome).strip().casefold() not in reservas_utilizadas_cf or (sub_atual and str(nome).strip().casefold() == sub_atual["jogador_entrou"].casefold()))
        ]
        self._abrir_modal_substituicao(
            titulo=f"Substituição: {titular_nome}",
            linha_principal=f"Titular que saiu: {titular_nome}",
            label_selecao="Entrou no lugar dele",
            opcoes=reservas,
            valor_inicial=sub_atual["jogador_entrou"] if sub_atual else (reservas[0] if reservas else ""),
            minuto_inicial=sub_atual["minuto"] if sub_atual else "",
            periodo_inicial=sub_atual["periodo"] if sub_atual else "",
            ao_salvar=lambda jogador_entrou, minuto, periodo: self._registrar_substituicao_titular_partida(
                titular_nome,
                {"jogador_entrou": jogador_entrou, "minuto": minuto, "periodo": periodo},
            ),
        )

    def _abrir_menu_contexto_reservas_preview(self, event):
        idx = self._indice_reserva_preview_por_evento(event)
        if idx is None:
            return
        lista = self.lista_reservas_preview
        lista.selection_clear(0, tk.END)
        lista.selection_set(idx)
        lista.activate(idx)
        esc = self._coletar_escalacao_partida()
        reservas = list(esc.get("reservas", []))
        nome = str(reservas[idx]).strip()
        if not nome:
            return
        sub_atual = next(
            (
                _normalizar_substituicao_partida(item)
                for item in esc.get("substituicoes", [])
                if _normalizar_substituicao_partida(item)
                and _normalizar_substituicao_partida(item)["jogador_entrou"].casefold() == nome.casefold()
            ),
            None,
        )
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="Editar entrada" if sub_atual else "Registrar entrada",
            command=lambda idx_res=idx: self._abrir_modal_substituicao_reserva(idx_res),
        )
        if sub_atual:
            menu.add_command(
                label="Remover entrada",
                command=lambda idx_res=idx: self._remover_substituicao_reserva_partida(idx_res),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _abrir_menu_contexto_titulares_preview(self, event):
        hit = self._titular_preview_por_evento(event)
        if not hit:
            return
        nome = str(hit.get("nome", "")).strip()
        if not nome:
            return
        esc = self._coletar_escalacao_partida()
        sub_atual = next(
            (
                sub
                for sub in (
                    _normalizar_substituicao_partida(item)
                    for item in esc.get("substituicoes", [])
                )
                if sub and sub["jogador_saiu"].casefold() == nome.casefold()
            ),
            None,
        )
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(
            label="Editar substituição" if sub_atual else "Substituição",
            command=lambda nome_tit=nome: self._abrir_modal_substituicao_titular(nome_tit),
        )
        if sub_atual:
            menu.add_command(
                label="Remover substituição",
                command=lambda nome_tit=nome: self._remover_substituicao_titular_partida(nome_tit),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _atualizar_elenco_disponivel_partida(self):
        self._elenco_info_por_nome_cf = {}
        jogadores = _ordenar_jogadores_elenco(list(self.elenco_atual.get("jogadores", [])))
        for jogador in jogadores:
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            self._elenco_info_por_nome_cf[nome.casefold()] = {
                "nome": nome,
                "posicao": _normalizar_posicao_elenco(jogador.get("posicao")),
                "condicao": _normalizar_condicao_elenco(jogador.get("condicao")),
            }

    def _ordenar_nomes_escalacao(self, nomes):
        ordem_posicao = {pos: idx for idx, pos in enumerate(POSICOES_ELENCO)}
        info_por_nome = getattr(self, "_elenco_info_por_nome_cf", {})
        return sorted(
            [n for n in nomes if n],
            key=lambda nome: (
                ordem_posicao.get(
                    info_por_nome.get(nome.casefold(), {}).get("posicao", ""),
                    len(POSICOES_ELENCO)
                ),
                nome.casefold(),
            )
        )

    def _escalacao_partida_base(self):
        return {
            "titulares_por_posicao": {pos: [] for pos in POSICOES_ELENCO},
            "reservas": [],
            "reservas_que_entraram": [],
            "substituicoes": [],
            "nao_relacionados": [],
            "lesionados": [],
            "suspensos": [],
            "servindo_selecao": [],
        }

    def _normalizar_escalacao_partida(self, escalacao):
        base = self._escalacao_partida_base()
        if not isinstance(escalacao, dict):
            return base

        tit_por_pos = escalacao.get("titulares_por_posicao")
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                nomes = tit_por_pos.get(pos, [])
                if isinstance(nomes, list):
                    base["titulares_por_posicao"][pos] = [str(n).strip() for n in nomes if str(n).strip()]
        else:
            # Compatibilidade com formato antigo: "titulares": []
            antigos = escalacao.get("titulares", [])
            if isinstance(antigos, list):
                for nome in antigos:
                    nome_limpo = str(nome).strip()
                    if not nome_limpo:
                        continue
                    info = self._elenco_info_por_nome_cf.get(nome_limpo.casefold(), {})
                    pos = _normalizar_posicao_elenco(info.get("posicao"))
                    base["titulares_por_posicao"].setdefault(pos, []).append(nome_limpo)

        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            nomes = escalacao.get(chave, [])
            if isinstance(nomes, list):
                base[chave] = [str(n).strip() for n in nomes if str(n).strip()]

        vistos = set()
        for pos in POSICOES_ELENCO:
            filtrados = []
            for nome in base["titulares_por_posicao"][pos]:
                cf = nome.casefold()
                if cf in vistos:
                    continue
                vistos.add(cf)
                filtrados.append(nome)
            # Preserva a ordem manual definida na modal/campinho.
            base["titulares_por_posicao"][pos] = filtrados
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            filtrados = []
            for nome in base[chave]:
                cf = nome.casefold()
                if cf in vistos:
                    continue
                vistos.add(cf)
                filtrados.append(nome)
            # Preserva a ordem manual das listas da escalação.
            base[chave] = filtrados
        reservas_que_entraram = []
        reservas_cf = {str(nome).strip().casefold() for nome in base["reservas"] if str(nome).strip()}
        bruto_entraram = escalacao.get("reservas_que_entraram")
        if not isinstance(bruto_entraram, list):
            bruto_entraram = list(base["reservas"])
        vistos_entraram = set()
        for nome in bruto_entraram:
            nome_limpo = str(nome).strip()
            chave = nome_limpo.casefold()
            if not nome_limpo or chave in vistos_entraram or chave not in reservas_cf:
                continue
            vistos_entraram.add(chave)
            reservas_que_entraram.append(nome_limpo)
        base["reservas_que_entraram"] = reservas_que_entraram
        substituicoes = []
        substituidos_cf = set()
        substitutos_cf = set()
        for item in escalacao.get("substituicoes", []) if isinstance(escalacao.get("substituicoes", []), list) else []:
            sub = _normalizar_substituicao_partida(item)
            if not sub:
                continue
            saiu_cf = sub["jogador_saiu"].casefold()
            entrou_cf = sub["jogador_entrou"].casefold()
            if entrou_cf not in reservas_cf or saiu_cf in substituidos_cf or entrou_cf in substitutos_cf:
                continue
            substituidos_cf.add(saiu_cf)
            substitutos_cf.add(entrou_cf)
            substituicoes.append(sub)
        base["substituicoes"] = sorted(
            substituicoes,
            key=lambda item: (item.get("minuto_absoluto", 999), item.get("jogador_entrou", "").casefold()),
        )
        if base["substituicoes"]:
            base["reservas_que_entraram"] = [item["jogador_entrou"] for item in base["substituicoes"]]
        return base

    def _atualizar_resumo_escalacao(self):
        esc = getattr(self, "escalacao_partida", self._escalacao_partida_base())
        titulares = sum(len(esc["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        reservas = len(esc.get("reservas", []))
        nao_rel = len(esc.get("nao_relacionados", []))
        lesionados = len(esc.get("lesionados", []))
        suspensos = len(esc.get("suspensos", []))
        servindo_selecao = len(esc.get("servindo_selecao", []))
        self.escalacao_resumo_var.set(
            f"Titulares: {titulares}/11 | Reservas: {reservas} (mín. 4) | "
            f"Não Relac.: {nao_rel} | Lesionados: {lesionados} | "
            f"Suspensos: {suspensos} | Seleção: {servindo_selecao}"
        )

    def _inicializar_escalacao_partida(self):
        base = self._escalacao_partida_base()
        for jogador in self.elenco_atual.get("jogadores", []):
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            condicao = _normalizar_condicao_elenco(jogador.get("condicao"))
            posicao = _normalizar_posicao_elenco(jogador.get("posicao"))
            if condicao == "Titular":
                base["titulares_por_posicao"].setdefault(posicao, []).append(nome)
            elif condicao == "Reserva":
                base["reservas"].append(nome)
            elif condicao == "Não Relacionado":
                base["nao_relacionados"].append(nome)
            elif condicao == "Lesionado":
                base["lesionados"].append(nome)
            elif condicao == "Suspenso":
                base["suspensos"].append(nome)
            elif condicao == "Servindo a seleção":
                base["servindo_selecao"].append(nome)
            # Emprestados ficam fora da escalação da partida.
        self._carregar_escalacao_partida(base)

    def _coletar_escalacao_partida(self):
        return self._normalizar_escalacao_partida(getattr(self, "escalacao_partida", self._escalacao_partida_base()))

    def _nomes_presentes_na_escalacao(self, escalacao):
        nomes = set()
        if not isinstance(escalacao, dict):
            return nomes
        tit_por_pos = escalacao.get("titulares_por_posicao", {})
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                for nome in tit_por_pos.get(pos, []):
                    nome_limpo = str(nome).strip()
                    if nome_limpo:
                        nomes.add(nome_limpo.casefold())
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            for nome in escalacao.get(chave, []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    nomes.add(nome_limpo.casefold())
        return nomes

    def _validar_escalacao_partida(self, escalacao, nomes_elenco_obrigatorios=None):
        titulares = sum(len(escalacao["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        goleiros_titulares = len(escalacao["titulares_por_posicao"].get("Goleiro", []))
        reservas = len(escalacao.get("reservas", []))
        if titulares != 11:
            return False, "A escalação precisa ter exatamente 11 titulares."
        if goleiros_titulares != 1:
            return False, "A escalação precisa ter exatamente 1 goleiro titular."
        if reservas < 4:
            return False, "A escalação precisa ter pelo menos 4 reservas."

        usando_elenco_atual = nomes_elenco_obrigatorios is None
        if usando_elenco_atual:
            nomes_elenco = {
                str(j.get("nome", "")).strip().casefold()
                for j in self.elenco_atual.get("jogadores", [])
                if (
                    isinstance(j, dict)
                    and str(j.get("nome", "")).strip()
                    and _normalizar_condicao_elenco(j.get("condicao")) != "Emprestado"
                )
            }
        else:
            nomes_elenco = {
                str(nome).strip().casefold()
                for nome in nomes_elenco_obrigatorios
                if str(nome).strip()
            }
        nomes_escalados = self._nomes_presentes_na_escalacao(escalacao)

        faltando = sorted(nomes_elenco - nomes_escalados)
        if faltando:
            if usando_elenco_atual:
                return False, "Todos os jogadores do elenco atual (exceto emprestados) precisam estar em alguma lista da escalação."
            return False, "Todos os jogadores do elenco-base da partida precisam estar em alguma lista da escalação."
        return True, ""

    def _carregar_escalacao_partida(self, escalacao):
        self.escalacao_partida = self._normalizar_escalacao_partida(escalacao)
        self._atualizar_resumo_escalacao()
        self._render_preview_escalacao()
        self._atualizar_opcoes_gol_vasco()

    def _ajustar_geometria_inicial(self):
        try:
            self.root.update_idletasks()
            largura_tela = self.root.winfo_screenwidth()
            altura_tela = self.root.winfo_screenheight()
            largura_janela = max(1000, int(largura_tela * 0.7))
            altura_janela = max(700, altura_tela)
            pos_x = max(0, (largura_tela - largura_janela) // 2)
            pos_y = max(0, (altura_tela - altura_janela) // 2)
            self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
        except Exception:
            self.root.geometry("1500x1000")
            self.root.after(10, self._centralizar_janela)

    def _centralizar_janela(self):
        try:
            self.root.update_idletasks()
            win_w = self.root.winfo_width()
            win_h = self.root.winfo_height()
            scr_w = self.root.winfo_screenwidth()
            scr_h = self.root.winfo_screenheight()
            pos_x = max(0, (scr_w - win_w) // 2)
            pos_y = max(0, (scr_h - win_h) // 2)
            self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        except Exception:
            pass

    def _cancelar_edicao(self):
        if self.editing_index is not None:
            self._limpar_formulario()

    def _abrir_calendario_popup(self, target_var=None):
        if not TKCALENDAR_OK:
            messagebox.showerror(
                "Calendário indisponível",
                "O recurso de calendário precisa do pacote 'tkcalendar'.\n"
                "Instale com 'pip install tkcalendar' e abra novamente."
            )
            return

        popup = getattr(self, "_calendar_popup", None)
        if popup and popup.winfo_exists():
            popup.lift()
            popup.focus_force()
            return

        top = tk.Toplevel(self.root)
        top.title("Selecionar data")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        try:
            top.attributes("-topmost", True)
        except tk.TclError:
            pass
        self._calendar_popup = top
        self._calendar_target_var = target_var or self.data_var

        try:
            data_atual = _parse_data_ptbr(self._calendar_target_var.get().strip())
        except Exception:
            data_atual = datetime.now()

        cal_kwargs = {"selectmode": "day", "date_pattern": "dd/mm/yyyy"}
        try:
            cal = Calendar(top, locale="pt_BR", **cal_kwargs)
        except Exception:
            cal = Calendar(top, **cal_kwargs)

        cal.selection_set(data_atual)
        cal.pack(padx=12, pady=12)

        buttons = ttk.Frame(top)
        buttons.pack(fill="x", pady=(0, 12), padx=12)
        ttk.Button(buttons, text="Cancelar", command=self._fechar_calendario_popup).pack(side="right", padx=(4, 0))
        ttk.Button(buttons, text="Usar data", command=lambda: self._confirmar_data_calendario(cal)).pack(side="right")

        top.protocol("WM_DELETE_WINDOW", self._fechar_calendario_popup)
        top.update_idletasks()
        try:
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()
            win_w = top.winfo_width()
            win_h = top.winfo_height()
            pos_x = root_x + (root_w - win_w) // 2
            pos_y = root_y + (root_h - win_h) // 2
            top.geometry(f"+{pos_x}+{pos_y}")
        except Exception:
            pass

    def _confirmar_data_calendario(self, calendario):
        if calendario:
            try:
                selecionada = calendario.selection_get()
            except Exception:
                selecionada = None
            if selecionada:
                target_var = getattr(self, "_calendar_target_var", self.data_var)
                target_var.set(selecionada.strftime("%d/%m/%Y"))
        self._fechar_calendario_popup()

    def _fechar_calendario_popup(self):
        popup = getattr(self, "_calendar_popup", None)
        if popup and popup.winfo_exists():
            try:
                popup.grab_release()
            except Exception:
                pass
            popup.destroy()
        self._calendar_popup = None
        self._calendar_target_var = None

    # --------------------- Handlers de Gols ---------------------
    def _renderizar_lista_eventos(self, listbox, eventos, formatter):
        listbox.delete(0, tk.END)
        for evento in eventos:
            listbox.insert(tk.END, formatter(evento))

    def _validar_input_inteiro(self, valor_proposto):
        return valor_proposto.isdigit() or valor_proposto == ""

    def _centralizar_modal_no_app(self, top):
        try:
            top.update_idletasks()
            top.wait_visibility()
        except Exception:
            pass
        top.update_idletasks()
        ancora = self.root
        try:
            if hasattr(self, "notebook") and self.notebook.select():
                ancora = self.nametowidget(self.notebook.select())
        except Exception:
            ancora = self.root
        try:
            root_x = ancora.winfo_rootx()
            root_y = ancora.winfo_rooty()
            root_w = ancora.winfo_width()
            root_h = ancora.winfo_height()
        except Exception:
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()
        top_w = max(top.winfo_width(), top.winfo_reqwidth())
        top_h = max(top.winfo_height(), top.winfo_reqheight())
        try:
            scr_w = top.winfo_screenwidth()
            scr_h = top.winfo_screenheight()
        except Exception:
            scr_w = root_x + root_w
            scr_h = root_y + root_h
        pos_x = root_x + (root_w - top_w) // 2
        pos_y = root_y + (root_h - top_h) // 2
        pos_x = max(0, min(pos_x, max(0, scr_w - top_w)))
        pos_y = max(0, min(pos_y, max(0, scr_h - top_h)))
        top.geometry(f"{top_w}x{top_h}+{pos_x}+{pos_y}")

    def _abrir_modal_tempo_evento(
        self,
        titulo,
        descricao,
        minuto_inicial="",
        periodo_inicial="",
        assistencia_inicial="",
        opcoes_assistencia=None,
        jogador_principal="",
    ):
        resultado = {}
        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.focus_force()
        top.resizable(False, False)
        top.configure(bg=self.colors["bg"])
        top.minsize(620, 260 if opcoes_assistencia is not None else 210)
        try:
            top.attributes("-topmost", True)
        except tk.TclError:
            pass

        card = tk.Frame(
            top,
            bg=self.colors["bg"],
            highlightthickness=1,
            highlightbackground=self.colors["bg2"],
            bd=0,
            padx=18,
            pady=16,
        )
        card.pack(fill="both", expand=True)
        card.columnconfigure(0, weight=1)

        periodo_map = {label: codigo for codigo, label in PERIODOS_EVENTO}
        periodo_map_inv = {codigo: label for codigo, label in PERIODOS_EVENTO}
        minuto_var = tk.StringVar(value=str(minuto_inicial or ""))
        periodo_var = tk.StringVar(value=periodo_map_inv.get(periodo_inicial, ""))
        assistencia_var = tk.StringVar(value=str(assistencia_inicial or ""))

        tk.Label(
            card,
            text=titulo,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Label(
            card,
            text=descricao,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        linha_tempo = tk.Frame(card, bg=self.colors["bg"])
        linha_tempo.grid(row=2, column=0, sticky="ew")
        linha_tempo.columnconfigure(0, weight=0)
        linha_tempo.columnconfigure(1, weight=0)
        linha_tempo.columnconfigure(2, weight=0)
        linha_tempo.columnconfigure(3, weight=1)
        vcmd = (self.root.register(self._validar_input_inteiro), "%P")
        tk.Label(linha_tempo, text="Minuto", bg=self.colors["bg"], fg=self.colors["tree_head_fg"]).grid(row=0, column=0, sticky="w", padx=(0, 10))
        entry_minuto = ttk.Entry(
            linha_tempo,
            textvariable=minuto_var,
            width=8,
            justify="center",
            validate="key",
            validatecommand=vcmd,
        )
        entry_minuto.grid(row=0, column=1, sticky="w")
        tk.Label(linha_tempo, text="Período", bg=self.colors["bg"], fg=self.colors["tree_head_fg"]).grid(row=0, column=2, sticky="w", padx=(18, 10))
        combo_periodo = ttk.Combobox(
            linha_tempo,
            textvariable=periodo_var,
            values=[label for _codigo, label in PERIODOS_EVENTO],
            state="readonly",
            width=28,
        )
        combo_periodo.grid(row=0, column=3, sticky="w")

        row_info = 3
        combo_assistencia = None
        if opcoes_assistencia is not None:
            assist_frame = tk.Frame(card, bg=self.colors["bg"])
            assist_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
            assist_frame.columnconfigure(1, weight=1)
            opcoes = [
                str(nome).strip()
                for nome in opcoes_assistencia
                if str(nome).strip() and str(nome).strip().casefold() != str(jogador_principal or "").strip().casefold()
            ]
            opcoes = sorted(set(opcoes), key=str.casefold)
            tk.Label(
                assist_frame,
                text="Assistência",
                bg=self.colors["bg"],
                fg=self.colors["tree_head_fg"],
            ).grid(row=0, column=0, sticky="w", padx=(0, 10))
            combo_assistencia = ttk.Combobox(
                assist_frame,
                textvariable=assistencia_var,
                values=[""] + opcoes,
                width=42,
            )
            combo_assistencia.grid(row=0, column=1, sticky="ew")
            self._forcar_cursor_visivel(combo_assistencia)
            row_info = 4

        info_texto = "Preencha o minuto e o período do gol."
        if opcoes_assistencia is not None:
            info_texto += " Assistência é opcional."
        tk.Label(
            card,
            text=info_texto,
            bg=self.colors["bg"],
            fg=self.colors["tree_head_fg"],
            font=("Segoe UI", 10),
        ).grid(row=row_info, column=0, sticky="w", pady=(8, 14))

        def confirmar():
            minuto_txt = minuto_var.get().strip()
            periodo_label = periodo_var.get().strip()
            minuto = _normalizar_minuto_partida(minuto_txt)
            periodo = periodo_map.get(periodo_label, "")
            if not minuto_txt:
                messagebox.showwarning(titulo, "Informe o minuto do lance.", parent=top)
                entry_minuto.focus_set()
                return
            if minuto is None:
                messagebox.showwarning(titulo, "Informe um minuto inteiro entre 0 e 120.", parent=top)
                entry_minuto.focus_set()
                return
            if not periodo:
                messagebox.showwarning(titulo, "Selecione o período do lance.", parent=top)
                combo_periodo.focus_set()
                return
            if minuto > _limite_minuto_evento_por_periodo(periodo):
                limite = _limite_minuto_evento_por_periodo(periodo)
                messagebox.showwarning(titulo, f"Esse período aceita minutos de 0 até {limite}.", parent=top)
                entry_minuto.focus_set()
                return
            assistencia = assistencia_var.get().strip()
            if assistencia and assistencia.casefold() == str(jogador_principal or "").strip().casefold():
                messagebox.showwarning(titulo, "A assistência não pode ser do próprio autor do gol.", parent=top)
                if combo_assistencia is not None:
                    combo_assistencia.focus_set()
                return
            resultado.update({"minuto": minuto, "periodo": periodo, "assistencia": assistencia})
            top.destroy()

        botoes = tk.Frame(card, bg=self.colors["bg"])
        botoes.grid(row=row_info + 1, column=0, sticky="e")
        ttk.Button(botoes, text="Salvar", command=confirmar).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text="Cancelar", command=top.destroy).pack(side="left")

        top.update_idletasks()
        self._centralizar_modal_no_app(top)
        entry_minuto.focus_set()
        top.bind("<Return>", lambda _e: confirmar())
        top.wait_window()
        return resultado or None

    def _registrar_evento_gol(self, lado, jogador, clube=""):
        nome = str(jogador or "").strip()
        if not nome:
            return
        titulo = "Tempo do gol"
        descricao = f"Jogador: {nome}"
        opcoes_assistencia = self.listas.get("jogadores_vasco", []) if lado == "vasco" else None
        tempo = self._abrir_modal_tempo_evento(
            titulo,
            descricao,
            opcoes_assistencia=opcoes_assistencia,
            jogador_principal=nome,
        )
        if not tempo:
            return
        evento = {
            "nome": nome,
            "minuto": tempo["minuto"],
            "periodo": tempo["periodo"],
        }
        assistencia = str(tempo.get("assistencia", "") or "").strip()
        if assistencia:
            evento["assistencia"] = assistencia
        if clube:
            evento["clube"] = clube
        if lado == "vasco":
            if assistencia and assistencia not in self.listas["jogadores_vasco"]:
                self.listas["jogadores_vasco"].append(assistencia)
                self._atualizar_opcoes_gol_vasco()
            self.gols_vasco_eventos.append(evento)
            self._renderizar_lista_eventos(self.lista_gols_vasco, self.gols_vasco_eventos, _formatar_evento_gol)
            self.entry_gol_vasco.delete(0, tk.END)
        else:
            self.gols_contra_eventos.append(evento)
            self._renderizar_lista_eventos(self.lista_gols_contra, self.gols_contra_eventos, _formatar_evento_gol)
            self.entry_gol_contra.delete(0, tk.END)

    def adicionar_gol_vasco(self, event):
        jogador = self.entry_gol_vasco.get().strip()
        if not jogador:
            return
        limite = self._obter_limite_gols("vasco")
        if len(getattr(self, "gols_vasco_eventos", [])) >= limite:
            messagebox.showwarning("Limite Atingido", f"O Vasco só fez {limite} gol(s).")
            return
        if jogador not in self.listas["jogadores_vasco"]:
            self.listas["jogadores_vasco"].append(jogador)
            self._atualizar_opcoes_gol_vasco()
        self._registrar_evento_gol("vasco", jogador)

    def adicionar_gol_contra(self, event):
        jogador = self.entry_gol_contra.get().strip()
        if not jogador:
            return
        limite = self._obter_limite_gols("adversario")
        if len(getattr(self, "gols_contra_eventos", [])) >= limite:
            messagebox.showwarning("Limite Atingido", f"O adversário só fez {limite} gol(s).")
            return
        if jogador not in self.listas["jogadores_contra"]:
            self.listas["jogadores_contra"].append(jogador)
            self.listas["jogadores_contra"] = sorted(self.listas["jogadores_contra"], key=lambda s: s.casefold())
            self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self._registrar_evento_gol("adversario", jogador, self.adversario_var.get().strip())

    def _obter_limite_gols(self, time):
        try:
            if time == "vasco":
                return int(self.placar_vasco.get())
            elif time == "adversario":
                return int(self.placar_adversario.get())
        except ValueError:
            return 0
        return 0

    def remover_gol_vasco(self, event=None):
        sel = self.lista_gols_vasco.curselection()
        if sel:
            del self.gols_vasco_eventos[sel[0]]
            self._renderizar_lista_eventos(self.lista_gols_vasco, self.gols_vasco_eventos, _formatar_evento_gol)

    def remover_gol_contra(self, event=None):
        sel = self.lista_gols_contra.curselection()
        if sel:
            del self.gols_contra_eventos[sel[0]]
            self._renderizar_lista_eventos(self.lista_gols_contra, self.gols_contra_eventos, _formatar_evento_gol)

    def adicionar_cartao_amarelo(self, event=None):
        jogador = self.entry_cartao_amarelo.get().strip()
        if not jogador:
            return
        self.cartoes_amarelos_eventos.append({"nome": jogador})
        self._renderizar_lista_eventos(self.lista_cartoes_amarelos, self.cartoes_amarelos_eventos, _formatar_evento_cartao)
        self.entry_cartao_amarelo.delete(0, tk.END)

    def remover_cartao_amarelo(self, event=None):
        sel = self.lista_cartoes_amarelos.curselection()
        if sel:
            del self.cartoes_amarelos_eventos[sel[0]]
            self._renderizar_lista_eventos(self.lista_cartoes_amarelos, self.cartoes_amarelos_eventos, _formatar_evento_cartao)

    def adicionar_cartao_vermelho(self, event=None):
        jogador = self.entry_cartao_vermelho.get().strip()
        if not jogador:
            return
        self.cartoes_vermelhos_eventos.append({"nome": jogador})
        self._renderizar_lista_eventos(self.lista_cartoes_vermelhos, self.cartoes_vermelhos_eventos, _formatar_evento_cartao)
        self.entry_cartao_vermelho.delete(0, tk.END)

    def remover_cartao_vermelho(self, event=None):
        sel = self.lista_cartoes_vermelhos.curselection()
        if sel:
            del self.cartoes_vermelhos_eventos[sel[0]]
            self._renderizar_lista_eventos(self.lista_cartoes_vermelhos, self.cartoes_vermelhos_eventos, _formatar_evento_cartao)

    # --------------------- Salvar ---------------------
    def salvar_partida(self):
        jogo_anterior = None
        participantes_antes = set()
        if self.editing_index is not None:
            jogos_existentes = carregar_dados_jogos()
            if 0 <= self.editing_index < len(jogos_existentes):
                jogo_anterior = jogos_existentes[self.editing_index]
                participantes_antes = _jogadores_que_participaram_do_jogo(jogo_anterior)
        data = self.data_entry.get()
        adversario = self._resolver_nome_clube_canonico(self.adversario_var.get().strip())
        competicao = self.competicao_var.get().strip()
        placar_vasco = self.placar_vasco.get().strip()
        placar_adv = self.placar_adversario.get().strip()
        local = self.local_var.get()
        estadio = self.estadio_var.get().strip() if hasattr(self, "estadio_var") else ""
        horario = self._obter_horario_formatado()
        capitao = self.capitao_partida_var.get().strip() if hasattr(self, "capitao_partida_var") else ""
        arbitragem = _normalizar_arbitragem({
            "arbitro": self.arbitro_var.get().strip() if hasattr(self, "arbitro_var") else "",
            "auxiliares": [
                self.auxiliar_1_var.get().strip() if hasattr(self, "auxiliar_1_var") else "",
                self.auxiliar_2_var.get().strip() if hasattr(self, "auxiliar_2_var") else "",
            ],
            "var": self.var_arbitragem_var.get().strip() if hasattr(self, "var_arbitragem_var") else "",
        })
        publico_pagante = _normalizar_inteiro_positivo(self.publico_pagante_var.get() if hasattr(self, "publico_pagante_var") else "")
        publico_presente = _normalizar_inteiro_positivo(self.publico_presente_var.get() if hasattr(self, "publico_presente_var") else "")
        renda = _normalizar_renda_brl(self.renda_var.get() if hasattr(self, "renda_var") else "")
        observacao = self.obs_text.get("1.0", "end").strip()
        tecnico = self.tecnico_var.get().strip() if hasattr(self, "tecnico_var") else ""
        posicao_tabela = None
        usa_posicao = self._competicao_usa_posicao(competicao)
        if usa_posicao and hasattr(self, "posicao_var"):
            posicao_txt = self.posicao_var.get().strip()
            if posicao_txt:
                try:
                    posicao_tabela = int(posicao_txt)
                except ValueError:
                    messagebox.showerror("Erro", "Informe apenas números inteiros para a posição na tabela.")
                    return
        elif hasattr(self, "posicao_var"):
            self.posicao_var.set("")

        escalacao_partida = self._coletar_escalacao_partida()
        if _escalacao_partida_vazia(escalacao_partida):
            escalacao_partida = {}
            escalacao_ok, escalacao_msg = True, ""
        else:
            nomes_base_edicao = (
                getattr(self, "_elenco_edicao_partida_cf", None)
                if self.editing_index is not None
                else None
            )
            escalacao_ok, escalacao_msg = self._validar_escalacao_partida(
                escalacao_partida,
                nomes_elenco_obrigatorios=nomes_base_edicao,
            )

        if not (data and adversario and placar_vasco and placar_adv):
            messagebox.showerror("Erro", "Preencha apenas os campos obrigatórios: data, adversário e placar.")
            return
        if horario and not re.match(r"^\d{2}:\d{2}$", horario):
            messagebox.showerror("Erro", "Informe o horário no formato HH:MM.")
            return
        if hasattr(self, "publico_pagante_var") and self.publico_pagante_var.get().strip() and publico_pagante is None:
            messagebox.showerror("Erro", "Informe um público pagante válido.")
            return
        if hasattr(self, "publico_presente_var") and self.publico_presente_var.get().strip() and publico_presente is None:
            messagebox.showerror("Erro", "Informe um público presente válido.")
            return
        if publico_pagante is not None and publico_presente is not None and publico_presente < publico_pagante:
            messagebox.showerror("Erro", "O público presente não pode ser menor que o público pagante.")
            return
        if hasattr(self, "renda_var") and self.renda_var.get().strip() and renda is None:
            messagebox.showerror("Erro", "Informe uma renda válida.")
            return
        if horario:
            horas, minutos = [int(parte) for parte in horario.split(":", 1)]
            if horas > 23 or minutos > 59:
                messagebox.showerror("Erro", "Informe um horário válido entre 00:00 e 23:59.")
                return
        if not escalacao_ok:
            messagebox.showerror("Escalação inválida", escalacao_msg)
            return

        # Gols (contados)
        titulares_cf = set()
        reservas_cf = set()
        tit_por_pos = escalacao_partida.get("titulares_por_posicao", {})
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                for nome_tit in tit_por_pos.get(pos, []):
                    nome_limpo = str(nome_tit).strip()
                    if nome_limpo:
                        titulares_cf.add(nome_limpo.casefold())
        for nome_res in escalacao_partida.get("reservas", []):
            nome_limpo = str(nome_res).strip()
            if nome_limpo:
                reservas_cf.add(nome_limpo.casefold())

        substituicoes_norm = [
            sub
            for sub in (
                _normalizar_substituicao_partida(item)
                for item in escalacao_partida.get("substituicoes", [])
            )
            if sub
        ]
        escalacao_partida["substituicoes"] = substituicoes_norm
        reservas_que_entraram_cf = {
            sub["jogador_entrou"].casefold()
            for sub in substituicoes_norm
        }

        for evento in getattr(self, "gols_vasco_eventos", []):
            nome_evento = str(evento.get("nome", "")).strip()
            nome_evento_cf = nome_evento.casefold()
            if nome_evento and nome_evento_cf in reservas_cf and nome_evento_cf not in titulares_cf:
                reservas_que_entraram_cf.add(nome_evento_cf)
        if reservas_que_entraram_cf:
            escalacao_partida["reservas_que_entraram"] = [
                nome for nome in escalacao_partida.get("reservas", [])
                if str(nome).strip() and str(nome).strip().casefold() in reservas_que_entraram_cf
            ]
        else:
            escalacao_partida["reservas_que_entraram"] = []

        eventos_gols_vasco = []
        for evento in getattr(self, "gols_vasco_eventos", []):
            nome = str(evento.get("nome", "")).strip()
            if not nome:
                continue
            nome_cf = nome.casefold()
            eventos_gols_vasco.append({
                "nome": nome,
                "minuto": _normalizar_minuto_partida(evento.get("minuto")),
                "periodo": str(evento.get("periodo", "")).strip(),
                "assistencia": str(evento.get("assistencia", "") or "").strip(),
                "saiu_do_banco": nome_cf in reservas_cf and nome_cf not in titulares_cf,
            })
        gols_vasco = _agrupar_eventos_gol(eventos_gols_vasco)

        eventos_gols_contra = []
        for evento in getattr(self, "gols_contra_eventos", []):
            nome = str(evento.get("nome", "")).strip()
            if not nome:
                continue
            eventos_gols_contra.append({
                "nome": nome,
                "minuto": _normalizar_minuto_partida(evento.get("minuto")),
                "periodo": str(evento.get("periodo", "")).strip(),
                "assistencia": str(evento.get("assistencia", "") or "").strip(),
                "clube": adversario,
            })
        gols_contra = _agrupar_eventos_gol(eventos_gols_contra)

        cartoes_amarelos_vasco = _agrupar_eventos_cartao(getattr(self, "cartoes_amarelos_eventos", []))
        cartoes_vermelhos_vasco = _agrupar_eventos_cartao(getattr(self, "cartoes_vermelhos_eventos", []))

        alterou_listas = False

        clubes_antes = len(self.listas.get("clubes_adversarios", []))
        adversario = self._registrar_clube_adversario(adversario)
        if len(self.listas.get("clubes_adversarios", [])) != clubes_antes:
            alterou_listas = True
        if hasattr(self, "adversario_var"):
            self.adversario_var.set(adversario)

        if competicao and competicao not in self.listas.get("competicoes", []):
            self.listas.setdefault("competicoes", []).append(competicao)
            self.listas["competicoes"] = sorted(self.listas["competicoes"], key=lambda s: s.casefold())
            self.competicao_entry['values'] = self.listas["competicoes"]
            alterou_listas = True
        if estadio and estadio not in self.listas.get("estadios", []):
            self.listas.setdefault("estadios", []).append(estadio)
            self.listas["estadios"] = sorted(self.listas["estadios"], key=lambda s: s.casefold())
            if hasattr(self, "estadio_entry"):
                self.estadio_entry['values'] = self.listas["estadios"]
            alterou_listas = True

        lista_tecnicos = self.listas.setdefault("tecnicos", [])
        if tecnico and tecnico not in lista_tecnicos:
            lista_tecnicos.append(tecnico)
            self.listas["tecnicos"] = sorted(lista_tecnicos, key=lambda s: s.casefold())
            alterou_listas = True
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(tecnico)
        self._atualizar_combo_tecnicos()

        arbitro = arbitragem.get("arbitro", "")
        if arbitro:
            lista_arbitros = self.listas.setdefault("arbitros", [])
            arbitros_chaves = {_chave_nome_arbitragem(nome) for nome in lista_arbitros}
            if _chave_nome_arbitragem(arbitro) not in arbitros_chaves:
                lista_arbitros.append(arbitro)
                self.listas["arbitros"] = _normalizar_lista_arbitragem_nomes(lista_arbitros)
                alterou_listas = True
            if hasattr(self, "arbitro_entry"):
                self.arbitro_entry["values"] = self.listas["arbitros"]

        auxiliares = arbitragem.get("auxiliares", [])
        if auxiliares:
            lista_auxiliares = self.listas.setdefault("auxiliares", [])
            auxiliares_chaves = {_chave_nome_arbitragem(nome) for nome in lista_auxiliares}
            alterou_aux = False
            for nome in auxiliares:
                chave_nome = _chave_nome_arbitragem(nome)
                if chave_nome not in auxiliares_chaves:
                    lista_auxiliares.append(nome)
                    auxiliares_chaves.add(chave_nome)
                    alterou_aux = True
            if alterou_aux:
                self.listas["auxiliares"] = _normalizar_lista_arbitragem_nomes(lista_auxiliares)
                alterou_listas = True
            if hasattr(self, "auxiliar_1_entry"):
                self.auxiliar_1_entry["values"] = self.listas["auxiliares"]
            if hasattr(self, "auxiliar_2_entry"):
                self.auxiliar_2_entry["values"] = self.listas["auxiliares"]

        var_nome = arbitragem.get("var", "")
        if var_nome:
            lista_vars = self.listas.setdefault("vars", [])
            vars_chaves = {_chave_nome_arbitragem(nome) for nome in lista_vars}
            if _chave_nome_arbitragem(var_nome) not in vars_chaves:
                lista_vars.append(var_nome)
                self.listas["vars"] = _normalizar_lista_arbitragem_nomes(lista_vars)
                alterou_listas = True
            if hasattr(self, "var_arbitragem_entry"):
                self.var_arbitragem_entry["values"] = self.listas["vars"]

        if alterou_listas:
            salvar_listas(self.listas)

        jogo = {
            "data": data,
            "adversario": adversario,
            "competicao": competicao,
            "local": local,  # 'casa' | 'fora'
            "estadio": estadio,
            "horario": horario,
            "placar": {"vasco": int(placar_vasco), "adversario": int(placar_adv)},
            "gols_vasco": gols_vasco,
            "gols_adversario": gols_contra,
            "cartoes_amarelos_vasco": cartoes_amarelos_vasco,
            "cartoes_vermelhos_vasco": cartoes_vermelhos_vasco,
            "observacao": observacao,  # <<< novo campo
            "capitao": capitao,
            "publico_pagante": publico_pagante,
            "publico_presente": publico_presente,
            "renda": renda,
            "tecnico": tecnico,
            "posicao_tabela": posicao_tabela,
            "escalacao_partida": escalacao_partida,
            "arbitragem": arbitragem,
        }
        participantes_depois = _jogadores_que_participaram_do_jogo(jogo)

        jogos = carregar_dados_jogos()
        if self.editing_index is not None:
            if 0 <= self.editing_index < len(jogos):
                jogos[self.editing_index] = jogo
                salvar_lista_jogos(jogos)
                self._ajustar_jogos_pelo_vasco_jogadores_historico(participantes_antes, participantes_depois)
                msg = "Partida atualizada com sucesso!"
            else:
                messagebox.showerror("Erro", "Não foi possível localizar o jogo selecionado para edição.")
                return
        else:
            jogos.append(jogo)
            salvar_lista_jogos(jogos)
            self._ajustar_jogos_pelo_vasco_jogadores_historico(set(), participantes_depois)
            msg = "Partida registrada com sucesso!"

        if self.editing_index is None:
            self._atualizar_condicoes_elenco_por_escalacao(escalacao_partida)
        self._limpar_formulario()
        self._atualizar_abas()
        self.notebook.select(self.frame_temporadas)

    def _abrir_importador_jogo_json(self):
        top = tk.Toplevel(self.root)
        top.title("Importar jogo por JSON")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.focus_force()
        top.geometry("900x620")
        top.configure(bg=self.colors["bg"])

        frame = ttk.Frame(top, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        status_var = tk.StringVar(
            value=(
                "Cole um jogo, uma lista, ou um objeto {\"jogos\": [...]}. "
                "Se bater com data + adversário, o app atualiza a partida existente."
            )
        )
        ttk.Label(frame, textvariable=status_var).grid(row=0, column=0, sticky="w", pady=(0, 8))

        texto = tk.Text(
            frame,
            wrap="none",
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["fg"],
        )
        texto.grid(row=1, column=0, sticky="nsew")
        self._forcar_cursor_visivel(texto)

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=texto.yview)
        scroll_y.grid(row=1, column=1, sticky="ns")
        texto.configure(yscrollcommand=scroll_y.set)

        botoes = ttk.Frame(frame)
        botoes.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        def carregar_arquivo():
            caminho = filedialog.askopenfilename(
                title="Selecionar JSON de jogo",
                filetypes=(("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")),
                parent=top,
            )
            if not caminho:
                return
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
            except Exception as exc:
                messagebox.showerror("Erro", f"Não foi possível ler o arquivo:\n{exc}", parent=top)
                return
            texto.delete("1.0", "end")
            texto.insert("1.0", conteudo)
            status_var.set(os.path.basename(caminho))

        def inserir_exemplo():
            if texto.get("1.0", "end").strip() and not messagebox.askyesno(
                "Inserir exemplo",
                "Substituir o conteúdo atual pelo exemplo JSON?",
                parent=top,
            ):
                return
            texto.delete("1.0", "end")
            texto.insert("1.0", self._exemplo_json_importacao_jogos())
            status_var.set("Exemplo inserido. Ajuste data/adversário antes de importar.")

        def copiar_exemplo():
            self.root.clipboard_clear()
            self.root.clipboard_append(self._exemplo_json_importacao_jogos())
            self.root.update()
            status_var.set("Exemplo JSON copiado para a área de transferência.")

        def copiar_prompt_claude():
            self.root.clipboard_clear()
            self.root.clipboard_append(self._prompt_claude_importacao_jogos())
            self.root.update()
            status_var.set("Prompt para Claude copiado para a área de transferência.")

        def importar():
            if self._importar_json_jogos_texto(texto.get("1.0", "end"), parent=top):
                top.destroy()

        ttk.Button(botoes, text="Carregar Arquivo", command=carregar_arquivo).pack(side="left")
        ttk.Button(botoes, text="Inserir Exemplo", command=inserir_exemplo).pack(side="left", padx=(8, 0))
        ttk.Button(botoes, text="Copiar Exemplo", command=copiar_exemplo).pack(side="left", padx=(8, 0))
        ttk.Button(botoes, text="Copiar Prompt Claude", command=copiar_prompt_claude).pack(side="left", padx=(8, 0))
        ttk.Button(botoes, text="Importar", command=importar).pack(side="right", padx=(8, 0))
        ttk.Button(botoes, text="Cancelar", command=top.destroy).pack(side="right")
        top.bind("<Escape>", lambda _e: top.destroy())
        texto.focus_set()

    def _exemplo_json_importacao_jogos(self):
        exemplo = {
            "jogos": [
                {
                    "data": "dd/mm/aaaa",
                    "adversario": "Nome do adversário como aparece no app",
                    "competicao": "Campeonato Brasileiro Serie A",
                    "local": "casa",
                    "placar": {"vasco": 0, "adversario": 0},
                    "estadio": "São Januário",
                    "horario": "HH:MM",
                    "tecnico": "Nome do técnico",
                    "capitao": "",
                    "publico_pagante": None,
                    "publico_presente": None,
                    "renda": None,
                    "arbitragem": {
                        "arbitro": "",
                        "auxiliares": ["", ""],
                        "var": "",
                    },
                    "gols_vasco": [
                        {
                            "nome": "Jogador do Vasco",
                            "minuto": 0,
                            "periodo": "1T",
                            "assistencia": "",
                        }
                    ],
                    "gols_adversario": [
                        {
                            "nome": "Jogador adversário",
                            "minuto": 0,
                            "periodo": "1T",
                            "assistencia": "",
                        }
                    ],
                    "cartoes_amarelos_vasco": [{"nome": "Jogador do Vasco"}],
                    "cartoes_vermelhos_vasco": [],
                    "estatisticas_vasco": {
                        "posse_bola": None,
                        "passes_certos": None,
                        "passes_errados": None,
                        "passes_tentados": None,
                        "precisao_passes": None,
                        "finalizacoes": None,
                        "finalizacoes_no_gol": None,
                        "escanteios": None,
                        "faltas_cometidas": None,
                        "desarmes": None,
                    },
                    "estatisticas_jogadores_vasco": [
                        {
                            "nome": "Jogador do Vasco",
                            "minutos": None,
                            "passes_certos": None,
                            "passes_errados": None,
                            "passes_tentados": None,
                            "finalizacoes": None,
                            "desarmes": None,
                            "nota_sofascore": None,
                        }
                    ],
                    "escalacao_partida": {
                        "titulares_por_posicao": {
                            "Goleiro": ["Goleiro"],
                            "Lateral-Direito": ["Lateral direito"],
                            "Zagueiro": ["Zagueiro 1", "Zagueiro 2"],
                            "Lateral-Esquerdo": ["Lateral esquerdo"],
                            "Volante": ["Volante 1", "Volante 2"],
                            "Meio-Campista": ["Meia"],
                            "Atacante": ["Atacante 1", "Atacante 2", "Atacante 3"],
                        },
                        "reservas": ["Reserva 1", "Reserva 2", "Reserva 3", "Reserva 4"],
                        "substituicoes": [
                            {
                                "jogador_entrou": "Reserva 1",
                                "jogador_saiu": "Atacante 1",
                                "minuto": 20,
                                "periodo": "2T",
                            }
                        ],
                        "nao_relacionados": [],
                        "lesionados": [],
                        "suspensos": [],
                        "servindo_selecao": [],
                    },
                    "observacao": "Resumo editorial do jogo, sem fontes ou links.",
                }
            ]
        }
        return json.dumps(exemplo, ensure_ascii=False, indent=2)

    def _prompt_claude_importacao_jogos(self):
        return (
            "Preencha dados de partidas do Vasco no formato JSON abaixo. "
            "Retorne somente JSON válido, sem Markdown, sem comentários e sem texto fora do JSON.\n\n"
            "Regras:\n"
            "- Pode retornar um objeto {\"jogos\": [...]} ou uma lista direta de jogos.\n"
            "- Para atualizar jogo já cadastrado, mantenha data + adversário; competição e local ajudam a evitar ambiguidade.\n"
            "- Só inclua campos que tiver pesquisado. Campos enviados vão sobrescrever o banco; campos omitidos ficam como estão.\n"
            "- Se alterar gols, cartões ou escalação, envie a lista completa daquele campo, pois listas substituem a lista anterior.\n"
            "- Em observacao, escreva apenas resumo e curiosidades do jogo, nunca fontes, links ou notas de pesquisa.\n"
            "- Use periodos 1T, 2T, 1P ou 2P. Para intervalo em substituições, use INT.\n\n"
            "- Use estatisticas_vasco somente para números do Vasco, sem números do adversário.\n"
            "- Use estatisticas_jogadores_vasco somente para jogadores do Vasco; cada item precisa ter nome.\n\n"
            "Modelo:\n"
            f"{self._exemplo_json_importacao_jogos()}"
        )

    def _importar_json_jogos_texto(self, texto_json: str, parent=None) -> bool:
        texto_json = str(texto_json or "").strip()
        if not texto_json:
            messagebox.showerror("Importar JSON", "Cole o JSON do jogo antes de importar.", parent=parent)
            return False
        try:
            payload = json.loads(texto_json)
        except json.JSONDecodeError as exc:
            messagebox.showerror("Importar JSON", f"JSON inválido: {exc}", parent=parent)
            return False

        try:
            operacoes = self._preparar_operacoes_importacao_jogos(payload)
        except ValueError as exc:
            messagebox.showerror("Importar JSON", str(exc), parent=parent)
            return False

        if not operacoes:
            messagebox.showerror("Importar JSON", "Nenhum jogo válido encontrado no JSON.", parent=parent)
            return False

        resumo = self._resumo_operacoes_importacao_jogos(operacoes)
        if not messagebox.askyesno("Confirmar importação", resumo, parent=parent):
            return False

        resultado = self._salvar_operacoes_importacao_jogos(operacoes)
        messagebox.showinfo(
            "Importação concluída",
            (
                f"{resultado['atualizados']} jogo{'s' if resultado['atualizados'] != 1 else ''} "
                f"atualizado{'s' if resultado['atualizados'] != 1 else ''}; "
                f"{resultado['novos']} jogo{'s' if resultado['novos'] != 1 else ''} "
                f"cadastrado{'s' if resultado['novos'] != 1 else ''}."
            ),
            parent=parent,
        )
        return True

    def _extrair_itens_payload_jogos_importacao(self, payload):
        if isinstance(payload, dict):
            for chave in ("jogos", "partidas", "matches"):
                if chave in payload:
                    itens = payload.get(chave)
                    if not isinstance(itens, list):
                        raise ValueError(f"'{chave}' precisa ser uma lista de jogos.")
                    return itens
            return [payload]
        if isinstance(payload, list):
            return payload
        raise ValueError("O JSON deve ser um objeto de jogo, uma lista de jogos ou {'jogos': [...]}.")

    def _normalizar_payload_jogos_importacao(self, payload):
        itens = self._extrair_itens_payload_jogos_importacao(payload)

        self._atualizar_elenco_disponivel_partida()
        jogos = []
        for idx, item in enumerate(itens, start=1):
            prefixo = f"Jogo {idx}: " if len(itens) > 1 else ""
            jogos.append(self._normalizar_jogo_importado(item, prefixo))
        return jogos

    def _preparar_operacoes_importacao_jogos(self, payload):
        itens = self._extrair_itens_payload_jogos_importacao(payload)
        if not itens:
            return []

        self._atualizar_elenco_disponivel_partida()
        jogos_trabalho = [copy.deepcopy(jogo) for jogo in carregar_dados_jogos()]
        operacoes = []
        erros = []

        for idx, item in enumerate(itens, start=1):
            prefixo = f"Jogo {idx}: " if len(itens) > 1 else ""
            if not isinstance(item, dict):
                erros.append(f"{prefixo}cada jogo precisa ser um objeto JSON.")
                continue
            try:
                indice, motivo = self._localizar_jogo_existente_importacao(item, jogos_trabalho)
                if indice is None:
                    jogo = self._normalizar_jogo_importado(item, prefixo)
                    operacoes.append({
                        "acao": "criar",
                        "indice": None,
                        "jogo": jogo,
                        "descricao": self._descricao_jogo_importacao(jogo),
                        "motivo": motivo,
                    })
                    jogos_trabalho.append(copy.deepcopy(jogo))
                    continue

                existente = jogos_trabalho[indice]
                mesclado = self._mesclar_json_jogo_importado(existente, item)
                jogo = self._normalizar_jogo_importado(
                    mesclado,
                    prefixo,
                    completar_escalacao_com_elenco=False,
                )
                operacoes.append({
                    "acao": "atualizar",
                    "indice": indice,
                    "jogo": jogo,
                    "antes": copy.deepcopy(existente),
                    "descricao": self._descricao_jogo_importacao(jogo),
                    "motivo": motivo,
                })
                jogos_trabalho[indice] = copy.deepcopy(jogo)
            except ValueError as exc:
                erros.append(str(exc))

        if erros:
            limite = "\n".join(erros[:8])
            sufixo = "" if len(erros) <= 8 else f"\n... e mais {len(erros) - 8} erro(s)."
            raise ValueError(f"Não foi possível preparar a importação:\n\n{limite}{sufixo}")

        return operacoes

    def _descricao_jogo_importacao(self, jogo):
        data = str(jogo.get("data", "") or "").strip()
        adversario = str(jogo.get("adversario", "") or "").strip()
        competicao = str(jogo.get("competicao", "") or "").strip()
        local = str(jogo.get("local", "") or "").strip()
        placar = jogo.get("placar") if isinstance(jogo.get("placar"), dict) else {}
        placar_txt = ""
        if "vasco" in placar and "adversario" in placar:
            placar_txt = f" {placar.get('vasco')}x{placar.get('adversario')}"
        extras = " · ".join(parte for parte in (competicao, local) if parte)
        return f"{data} - {adversario}{placar_txt}" + (f" ({extras})" if extras else "")

    def _resumo_operacoes_importacao_jogos(self, operacoes):
        atualizacoes = [op for op in operacoes if op.get("acao") == "atualizar"]
        novos = [op for op in operacoes if op.get("acao") == "criar"]
        linhas = [
            f"Atualizar existentes: {len(atualizacoes)}",
            f"Cadastrar novos: {len(novos)}",
            "",
            "Campos enviados no JSON substituem os dados atuais; campos omitidos permanecem como estão.",
        ]
        previa = []
        for op in operacoes[:10]:
            marcador = "Atualizar" if op.get("acao") == "atualizar" else "Cadastrar"
            previa.append(f"- {marcador}: {op.get('descricao', '')}")
        if previa:
            linhas.extend(["", "Prévia:", *previa])
        if len(operacoes) > 10:
            linhas.append(f"... e mais {len(operacoes) - 10}.")
        if novos:
            linhas.extend([
                "",
                "Atenção: jogos em 'Cadastrar novos' não bateram com uma partida existente. "
                "Confira se não há erro de data/adversário antes de confirmar.",
            ])
        return "\n".join(linhas)

    def _chave_fuzzy_importacao(self, valor, *, tipo="geral"):
        texto = str(valor or "").strip()
        if not texto:
            return "", set()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
        texto = re.sub(r"[^0-9a-zA-Z]+", " ", texto).casefold()
        tokens = [tok for tok in texto.split() if tok]
        stopwords = {"de", "do", "da", "dos", "das", "e"}
        if tipo == "competicao":
            stopwords |= {
                "betano",
                "betnado",
                "betnacional",
                "pixbet",
                "kings",
                "superbet",
                "sicredi",
            }
        tokens = [tok for tok in tokens if tok not in stopwords]
        return " ".join(tokens), set(tokens)

    def _resolver_fuzzy_importacao(self, valor, opcoes, *, tipo="geral", threshold=0.78):
        valor_limpo = str(valor or "").strip()
        if not valor_limpo:
            return ""

        opcoes_limpas = []
        vistos = set()
        for opcao in opcoes or []:
            nome = str(opcao or "").strip()
            chave_nome = nome.casefold()
            if not nome or chave_nome in vistos:
                continue
            vistos.add(chave_nome)
            opcoes_limpas.append(nome)

        entrada_chave, entrada_tokens = self._chave_fuzzy_importacao(valor_limpo, tipo=tipo)
        if not entrada_chave:
            return valor_limpo

        melhor = None
        segundo_score = 0.0
        for opcao in opcoes_limpas:
            opcao_chave, opcao_tokens = self._chave_fuzzy_importacao(opcao, tipo=tipo)
            if not opcao_chave:
                continue
            if entrada_chave == opcao_chave:
                score = 1.0
            else:
                ratio = SequenceMatcher(None, entrada_chave, opcao_chave).ratio()
                inter = entrada_tokens & opcao_tokens
                uniao = entrada_tokens | opcao_tokens
                jaccard = (len(inter) / len(uniao)) if uniao else 0.0
                subset = bool(inter) and (inter == entrada_tokens or inter == opcao_tokens)
                score = max(ratio, jaccard)
                if subset and min(len(entrada_tokens), len(opcao_tokens)) >= 1:
                    score = max(score, 0.92)
            if melhor is None or score > melhor[0]:
                segundo_score = melhor[0] if melhor else 0.0
                melhor = (score, opcao)
            elif score > segundo_score:
                segundo_score = score

        if not melhor:
            return valor_limpo
        score, nome = melhor
        if score >= threshold and (score - segundo_score >= 0.08 or score >= 0.98):
            return nome
        return valor_limpo

    def _opcoes_importacao_campo(self, chave_lista):
        opcoes = list(self.listas.get(chave_lista, [])) if isinstance(self.listas, dict) else []
        if chave_lista == "competicoes":
            for jogo in carregar_dados_jogos():
                nome = str(jogo.get("competicao", "") or "").strip()
                if nome:
                    opcoes.append(nome)
        elif chave_lista == "estadios":
            for jogo in carregar_dados_jogos():
                nome = str(jogo.get("estadio", "") or "").strip()
                if nome:
                    opcoes.append(nome)
        elif chave_lista == "tecnicos":
            for jogo in carregar_dados_jogos():
                nome = str(jogo.get("tecnico", "") or "").strip()
                if nome:
                    opcoes.append(nome)
        return opcoes

    def _resolver_competicao_importacao(self, valor):
        resolvido = self._resolver_fuzzy_importacao(
            valor,
            self._opcoes_importacao_campo("competicoes"),
            tipo="competicao",
            threshold=0.72,
        )
        chave, tokens = self._chave_fuzzy_importacao(resolvido, tipo="competicao")
        if tokens == {"copa", "brasil"}:
            return "Copa do Brasil"
        return resolvido

    def _normalizar_data_importacao(self, valor):
        texto = str(valor or "").strip()
        if not texto:
            return ""
        if _parse_data_ptbr_safe(texto):
            return texto
        match_iso = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", texto)
        if match_iso:
            ano, mes, dia = match_iso.groups()
            candidato = f"{dia}/{mes}/{ano}"
            if _parse_data_ptbr_safe(candidato):
                return candidato
        return texto

    def _valor_json_importacao(self, item, *chaves, padrao=""):
        if not isinstance(item, dict):
            return padrao
        for chave in chaves:
            if chave in item:
                return item.get(chave)
        return padrao

    def _adversario_json_importacao(self, item):
        adversario = self._valor_json_importacao(item, "adversario", "oponente", "opponent", padrao="")
        adversario = str(adversario or "").strip()
        if adversario:
            return adversario
        confronto = str(self._valor_json_importacao(item, "jogo", "partida", "confronto", padrao="") or "").strip()
        if confronto:
            extraido = _extrair_adversario_de_jogo(confronto).replace("Vasco", "").strip()
            if extraido:
                return extraido
        return ""

    def _int_json_importacao_se_possivel(self, valor):
        if valor in (None, "") or isinstance(valor, bool):
            return None
        try:
            return int(str(valor).strip())
        except Exception:
            return None

    def _localizar_jogo_existente_importacao(self, item, jogos_existentes):
        id_raw = self._valor_json_importacao(item, "db_match_id", "match_id", "id", padrao=None)
        id_busca = self._int_json_importacao_se_possivel(id_raw)
        if id_busca is not None:
            encontrados = [
                (idx, jogo)
                for idx, jogo in enumerate(jogos_existentes)
                if self._int_json_importacao_se_possivel(jogo.get("db_match_id")) == id_busca
            ]
            if len(encontrados) == 1:
                return encontrados[0][0], "id"
            if len(encontrados) > 1:
                raise ValueError(f"ID {id_busca} encontrou mais de uma partida.")

        data = self._normalizar_data_importacao(self._valor_json_importacao(item, "data", "date", padrao=""))
        adversario_raw = self._adversario_json_importacao(item)
        if not data or not adversario_raw:
            return None, "sem data/adversário suficientes para localizar existente"
        if not _parse_data_ptbr_safe(data):
            return None, "data não está em dd/mm/aaaa"

        adversario = self._resolver_fuzzy_importacao(
            adversario_raw,
            self._opcoes_clubes_adversarios(),
            tipo="geral",
            threshold=0.76,
        )
        adversario = self._resolver_nome_clube_canonico(adversario)
        chave_adv = _chave_nome_consulta(adversario)
        if not chave_adv:
            return None, "adversário vazio"

        competicao_raw = self._valor_json_importacao(item, "competicao", "campeonato", "competition", padrao="")
        competicao = self._resolver_competicao_importacao(competicao_raw) if str(competicao_raw or "").strip() else ""
        chave_comp = self._chave_fuzzy_importacao(competicao, tipo="competicao")[0] if competicao else ""
        local = str(self._valor_json_importacao(item, "local", padrao="") or "").strip().casefold()
        placar = item.get("placar") if isinstance(item.get("placar"), dict) else {}
        placar_vasco = self._int_json_importacao_se_possivel(placar.get("vasco")) if placar else None
        placar_adv = self._int_json_importacao_se_possivel(placar.get("adversario")) if placar else None

        candidatos = []
        for idx, jogo in enumerate(jogos_existentes):
            if str(jogo.get("data", "") or "").strip() != data:
                continue
            if _chave_nome_consulta(jogo.get("adversario", "")) != chave_adv:
                continue
            score = 10
            if chave_comp:
                chave_jogo = self._chave_fuzzy_importacao(jogo.get("competicao", ""), tipo="competicao")[0]
                if chave_jogo != chave_comp:
                    continue
                score += 3
            if local in {"casa", "fora"}:
                if str(jogo.get("local", "") or "").strip().casefold() != local:
                    continue
                score += 1
            placar_jogo = jogo.get("placar") if isinstance(jogo.get("placar"), dict) else {}
            if placar_vasco is not None and placar_adv is not None:
                jogo_vasco = self._int_json_importacao_se_possivel(placar_jogo.get("vasco"))
                jogo_adv = self._int_json_importacao_se_possivel(placar_jogo.get("adversario"))
                if jogo_vasco == placar_vasco and jogo_adv == placar_adv:
                    score += 1
            candidatos.append((score, idx))

        if not candidatos:
            return None, "não encontrou partida existente"
        candidatos.sort(reverse=True)
        if len(candidatos) > 1 and candidatos[0][0] == candidatos[1][0]:
            desc = f"{data} - {adversario}"
            raise ValueError(f"{desc}: mais de uma partida possível. Informe competição, local ou db_match_id.")
        return candidatos[0][1], "data/adversário"

    def _mesclar_dicts_json_importacao(self, base, entrada):
        saida = copy.deepcopy(base) if isinstance(base, dict) else {}
        if not isinstance(entrada, dict):
            return saida
        for chave, valor in entrada.items():
            if isinstance(valor, dict) and isinstance(saida.get(chave), dict):
                saida[chave] = self._mesclar_dicts_json_importacao(saida.get(chave), valor)
            else:
                saida[chave] = copy.deepcopy(valor)
        return saida

    def _mesclar_json_jogo_importado(self, existente, entrada):
        mesclado = copy.deepcopy(existente) if isinstance(existente, dict) else {}
        aliases = {
            "campeonato": "competicao",
            "competition": "competicao",
            "date": "data",
            "hora": "horario",
            "observacoes": "observacao",
            "oponente": "adversario",
            "opponent": "adversario",
            "escalacao": "escalacao_partida",
            "stats_vasco": "estatisticas_vasco",
            "estatisticas_time_vasco": "estatisticas_vasco",
            "estatisticas_equipe_vasco": "estatisticas_vasco",
            "stats_jogadores_vasco": "estatisticas_jogadores_vasco",
            "estatisticas_individuais_vasco": "estatisticas_jogadores_vasco",
            "estatisticas_individuais_jogadores_vasco": "estatisticas_jogadores_vasco",
        }
        ignorar = {"db_match_id", "db_tecnico_id", "match_id", "id", "_comentario", "_instrucoes"}
        for chave, valor in entrada.items() if isinstance(entrada, dict) else []:
            if chave in ignorar:
                continue
            chave_destino = aliases.get(chave, chave)
            if chave_destino == "data":
                valor = self._normalizar_data_importacao(valor)
            if (
                chave_destino in {"placar", "arbitragem", "gols_anulados", "escalacao_partida", "estatisticas_vasco"}
                and isinstance(valor, dict)
                and isinstance(mesclado.get(chave_destino), dict)
            ):
                mesclado[chave_destino] = self._mesclar_dicts_json_importacao(mesclado.get(chave_destino), valor)
            else:
                mesclado[chave_destino] = copy.deepcopy(valor)
        return mesclado

    def _opcoes_jogadores_importacao(self):
        opcoes = []
        for jogador in getattr(self, "elenco_atual", {}).get("jogadores", []):
            if isinstance(jogador, dict):
                nome = str(jogador.get("nome", "") or "").strip()
                if nome:
                    opcoes.append(nome)
        opcoes.extend(self.listas.get("jogadores_vasco", []))
        historico = getattr(self, "jogadores_historico", {})
        for jogador in historico.get("jogadores", []) if isinstance(historico, dict) else []:
            if isinstance(jogador, dict):
                nome = str(jogador.get("nome", "") or "").strip()
                if nome:
                    opcoes.append(nome)
        for jogo in carregar_dados_jogos():
            esc = jogo.get("escalacao_partida", jogo.get("escalacao", {}))
            if isinstance(esc, dict):
                tit_por_pos = esc.get("titulares_por_posicao", {})
                if isinstance(tit_por_pos, dict):
                    for pos in POSICOES_ELENCO:
                        opcoes.extend(tit_por_pos.get(pos, []))
                for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
                    opcoes.extend(esc.get(chave, []))
            for evento in _expandir_eventos_gol(jogo.get("gols_vasco", [])):
                opcoes.append(evento.get("nome", ""))
            for evento in _expandir_eventos_cartao(jogo.get("cartoes_amarelos_vasco", [])):
                opcoes.append(evento.get("nome", ""))
            for evento in _expandir_eventos_cartao(jogo.get("cartoes_vermelhos_vasco", [])):
                opcoes.append(evento.get("nome", ""))
            for jogador_stats in jogo.get("estatisticas_jogadores_vasco", []):
                if isinstance(jogador_stats, dict):
                    opcoes.append(jogador_stats.get("nome", ""))
        return opcoes

    def _resolver_jogador_importacao(self, nome):
        opcoes_elenco = [
            str(jogador.get("nome", "") or "").strip()
            for jogador in getattr(self, "elenco_atual", {}).get("jogadores", [])
            if isinstance(jogador, dict) and str(jogador.get("nome", "") or "").strip()
        ]
        resolvido_elenco = self._resolver_fuzzy_importacao(
            nome,
            opcoes_elenco,
            tipo="pessoa",
            threshold=0.72,
        )
        if str(resolvido_elenco or "").strip() and str(resolvido_elenco).strip() != str(nome or "").strip():
            return resolvido_elenco
        return self._resolver_fuzzy_importacao(
            nome,
            self._opcoes_jogadores_importacao(),
            tipo="pessoa",
            threshold=0.72,
        )

    def _resolver_jogador_contra_importacao(self, nome):
        opcoes = list(self.listas.get("jogadores_contra", []))
        for jogo in carregar_dados_jogos():
            for evento in _expandir_eventos_gol(jogo.get("gols_adversario", [])):
                opcoes.append(evento.get("nome", ""))
        return self._resolver_fuzzy_importacao(nome, opcoes, tipo="pessoa", threshold=0.72)

    def _normalizar_arbitragem_importada(self, dados):
        arbitragem = _normalizar_arbitragem(dados)
        resolvida = {
            "arbitro": self._resolver_fuzzy_importacao(
                arbitragem.get("arbitro", ""),
                self.listas.get("arbitros", []),
                tipo="pessoa",
                threshold=0.76,
            ),
            "auxiliares": [
                self._resolver_fuzzy_importacao(
                    auxiliar,
                    self.listas.get("auxiliares", []),
                    tipo="pessoa",
                    threshold=0.76,
                )
                for auxiliar in arbitragem.get("auxiliares", [])
            ],
            "var": self._resolver_fuzzy_importacao(
                arbitragem.get("var", ""),
                self.listas.get("vars", []),
                tipo="pessoa",
                threshold=0.76,
            ),
        }
        return _normalizar_arbitragem(resolvida)

    def _normalizar_nomes_importados_lista(self, nomes):
        if not isinstance(nomes, list):
            return nomes
        return [self._resolver_jogador_importacao(nome) for nome in nomes]

    def _posicao_historico_jogador_importacao(self, nome):
        alvo = _chave_nome_jogador(nome)
        if not alvo:
            return ""
        historico = getattr(self, "jogadores_historico", {})
        for jogador in historico.get("jogadores", []) if isinstance(historico, dict) else []:
            if not isinstance(jogador, dict):
                continue
            if _chave_nome_jogador(jogador.get("nome", "")) != alvo:
                continue
            posicao = str(jogador.get("posicao", "") or "").strip()
            if posicao in POSICOES_ELENCO:
                return posicao
        return ""

    def _coletar_jogadores_escalacao_importada_para_elenco(self, escalacao, data_jogo=""):
        if not isinstance(escalacao, dict) or not escalacao:
            return []

        candidatos = {}
        titulares_pos_por_cf = {}

        def registrar(nome, posicao, condicao):
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                return
            chave = nome_limpo.casefold()
            posicao_norm = _normalizar_posicao_elenco(
                posicao or self._posicao_historico_jogador_importacao(nome_limpo)
            )
            novo = {
                "nome": nome_limpo,
                "posicao": posicao_norm,
                "condicao": _normalizar_condicao_elenco(condicao),
                "capitao": False,
                "data_registro": str(data_jogo or "").strip(),
                "data_entrada": str(data_jogo or "").strip(),
            }
            atual = candidatos.get(chave)
            if not atual:
                candidatos[chave] = novo
                return
            if atual.get("posicao") == "Meio-Campista" and posicao_norm != "Meio-Campista":
                atual["posicao"] = posicao_norm
            atual["condicao"] = novo["condicao"]

        titulares_por_posicao = escalacao.get("titulares_por_posicao", {})
        if isinstance(titulares_por_posicao, dict):
            for posicao in POSICOES_ELENCO:
                for nome in titulares_por_posicao.get(posicao, []):
                    nome_limpo = str(nome or "").strip()
                    if not nome_limpo:
                        continue
                    titulares_pos_por_cf[nome_limpo.casefold()] = posicao
                    registrar(nome_limpo, posicao, "Titular")

        posicao_reserva_por_cf = {}
        for sub in escalacao.get("substituicoes", []) if isinstance(escalacao.get("substituicoes", []), list) else []:
            if not isinstance(sub, dict):
                continue
            entrou = str(sub.get("jogador_entrou", "") or "").strip()
            saiu = str(sub.get("jogador_saiu", "") or "").strip()
            posicao_saiu = titulares_pos_por_cf.get(saiu.casefold())
            if entrou and posicao_saiu:
                posicao_reserva_por_cf.setdefault(entrou.casefold(), posicao_saiu)

        for nome in escalacao.get("reservas", []) if isinstance(escalacao.get("reservas", []), list) else []:
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                continue
            posicao = self._posicao_historico_jogador_importacao(nome_limpo) or posicao_reserva_por_cf.get(nome_limpo.casefold(), "")
            registrar(nome_limpo, posicao, "Reserva")

        for chave, condicao in (
            ("nao_relacionados", "Não Relacionado"),
            ("lesionados", "Lesionado"),
            ("suspensos", "Suspenso"),
            ("servindo_selecao", "Servindo a seleção"),
        ):
            for nome in escalacao.get(chave, []) if isinstance(escalacao.get(chave, []), list) else []:
                nome_limpo = str(nome or "").strip()
                if not nome_limpo:
                    continue
                registrar(nome_limpo, self._posicao_historico_jogador_importacao(nome_limpo), condicao)

        return list(candidatos.values())

    def _garantir_jogadores_importados_no_elenco_atual(self, jogos_importados):
        if not isinstance(jogos_importados, list) or not jogos_importados:
            return

        atuais_cf = {
            str(jogador.get("nome", "") or "").strip().casefold()
            for jogador in self.elenco_atual.get("jogadores", [])
            if isinstance(jogador, dict) and str(jogador.get("nome", "") or "").strip()
        }
        candidatos = {}
        jogos_ordenados = sorted(
            [jogo for jogo in jogos_importados if isinstance(jogo, dict)],
            key=lambda jogo: _parse_data_ptbr_safe(str(jogo.get("data", "") or "").strip()) or datetime.max,
        )

        for jogo in jogos_ordenados:
            for jogador in self._coletar_jogadores_escalacao_importada_para_elenco(
                jogo.get("escalacao_partida", {}),
                jogo.get("data", ""),
            ):
                nome = str(jogador.get("nome", "") or "").strip()
                if not nome:
                    continue
                chave = nome.casefold()
                if chave in atuais_cf:
                    continue
                atual = candidatos.get(chave)
                if not atual:
                    candidatos[chave] = jogador
                    continue
                if atual.get("posicao") == "Meio-Campista" and jogador.get("posicao") != "Meio-Campista":
                    atual["posicao"] = jogador["posicao"]
                atual["condicao"] = jogador["condicao"]

        if not candidatos:
            return

        jogadores_novos = []
        for jogador in candidatos.values():
            jogadores_novos.append({
                "nome": jogador["nome"],
                "posicao": _normalizar_posicao_elenco(jogador.get("posicao")),
                "condicao": _normalizar_condicao_elenco(jogador.get("condicao")),
                "capitao": False,
                "data_registro": str(jogador.get("data_registro", "") or "").strip(),
                "data_entrada": str(jogador.get("data_entrada", "") or "").strip(),
            })

        self.elenco_atual.setdefault("jogadores", []).extend(
            {
                "nome": jogador["nome"],
                "posicao": jogador["posicao"],
                "condicao": jogador["condicao"],
                "capitao": False,
            }
            for jogador in jogadores_novos
        )
        salvar_elenco_atual(self.elenco_atual)
        self.elenco_atual = carregar_elenco_atual()
        self._adicionar_jogadores_historico(jogadores_novos)
        self._atualizar_elenco_disponivel_partida()
        if hasattr(self, "_render_elenco_atual"):
            self._render_elenco_atual()
        if hasattr(self, "_render_aba_jogadores_historico"):
            self._render_aba_jogadores_historico()

    def _canonicalizar_escalacao_importada(self, bruto):
        if not isinstance(bruto, dict):
            return bruto
        out = dict(bruto)
        tit = out.get("titulares_por_posicao")
        if isinstance(tit, dict):
            tit_norm = {}
            for pos in POSICOES_ELENCO:
                nomes = tit.get(pos, [])
                tit_norm[pos] = self._normalizar_nomes_importados_lista(nomes) if isinstance(nomes, list) else nomes
            out["titulares_por_posicao"] = tit_norm
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            nomes = out.get(chave)
            if isinstance(nomes, list):
                out[chave] = self._normalizar_nomes_importados_lista(nomes)
        reservas_cf_para_nome = {
            str(nome).strip().casefold(): str(nome).strip()
            for nome in out.get("reservas", [])
            if str(nome).strip()
        }
        titulares_cf_para_nome = {}
        tit = out.get("titulares_por_posicao", {})
        if isinstance(tit, dict):
            for pos in POSICOES_ELENCO:
                for nome in tit.get(pos, []):
                    nome_limpo = str(nome).strip()
                    if nome_limpo:
                        titulares_cf_para_nome[nome_limpo.casefold()] = nome_limpo
        subs = out.get("substituicoes")
        if isinstance(subs, list):
            subs_norm = []
            for sub in subs:
                if not isinstance(sub, dict):
                    subs_norm.append(sub)
                    continue
                sub_norm = dict(sub)
                entrou = self._resolver_jogador_importacao(sub_norm.get("jogador_entrou", ""))
                saiu = self._resolver_jogador_importacao(sub_norm.get("jogador_saiu", ""))
                sub_norm["jogador_entrou"] = reservas_cf_para_nome.get(str(entrou).strip().casefold(), entrou)
                sub_norm["jogador_saiu"] = titulares_cf_para_nome.get(str(saiu).strip().casefold(), saiu)
                subs_norm.append(sub_norm)
            out["substituicoes"] = subs_norm
        entraram = out.get("reservas_que_entraram")
        if isinstance(entraram, list):
            entraram_norm = []
            for nome in entraram:
                nome_resolvido = self._resolver_jogador_importacao(nome)
                entraram_norm.append(
                    reservas_cf_para_nome.get(str(nome_resolvido).strip().casefold(), nome_resolvido)
                )
            out["reservas_que_entraram"] = entraram_norm
        return out

    def _slug_estatistica_importada(self, chave):
        texto = str(chave or "").strip()
        if not texto:
            return ""
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
        texto = re.sub(r"%", " pct ", texto)
        texto = re.sub(r"[^0-9a-zA-Z]+", "_", texto.casefold()).strip("_")
        return re.sub(r"_+", "_", texto)

    def _chave_estatistica_importada(self, chave):
        slug = self._slug_estatistica_importada(chave)
        return ESTATISTICAS_VASCO_ALIASES.get(slug, slug)

    def _valor_estatistica_importada(self, valor, campo, percentual=False):
        if valor in (None, ""):
            return None
        if isinstance(valor, bool):
            raise ValueError(f"{campo} precisa ser um número.")
        txt = str(valor).strip().replace("%", "").replace(" ", "")
        if not txt:
            return None
        if "," in txt:
            txt = txt.replace(".", "").replace(",", ".")
        elif re.match(r"^\d{1,3}(?:\.\d{3})+$", txt):
            txt = txt.replace(".", "")
        try:
            numero = float(txt)
        except Exception:
            raise ValueError(f"{campo} precisa ser um número válido.")
        if numero < 0:
            raise ValueError(f"{campo} não pode ser negativo.")
        if percentual and numero > 100:
            raise ValueError(f"{campo} não pode passar de 100%.")
        if numero.is_integer():
            return int(numero)
        return round(numero, 4)

    def _normalizar_estatisticas_importadas(self, dados, label, prefixo=""):
        if dados in (None, ""):
            return {}
        if not isinstance(dados, dict):
            raise ValueError(f"{prefixo}{label} precisa ser um objeto.")

        saida = {}

        def adicionar(chave_raw, valor_raw):
            chave = self._chave_estatistica_importada(chave_raw)
            if not chave:
                return
            campo = f"{prefixo}{label}.{chave}"
            saida[chave] = self._valor_estatistica_importada(
                valor_raw,
                campo,
                percentual=chave in ESTATISTICAS_PERCENTUAIS,
            )

        for chave_raw, valor_raw in dados.items():
            if isinstance(valor_raw, dict):
                grupo = self._slug_estatistica_importada(chave_raw)
                if grupo not in {"passes", "cruzamentos", "lancamentos"}:
                    raise ValueError(f"{prefixo}{label}.{chave_raw} precisa ser número ou null.")
                for sub_chave, sub_valor in valor_raw.items():
                    adicionar(f"{grupo}_{sub_chave}", sub_valor)
                continue
            adicionar(chave_raw, valor_raw)

        self._completar_estatisticas_de_passes(saida, label, prefixo)
        return saida

    def _completar_estatisticas_de_passes(self, stats, label, prefixo=""):
        certos = stats.get("passes_certos")
        errados = stats.get("passes_errados")
        tentados = stats.get("passes_tentados")
        if certos is not None and errados is not None and tentados is None:
            stats["passes_tentados"] = certos + errados
            tentados = stats["passes_tentados"]
        elif certos is not None and tentados is not None and errados is None:
            if tentados < certos:
                raise ValueError(f"{prefixo}{label}.passes_tentados não pode ser menor que passes_certos.")
            stats["passes_errados"] = tentados - certos
        elif errados is not None and tentados is not None and certos is None:
            if tentados < errados:
                raise ValueError(f"{prefixo}{label}.passes_tentados não pode ser menor que passes_errados.")
            stats["passes_certos"] = tentados - errados
            certos = stats["passes_certos"]
        if (
            stats.get("precisao_passes") is None
            and certos is not None
            and tentados not in (None, 0)
        ):
            stats["precisao_passes"] = round((certos / tentados) * 100, 1)

    def _estatisticas_vasco_importadas(self, item, prefixo=""):
        for chave in (
            "estatisticas_vasco",
            "stats_vasco",
            "estatisticas_time_vasco",
            "estatisticas_equipe_vasco",
        ):
            if chave in item:
                return self._normalizar_estatisticas_importadas(item.get(chave), "estatisticas_vasco", prefixo)
        return {}

    def _estatisticas_jogadores_vasco_importadas(self, item, prefixo=""):
        bruto = None
        for chave in (
            "estatisticas_jogadores_vasco",
            "stats_jogadores_vasco",
            "estatisticas_individuais_vasco",
            "estatisticas_individuais_jogadores_vasco",
        ):
            if chave in item:
                bruto = item.get(chave)
                break
        if bruto in (None, ""):
            return []
        if isinstance(bruto, dict):
            bruto = [
                {**stats, "nome": nome}
                for nome, stats in bruto.items()
                if isinstance(stats, dict)
            ]
        if not isinstance(bruto, list):
            raise ValueError(f"{prefixo}estatisticas_jogadores_vasco precisa ser uma lista ou objeto por jogador.")

        saida = []
        vistos = set()
        for idx, jogador_stats in enumerate(bruto, start=1):
            if not isinstance(jogador_stats, dict):
                raise ValueError(f"{prefixo}estatisticas_jogadores_vasco[{idx}] precisa ser um objeto.")
            nome = self._resolver_jogador_importacao(jogador_stats.get("nome", ""))
            if not nome:
                raise ValueError(f"{prefixo}estatisticas_jogadores_vasco[{idx}].nome é obrigatório.")
            nome_cf = nome.casefold()
            if nome_cf in vistos:
                raise ValueError(f"{prefixo}estatisticas_jogadores_vasco tem jogador duplicado: {nome}.")
            vistos.add(nome_cf)
            numeros = {
                chave: valor
                for chave, valor in jogador_stats.items()
                if str(chave).strip().casefold() != "nome"
            }
            stats_norm = self._normalizar_estatisticas_importadas(
                numeros,
                f"estatisticas_jogadores_vasco[{nome}]",
                prefixo,
            )
            saida.append({"nome": nome, **stats_norm})
        return saida

    def _normalizar_jogo_importado(self, item, prefixo="", completar_escalacao_com_elenco=True):
        if not isinstance(item, dict):
            raise ValueError(f"{prefixo}cada jogo precisa ser um objeto JSON.")

        data = self._normalizar_data_importacao(self._valor_json_importacao(item, "data", "date", padrao=""))
        adversario = self._resolver_fuzzy_importacao(
            self._adversario_json_importacao(item),
            self._opcoes_clubes_adversarios(),
            tipo="geral",
            threshold=0.76,
        )
        adversario = self._resolver_nome_clube_canonico(adversario)
        competicao = self._resolver_competicao_importacao(
            self._valor_json_importacao(item, "competicao", "campeonato", "competition", padrao="")
        )
        local = str(item.get("local", "casa") or "casa").strip().casefold()
        estadio = self._resolver_fuzzy_importacao(
            item.get("estadio", ""),
            self._opcoes_importacao_campo("estadios"),
            tipo="geral",
            threshold=0.76,
        )
        horario = self._normalizar_horario_importado(item.get("horario", item.get("hora", "")), prefixo)
        tecnico = self._resolver_fuzzy_importacao(
            item.get("tecnico", ""),
            self._opcoes_importacao_campo("tecnicos"),
            tipo="pessoa",
            threshold=0.76,
        )
        capitao = self._resolver_jogador_importacao(item.get("capitao", ""))
        observacao = str(self._valor_json_importacao(item, "observacao", "observacoes", padrao="") or "").strip()

        if not data or not adversario:
            raise ValueError(f"{prefixo}informe data e adversário.")
        if not _parse_data_ptbr_safe(data):
            raise ValueError(f"{prefixo}data inválida. Use dd/mm/aaaa.")
        if local not in {"casa", "fora"}:
            raise ValueError(f"{prefixo}local inválido. Use 'casa' ou 'fora'.")

        placar = item.get("placar")
        if not isinstance(placar, dict):
            raise ValueError(f"{prefixo}informe o placar como objeto com 'vasco' e 'adversario'.")
        placar_vasco = self._int_importado_obrigatorio(placar.get("vasco"), f"{prefixo}placar.vasco")
        placar_adv = self._int_importado_obrigatorio(placar.get("adversario"), f"{prefixo}placar.adversario")
        if placar_vasco < 0 or placar_adv < 0:
            raise ValueError(f"{prefixo}placar não pode ter número negativo.")

        publico_pagante = self._int_importado_opcional(item.get("publico_pagante"), f"{prefixo}publico_pagante")
        publico_presente = self._int_importado_opcional(item.get("publico_presente"), f"{prefixo}publico_presente")
        if publico_pagante is not None and publico_presente is not None and publico_presente < publico_pagante:
            raise ValueError(f"{prefixo}publico_presente não pode ser menor que publico_pagante.")
        renda = self._float_importado_opcional(item.get("renda"), f"{prefixo}renda")

        posicao_tabela = None
        if self._competicao_usa_posicao(competicao):
            posicao_tabela = self._int_importado_opcional(item.get("posicao_tabela"), f"{prefixo}posicao_tabela")

        escalacao_partida = self._normalizar_escalacao_importada(
            item,
            prefixo,
            completar_com_elenco=completar_escalacao_com_elenco,
        )
        titulares_cf, reservas_cf = self._chaves_titulares_reservas(escalacao_partida)

        gols_vasco = self._normalizar_gols_importados(
            item.get("gols_vasco", []),
            "vasco",
            adversario,
            placar_vasco,
            titulares_cf,
            reservas_cf,
            prefixo,
        )
        gols_adversario = self._normalizar_gols_importados(
            item.get("gols_adversario", []),
            "adversario",
            adversario,
            placar_adv,
            titulares_cf,
            reservas_cf,
            prefixo,
        )
        estatisticas_vasco = self._estatisticas_vasco_importadas(item, prefixo)
        estatisticas_jogadores_vasco = self._estatisticas_jogadores_vasco_importadas(item, prefixo)

        if escalacao_partida:
            reservas_que_entraram_cf = {
                sub["jogador_entrou"].casefold()
                for sub in escalacao_partida.get("substituicoes", [])
                if isinstance(sub, dict)
            }
            for evento in _expandir_eventos_gol(gols_vasco):
                nome_cf = str(evento.get("nome", "")).strip().casefold()
                if nome_cf in reservas_cf and nome_cf not in titulares_cf:
                    reservas_que_entraram_cf.add(nome_cf)
            escalacao_partida["reservas_que_entraram"] = [
                nome for nome in escalacao_partida.get("reservas", [])
                if str(nome).strip().casefold() in reservas_que_entraram_cf
            ]

        return {
            "data": data,
            "adversario": adversario,
            "competicao": competicao,
            "local": local,
            "estadio": estadio,
            "horario": horario,
            "placar": {"vasco": placar_vasco, "adversario": placar_adv},
            "gols_vasco": gols_vasco,
            "gols_adversario": gols_adversario,
            "cartoes_amarelos_vasco": self._normalizar_cartoes_importados(
                item.get("cartoes_amarelos_vasco", []),
                f"{prefixo}cartoes_amarelos_vasco",
            ),
            "cartoes_vermelhos_vasco": self._normalizar_cartoes_importados(
                item.get("cartoes_vermelhos_vasco", []),
                f"{prefixo}cartoes_vermelhos_vasco",
            ),
            "observacao": observacao,
            "capitao": capitao,
            "publico_pagante": publico_pagante,
            "publico_presente": publico_presente,
            "renda": renda,
            "tecnico": tecnico,
            "posicao_tabela": posicao_tabela,
            "escalacao_partida": escalacao_partida,
            "arbitragem": self._normalizar_arbitragem_importada(item.get("arbitragem", {})),
            "estatisticas_vasco": estatisticas_vasco,
            "estatisticas_jogadores_vasco": estatisticas_jogadores_vasco,
        }

    def _normalizar_escalacao_importada(self, item, prefixo="", completar_com_elenco=True):
        bruto = item.get("escalacao_partida", item.get("escalacao", {}))
        if _escalacao_partida_vazia(bruto):
            return {}
        if not isinstance(bruto, dict):
            raise ValueError(f"{prefixo}escalacao_partida precisa ser um objeto.")
        bruto = self._canonicalizar_escalacao_importada(bruto)

        escalacao_payload = dict(bruto)
        if "reservas_que_entraram" not in escalacao_payload:
            escalacao_payload["reservas_que_entraram"] = []
        elif not isinstance(escalacao_payload.get("reservas_que_entraram"), list):
            raise ValueError(f"{prefixo}reservas_que_entraram precisa ser uma lista.")

        substituicoes_brutas = escalacao_payload.get("substituicoes", [])
        if substituicoes_brutas in (None, ""):
            substituicoes_brutas = []
            escalacao_payload["substituicoes"] = []
        if not isinstance(substituicoes_brutas, list):
            raise ValueError(f"{prefixo}substituicoes precisa ser uma lista.")
        for sub_idx, sub in enumerate(substituicoes_brutas, start=1):
            if not isinstance(sub, dict):
                raise ValueError(f"{prefixo}substituição {sub_idx} precisa ser um objeto.")
            if not _normalizar_substituicao_partida(sub):
                raise ValueError(
                    f"{prefixo}substituição {sub_idx} inválida. Informe jogador_entrou, "
                    "jogador_saiu e periodo. Para intervalo, use INT ou INTP; minuto pode ser 0 ou omitido."
                )

        escalacao = self._normalizar_escalacao_partida(escalacao_payload)
        if len(substituicoes_brutas) != len(escalacao.get("substituicoes", [])):
            raise ValueError(
                f"{prefixo}há substituição duplicada, jogador que entrou fora da lista de reservas "
                "ou jogador substituído repetido."
            )
        if completar_com_elenco:
            escalacao = self._completar_escalacao_importada_com_elenco(escalacao)

        nomes_obrigatorios = None if completar_com_elenco else self._nomes_presentes_na_escalacao(escalacao)
        ok, msg = self._validar_escalacao_partida(escalacao, nomes_elenco_obrigatorios=nomes_obrigatorios)
        if not ok:
            raise ValueError(f"{prefixo}{msg}")
        return escalacao

    def _completar_escalacao_importada_com_elenco(self, escalacao):
        if not isinstance(escalacao, dict):
            return escalacao

        mencionados = set()
        tit_por_pos = escalacao.get("titulares_por_posicao", {})
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                for nome in tit_por_pos.get(pos, []):
                    nome_limpo = str(nome).strip()
                    if nome_limpo:
                        mencionados.add(nome_limpo.casefold())
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            for nome in escalacao.get(chave, []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    mencionados.add(nome_limpo.casefold())

        destino_por_condicao = {
            "Titular": "nao_relacionados",
            "Reserva": "nao_relacionados",
            "Não Relacionado": "nao_relacionados",
            "Lesionado": "lesionados",
            "Suspenso": "suspensos",
            "Servindo a seleção": "servindo_selecao",
        }
        for jogador in self.elenco_atual.get("jogadores", []):
            if not isinstance(jogador, dict):
                continue
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            condicao = _normalizar_condicao_elenco(jogador.get("condicao"))
            if condicao == "Emprestado" or nome.casefold() in mencionados:
                continue
            destino = destino_por_condicao.get(condicao, "nao_relacionados")
            escalacao.setdefault(destino, []).append(nome)
            mencionados.add(nome.casefold())
        return self._normalizar_escalacao_partida(escalacao)

    def _normalizar_gols_importados(self, dados, lado, adversario, limite, titulares_cf, reservas_cf, prefixo=""):
        if dados in (None, ""):
            dados = []
        if not isinstance(dados, list):
            raise ValueError(f"{prefixo}{'gols_vasco' if lado == 'vasco' else 'gols_adversario'} precisa ser uma lista.")
        eventos = _expandir_eventos_gol(dados)
        if len(eventos) > limite:
            label = "Vasco" if lado == "vasco" else "adversário"
            raise ValueError(f"{prefixo}há mais autores de gols do {label} do que gols no placar.")

        normalizados = []
        for idx, evento in enumerate(eventos, start=1):
            if lado == "vasco":
                nome = self._resolver_jogador_importacao(evento.get("nome", ""))
            else:
                nome = self._resolver_jogador_contra_importacao(evento.get("nome", ""))
            if not nome:
                raise ValueError(f"{prefixo}gol {idx} está sem nome do jogador.")
            minuto, periodo = self._normalizar_tempo_evento_importado(evento, f"{prefixo}gol {idx}")
            item = {
                "nome": nome,
                "minuto": minuto,
                "periodo": periodo,
            }
            assistencia = str(evento.get("assistencia", "") or "").strip()
            if lado == "vasco":
                nome_cf = nome.casefold()
                if titulares_cf or reservas_cf:
                    item["saiu_do_banco"] = nome_cf in reservas_cf and nome_cf not in titulares_cf
                else:
                    item["saiu_do_banco"] = bool(evento.get("saiu_do_banco", False))
                if assistencia:
                    assistencia = self._resolver_jogador_importacao(assistencia)
                    if assistencia and assistencia.casefold() == nome.casefold():
                        raise ValueError(f"{prefixo}gol {idx}: assistência não pode ser do próprio autor do gol.")
                    if assistencia:
                        item["assistencia"] = assistencia
            else:
                if assistencia:
                    assistencia = self._resolver_jogador_contra_importacao(assistencia)
                    if assistencia and assistencia.casefold() == nome.casefold():
                        raise ValueError(f"{prefixo}gol {idx}: assistência não pode ser do próprio autor do gol.")
                    if assistencia:
                        item["assistencia"] = assistencia
                item["clube"] = str(evento.get("clube", "") or "").strip() or adversario
            normalizados.append(item)
        return _agrupar_eventos_gol(normalizados)

    def _normalizar_tempo_evento_importado(self, evento, label):
        minuto_raw = evento.get("minuto")
        periodo = _normalizar_periodo_partida(evento.get("periodo"), substituicao=False)
        minuto = self._minuto_importado_opcional(minuto_raw, label)
        if minuto is None:
            if str(evento.get("periodo", "") or "").strip():
                raise ValueError(f"{label}: período informado sem minuto.")
            return None, ""
        if periodo not in {codigo for codigo, _label in PERIODOS_EVENTO}:
            raise ValueError(f"{label}: periodo inválido. Use 1T, 2T, 1P ou 2P.")
        if minuto > _limite_minuto_evento_por_periodo(periodo):
            raise ValueError(f"{label}: o periodo {periodo} aceita no máximo {_limite_minuto_evento_por_periodo(periodo)}.")
        return minuto, periodo

    def _normalizar_cartoes_importados(self, dados, label):
        if dados in (None, ""):
            return []
        if not isinstance(dados, list):
            raise ValueError(f"{label} precisa ser uma lista.")
        eventos = []
        for evento in _expandir_eventos_cartao(dados):
            nome = self._resolver_jogador_importacao(evento.get("nome", ""))
            if nome:
                eventos.append({"nome": nome})
        return _agrupar_eventos_cartao(eventos)

    def _normalizar_horario_importado(self, valor, prefixo=""):
        horario = str(valor or "").strip()
        if not horario:
            return ""
        if not re.match(r"^\d{2}:\d{2}$", horario):
            raise ValueError(f"{prefixo}horário inválido. Use HH:MM.")
        horas, minutos = [int(parte) for parte in horario.split(":", 1)]
        if horas > 23 or minutos > 59:
            raise ValueError(f"{prefixo}horário inválido. Use um valor entre 00:00 e 23:59.")
        return horario

    def _int_importado_obrigatorio(self, valor, campo):
        if valor in (None, ""):
            raise ValueError(f"{campo} é obrigatório.")
        return self._int_importado_opcional(valor, campo)

    def _int_importado_opcional(self, valor, campo):
        if valor in (None, ""):
            return None
        if isinstance(valor, bool):
            raise ValueError(f"{campo} precisa ser um número inteiro.")
        txt = str(valor).strip()
        if not re.match(r"^-?\d+$", txt):
            raise ValueError(f"{campo} precisa ser um número inteiro.")
        numero = int(txt)
        if numero < 0:
            raise ValueError(f"{campo} não pode ser negativo.")
        return numero

    def _minuto_importado_opcional(self, valor, campo):
        if valor in (None, ""):
            return None
        txt = str(valor).strip().replace("'", "")
        if not re.match(r"^\d+$", txt):
            raise ValueError(f"{campo}: minuto precisa ser um inteiro entre 0 e 120.")
        minuto = int(txt)
        if minuto < 0 or minuto > 120:
            raise ValueError(f"{campo}: minuto precisa estar entre 0 e 120.")
        return minuto

    def _float_importado_opcional(self, valor, campo):
        if valor in (None, ""):
            return None
        if isinstance(valor, bool):
            raise ValueError(f"{campo} precisa ser um número.")
        txt = str(valor).strip().replace("R$", "").replace(" ", "")
        if "," in txt:
            txt = txt.replace(".", "").replace(",", ".")
        try:
            numero = float(txt)
        except Exception:
            raise ValueError(f"{campo} precisa ser um número válido.")
        if numero < 0:
            raise ValueError(f"{campo} não pode ser negativo.")
        return numero

    def _chaves_titulares_reservas(self, escalacao_partida):
        titulares_cf = set()
        reservas_cf = set()
        if not isinstance(escalacao_partida, dict):
            return titulares_cf, reservas_cf
        tit_por_pos = escalacao_partida.get("titulares_por_posicao", {})
        if isinstance(tit_por_pos, dict):
            for pos in POSICOES_ELENCO:
                for nome in tit_por_pos.get(pos, []):
                    nome_limpo = str(nome).strip()
                    if nome_limpo:
                        titulares_cf.add(nome_limpo.casefold())
        for nome in escalacao_partida.get("reservas", []):
            nome_limpo = str(nome).strip()
            if nome_limpo:
                reservas_cf.add(nome_limpo.casefold())
        return titulares_cf, reservas_cf

    def _jogos_importados_possivelmente_duplicados(self, jogos_importados):
        existentes = carregar_dados_jogos()
        chaves = {
            (
                str(jogo.get("data", "") or "").strip(),
                str(jogo.get("adversario", "") or "").strip().casefold(),
                str(jogo.get("competicao", "") or "").strip().casefold(),
            )
            for jogo in existentes
            if isinstance(jogo, dict)
        }
        duplicados = []
        for jogo in jogos_importados:
            chave = (
                str(jogo.get("data", "") or "").strip(),
                str(jogo.get("adversario", "") or "").strip().casefold(),
                str(jogo.get("competicao", "") or "").strip().casefold(),
            )
            if chave in chaves:
                duplicados.append(
                    f"{jogo.get('data', '')} - Vasco x {jogo.get('adversario', '')} ({jogo.get('competicao', '')})"
                )
        return duplicados

    def _salvar_operacoes_importacao_jogos(self, operacoes):
        jogos = carregar_dados_jogos()
        atualizados = 0
        novos = 0
        ajustes_historico = []
        jogos_novos = []

        for op in operacoes:
            jogo = copy.deepcopy(op.get("jogo", {}))
            if not isinstance(jogo, dict):
                continue
            jogo["adversario"] = self._registrar_clube_adversario(jogo.get("adversario", ""))
            self._registrar_listas_jogo_importado(jogo)

            if op.get("acao") == "atualizar":
                indice = op.get("indice")
                if not isinstance(indice, int) or not (0 <= indice < len(jogos)):
                    raise ValueError("Não foi possível localizar uma partida preparada para atualização.")
                antes = jogos[indice]
                jogos[indice] = jogo
                ajustes_historico.append((
                    _jogadores_que_participaram_do_jogo(antes),
                    _jogadores_que_participaram_do_jogo(jogo),
                ))
                atualizados += 1
            else:
                jogos.append(jogo)
                jogos_novos.append(jogo)
                ajustes_historico.append((set(), _jogadores_que_participaram_do_jogo(jogo)))
                novos += 1

        salvar_lista_jogos(jogos)
        salvar_listas(_ordenar_listas(self.listas))
        self._atualizar_combo_tecnicos()
        self._atualizar_combos_arbitragem()
        if hasattr(self, "competicao_entry"):
            self.competicao_entry["values"] = self.listas.get("competicoes", [])
        if hasattr(self, "entry_gol_contra"):
            self.entry_gol_contra["values"] = self.listas.get("jogadores_contra", [])
        self._atualizar_opcoes_gol_vasco()

        if jogos_novos:
            self._garantir_jogadores_importados_no_elenco_atual(jogos_novos)

        for antes, depois in ajustes_historico:
            self._ajustar_jogos_pelo_vasco_jogadores_historico(antes, depois)

        jogos_com_escalacao = [
            jogo for jogo in jogos_novos
            if isinstance(jogo.get("escalacao_partida"), dict) and jogo.get("escalacao_partida")
        ]
        if jogos_com_escalacao:
            ultimo = max(
                jogos_com_escalacao,
                key=lambda jogo: _parse_data_ptbr_safe(str(jogo.get("data", "")).strip()) or datetime.min,
            )
            self._atualizar_condicoes_elenco_por_escalacao(ultimo.get("escalacao_partida", {}))
        self._limpar_formulario()
        self._atualizar_abas()
        self.notebook.select(self.frame_temporadas)
        return {"atualizados": atualizados, "novos": novos}

    def _salvar_jogos_importados(self, jogos_importados):
        jogos = carregar_dados_jogos()
        self._garantir_jogadores_importados_no_elenco_atual(jogos_importados)
        for jogo in jogos_importados:
            jogo["adversario"] = self._registrar_clube_adversario(jogo.get("adversario", ""))
            self._registrar_listas_jogo_importado(jogo)
            jogos.append(jogo)

        salvar_lista_jogos(jogos)
        salvar_listas(_ordenar_listas(self.listas))
        self._atualizar_combo_tecnicos()
        self._atualizar_combos_arbitragem()
        if hasattr(self, "competicao_entry"):
            self.competicao_entry["values"] = self.listas.get("competicoes", [])
        if hasattr(self, "entry_gol_contra"):
            self.entry_gol_contra["values"] = self.listas.get("jogadores_contra", [])
        self._atualizar_opcoes_gol_vasco()

        for jogo in jogos_importados:
            self._ajustar_jogos_pelo_vasco_jogadores_historico(set(), _jogadores_que_participaram_do_jogo(jogo))

        jogos_com_escalacao = [
            jogo for jogo in jogos_importados
            if isinstance(jogo.get("escalacao_partida"), dict) and jogo.get("escalacao_partida")
        ]
        if jogos_com_escalacao:
            ultimo = max(
                jogos_com_escalacao,
                key=lambda jogo: _parse_data_ptbr_safe(str(jogo.get("data", "")).strip()) or datetime.min,
            )
            self._atualizar_condicoes_elenco_por_escalacao(ultimo.get("escalacao_partida", {}))
        self._limpar_formulario()
        self._atualizar_abas()
        self.notebook.select(self.frame_temporadas)

    def _registrar_listas_jogo_importado(self, jogo):
        def add_unico(chave, nome):
            nome_limpo = _normalizar_nome_arbitragem(nome) if chave in {"arbitros", "auxiliares", "vars"} else str(nome or "").strip()
            if not nome_limpo:
                return
            lista = self.listas.setdefault(chave, [])
            if chave in {"arbitros", "auxiliares", "vars"}:
                existe = any(_chave_nome_arbitragem(item) == _chave_nome_arbitragem(nome_limpo) for item in lista)
            else:
                existe = any(str(item).casefold() == nome_limpo.casefold() for item in lista)
            if not existe:
                lista.append(nome_limpo)

        add_unico("competicoes", jogo.get("competicao", ""))
        add_unico("tecnicos", jogo.get("tecnico", ""))
        add_unico("estadios", jogo.get("estadio", ""))

        arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
        add_unico("arbitros", arbitragem.get("arbitro", ""))
        for auxiliar in arbitragem.get("auxiliares", []):
            add_unico("auxiliares", auxiliar)
        add_unico("vars", arbitragem.get("var", ""))

        for evento in _expandir_eventos_gol(jogo.get("gols_vasco", [])):
            add_unico("jogadores_vasco", evento.get("nome", ""))
        for evento in _expandir_eventos_gol(jogo.get("gols_adversario", [])):
            add_unico("jogadores_contra", evento.get("nome", ""))

    def _limpar_formulario(self):
        self.editing_index = None
        self._elenco_edicao_partida_cf = None
        if hasattr(self, "salvar_btn_label"):
            self.salvar_btn_label.set("Salvar Partida")
        if hasattr(self, "modo_edicao_var"):
            self.modo_edicao_var.set("")
        if hasattr(self, "btn_cancelar_edicao"):
            self.btn_cancelar_edicao.state(["disabled"])
        self.data_var.set(datetime.now().strftime("%d/%m/%Y"))
        self._fechar_calendario_popup()
        self.adversario_var.set("")
        self.competicao_var.set("")
        if hasattr(self, "estadio_var"):
            self.estadio_var.set("")
        if hasattr(self, "horario_hora_var"):
            self.horario_hora_var.set("")
        if hasattr(self, "horario_minuto_var"):
            self.horario_minuto_var.set("")
        if hasattr(self, "capitao_partida_var"):
            self.capitao_partida_var.set("")
        if hasattr(self, "arbitro_var"):
            self.arbitro_var.set("")
        if hasattr(self, "auxiliar_1_var"):
            self.auxiliar_1_var.set("")
        if hasattr(self, "auxiliar_2_var"):
            self.auxiliar_2_var.set("")
        if hasattr(self, "var_arbitragem_var"):
            self.var_arbitragem_var.set("")
        if hasattr(self, "publico_pagante_var"):
            self.publico_pagante_var.set("")
        if hasattr(self, "publico_presente_var"):
            self.publico_presente_var.set("")
        if hasattr(self, "renda_var"):
            self.renda_var.set("")
        if hasattr(self, "posicao_var"):
            self.posicao_var.set("")
        self._atualizar_estado_posicao()
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(self.listas.get("tecnico_atual", "Fernando Diniz"))
        self.placar_vasco.delete(0, tk.END)
        self.placar_adversario.delete(0, tk.END)
        self.gols_vasco_eventos = []
        self.gols_contra_eventos = []
        self.cartoes_amarelos_eventos = []
        self.cartoes_vermelhos_eventos = []
        self.lista_gols_vasco.delete(0, tk.END)
        self.lista_gols_contra.delete(0, tk.END)
        self.lista_cartoes_amarelos.delete(0, tk.END)
        self.lista_cartoes_vermelhos.delete(0, tk.END)
        self.entry_gol_vasco.delete(0, tk.END)
        self.entry_gol_contra.delete(0, tk.END)
        self.entry_cartao_amarelo.delete(0, tk.END)
        self.entry_cartao_vermelho.delete(0, tk.END)
        self.obs_text.delete("1.0", "end")
        self._atualizar_elenco_disponivel_partida()
        self._inicializar_escalacao_partida()
        self._atualizar_opcoes_capitao_partida(preservar_valor=False)

    def _remover_futuro_registrado(self, data_txt: str, adversario: str, competicao: str):
        futuros = carregar_jogos_futuros()
        if not futuros:
            return
        adv_cf = (adversario or "").casefold()
        comp_cf = (competicao or "").casefold()
        kept = []
        removed = 0
        for item in futuros:
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                kept.append(item)
                continue
            if normalizado.get("data") != data_txt:
                kept.append(item)
                continue
            adv_item = _extrair_adversario_de_jogo(normalizado.get("jogo", "")).replace("Vasco", "").strip()
            if adv_item and adv_item.casefold() == adv_cf:
                if comp_cf and normalizado.get("campeonato") and normalizado["campeonato"].casefold() != comp_cf:
                    kept.append(item)
                    continue
                removed += 1
                continue
            kept.append(item)
        if removed:
            salvar_lista_futuros(kept)
            self._render_lista_futuros()

    def _carregar_jogo_para_edicao(self, jogo_idx):
        jogos = carregar_dados_jogos()
        if not (0 <= jogo_idx < len(jogos)):
            messagebox.showerror("Erro", "Não foi possível carregar o jogo selecionado.")
            return

        jogo = jogos[jogo_idx]
        self.editing_index = jogo_idx
        self._elenco_edicao_partida_cf = None
        self.notebook.select(self.frame_registro)
        adversario = jogo.get("adversario", "")
        data = jogo.get("data", "")
        tecnico_jogo = str(jogo.get("tecnico", "") or "").strip()
        if not tecnico_jogo:
            tecnico_jogo = str(self.listas.get("tecnico_atual", "") or "Fernando Diniz").strip()
        self.salvar_btn_label.set("Salvar Alterações")
        self.modo_edicao_var.set(f"Editando: {adversario} ({data}) | Técnico: {tecnico_jogo}")
        self.btn_cancelar_edicao.state(["!disabled"])

        self.data_var.set(data)
        self.adversario_var.set(adversario)
        self.competicao_var.set(jogo.get("competicao", ""))
        if hasattr(self, "estadio_var"):
            self.estadio_var.set(str(jogo.get("estadio", "")).strip())
        horario = str(jogo.get("horario", "")).strip()
        if hasattr(self, "horario_hora_var"):
            self.horario_hora_var.set(horario[:2] if len(horario) >= 2 else "")
        if hasattr(self, "horario_minuto_var"):
            self.horario_minuto_var.set(horario[3:5] if len(horario) >= 5 and ":" in horario else "")
        self._atualizar_estado_posicao()
        if hasattr(self, "posicao_var"):
            posicao = jogo.get("posicao_tabela")
            if posicao not in (None, "") and self._competicao_usa_posicao(self.competicao_var.get()):
                self.posicao_var.set(str(posicao))
            else:
                self.posicao_var.set("")
        self.local_var.set(jogo.get("local", "casa"))
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(tecnico_jogo)

        placar = jogo.get("placar", {})
        self.placar_vasco.delete(0, tk.END)
        self.placar_vasco.insert(0, str(placar.get("vasco", "")))
        self.placar_adversario.delete(0, tk.END)
        self.placar_adversario.insert(0, str(placar.get("adversario", "")))

        self.gols_vasco_eventos = _expandir_eventos_gol(jogo.get("gols_vasco", []))
        self.gols_contra_eventos = _expandir_eventos_gol(jogo.get("gols_adversario", []))
        self.cartoes_amarelos_eventos = _expandir_eventos_cartao(jogo.get("cartoes_amarelos_vasco", []))
        self.cartoes_vermelhos_eventos = _expandir_eventos_cartao(jogo.get("cartoes_vermelhos_vasco", []))
        self._renderizar_lista_eventos(self.lista_gols_vasco, self.gols_vasco_eventos, _formatar_evento_gol)
        self._renderizar_lista_eventos(self.lista_gols_contra, self.gols_contra_eventos, _formatar_evento_gol)
        self._renderizar_lista_eventos(self.lista_cartoes_amarelos, self.cartoes_amarelos_eventos, _formatar_evento_cartao)
        self._renderizar_lista_eventos(self.lista_cartoes_vermelhos, self.cartoes_vermelhos_eventos, _formatar_evento_cartao)
        escalacao_salva = jogo.get("escalacao_partida", jogo.get("escalacao", {}))
        tem_escalacao = False
        if isinstance(escalacao_salva, dict):
            tit_por_pos = escalacao_salva.get("titulares_por_posicao")
            if isinstance(tit_por_pos, dict) and any(tit_por_pos.get(pos) for pos in POSICOES_ELENCO):
                tem_escalacao = True
            if not tem_escalacao and any(escalacao_salva.get(k) for k, _ in CATEGORIAS_ESCALACAO_EXTRAS):
                tem_escalacao = True
            if not tem_escalacao and escalacao_salva.get("titulares"):
                tem_escalacao = True
        if tem_escalacao:
            self._carregar_escalacao_partida(escalacao_salva)
            self._elenco_edicao_partida_cf = self._nomes_presentes_na_escalacao(self.escalacao_partida)
        else:
            self._carregar_escalacao_partida({})
            self._elenco_edicao_partida_cf = set()
        if hasattr(self, "capitao_partida_var"):
            self._atualizar_opcoes_capitao_partida(preservar_valor=False)
            self.capitao_partida_var.set(str(jogo.get("capitao", "")).strip())
        arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
        if hasattr(self, "arbitro_var"):
            self.arbitro_var.set(arbitragem.get("arbitro", ""))
        auxiliares = arbitragem.get("auxiliares", [])
        if hasattr(self, "auxiliar_1_var"):
            self.auxiliar_1_var.set(auxiliares[0] if len(auxiliares) > 0 else "")
        if hasattr(self, "auxiliar_2_var"):
            self.auxiliar_2_var.set(auxiliares[1] if len(auxiliares) > 1 else "")
        if hasattr(self, "var_arbitragem_var"):
            self.var_arbitragem_var.set(arbitragem.get("var", ""))
        if hasattr(self, "publico_pagante_var"):
            self.publico_pagante_var.set("" if jogo.get("publico_pagante") in (None, "") else str(jogo.get("publico_pagante")))
        if hasattr(self, "publico_presente_var"):
            self.publico_presente_var.set("" if jogo.get("publico_presente") in (None, "") else str(jogo.get("publico_presente")))
        if hasattr(self, "renda_var"):
            self.renda_var.set("" if jogo.get("renda") in (None, "") else _formatar_renda_brl(jogo.get("renda")))

        self.obs_text.delete("1.0", "end")
        self.obs_text.insert("1.0", jogo.get("observacao", ""))

    def _texto_detalhe_partida(self, valor):
        if valor in (None, ""):
            return "—"
        if isinstance(valor, (list, tuple)):
            itens = [str(item).strip() for item in valor if str(item).strip()]
            return ", ".join(itens) if itens else "—"
        txt = str(valor).strip()
        return txt if txt else "—"

    def _placar_detalhe_partida(self, jogo):
        adversario = str(jogo.get("adversario", "") or "").strip() or "Adversário"
        placar = jogo.get("placar", {}) if isinstance(jogo.get("placar"), dict) else {}
        gols_vasco = int(placar.get("vasco", 0) or 0)
        gols_adv = int(placar.get("adversario", 0) or 0)
        if str(jogo.get("local", "") or "").casefold() == "fora":
            return f"{adversario} {gols_adv} x {gols_vasco} Vasco"
        return f"Vasco {gols_vasco} x {gols_adv} {adversario}"

    def _resultado_detalhe_partida(self, jogo):
        placar = jogo.get("placar", {}) if isinstance(jogo.get("placar"), dict) else {}
        gols_vasco = int(placar.get("vasco", 0) or 0)
        gols_adv = int(placar.get("adversario", 0) or 0)
        if gols_vasco > gols_adv:
            return "Vitória"
        if gols_vasco < gols_adv:
            return "Derrota"
        return "Empate"

    def _criar_tree_modal_partida(self, parent, columns, headings, widths, *, height=8):
        wrap = ttk.Frame(parent)
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)
        tv = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for col, heading, width in zip(columns, headings, widths):
            tv.heading(col, text=heading)
            anchor = "center" if col in {"minuto", "qtd", "numero"} else "w"
            tv.column(col, width=width, anchor=anchor, stretch=True)
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        sy.grid(row=0, column=1, sticky="ns")
        tv.configure(yscrollcommand=sy.set)
        return wrap, tv

    def _abrir_modal_detalhes_partida_por_indice(self, jogo_idx):
        jogos = carregar_dados_jogos()
        if not (0 <= jogo_idx < len(jogos)):
            messagebox.showerror("Erro", "Não foi possível carregar o jogo selecionado.")
            return
        self._abrir_modal_detalhes_partida(jogos[jogo_idx], jogo_idx)

    def _abrir_modal_detalhes_partida(self, jogo, jogo_idx=None):
        if not isinstance(jogo, dict):
            messagebox.showerror("Erro", "Não foi possível carregar os detalhes da partida.")
            return

        top = tk.Toplevel(self.root)
        top.title(f"Detalhes da partida - {self._placar_detalhe_partida(jogo)}")
        top.transient(self.root)
        top.lift()
        top.focus_force()
        top.minsize(980, 680)
        top.configure(bg=self.colors["bg"])

        container = ttk.Frame(top, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        titulo = ttk.Label(
            container,
            text=self._placar_detalhe_partida(jogo),
            font=("Segoe UI", 15, "bold"),
        )
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 8))

        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky="nsew")

        # Aba Resumo
        aba_resumo = ttk.Frame(notebook, padding=10)
        aba_resumo.columnconfigure(0, weight=1)
        aba_resumo.rowconfigure(0, weight=1)
        notebook.add(aba_resumo, text="Resumo")
        wrap_resumo, tv_resumo = self._criar_tree_modal_partida(
            aba_resumo,
            ("campo", "valor"),
            ("Campo", "Valor"),
            (220, 680),
            height=20,
        )
        wrap_resumo.grid(row=0, column=0, sticky="nsew")

        arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
        resumo_rows = [
            ("Data", jogo.get("data", "")),
            ("Competição", jogo.get("competicao", "")),
            ("Adversário", jogo.get("adversario", "")),
            ("Local", "Casa" if str(jogo.get("local", "")).casefold() != "fora" else "Fora"),
            ("Placar", self._placar_detalhe_partida(jogo)),
            ("Resultado", self._resultado_detalhe_partida(jogo)),
            ("Estádio", jogo.get("estadio", "")),
            ("Horário", jogo.get("horario", "")),
            ("Técnico", jogo.get("tecnico", "")),
            ("Capitão", jogo.get("capitao", "")),
            ("Posição na tabela", jogo.get("posicao_tabela", "")),
            ("Público pagante", _formatar_publico(jogo.get("publico_pagante"))),
            ("Público presente", _formatar_publico(jogo.get("publico_presente"))),
            ("Renda", _formatar_renda_brl(jogo.get("renda"))),
            ("Árbitro", arbitragem.get("arbitro", "")),
            ("Auxiliares", arbitragem.get("auxiliares", [])),
            ("VAR", arbitragem.get("var", "")),
            ("ID da partida no banco", jogo.get("db_match_id", "")),
            ("ID do técnico no banco", jogo.get("db_tecnico_id", "")),
        ]
        for i, (campo, valor) in enumerate(resumo_rows):
            tv_resumo.insert("", "end", values=(campo, self._texto_detalhe_partida(valor)), tags=("odd",) if i % 2 else ())

        # Aba Escalação
        aba_esc = ttk.Frame(notebook, padding=10)
        aba_esc.columnconfigure(0, weight=1)
        aba_esc.rowconfigure(1, weight=1)
        aba_esc.rowconfigure(2, weight=1)
        notebook.add(aba_esc, text="Escalação")

        esc = jogo.get("escalacao_partida", jogo.get("escalacao", {}))
        esc = self._normalizar_escalacao_partida(esc if isinstance(esc, dict) else {})
        titulares = sum(len(esc["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        ttk.Label(
            aba_esc,
            text=(
                f"Titulares: {titulares}/11 | Reservas: {len(esc.get('reservas', []))} | "
                f"Substituições: {len(esc.get('substituicoes', []))}"
            ),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        superior = ttk.Frame(aba_esc)
        superior.grid(row=1, column=0, sticky="nsew")
        superior.columnconfigure(0, weight=1)
        superior.columnconfigure(1, weight=1)
        superior.rowconfigure(0, weight=1)

        titulares_frame = ttk.Labelframe(superior, text="Titulares", padding=6)
        titulares_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        titulares_frame.columnconfigure(0, weight=1)
        titulares_frame.rowconfigure(0, weight=1)
        wrap_tit, tv_tit = self._criar_tree_modal_partida(
            titulares_frame,
            ("posicao", "jogadores"),
            ("Posição", "Jogadores"),
            (180, 360),
            height=9,
        )
        wrap_tit.grid(row=0, column=0, sticky="nsew")
        for i, pos in enumerate(POSICOES_ELENCO):
            nomes = esc["titulares_por_posicao"].get(pos, [])
            tv_tit.insert("", "end", values=(pos, self._texto_detalhe_partida(nomes)), tags=("odd",) if i % 2 else ())

        reservas_frame = ttk.Labelframe(superior, text="Reservas e status", padding=6)
        reservas_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        reservas_frame.columnconfigure(0, weight=1)
        reservas_frame.rowconfigure(0, weight=1)
        wrap_res, tv_res = self._criar_tree_modal_partida(
            reservas_frame,
            ("grupo", "nomes"),
            ("Grupo", "Nomes"),
            (150, 390),
            height=9,
        )
        wrap_res.grid(row=0, column=0, sticky="nsew")
        grupos_reservas = [
            ("Reservas", esc.get("reservas", [])),
            ("Entraram", esc.get("reservas_que_entraram", [])),
            ("Não relacionados", esc.get("nao_relacionados", [])),
            ("Lesionados", esc.get("lesionados", [])),
            ("Suspensos", esc.get("suspensos", [])),
            ("Seleção", esc.get("servindo_selecao", [])),
        ]
        for i, (grupo, nomes) in enumerate(grupos_reservas):
            tv_res.insert("", "end", values=(grupo, self._texto_detalhe_partida(nomes)), tags=("odd",) if i % 2 else ())

        subs_frame = ttk.Labelframe(aba_esc, text="Substituições", padding=6)
        subs_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        subs_frame.columnconfigure(0, weight=1)
        subs_frame.rowconfigure(0, weight=1)
        wrap_subs, tv_subs = self._criar_tree_modal_partida(
            subs_frame,
            ("minuto", "entrou", "saiu"),
            ("Minuto", "Entrou", "Saiu"),
            (110, 300, 300),
            height=8,
        )
        wrap_subs.grid(row=0, column=0, sticky="nsew")
        subs = [
            sub for sub in (_normalizar_substituicao_partida(item) for item in esc.get("substituicoes", []))
            if sub
        ]
        if subs:
            for i, sub in enumerate(subs):
                tv_subs.insert(
                    "",
                    "end",
                    values=(
                        _formatar_minuto_periodo(sub.get("minuto"), sub.get("periodo")),
                        sub.get("jogador_entrou", ""),
                        sub.get("jogador_saiu", ""),
                    ),
                    tags=("odd",) if i % 2 else (),
                )
        else:
            tv_subs.insert("", "end", values=("—", "—", "—"))

        # Aba Eventos
        aba_eventos = ttk.Frame(notebook, padding=10)
        aba_eventos.columnconfigure(0, weight=1)
        aba_eventos.rowconfigure(0, weight=1)
        notebook.add(aba_eventos, text="Eventos")
        wrap_eventos, tv_eventos = self._criar_tree_modal_partida(
            aba_eventos,
            ("tipo", "jogador", "minuto", "detalhe"),
            ("Tipo", "Jogador", "Minuto", "Detalhe"),
            (170, 300, 110, 300),
            height=22,
        )
        wrap_eventos.grid(row=0, column=0, sticky="nsew")

        eventos = []
        for evento in _expandir_eventos_gol(jogo.get("gols_vasco", [])):
            assistencia = str(evento.get("assistencia", "") or "").strip()
            eventos.append((
                "Gol do Vasco",
                evento.get("nome", ""),
                _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo")) if evento.get("minuto") is not None else "—",
                " · ".join([parte for parte in (
                    f"Assistência: {assistencia}" if assistencia else "",
                    "Saiu do banco" if evento.get("saiu_do_banco") else "",
                ) if parte]),
            ))
        for evento in _expandir_eventos_gol(jogo.get("gols_adversario", [])):
            assistencia = str(evento.get("assistencia", "") or "").strip()
            eventos.append((
                "Gol adversário",
                evento.get("nome", ""),
                _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo")) if evento.get("minuto") is not None else "—",
                " · ".join([parte for parte in (
                    evento.get("clube", "") or jogo.get("adversario", ""),
                    f"Assistência: {assistencia}" if assistencia else "",
                ) if parte]),
            ))
        gols_anulados = jogo.get("gols_anulados", {}) if isinstance(jogo.get("gols_anulados"), dict) else {}
        for lado, label in (("vasco", "Gol anulado Vasco"), ("adversario", "Gol anulado adversário")):
            for evento in _expandir_eventos_gol(gols_anulados.get(lado, [])):
                eventos.append((
                    label,
                    evento.get("nome", ""),
                    _formatar_minuto_periodo(evento.get("minuto"), evento.get("periodo")) if evento.get("minuto") is not None else "—",
                    evento.get("clube", ""),
                ))
        for evento in _expandir_eventos_cartao(jogo.get("cartoes_amarelos_vasco", [])):
            eventos.append(("Cartão amarelo Vasco", evento.get("nome", ""), "—", ""))
        for evento in _expandir_eventos_cartao(jogo.get("cartoes_vermelhos_vasco", [])):
            eventos.append(("Cartão vermelho Vasco", evento.get("nome", ""), "—", ""))

        if eventos:
            for i, row in enumerate(eventos):
                tv_eventos.insert("", "end", values=tuple(self._texto_detalhe_partida(v) for v in row), tags=("odd",) if i % 2 else ())
        else:
            tv_eventos.insert("", "end", values=("—", "—", "—", "—"))

        # Aba Scouts
        aba_scouts = ttk.Frame(notebook, padding=10)
        aba_scouts.columnconfigure(0, weight=1)
        aba_scouts.rowconfigure(0, weight=1)
        aba_scouts.rowconfigure(1, weight=1)
        notebook.add(aba_scouts, text="Scouts")

        scouts_time_frame = ttk.Labelframe(aba_scouts, text="Scouts do Vasco", padding=6)
        scouts_time_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        scouts_time_frame.columnconfigure(0, weight=1)
        scouts_time_frame.rowconfigure(0, weight=1)
        wrap_scouts_time, tv_scouts_time = self._criar_tree_modal_partida(
            scouts_time_frame,
            ("estatistica", "valor"),
            ("Estatística", "Valor"),
            (360, 240),
            height=9,
        )
        wrap_scouts_time.grid(row=0, column=0, sticky="nsew")

        stats_vasco = jogo.get("estatisticas_vasco") if isinstance(jogo.get("estatisticas_vasco"), dict) else {}
        chaves_stats_vasco = self._ordenar_chaves_estatisticas_jogador(stats_vasco)
        if chaves_stats_vasco:
            for i, chave in enumerate(chaves_stats_vasco):
                tv_scouts_time.insert(
                    "",
                    "end",
                    values=(
                        self._formatar_nome_estatistica_jogador(chave),
                        self._formatar_valor_estatistica_jogador(chave, stats_vasco.get(chave)),
                    ),
                    tags=("odd",) if i % 2 else (),
                )
        else:
            tv_scouts_time.insert("", "end", values=("Sem scouts do Vasco importados", "—"))

        scouts_jogadores_frame = ttk.Labelframe(aba_scouts, text="Scouts dos jogadores do Vasco", padding=6)
        scouts_jogadores_frame.grid(row=1, column=0, sticky="nsew")
        scouts_jogadores_frame.columnconfigure(0, weight=1)
        scouts_jogadores_frame.rowconfigure(1, weight=1)

        seletor_scout_jogador = ttk.Frame(scouts_jogadores_frame)
        seletor_scout_jogador.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        seletor_scout_jogador.columnconfigure(1, weight=1)
        ttk.Label(seletor_scout_jogador, text="Jogador:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        jogador_scout_var = tk.StringVar(value="")
        combo_scout_jogador = ttk.Combobox(
            seletor_scout_jogador,
            textvariable=jogador_scout_var,
            state="readonly",
            width=36,
        )
        combo_scout_jogador.grid(row=0, column=1, sticky="w")

        wrap_scouts_jogadores, tv_scouts_jogadores = self._criar_tree_modal_partida(
            scouts_jogadores_frame,
            ("estatistica", "valor"),
            ("Estatística", "Valor"),
            (420, 220),
            height=10,
        )
        wrap_scouts_jogadores.grid(row=1, column=0, sticky="nsew")

        stats_jogadores = jogo.get("estatisticas_jogadores_vasco")
        stats_jogadores_por_nome = {}
        if isinstance(stats_jogadores, list):
            for item in sorted(
                [s for s in stats_jogadores if isinstance(s, dict)],
                key=lambda s: str(s.get("nome", "") or "").casefold(),
            ):
                nome = str(item.get("nome", "") or "").strip()
                if not nome:
                    continue
                stats_jogadores_por_nome.setdefault(nome, item)

        def _render_scout_jogador(_event=None):
            for iid in tv_scouts_jogadores.get_children():
                tv_scouts_jogadores.delete(iid)
            nome = jogador_scout_var.get()
            item = stats_jogadores_por_nome.get(nome)
            if not item:
                tv_scouts_jogadores.insert("", "end", values=("Sem scouts individuais importados", "—"))
                return
            chaves = self._ordenar_chaves_estatisticas_jogador(item)
            if not chaves:
                tv_scouts_jogadores.insert("", "end", values=("Sem scouts para o jogador selecionado", "—"))
                return
            for i, chave in enumerate(chaves):
                tv_scouts_jogadores.insert(
                    "",
                    "end",
                    values=(
                        self._formatar_nome_estatistica_jogador(chave),
                        self._formatar_valor_estatistica_jogador(chave, item.get(chave)),
                    ),
                    tags=("odd",) if i % 2 else (),
                )

        nomes_scouts_jogadores = sorted(stats_jogadores_por_nome, key=lambda n: n.casefold())
        if nomes_scouts_jogadores:
            combo_scout_jogador.configure(values=nomes_scouts_jogadores)
            jogador_scout_var.set(nomes_scouts_jogadores[0])
            combo_scout_jogador.bind("<<ComboboxSelected>>", _render_scout_jogador)
            _render_scout_jogador()
        else:
            combo_scout_jogador.configure(state="disabled")
            tv_scouts_jogadores.insert("", "end", values=("Sem scouts individuais importados", "—"))

        # Aba Observações
        aba_obs = ttk.Frame(notebook, padding=10)
        aba_obs.columnconfigure(0, weight=1)
        aba_obs.rowconfigure(0, weight=1)
        notebook.add(aba_obs, text="Observações")
        obs = tk.Text(
            aba_obs,
            wrap="word",
            height=12,
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            insertbackground=self.colors["fg"],
        )
        obs.grid(row=0, column=0, sticky="nsew")
        obs.insert("1.0", str(jogo.get("observacao", "") or ""))
        obs.configure(state="disabled")
        sy_obs = ttk.Scrollbar(aba_obs, orient="vertical", command=obs.yview)
        sy_obs.grid(row=0, column=1, sticky="ns")
        obs.configure(yscrollcommand=sy_obs.set)

        botoes = ttk.Frame(container)
        botoes.grid(row=2, column=0, sticky="e", pady=(10, 0))
        if jogo_idx is not None:
            ttk.Button(
                botoes,
                text="Enviar para edição",
                command=lambda idx=jogo_idx, modal=top: (modal.destroy(), self._carregar_jogo_para_edicao(idx)),
            ).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text="Fechar", command=top.destroy).pack(side="left")

        top.update_idletasks()
        self._centralizar_modal_no_app(top)

    def _abrir_modal_scouts_temporada(self, ano, linhas_base):
        linhas_base = list(linhas_base or [])
        jogos = [r.get("raw") for r in linhas_base if isinstance(r, dict) and isinstance(r.get("raw"), dict)]
        linhas_time, linhas_jogadores, resumo = self._agregar_estatisticas_vasco_jogos(jogos)

        top = tk.Toplevel(self.root)
        top.title(f"Scouts consolidados - {ano}")
        top.transient(self.root)
        top.lift()
        top.focus_force()
        top.minsize(860, 620)
        top.configure(bg=self.colors["bg"])

        container = ttk.Frame(top, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        resumo_txt = (
            f"Recorte atual: {resumo['jogos']} jogos | "
            f"jogos com scout do Vasco: {resumo['jogos_com_scout_time']} | "
            f"jogos com scout de jogadores: {resumo['jogos_com_scout_jogadores']}"
        )
        ttk.Label(container, text=resumo_txt, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))

        notebook = ttk.Notebook(container)
        notebook.grid(row=1, column=0, sticky="nsew")

        aba_time = ttk.Frame(notebook, padding=10)
        aba_time.columnconfigure(0, weight=1)
        aba_time.rowconfigure(0, weight=1)
        notebook.add(aba_time, text="Vasco")
        wrap_time, tv_time = self._criar_tree_modal_partida(
            aba_time,
            ("estatistica", "total", "media", "jogos"),
            ("Estatística", "Total", "Média", "Jogos com dado"),
            (300, 160, 160, 130),
            height=20,
        )
        wrap_time.grid(row=0, column=0, sticky="nsew")
        if linhas_time:
            for i, row in enumerate(linhas_time):
                tv_time.insert(
                    "",
                    "end",
                    values=(row["estatistica"], row["total"], row["media"], row["jogos"]),
                    tags=("odd",) if i % 2 else (),
                )
        else:
            tv_time.insert("", "end", values=("Sem scouts do Vasco no recorte atual", "—", "—", "—"))

        aba_jogadores = ttk.Frame(notebook, padding=10)
        aba_jogadores.columnconfigure(0, weight=1)
        aba_jogadores.rowconfigure(0, weight=1)
        notebook.add(aba_jogadores, text="Jogadores")
        wrap_jogadores, tv_jogadores = self._criar_tree_modal_partida(
            aba_jogadores,
            ("jogador", "estatistica", "total", "media", "jogos"),
            ("Jogador", "Estatística", "Total", "Média", "Jogos com dado"),
            (220, 230, 120, 120, 120),
            height=20,
        )
        wrap_jogadores.grid(row=0, column=0, sticky="nsew")
        if linhas_jogadores:
            for i, row in enumerate(linhas_jogadores):
                tv_jogadores.insert(
                    "",
                    "end",
                    values=(row["jogador"], row["estatistica"], row["total"], row["media"], row["jogos"]),
                    tags=("odd",) if i % 2 else (),
                )
        else:
            tv_jogadores.insert("", "end", values=("Sem scouts individuais no recorte atual", "—", "—", "—", "—"))

        botoes = ttk.Frame(container)
        botoes.grid(row=2, column=0, sticky="e", pady=(10, 0))
        ttk.Button(botoes, text="Fechar", command=top.destroy).pack(side="left")

        top.update_idletasks()
        self._centralizar_modal_no_app(top)

    def _on_tree_double_click(self, event):
        tree = event.widget
        iid = tree.identify_row(event.y)
        if not iid:
            return
        mapping = getattr(tree, "_item_to_idx", {})
        jogo_idx = mapping.get(iid)
        if jogo_idx is None:
            return
        tree.selection_set(iid)
        self._abrir_modal_detalhes_partida_por_indice(jogo_idx)

    def _abrir_menu_contexto_temporadas(self, event):
        tree = event.widget
        iid = tree.identify_row(event.y)
        if not iid:
            return
        tree.focus(iid)

        selecao_atual = tree.selection()
        if iid not in selecao_atual:
            tree.selection_set(iid)
            selecao_atual = (iid,)

        mapping = getattr(tree, "_item_to_idx", {})
        jogos = carregar_dados_jogos()

        jogos_selecionados = []
        for selected_iid in selecao_atual:
            jogo_idx_sel = mapping.get(selected_iid)
            if jogo_idx_sel is None:
                continue
            if 0 <= jogo_idx_sel < len(jogos):
                jogos_selecionados.append(jogos[jogo_idx_sel])

        if not jogos_selecionados:
            return

        jogo_idx = mapping.get(iid)
        if jogo_idx is None or not (0 <= jogo_idx < len(jogos)):
            return
        jogo = jogos[jogo_idx]

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Ver detalhes", command=lambda idx=jogo_idx: self._abrir_modal_detalhes_partida_por_indice(idx))
        menu.add_command(label="Enviar para edição", command=lambda idx=jogo_idx: self._carregar_jogo_para_edicao(idx))
        submenu_copiar = tk.Menu(menu, tearoff=0)
        submenu_copiar.add_command(
            label="Confronto com placar",
            command=lambda item=jogo: self._copiar_texto_temporadas(
                self._formatar_confronto_temporadas(item, incluir_placar=True)
            ),
        )
        submenu_copiar.add_command(
            label="Confronto com data",
            command=lambda item=jogo: self._copiar_texto_temporadas(
                self._formatar_confronto_temporadas(item, incluir_data=True)
            ),
        )
        submenu_copiar.add_separator()
        submenu_copiar.add_command(
            label="ID do confronto no banco",
            command=lambda itens=jogos_selecionados: self._copiar_ids_confrontos_temporadas(
                itens
            ),
        )
        submenu_copiar.add_command(
            label="ID do tecnico da partida",
            command=lambda item=jogo: self._copiar_campo_banco_temporadas(
                item.get("db_tecnico_id"),
                "ID do tecnico",
            ),
        )
        menu.add_cascade(label="Copiar", menu=submenu_copiar)
        menu.add_separator()
        menu.add_command(label="Excluir jogo", command=lambda idx=jogo_idx: self._excluir_jogo_por_indice(idx))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _formatar_confronto_temporadas(self, jogo, incluir_placar=False, incluir_data=False):
        adversario = str(jogo.get("adversario", "") or "").strip()
        data = str(jogo.get("data", "") or "").strip()
        local = str(jogo.get("local", "") or "").strip().casefold()
        placar = jogo.get("placar") or {}
        gols_vasco = int(placar.get("vasco", 0) or 0)
        gols_adversario = int(placar.get("adversario", 0) or 0)

        if local == "fora":
            confronto = f"{adversario} x Vasco"
            if incluir_placar:
                confronto = f"{adversario} {gols_adversario} x {gols_vasco} Vasco"
        else:
            confronto = f"Vasco x {adversario}"
            if incluir_placar:
                confronto = f"Vasco {gols_vasco} x {gols_adversario} {adversario}"

        if incluir_data and data:
            return f"{data} - {confronto}"
        return confronto

    def _copiar_texto_temporadas(self, texto):
        if not str(texto or "").strip():
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.root.update()

    def _copiar_campo_banco_temporadas(self, valor, descricao):
        if valor in (None, ""):
            messagebox.showwarning("Copiar", f"{descricao} não disponível para esta partida.")
            return
        self._copiar_texto_temporadas(str(valor))

    def _copiar_ids_confrontos_temporadas(self, jogos):
        ids = []
        for jogo in jogos:
            valor = jogo.get("db_match_id")
            if valor in (None, ""):
                continue
            ids.append(str(valor))

        if not ids:
            messagebox.showwarning("Copiar", "ID do confronto não disponível para as partidas selecionadas.")
            return

        self._copiar_texto_temporadas(",".join(ids) + ",")

    def _excluir_jogo_por_indice(self, jogo_idx):
        jogos = carregar_dados_jogos()
        if not (0 <= jogo_idx < len(jogos)):
            messagebox.showerror("Erro", "Não foi possível localizar o jogo para exclusão.")
            return

        jogo = jogos[jogo_idx]
        participantes = _jogadores_que_participaram_do_jogo(jogo)
        desc = f"{jogo.get('data', '')} - Vasco x {jogo.get('adversario', '')} ({jogo.get('competicao', '')})"
        if not messagebox.askyesno("Excluir jogo", f"Deseja excluir este jogo?\n\n{desc}"):
            return

        jogos.pop(jogo_idx)
        salvar_lista_jogos(jogos)
        self._ajustar_jogos_pelo_vasco_jogadores_historico(participantes, set())

        if self.editing_index == jogo_idx:
            self._limpar_formulario()
        elif self.editing_index is not None and self.editing_index > jogo_idx:
            self.editing_index -= 1

        self._atualizar_abas()
        messagebox.showinfo("Sucesso", "Jogo excluído com sucesso.")

    _LAZY_TAB_LOADERS: list[tuple[str, str]] = [
        ("frame_temporadas", "_carregar_temporadas"),
        ("frame_geral", "_carregar_geral"),
        ("frame_estadios", "_carregar_estadios"),
        ("frame_comparativo", "_carregar_comparativo"),
        ("frame_graficos", "_carregar_graficos"),
        ("frame_tecnicos", "_carregar_tecnicos"),
        ("frame_arbitros", "_carregar_arbitros"),
        ("frame_titulos", "_carregar_titulos"),
    ]

    def _marcar_tabs_sujas(self):
        """Marca todas as abas estatísticas como desatualizadas e recarrega a ativa imediatamente."""
        for frame_attr, _ in self._LAZY_TAB_LOADERS:
            self._tabs_sujas.add(frame_attr)
        atual = self.notebook.select()
        for frame_attr, loader in self._LAZY_TAB_LOADERS:
            frame = getattr(self, frame_attr, None)
            if frame is not None and str(atual) == str(frame):
                getattr(self, loader)()
                self._tabs_sujas.discard(frame_attr)
                break

    def _atualizar_abas(self):
        self.elenco_atual = carregar_elenco_atual()
        self.titulos_vasco = carregar_titulos_vasco()
        self.jogadores_historico = carregar_jogadores_historico()
        self._sincronizar_jogadores_historico()
        self._atualizar_elenco_disponivel_partida()
        self._marcar_tabs_sujas()
        self._render_aba_jogadores_historico()
        if hasattr(self, "retro_adversario_combo"):
            self._atualizar_opcoes_aba_retro()
            if self.retro_adversario_var.get().strip():
                self._atualizar_retro_aba_adversario()

    # --------------------- Menu de contexto ---------------------
    def mostrar_menu_contexto(self, event, tipo):
        widget = event.widget
        selecionado = widget.get().strip()
        if not selecionado:
            return

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Excluir '{selecionado}'",
                         command=lambda: self.excluir_nome(selecionado, tipo, widget))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def excluir_nome(self, nome, tipo, widget):
        alterou = False
        if tipo == "vasco" and nome in self.listas["jogadores_vasco"]:
            self.listas["jogadores_vasco"].remove(nome); alterou = True
            widget['values'] = self.listas["jogadores_vasco"]
        elif tipo == "contra" and nome in self.listas["jogadores_contra"]:
            self.listas["jogadores_contra"].remove(nome); alterou = True
            widget['values'] = self.listas["jogadores_contra"]
        elif tipo == "clubes" and nome in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].remove(nome); alterou = True
            widget['values'] = self.listas["clubes_adversarios"]
        elif tipo == "competicoes" and nome in self.listas.get("competicoes", []):
            self.listas["competicoes"].remove(nome); alterou = True
            widget['values'] = self.listas.get("competicoes", [])
        elif tipo == "tecnicos" and nome in self.listas.get("tecnicos", []):
            self.listas["tecnicos"].remove(nome); alterou = True
            widget['values'] = self.listas.get("tecnicos", [])
            if self.listas.get("tecnico_atual") == nome:
                novo = self.listas["tecnicos"][0] if self.listas["tecnicos"] else "Fernando Diniz"
                self.listas["tecnico_atual"] = novo
                if hasattr(self, "tecnico_var"):
                    self.tecnico_var.set(novo)
                self._atualizar_combo_tecnicos()
        elif tipo == "arbitros" and nome in self.listas.get("arbitros", []):
            self.listas["arbitros"].remove(nome); alterou = True
            self._atualizar_combos_arbitragem()
        elif tipo == "auxiliares" and nome in self.listas.get("auxiliares", []):
            self.listas["auxiliares"].remove(nome); alterou = True
            self._atualizar_combos_arbitragem()
        elif tipo == "vars" and nome in self.listas.get("vars", []):
            self.listas["vars"].remove(nome); alterou = True
            self._atualizar_combos_arbitragem()

        if alterou:
            salvar_listas(self.listas)
            widget.set("")
        else:
            messagebox.showwarning("Não encontrado", f"'{nome}' não está na lista.")

    # --------------------- Helper: tooltips no Treeview ---------------------
    def _bind_treeview_tooltips(self, tree: ttk.Treeview, tooltip_map: dict):
        """Mostra tooltip com texto de tooltip_map[iid] ao passar o mouse nas linhas do Treeview."""
        tooltip = Tooltip(self.root, delay=400)
        state = {"current": None}

        def on_motion(e):
            item = tree.identify_row(e.y)
            if item != state["current"]:
                tooltip.cancel()
                state["current"] = item
                if item and item in tooltip_map:
                    text = tooltip_map[item]
                    tooltip.schedule(lambda t=text, xr=e.x_root, yr=e.y_root: tooltip.show(t, xr, yr))

        def on_leave(_):
            tooltip.cancel()

        def on_destroy(_):
            tooltip.cancel()

        tree.bind("<Motion>", on_motion)
        tree.bind("<Leave>", on_leave)
        tree.bind("<Destroy>", on_destroy)

    def _forcar_cursor_visivel(self, widget):
        if widget is None:
            return
        def _aplicar():
            aplicado = False
            for opt in ("insertbackground", "insertcolor"):
                try:
                    widget.configure(**{opt: self.colors["accent"]})
                    aplicado = True
                    break
                except tk.TclError:
                    continue
            if not aplicado:
                try:
                    widget.tk.call(widget._w, "configure", "-insertbackground", self.colors["accent"])
                except tk.TclError:
                    pass
            try:
                widget.configure(insertwidth=2)
            except tk.TclError:
                pass
        try:
            _aplicar()
        except tk.TclError:
            self.root.after(30, _aplicar)

    def _atualizar_combo_tecnicos(self):
        if hasattr(self, "tecnico_entry"):
            self.tecnico_entry['values'] = self.listas.get("tecnicos", [])

    def _atualizar_combos_arbitragem(self):
        if hasattr(self, "arbitro_entry"):
            self.arbitro_entry["values"] = self.listas.get("arbitros", [])
        if hasattr(self, "auxiliar_1_entry"):
            self.auxiliar_1_entry["values"] = self.listas.get("auxiliares", [])
        if hasattr(self, "auxiliar_2_entry"):
            self.auxiliar_2_entry["values"] = self.listas.get("auxiliares", [])
        if hasattr(self, "var_arbitragem_entry"):
            self.var_arbitragem_entry["values"] = self.listas.get("vars", [])
        if hasattr(self, "elenco_tecnico_entry"):
            self.elenco_tecnico_entry['values'] = self.listas.get("tecnicos", [])
        self._atualizar_combo_estadios()

    def _atualizar_combo_estadios(self, adversario: str | None = None):
        if hasattr(self, "estadio_entry"):
            base = list(self.listas.get("estadios", []))
            alvo = adversario
            if alvo is None and hasattr(self, "adversario_var"):
                alvo = self.adversario_var.get().strip()
            relacionados = carregar_estadios_adversario(alvo or "")
            self.estadio_entry["values"] = self._ordenar_opcoes_estadios(base, relacionados)

    def _reordenar_estadios_para_adversario(self, adversario: str):
        self._atualizar_combo_estadios(adversario)

    def _ordenar_opcoes_estadios(self, base, relacionados=None):
        ordenados = []
        vistos = set()
        for nome in (relacionados or []):
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                continue
            chave = nome_limpo.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            ordenados.append(nome_limpo)
        for nome in base or []:
            nome_limpo = str(nome or "").strip()
            if not nome_limpo:
                continue
            chave = nome_limpo.casefold()
            if chave in vistos:
                continue
            vistos.add(chave)
            ordenados.append(nome_limpo)

        sao_januario = next((n for n in ordenados if n.casefold() == "são januário".casefold()), None)
        maracana = next((n for n in ordenados if n.casefold() == "maracanã".casefold()), None)
        resto = [
            n for n in ordenados
            if n.casefold() not in {"são januário".casefold(), "maracanã".casefold()}
        ]
        final = []
        if sao_januario:
            final.append(sao_januario)
        if maracana:
            final.append(maracana)
        final.extend(resto)
        return final

    def _mascara_campo_horario(self, var_name, proximo_widget=None):
        var = getattr(self, var_name, None)
        if var is None:
            return
        atual = var.get()
        formatado = re.sub(r"\D", "", atual)[:2]
        if atual != formatado:
            var.set(formatado)
            return
        if len(formatado) == 2 and proximo_widget is not None:
            try:
                proximo_widget.focus_set()
                proximo_widget.icursor(tk.END)
            except Exception:
                pass

    def _obter_horario_formatado(self) -> str:
        hora = self.horario_hora_var.get().strip() if hasattr(self, "horario_hora_var") else ""
        minuto = self.horario_minuto_var.get().strip() if hasattr(self, "horario_minuto_var") else ""
        if not hora or not minuto:
            return ""
        return f"{hora}:{minuto}"

    def _preencher_estadio_por_adversario(self, adversario: str, local: str):
        if not hasattr(self, "estadio_var"):
            return
        self._reordenar_estadios_para_adversario(adversario)
        local_norm = str(local or "").strip().casefold()
        if local_norm == "casa":
            self.estadio_var.set("São Januário")
            return
        estadio_adversario = carregar_estadio_adversario(adversario)
        if estadio_adversario:
            if estadio_adversario not in self.listas.get("estadios", []):
                self.listas.setdefault("estadios", []).append(estadio_adversario)
                self.listas = _ordenar_listas(self.listas)
                salvar_listas(self.listas)
                self._atualizar_combo_tecnicos()
            self.estadio_var.set(estadio_adversario)

    def _sugerir_estadio_por_adversario(self, adversario: str, local: str) -> str:
        local_norm = str(local or "").strip().casefold()
        if local_norm == "casa":
            return "São Januário"
        if local_norm == "fora":
            return carregar_estadio_adversario(adversario)
        return ""

    def _ao_mudar_adversario_registro(self, *_args):
        adversario = self.adversario_var.get().strip() if hasattr(self, "adversario_var") else ""
        self._reordenar_estadios_para_adversario(adversario)
        if not adversario:
            return
        if hasattr(self, "local_var") and self.local_var.get() == "fora":
            self._preencher_estadio_por_adversario(adversario, "fora")

    def _ao_mudar_local_registro(self, *_args):
        if not hasattr(self, "local_var") or not hasattr(self, "adversario_var"):
            return
        local = self.local_var.get().strip().casefold()
        adversario = self.adversario_var.get().strip()
        if local == "fora":
            if adversario:
                self._preencher_estadio_por_adversario(adversario, "fora")
            return
        if local == "casa" and hasattr(self, "estadio_var"):
            self.estadio_var.set("São Januário")

    def _competicao_usa_posicao(self, nome):
        if not nome:
            return False
        return nome.strip().casefold() in {item.casefold() for item in COMPETICOES_COM_POSICAO_TABELA}

    def _competicao_usa_grafico_posicao(self, nome):
        if not nome:
            return False
        return nome.strip().casefold() in {item.casefold() for item in COMPETICOES_COM_GRAFICO_POSICAO}

    def _competicao_eh_brasileiro_serie_a_ou_b(self, nome):
        if not nome:
            return False
        nome_cf = nome.strip().casefold()
        return nome_cf in {
            "campeonato brasileiro serie a",
            "campeonato brasileiro série a",
            "campeonato brasileiro serie b",
            "campeonato brasileiro série b",
        }

    def _encontrar_competicao_brasileira_para_comparativo(self, comps_ano, competicao_atual):
        if not isinstance(comps_ano, dict) or not self._competicao_eh_brasileiro_serie_a_ou_b(competicao_atual):
            return competicao_atual
        for nome in comps_ano.keys():
            if self._competicao_eh_brasileiro_serie_a_ou_b(nome):
                return nome
        return competicao_atual

    def _atualizar_estado_posicao(self):
        if not hasattr(self, "posicao_entry") or not hasattr(self, "posicao_var"):
            return
        comp = self.competicao_var.get().strip() if hasattr(self, "competicao_var") else ""
        if self._competicao_usa_posicao(comp):
            self.posicao_entry.state(["!disabled"])
        else:
            self.posicao_entry.state(["disabled"])
            self.posicao_var.set("")

    # --------------------- Temporadas ---------------------
    def _carregar_temporadas(self):
        for widget in self.frame_temporadas.winfo_children():
            widget.destroy()
        self._temporadas_filtros_vars = []

        jogos = carregar_dados_jogos()
        if not jogos:
            ttk.Label(self.frame_temporadas, text="Ainda não há jogos registrados.").pack(anchor="w")
            return

        temporadas = defaultdict(list)
        artilheiros_totais = Counter()
        carrascos_totais = Counter()
        for idx, jogo in enumerate(jogos):
            ano = jogo["data"][-4:]
            temporadas[ano].append((idx, jogo))
            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    artilheiros_totais[g["nome"]] += g["gols"]
            for g in jogo.get("gols_adversario", []):
                if isinstance(g, dict):
                    carrascos_totais[g["nome"]] += g["gols"]
        invicto_totais = 0
        invicto_max_totais = 0
        derrota_totais = 0
        derrota_max_totais = 0
        streak_inv = 0
        streak_der = 0
        for jogo in sorted(jogos, key=lambda j: _parse_data_ptbr(j["data"])):
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            vasco = placar.get("vasco", 0)
            adv = placar.get("adversario", 0)
            if vasco >= adv:
                streak_inv += 1
                invicto_max_totais = max(invicto_max_totais, streak_inv)
                streak_der = 0
            else:
                streak_der += 1
                derrota_max_totais = max(derrota_max_totais, streak_der)
                streak_inv = 0

        if not temporadas:
            ttk.Label(self.frame_temporadas, text="Não foi possível agrupar as temporadas.").pack(anchor="w")
            return

        nb = ttk.Notebook(self.frame_temporadas)
        nb.pack(fill="both", expand=True)

        anos_ordenados = sorted(temporadas.keys())
        limite_abas = 10
        limite_temporadas_visiveis = limite_abas if len(anos_ordenados) <= limite_abas else limite_abas - 1
        anos_visiveis = anos_ordenados[-limite_temporadas_visiveis:]
        anos_ocultos = anos_ordenados[:-limite_temporadas_visiveis]

        if anos_ocultos:
            frame_mais = ttk.Frame(nb, padding=10)
            nb.add(frame_mais, text="Mais")

            topo = ttk.Frame(frame_mais)
            topo.pack(fill="x", pady=(0, 8))
            ttk.Label(
                topo,
                text="Temporadas antigas ficam aqui para manter no máximo 10 abas visíveis.",
            ).pack(side="left")

            seletor_wrap = ttk.Frame(frame_mais)
            seletor_wrap.pack(fill="x", pady=(0, 8))
            ttk.Label(seletor_wrap, text="Carregar temporada:").pack(side="left")
            temporada_antiga_var = tk.StringVar(value=str(anos_ocultos[-1]))
            combo_temporadas_antigas = ttk.Combobox(
                seletor_wrap,
                textvariable=temporada_antiga_var,
                values=list(reversed(anos_ocultos)),
                state="readonly",
                width=10,
            )
            combo_temporadas_antigas.pack(side="left", padx=(8, 8))

            container_temporada_antiga = ttk.Frame(frame_mais)
            container_temporada_antiga.pack(fill="both", expand=True)

            def _render_temporada_antiga(_event=None):
                ano_sel = temporada_antiga_var.get().strip()
                if not ano_sel or ano_sel not in temporadas:
                    return
                for child in container_temporada_antiga.winfo_children():
                    child.destroy()
                self._montar_conteudo_temporada(container_temporada_antiga, ano_sel, temporadas[ano_sel])

            combo_temporadas_antigas.bind("<<ComboboxSelected>>", _render_temporada_antiga)
            ttk.Button(seletor_wrap, text="Carregar", command=_render_temporada_antiga).pack(side="left")
            _render_temporada_antiga()

        for idx, ano in enumerate(anos_visiveis):
            frame_ano = ttk.Frame(nb, padding=10)
            nb.add(frame_ano, text=str(ano))
            self._montar_conteudo_temporada(frame_ano, ano, temporadas[ano])

        try:
            if nb.tabs():
                nb.select(len(nb.tabs()) - 1)
        except tk.TclError:
            pass

    def _montar_conteudo_temporada(self, frame_ano, ano, jogos_ano):
        vitorias = empates = derrotas = 0
        gols_pro = gols_contra = 0
        artilheiros = Counter()
        carrascos = Counter()
        publico_pagante_total = 0
        publico_presente_total = 0
        renda_total = 0.0
        publico_pagante_casa = 0
        publico_presente_casa = 0
        renda_casa = 0.0
        publico_pagante_fora = 0
        publico_presente_fora = 0
        renda_fora = 0.0

        rows = []
        streak_inv = streak_sem_vitoria = 0
        invicto_max = sem_vitoria_max = 0
        for idx_global, jogo in sorted(jogos_ano, key=lambda j: _parse_data_ptbr(j[1]["data"])):
            local = jogo.get("local", "desconhecido").capitalize()
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            competicao = jogo.get("competicao", "Competição Desconhecida")
            data = jogo["data"]
            adversario = jogo["adversario"]

            resultado = "Empate"
            if placar["vasco"] > placar["adversario"]:
                resultado = "Vitória"
                vitorias += 1
                streak_inv += 1
                invicto_max = max(invicto_max, streak_inv)
                streak_sem_vitoria = 0
            elif placar["vasco"] < placar["adversario"]:
                resultado = "Derrota"
                derrotas += 1
                streak_sem_vitoria += 1
                sem_vitoria_max = max(sem_vitoria_max, streak_sem_vitoria)
                streak_inv = 0
            else:
                empates += 1
                streak_inv += 1
                invicto_max = max(invicto_max, streak_inv)
                streak_sem_vitoria += 1
                sem_vitoria_max = max(sem_vitoria_max, streak_sem_vitoria)

            gols_pro += placar.get("vasco", 0)
            gols_contra += placar.get("adversario", 0)
            publico_pagante_jogo = jogo.get("publico_pagante")
            publico_presente_jogo = jogo.get("publico_presente")
            renda_jogo = jogo.get("renda")
            try:
                publico_pagante_jogo = int(publico_pagante_jogo) if publico_pagante_jogo is not None else 0
            except Exception:
                publico_pagante_jogo = 0
            try:
                publico_presente_jogo = int(publico_presente_jogo) if publico_presente_jogo is not None else 0
            except Exception:
                publico_presente_jogo = 0
            try:
                renda_jogo = float(renda_jogo) if renda_jogo is not None else 0.0
            except Exception:
                renda_jogo = 0.0

            publico_pagante_total += publico_pagante_jogo
            publico_presente_total += publico_presente_jogo
            renda_total += renda_jogo
            local_jogo = str(jogo.get("local", "")).strip().casefold()
            if local_jogo == "fora":
                publico_pagante_fora += publico_pagante_jogo
                publico_presente_fora += publico_presente_jogo
                renda_fora += renda_jogo
            else:
                publico_pagante_casa += publico_pagante_jogo
                publico_presente_casa += publico_presente_jogo
                renda_casa += renda_jogo

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    artilheiros[g["nome"]] += g["gols"]
            for g in jogo.get("gols_adversario", []):
                if isinstance(g, dict):
                    carrascos[g["nome"]] += g["gols"]

            rows.append({
                "data": data,
                "local": local,
                "competicao": competicao,
                "adversario": adversario,
                "resultado": resultado,
                "tecnico": str(jogo.get("tecnico", "") or "").strip(),
                "raw": jogo,
                "idx": idx_global,
            })

        jogos_disputados = len(jogos_ano)
        saldo = gols_pro - gols_contra
        aproveitamento = round(((vitorias * 3 + empates) / (jogos_disputados * 3)) * 100, 1) if jogos_disputados else 0.0
        media_gols_pro = round(gols_pro / jogos_disputados, 2) if jogos_disputados else 0.0
        media_gols_contra = round(gols_contra / jogos_disputados, 2) if jogos_disputados else 0.0
        scouts_temporada_state = {"linhas": rows}
        recorte_wrap = ttk.Frame(frame_ano)
        recorte_wrap.pack(fill="x", pady=(0, 8))
        ttk.Label(recorte_wrap, text="Recorte:").pack(side="left")
        filtro_local_var = tk.StringVar(value="todos")
        ttk.Radiobutton(recorte_wrap, text="Todos", variable=filtro_local_var, value="todos").pack(side="left", padx=(8, 6))
        ttk.Radiobutton(recorte_wrap, text="Casa", variable=filtro_local_var, value="casa").pack(side="left", padx=6)
        ttk.Radiobutton(recorte_wrap, text="Fora", variable=filtro_local_var, value="fora").pack(side="left", padx=6)
        ttk.Button(
            recorte_wrap,
            text="Ver scouts do recorte",
            command=lambda ano_ref=ano, state=scouts_temporada_state: self._abrir_modal_scouts_temporada(
                ano_ref,
                state.get("linhas", []),
            ),
        ).pack(side="left", padx=(14, 0))

        cards = ttk.Frame(frame_ano)
        cards.pack(fill="x", pady=(0, 8))
        cards.columnconfigure((0, 1, 2, 3), weight=1)

        def make_card(parent, titulo, var):
            lf = ttk.Labelframe(parent, text=titulo, style="Card.TLabelframe")
            ttk.Label(lf, textvariable=var, style="CardValue.TLabel").pack()
            return lf

        card_specs = [
            ("Jogos", "jogos"),
            ("Vitórias", "vitorias"),
            ("Empates", "empates"),
            ("Derrotas", "derrotas"),
            ("Gols Pró", "gols_pro"),
            ("Gols Contra", "gols_contra"),
            ("Saldo", "saldo"),
            ("Aproveitamento (%)", "aproveitamento"),
            ("Média gols pró", "media_gols_pro"),
            ("Média gols contra", "media_gols_contra"),
            ("Maior sequência invicta", "invicto_max"),
            ("Maior tempo sem vitórias", "sem_vitoria_max"),
            ("Público Pagante", "publico_pagante"),
            ("Público Presente", "publico_presente"),
            ("Renda", "renda"),
            ("Jogos com scout", "scout_jogos"),
            ("Posse média", "scout_posse"),
            ("Finalizações", "scout_finalizacoes"),
            ("Chutes no gol", "scout_finalizacoes_no_gol"),
        ]
        card_vars = {chave: tk.StringVar(value="0") for _titulo, chave in card_specs}
        for idx_card, (titulo, chave) in enumerate(card_specs):
            linha, coluna = divmod(idx_card, 4)
            make_card(cards, titulo, card_vars[chave]).grid(row=linha, column=coluna, sticky="nsew", padx=4, pady=4)

        def _atualizar_cards_temporada(linhas_base):
            jogos_filtrados = len(linhas_base)
            vitorias_f = empates_f = derrotas_f = 0
            gols_pro_f = gols_contra_f = 0
            publico_pagante_f = 0
            publico_presente_f = 0
            renda_f = 0.0
            streak_inv_f = streak_sem_vitoria_f = 0
            invicto_max_f = sem_vitoria_max_f = 0

            linhas_ordenadas_data = sorted(
                linhas_base,
                key=lambda r: _parse_data_ptbr_safe(str(r.get("data", ""))) or datetime.min,
            )
            for r in linhas_ordenadas_data:
                jogo_raw = r.get("raw", {})
                placar = jogo_raw.get("placar", {"vasco": 0, "adversario": 0})
                vasco = int(placar.get("vasco", 0) or 0)
                adv = int(placar.get("adversario", 0) or 0)
                gols_pro_f += vasco
                gols_contra_f += adv
                publico_pagante_f += _normalizar_inteiro_positivo(jogo_raw.get("publico_pagante")) or 0
                publico_presente_f += _normalizar_inteiro_positivo(jogo_raw.get("publico_presente")) or 0
                renda_f += _normalizar_renda_brl(jogo_raw.get("renda")) or 0.0

                if vasco > adv:
                    vitorias_f += 1
                    streak_inv_f += 1
                    invicto_max_f = max(invicto_max_f, streak_inv_f)
                    streak_sem_vitoria_f = 0
                elif vasco < adv:
                    derrotas_f += 1
                    streak_sem_vitoria_f += 1
                    sem_vitoria_max_f = max(sem_vitoria_max_f, streak_sem_vitoria_f)
                    streak_inv_f = 0
                else:
                    empates_f += 1
                    streak_inv_f += 1
                    invicto_max_f = max(invicto_max_f, streak_inv_f)
                    streak_sem_vitoria_f += 1
                    sem_vitoria_max_f = max(sem_vitoria_max_f, streak_sem_vitoria_f)

            saldo_f = gols_pro_f - gols_contra_f
            aproveitamento_f = round(((vitorias_f * 3 + empates_f) / (jogos_filtrados * 3)) * 100, 1) if jogos_filtrados else 0.0
            media_gols_pro_f = round(gols_pro_f / jogos_filtrados, 2) if jogos_filtrados else 0.0
            media_gols_contra_f = round(gols_contra_f / jogos_filtrados, 2) if jogos_filtrados else 0.0
            _, _, resumo_scout = self._agregar_estatisticas_vasco_jogos([
                r.get("raw") for r in linhas_base if isinstance(r.get("raw"), dict)
            ])

            card_vars["jogos"].set(str(jogos_filtrados))
            card_vars["vitorias"].set(str(vitorias_f))
            card_vars["empates"].set(str(empates_f))
            card_vars["derrotas"].set(str(derrotas_f))
            card_vars["gols_pro"].set(str(gols_pro_f))
            card_vars["gols_contra"].set(str(gols_contra_f))
            card_vars["saldo"].set(str(saldo_f))
            card_vars["aproveitamento"].set(str(aproveitamento_f))
            card_vars["media_gols_pro"].set(str(media_gols_pro_f))
            card_vars["media_gols_contra"].set(str(media_gols_contra_f))
            card_vars["invicto_max"].set(str(invicto_max_f))
            card_vars["sem_vitoria_max"].set(str(sem_vitoria_max_f))
            card_vars["publico_pagante"].set(_formatar_publico(publico_pagante_f))
            card_vars["publico_presente"].set(_formatar_publico(publico_presente_f))
            card_vars["renda"].set(_formatar_renda_brl(renda_f))
            card_vars["scout_jogos"].set(str(resumo_scout["jogos_com_scout_time"]))
            card_vars["scout_posse"].set(self._formatar_valor_estatistica_agregada("posse_bola", resumo_scout["posse_media"]))
            card_vars["scout_finalizacoes"].set(self._formatar_valor_estatistica_agregada("finalizacoes", resumo_scout["finalizacoes_total"]))
            card_vars["scout_finalizacoes_no_gol"].set(self._formatar_valor_estatistica_agregada("finalizacoes_no_gol", resumo_scout["finalizacoes_no_gol_total"]))

        filtros_temporada = ttk.Frame(frame_ano)
        filtros_temporada.pack(fill="x", pady=(0, 6))
        ttk.Label(filtros_temporada, text="Filtrar (adversário, placar, resultado: vv/ee/dd):").pack(side="left")
        filtro_adversario_var = tk.StringVar(value="")
        self._temporadas_filtros_vars.append(filtro_adversario_var)
        entry_filtro_adversario = ttk.Entry(filtros_temporada, textvariable=filtro_adversario_var, width=28)
        entry_filtro_adversario.pack(side="left", padx=(6, 6))
        self._forcar_cursor_visivel(entry_filtro_adversario)
        ttk.Label(filtros_temporada, text="Estádio:").pack(side="left", padx=(8, 0))
        estadios_temporada = sorted({
            str((r.get("raw") or {}).get("estadio", "")).strip()
            for r in rows
            if str((r.get("raw") or {}).get("estadio", "")).strip()
        }, key=lambda s: s.casefold())
        ttk.Label(filtros_temporada, text="Competição:").pack(side="left", padx=(8, 0))
        competicoes_temporada = sorted({
            str(r.get("competicao", "")).strip()
            for r in rows
            if str(r.get("competicao", "")).strip()
        }, key=lambda s: s.casefold())
        filtro_estadio_var = tk.StringVar(value="Todos")
        self._temporadas_filtros_vars.append(filtro_estadio_var)
        combo_filtro_estadio = ttk.Combobox(
            filtros_temporada,
            textvariable=filtro_estadio_var,
            values=["Todos"] + estadios_temporada,
            state="readonly",
            width=26,
        )
        combo_filtro_estadio.pack(side="left", padx=(6, 6))
        filtro_competicao_var = tk.StringVar(value="Todas")
        self._temporadas_filtros_vars.append(filtro_competicao_var)
        combo_filtro_competicao = ttk.Combobox(
            filtros_temporada,
            textvariable=filtro_competicao_var,
            values=["Todas"] + competicoes_temporada,
            state="readonly",
            width=26,
        )
        combo_filtro_competicao.pack(side="left", padx=(6, 6))

        table_wrap = ttk.Frame(frame_ano)
        table_wrap.pack(fill="both", expand=True)

        cols = ("data", "local", "competicao", "adversario", "resultado", "tecnico", "placar")
        tv = ttk.Treeview(
            table_wrap,
            columns=cols,
            show="headings",
            height=min(16, max(8, len(rows))),
            selectmode="extended",
        )
        for c, w in zip(cols, (90, 80, 190, 170, 110, 160, 250)):
            tv.heading(c, text=c.capitalize() if c != "placar" else "Placar")
            tv.column(c, anchor="w", width=w, stretch=True)

        sy = ttk.Scrollbar(table_wrap, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        tv.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        tv.tag_configure("odd", background=self.colors["row_alt_bg"])

        tooltip_map = {}
        obs_map = {}
        item_to_idx = {}
        sort_state = {"col": "data", "reverse": True}

        self._bind_treeview_tooltips(tv, tooltip_map)
        tv._item_to_idx = item_to_idx
        tv.bind("<Double-1>", self._on_tree_double_click)
        tv.bind("<Button-3>", self._abrir_menu_contexto_temporadas)
        tv.bind("<Control-Button-1>", self._abrir_menu_contexto_temporadas)

        obs_frame = ttk.Frame(frame_ano)
        obs_header = ttk.Frame(obs_frame)
        obs_title = ttk.Label(obs_header, text="Observações:", font=("Segoe UI", 11, "bold"))
        obs_title.pack(side="left", pady=(8, 2))
        btn_close = ttk.Button(
            obs_header,
            text="✕",
            width=3,
            command=lambda f=obs_frame: f.pack_forget()
        )
        btn_close.pack(side="right")
        obs_label = ttk.Label(obs_frame, text="", wraplength=980, justify="left")

        def _upd_wrap(_e=None, lbl=None, container=None):
            if lbl and container and container.winfo_width() > 40:
                lbl.configure(wraplength=container.winfo_width() - 40)

        frame_ano.bind("<Configure>", lambda e, lbl=obs_label, container=frame_ano: _upd_wrap(e, lbl, container))

        def on_select_factory(tv_ref, obs_frame_ref, obs_header_ref, obs_label_ref, obs_map_ref):
            def on_select(_):
                sel = tv_ref.selection()
                if not sel:
                    obs_frame_ref.pack_forget()
                    return

                iid = sel[0]
                txt = obs_map_ref.get(iid, "").strip()

                if txt:
                    if not obs_frame_ref.winfo_ismapped():
                        obs_frame_ref.pack(fill="x", padx=2, pady=(6, 0))
                        obs_header_ref.pack(fill="x")
                        obs_label_ref.pack(anchor="w", pady=(0, 6))
                    obs_label_ref.configure(text=txt)
                else:
                    obs_frame_ref.pack_forget()
            return on_select

        tv.bind("<<TreeviewSelect>>", on_select_factory(tv, obs_frame, obs_header, obs_label, obs_map))

        def _render_rows_temporada(
            rows_base,
            termo_busca="",
            estadio_sel="Todos",
            competicao_sel="Todas",
            local_sel="todos",
            tv_ref=tv,
            tooltip_map_ref=tooltip_map,
            obs_map_ref=obs_map,
            item_to_idx_ref=item_to_idx,
            obs_frame_ref=obs_frame,
            sort_state_ref=sort_state,
        ):
            termo_txt = str(termo_busca or "").strip()
            termo_cf = termo_txt.casefold()
            termo_norm = _chave_nome_jogador(termo_txt)
            resultado_por_termo = None
            if termo_cf == "vv":
                resultado_por_termo = "vitoria"
            elif termo_cf == "ee":
                resultado_por_termo = "empate"
            elif termo_cf == "dd":
                resultado_por_termo = "derrota"
            score_match = re.match(r"^\s*(\d+)\s*x\s*(\d+)\s*$", termo_txt, flags=re.IGNORECASE)
            tv_ref.delete(*tv_ref.get_children())
            tooltip_map_ref.clear()
            obs_map_ref.clear()
            item_to_idx_ref.clear()
            obs_frame_ref.pack_forget()

            linhas = rows_base
            local_sel = str(local_sel or "todos").strip().casefold()
            if local_sel in {"casa", "fora"}:
                linhas = [
                    r for r in linhas
                    if str((r.get("raw") or {}).get("local", "")).strip().casefold() == local_sel
                ]
            if termo_cf:
                if score_match:
                    vasco_q = int(score_match.group(1))
                    adv_q = int(score_match.group(2))
                    linhas_score = []
                    for r in linhas:
                        placar = (r.get("raw") or {}).get("placar", {})
                        try:
                            v = int(placar.get("vasco", -999))
                            a = int(placar.get("adversario", -999))
                        except Exception:
                            continue
                        if v == vasco_q and a == adv_q:
                            linhas_score.append(r)
                    linhas = linhas_score
                else:
                    linhas = [
                        r for r in linhas
                        if (
                            termo_cf in str(r.get("adversario", "")).casefold()
                            or termo_norm in _chave_nome_jogador(r.get("adversario", ""))
                            or termo_cf in str(r.get("competicao", "")).casefold()
                            or termo_norm in _chave_nome_jogador(r.get("competicao", ""))
                            or termo_cf in str(r.get("tecnico", "")).casefold()
                            or termo_norm in _chave_nome_jogador(r.get("tecnico", ""))
                            or (
                                resultado_por_termo is not None
                                and resultado_por_termo == _chave_nome_jogador(r.get("resultado", ""))
                            )
                        )
                    ]
            estadio_sel = str(estadio_sel or "").strip()
            if estadio_sel and estadio_sel != "Todos":
                linhas = [
                    r for r in linhas
                    if str((r.get("raw") or {}).get("estadio", "")).strip().casefold() == estadio_sel.casefold()
                ]
            competicao_sel = str(competicao_sel or "").strip()
            if competicao_sel and competicao_sel != "Todas":
                linhas = [
                    r for r in linhas
                    if str(r.get("competicao", "")).strip().casefold() == competicao_sel.casefold()
                ]

            scouts_temporada_state["linhas"] = list(linhas)
            _atualizar_cards_temporada(linhas)

            def _sort_key(r):
                col = sort_state_ref["col"]
                jogo_raw = r.get("raw", {})
                if col == "data":
                    return _parse_data_ptbr_safe(str(r.get("data", ""))) or datetime.min
                if col == "local":
                    return str(r.get("local", "")).casefold()
                if col == "competicao":
                    return str(r.get("competicao", "")).casefold()
                if col == "adversario":
                    return _chave_nome_jogador(r.get("adversario", ""))
                if col == "resultado":
                    ordem_resultado = {"vitoria": 0, "empate": 1, "derrota": 2}
                    return ordem_resultado.get(_chave_nome_jogador(r.get("resultado", "")), 99)
                if col == "tecnico":
                    return _chave_nome_jogador(r.get("tecnico", ""))
                if col == "placar":
                    placar = jogo_raw.get("placar", {})
                    try:
                        v = int(placar.get("vasco", -1))
                        a = int(placar.get("adversario", -1))
                    except Exception:
                        v, a = -1, -1
                    return (v, a)
                return str(r.get(col, "")).casefold()

            linhas = sorted(linhas, key=_sort_key, reverse=sort_state_ref["reverse"])

            for i, r in enumerate(linhas, start=1):
                jogo_raw = r["raw"]
                placar = jogo_raw.get("placar", {"vasco": 0, "adversario": 0})
                vasco_g = placar.get("vasco", 0)
                adv_g = placar.get("adversario", 0)
                adversario = jogo_raw.get("adversario", "Adversário")
                local_raw = jogo_raw.get("local", "casa")
                local_disp = local_raw.capitalize()

                if local_raw == "casa":
                    placar_fmt = f"Vasco {vasco_g} x {adv_g} {adversario}"
                else:
                    placar_fmt = f"{adversario} {adv_g} x {vasco_g} Vasco"

                iid = tv_ref.insert(
                    "",
                    "end",
                    values=(
                        r["data"],
                        local_disp,
                        r["competicao"],
                        adversario,
                        self._formatar_resultado_com_bolinha(r.get("resultado", "")),
                        r.get("tecnico", ""),
                        placar_fmt,
                    ),
                    tags=("odd" if i % 2 else "",),
                )
                tooltip_map_ref[iid] = self._tooltip_gols_text(jogo_raw)
                obs_map_ref[iid] = jogo_raw.get("observacao", "").strip()
                item_to_idx_ref[iid] = r["idx"]

        def _limpar_filtro_temporada():
            filtro_local_var.set("todos")
            filtro_adversario_var.set("")
            filtro_estadio_var.set("Todos")
            filtro_competicao_var.set("Todas")

        def _toggle_sort_temporada(
            coluna,
            sort_state_ref=sort_state,
            rows_ref=rows,
            filtro_var=filtro_adversario_var,
            filtro_estadio_var_ref=filtro_estadio_var,
            filtro_competicao_var_ref=filtro_competicao_var,
            filtro_local_var_ref=filtro_local_var,
            render_fn=_render_rows_temporada,
        ):
            if sort_state_ref["col"] == coluna:
                sort_state_ref["reverse"] = not sort_state_ref["reverse"]
            else:
                sort_state_ref["col"] = coluna
                sort_state_ref["reverse"] = False
            render_fn(
                rows_ref,
                filtro_var.get(),
                filtro_estadio_var_ref.get(),
                filtro_competicao_var_ref.get(),
                filtro_local_var_ref.get(),
            )

        ttk.Button(filtros_temporada, text="Limpar", command=_limpar_filtro_temporada).pack(side="left")
        filtro_adversario_var.trace_add(
            "write",
            lambda *_args, rows_ref=rows, filtro_var=filtro_adversario_var, filtro_estadio_var_ref=filtro_estadio_var, filtro_competicao_var_ref=filtro_competicao_var, filtro_local_var_ref=filtro_local_var, render_fn=_render_rows_temporada: render_fn(rows_ref, filtro_var.get(), filtro_estadio_var_ref.get(), filtro_competicao_var_ref.get(), filtro_local_var_ref.get())
        )
        filtro_estadio_var.trace_add(
            "write",
            lambda *_args, rows_ref=rows, filtro_var=filtro_adversario_var, filtro_estadio_var_ref=filtro_estadio_var, filtro_competicao_var_ref=filtro_competicao_var, filtro_local_var_ref=filtro_local_var, render_fn=_render_rows_temporada: render_fn(rows_ref, filtro_var.get(), filtro_estadio_var_ref.get(), filtro_competicao_var_ref.get(), filtro_local_var_ref.get())
        )
        filtro_competicao_var.trace_add(
            "write",
            lambda *_args, rows_ref=rows, filtro_var=filtro_adversario_var, filtro_estadio_var_ref=filtro_estadio_var, filtro_competicao_var_ref=filtro_competicao_var, filtro_local_var_ref=filtro_local_var, render_fn=_render_rows_temporada: render_fn(rows_ref, filtro_var.get(), filtro_estadio_var_ref.get(), filtro_competicao_var_ref.get(), filtro_local_var_ref.get())
        )
        filtro_local_var.trace_add(
            "write",
            lambda *_args, rows_ref=rows, filtro_var=filtro_adversario_var, filtro_estadio_var_ref=filtro_estadio_var, filtro_competicao_var_ref=filtro_competicao_var, filtro_local_var_ref=filtro_local_var, render_fn=_render_rows_temporada: render_fn(rows_ref, filtro_var.get(), filtro_estadio_var_ref.get(), filtro_competicao_var_ref.get(), filtro_local_var_ref.get())
        )
        for c in cols:
            if c == "tecnico":
                titulo = "Técnico"
            elif c == "resultado":
                titulo = "Resultado"
            else:
                titulo = c.capitalize() if c != "placar" else "Placar"
            tv.heading(c, text=titulo, command=lambda col=c, toggle_fn=_toggle_sort_temporada: toggle_fn(col))
        _render_rows_temporada(rows, "", filtro_estadio_var.get(), filtro_competicao_var.get(), filtro_local_var.get())

    def _tooltip_gols_text(self, jogo):
        def fmt_lista(lst):
            if not lst:
                return "—"
            partes = []
            for g in lst:
                if isinstance(g, dict):
                    nome = g.get("nome", "Desconhecido")
                    qtd = int(g.get("gols", 0))
                    saiu_banco = bool(g.get("saiu_do_banco", False))
                    nome_fmt = f"🪑 {nome}" if saiu_banco else str(nome)
                    minutos = _normalizar_lista_minutos(g.get("minutos", []))
                    if minutos:
                        minutos_fmt = ", ".join(f"{m}'" for m in minutos)
                        nome_fmt = f"{nome_fmt} ({minutos_fmt})"
                    partes.append(f"{nome_fmt} x{qtd}" if qtd > 1 else nome_fmt)
                elif isinstance(g, str):
                    partes.append(g)
            return ", ".join(partes)

        def fmt_cartoes(lst):
            if not lst:
                return "—"
            partes = []
            for item in lst:
                if isinstance(item, dict):
                    nome = str(item.get("nome", "")).strip() or "Desconhecido"
                    try:
                        qtd = int(item.get("cartoes", item.get("qtd", 1)))
                    except Exception:
                        qtd = 1
                    partes.append(f"{nome} x{qtd}" if qtd > 1 else nome)
                elif isinstance(item, str):
                    partes.append(item)
            return ", ".join(partes) if partes else "—"

        gols_vasco = fmt_lista(jogo.get("gols_vasco", []))
        gols_adv = fmt_lista(jogo.get("gols_adversario", []))
        amarelos = fmt_cartoes(jogo.get("cartoes_amarelos_vasco", []))
        vermelhos = fmt_cartoes(jogo.get("cartoes_vermelhos_vasco", []))
        estadio = str(jogo.get("estadio", "")).strip() or "—"
        horario = str(jogo.get("horario", "")).strip() or "—"
        capitao = str(jogo.get("capitao", "")).strip() or "—"
        publico_pagante = _formatar_publico(jogo.get("publico_pagante"))
        publico_presente = _formatar_publico(jogo.get("publico_presente"))
        renda = _formatar_renda_brl(jogo.get("renda"))
        return (
            f"Estádio: {estadio}\n"
            f"Horário: {horario}\n"
            f"Capitão: {capitao}\n"
            f"Público pagante: {publico_pagante}\n"
            f"Público presente: {publico_presente}\n"
            f"Renda: {renda}\n"
            f"Gols do Vasco: {gols_vasco}\n"
            f"Gols do {jogo.get('adversario','Adversário')}: {gols_adv}\n"
            f"Amarelos do Vasco: {amarelos}\n"
            f"Vermelhos do Vasco: {vermelhos}"
        )

    # --------------------- Geral ---------------------
    def _carregar_geral(self):
        for widget in self.frame_geral.winfo_children():
            widget.destroy()

        jogos = carregar_dados_jogos()
        total = len(jogos)
        vitorias = empates = derrotas = 0
        gols_pro = gols_contra = 0
        artilheiros = Counter()
        carrascos = Counter()
        streak_inv = streak_der = 0
        invicto_max = derrota_max = 0

        jogos_ord = sorted(jogos, key=lambda j: _parse_data_ptbr(j["data"]))
        for jogo in jogos_ord:
            placar = jogo.get("placar")
            if not placar:
                continue

            gols_pro += placar.get("vasco", 0)
            gols_contra += placar.get("adversario", 0)

            if placar["vasco"] > placar["adversario"]:
                vitorias += 1
                streak_inv += 1
                invicto_max = max(invicto_max, streak_inv)
                streak_der = 0
            elif placar["vasco"] < placar["adversario"]:
                derrotas += 1
                streak_der += 1
                derrota_max = max(derrota_max, streak_der)
                streak_inv = 0
            else:
                empates += 1
                streak_inv += 1
                invicto_max = max(invicto_max, streak_inv)
                streak_der = 0

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    artilheiros[g["nome"]] += g["gols"]
            for g in jogo.get("gols_adversario", []):
                if isinstance(g, dict):
                    carrascos[g["nome"]] += g["gols"]

        saldo = gols_pro - gols_contra
        aproveitamento = round(((vitorias * 3 + empates) / (total * 3)) * 100, 1) if total else 0.0
        media_gols_pro = round(gols_pro / total, 2) if total else 0.0
        media_gols_contra = round(gols_contra / total, 2) if total else 0.0

        # Cards
        cards = ttk.Frame(self.frame_geral)
        cards.pack(fill="x", pady=(0, 10))
        cards.columnconfigure((0, 1, 2, 3), weight=1)

        def make_card(parent, titulo, valor):
            lf = ttk.Labelframe(parent, text=titulo, style="Card.TLabelframe")
            ttk.Label(lf, text=str(valor), style="CardValue.TLabel").pack()
            return lf

        make_card(cards, "Jogos", total).grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Vitórias", vitorias).grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Empates", empates).grid(row=0, column=2, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Derrotas", derrotas).grid(row=0, column=3, sticky="nsew", padx=6, pady=6)

        make_card(cards, "Gols Pró", gols_pro).grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Gols Contra", gols_contra).grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Saldo", saldo).grid(row=1, column=2, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Aproveitamento (%)", f"{aproveitamento}").grid(row=1, column=3, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Média gols pró", media_gols_pro).grid(row=2, column=0, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Média gols contra", media_gols_contra).grid(row=2, column=1, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Maior sequência invicta", invicto_max).grid(row=2, column=2, sticky="nsew", padx=6, pady=6)
        make_card(cards, "Maior sequência derrotas", derrota_max).grid(row=2, column=3, sticky="nsew", padx=6, pady=6)

        # Tabelas
        tables = ttk.Frame(self.frame_geral)
        tables.pack(fill="both", expand=True)

        def _criar_lista_filtravel(parent, titulo, heading_jogador, largura_jogador, dados, padx):
            frame = ttk.Labelframe(parent, text=titulo, padding=8)
            frame.pack(side="left", fill="both", expand=True, padx=padx)

            filtros = ttk.Frame(frame)
            filtros.pack(fill="x", pady=(0, 6))
            ttk.Label(filtros, text="Buscar:").pack(side="left")
            termo_var = tk.StringVar()
            entry_busca = ttk.Entry(filtros, textvariable=termo_var, width=24)
            entry_busca.pack(side="left", padx=(6, 6))

            tv = ttk.Treeview(frame, columns=("jogador", "gols"), show="headings", height=12)
            tv.heading("jogador", text=heading_jogador)
            tv.heading("gols", text="Gols")
            tv.column("jogador", anchor="w", width=largura_jogador)
            tv.column("gols", anchor="center", width=80)
            tv.tag_configure("odd", background=self.colors["row_alt_bg"])
            tv.pack(fill="both", expand=True)

            def _render(lista):
                tv.delete(*tv.get_children())
                for i, (nome, qtd) in enumerate(lista, start=1):
                    tv.insert("", "end", values=(nome, qtd), tags=("odd" if i % 2 else "",))

            def _aplicar_filtro(*_):
                termo = termo_var.get().strip().casefold()
                if not termo:
                    _render(dados)
                    return
                filtrados = [(nome, qtd) for nome, qtd in dados if termo in str(nome).casefold()]
                _render(filtrados)

            def _limpar_filtro():
                termo_var.set("")
                _render(dados)

            ttk.Button(filtros, text="Limpar", command=_limpar_filtro).pack(side="left")
            termo_var.trace_add("write", _aplicar_filtro)

            _render(dados)

        artilheiros_lista = artilheiros.most_common()
        carrascos_lista = carrascos.most_common()

        _criar_lista_filtravel(
            tables,
            "Artilheiros do Vasco",
            "Jogador",
            240,
            artilheiros_lista,
            (0, 6),
        )
        _criar_lista_filtravel(
            tables,
            "Carrascos (Gols contra o Vasco)",
            "Jogador (Adversário)",
            260,
            carrascos_lista,
            (6, 0),
        )

    # --------------------- Estádios ---------------------
    def _carregar_estadios(self):
        for widget in self.frame_estadios.winfo_children():
            widget.destroy()

        self.frame_estadios.columnconfigure(0, weight=1)
        self.frame_estadios.rowconfigure(1, weight=1)
        self.frame_estadios.rowconfigure(2, weight=2)

        ttk.Label(
            self.frame_estadios,
            text="Resumo de todos os estádios em que o Vasco já jogou.",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        jogos = carregar_dados_jogos()
        agrupados = {}
        for idx, jogo in enumerate(sorted(jogos, key=lambda j: _parse_data_ptbr_safe(str(j.get("data", ""))) or datetime.min)):
            estadio = str(jogo.get("estadio", "")).strip() or "Não informado"
            placar = jogo.get("placar") or {}
            try:
                gols_pro = int(placar.get("vasco", 0) or 0)
                gols_contra = int(placar.get("adversario", 0) or 0)
            except Exception:
                gols_pro = 0
                gols_contra = 0
            bucket = agrupados.setdefault(
                estadio,
                {
                    "estadio": estadio,
                    "jogos": 0,
                    "vitorias": 0,
                    "empates": 0,
                    "derrotas": 0,
                    "gols_pro": 0,
                    "gols_contra": 0,
                    "saldo": 0,
                    "partidas": [],
                },
            )
            bucket["jogos"] += 1
            bucket["gols_pro"] += gols_pro
            bucket["gols_contra"] += gols_contra
            if gols_pro > gols_contra:
                bucket["vitorias"] += 1
            elif gols_pro < gols_contra:
                bucket["derrotas"] += 1
            else:
                bucket["empates"] += 1
            bucket["saldo"] = bucket["gols_pro"] - bucket["gols_contra"]
            bucket["partidas"].append((idx, jogo))

        esquerda = ttk.Labelframe(self.frame_estadios, text="Estádios", padding=8)
        esquerda.grid(row=1, column=0, sticky="nsew")
        esquerda.columnconfigure(0, weight=1)
        esquerda.rowconfigure(1, weight=1)

        filtros = ttk.Frame(esquerda)
        filtros.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))
        ttk.Label(filtros, text="Buscar:").pack(side="left")
        self.estadios_busca_var = tk.StringVar(value="")
        entry_estadios_busca = ttk.Entry(filtros, textvariable=self.estadios_busca_var, width=24)
        entry_estadios_busca.pack(side="left", padx=(6, 6))
        self._forcar_cursor_visivel(entry_estadios_busca)

        cols_estadios = ("estadio", "jogos", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo")
        self.tv_estadios = ttk.Treeview(esquerda, columns=cols_estadios, show="headings", height=16)
        titulos_estadios = {
            "estadio": "Estádio",
            "jogos": "Jogos",
            "vitorias": "Vitórias",
            "empates": "Empates",
            "derrotas": "Derrotas",
            "gols_pro": "Gols Pró",
            "gols_contra": "Gols Contra",
            "saldo": "Saldo",
        }
        larguras_estadios = {
            "estadio": 220,
            "jogos": 70,
            "vitorias": 70,
            "empates": 70,
            "derrotas": 70,
            "gols_pro": 80,
            "gols_contra": 90,
            "saldo": 70,
        }
        for col in cols_estadios:
            self.tv_estadios.heading(col, text=titulos_estadios[col])
            anchor = "w" if col == "estadio" else "center"
            self.tv_estadios.column(col, width=larguras_estadios[col], anchor=anchor, stretch=(col == "estadio"))
        self.tv_estadios.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_estadios.grid(row=1, column=0, sticky="nsew")
        sy_estadios = ttk.Scrollbar(esquerda, orient="vertical", command=self.tv_estadios.yview)
        sy_estadios.grid(row=1, column=1, sticky="ns")
        self.tv_estadios.configure(yscrollcommand=sy_estadios.set)

        direita = ttk.Labelframe(self.frame_estadios, text="Jogos no Estádio", padding=8)
        direita.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        direita.columnconfigure(0, weight=1)
        direita.rowconfigure(1, weight=1)

        self.estadios_detalhe_var = tk.StringVar(value="Selecione um estádio para ver os jogos.")
        ttk.Label(direita, textvariable=self.estadios_detalhe_var).grid(row=0, column=0, sticky="w", pady=(0, 8))

        cols_jogos = ("data", "local", "competicao", "adversario", "resultado", "placar")
        self.tv_estadios_jogos = ttk.Treeview(direita, columns=cols_jogos, show="headings", height=16)
        for c, w in zip(cols_jogos, (90, 80, 170, 170, 110, 250)):
            titulo = "Placar" if c == "placar" else ("Resultado" if c == "resultado" else c.capitalize())
            self.tv_estadios_jogos.heading(c, text=titulo)
            self.tv_estadios_jogos.column(c, anchor="w", width=w, stretch=True)
        self.tv_estadios_jogos.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_estadios_jogos.grid(row=1, column=0, sticky="nsew")
        sy_jogos = ttk.Scrollbar(direita, orient="vertical", command=self.tv_estadios_jogos.yview)
        sy_jogos.grid(row=1, column=1, sticky="ns")
        self.tv_estadios_jogos.configure(yscrollcommand=sy_jogos.set)

        tooltip_map = {}
        item_to_idx = {}
        self._bind_treeview_tooltips(self.tv_estadios_jogos, tooltip_map)
        self.tv_estadios_jogos._item_to_idx = item_to_idx
        self.tv_estadios_jogos.bind("<Double-1>", self._on_tree_double_click)
        self.tv_estadios_jogos.bind("<Button-3>", self._abrir_menu_contexto_temporadas)
        self.tv_estadios_jogos.bind("<Control-Button-1>", self._abrir_menu_contexto_temporadas)

        estadios_rows = sorted(agrupados.values(), key=lambda item: (str(item.get("estadio", "")).casefold(),))
        iid_to_estadio = {}

        def _render_estadios():
            termo = self.estadios_busca_var.get().strip().casefold() if hasattr(self, "estadios_busca_var") else ""
            selecionado = self.tv_estadios.selection()
            selecionado_nome = ""
            if selecionado:
                vals = self.tv_estadios.item(selecionado[0], "values")
                if vals:
                    selecionado_nome = str(vals[0]).strip()

            self.tv_estadios.delete(*self.tv_estadios.get_children())
            iid_to_estadio.clear()
            novo_sel = None
            exibidos = []
            for item in estadios_rows:
                estadio = str(item.get("estadio", "")).strip()
                if termo and termo not in estadio.casefold():
                    continue
                exibidos.append(item)
            for i, item in enumerate(exibidos, start=1):
                iid = self.tv_estadios.insert(
                    "",
                    "end",
                    values=(
                        item["estadio"],
                        item["jogos"],
                        item["vitorias"],
                        item["empates"],
                        item["derrotas"],
                        item["gols_pro"],
                        item["gols_contra"],
                        item["saldo"],
                    ),
                    tags=("odd",) if i % 2 else (),
                )
                iid_to_estadio[iid] = item
                if selecionado_nome and item["estadio"] == selecionado_nome:
                    novo_sel = iid
            if not novo_sel and self.tv_estadios.get_children():
                novo_sel = self.tv_estadios.get_children()[0]
            if novo_sel:
                self.tv_estadios.selection_set(novo_sel)
                self.tv_estadios.focus(novo_sel)
                _ao_selecionar_estadio()
            else:
                self.estadios_detalhe_var.set("Selecione um estádio para ver os jogos.")
                self.tv_estadios_jogos.delete(*self.tv_estadios_jogos.get_children())
                tooltip_map.clear()
                item_to_idx.clear()

        def _ao_selecionar_estadio(_event=None):
            sel = self.tv_estadios.selection()
            if not sel:
                return
            item = iid_to_estadio.get(sel[0])
            if not item:
                return
            estadio = str(item.get("estadio", "")).strip()
            self.estadios_detalhe_var.set(f"Jogos do Vasco em {estadio}")
            self.tv_estadios_jogos.delete(*self.tv_estadios_jogos.get_children())
            tooltip_map.clear()
            item_to_idx.clear()
            for i, (idx_global, jogo_raw) in enumerate(item.get("partidas", []), start=1):
                placar = jogo_raw.get("placar", {"vasco": 0, "adversario": 0})
                vasco_g = int(placar.get("vasco", 0) or 0)
                adv_g = int(placar.get("adversario", 0) or 0)
                adversario = str(jogo_raw.get("adversario", "")).strip() or "Adversário"
                local_raw = str(jogo_raw.get("local", "casa")).strip().casefold()
                if local_raw == "fora":
                    placar_fmt = f"{adversario} {adv_g} x {vasco_g} Vasco"
                else:
                    placar_fmt = f"Vasco {vasco_g} x {adv_g} {adversario}"
                resultado = "Empate"
                if vasco_g > adv_g:
                    resultado = "Vitória"
                elif vasco_g < adv_g:
                    resultado = "Derrota"
                iid = self.tv_estadios_jogos.insert(
                    "",
                    "end",
                    values=(
                        str(jogo_raw.get("data", "")).strip(),
                        local_raw.capitalize() if local_raw else "—",
                        str(jogo_raw.get("competicao", "")).strip() or "—",
                        adversario,
                        self._formatar_resultado_com_bolinha(resultado),
                        placar_fmt,
                    ),
                    tags=("odd",) if i % 2 else (),
                )
                tooltip_map[iid] = self._tooltip_gols_text(jogo_raw)
                item_to_idx[iid] = idx_global

        self.tv_estadios.bind("<<TreeviewSelect>>", _ao_selecionar_estadio)
        self.estadios_busca_var.trace_add("write", lambda *_: _render_estadios())
        ttk.Button(filtros, text="Limpar", command=lambda: self.estadios_busca_var.set("")).pack(side="left")
        _render_estadios()

    # --------------------- Comparativo ---------------------
    def _carregar_comparativo(self):
        for widget in self.frame_comparativo.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.frame_comparativo, highlightthickness=0, bg=self.colors["bg"])
        scrollbar = ttk.Scrollbar(self.frame_comparativo, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        scroll_frame = ttk.Frame(canvas, padding=8)
        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _update_scroll_region(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", _update_scroll_region)

        def _update_width(event):
            canvas.itemconfigure(window_id, width=event.width)

        canvas.bind("<Configure>", _update_width)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        jogos = carregar_dados_jogos()
        temporadas = self._agrupar_por_temporada(jogos)
        anos = sorted(temporadas.keys())
        if len(anos) < 2:
            ttk.Label(
                scroll_frame,
                text="Cadastre pelo menos duas temporadas completas para ver o comparativo."
            ).pack(anchor="w")
            return

        ano_atual = anos[-1]
        ano_anterior = anos[-2]
        jogos_atual = temporadas.get(ano_atual, [])
        jogos_anterior = temporadas.get(ano_anterior, [])
        if not jogos_atual:
            ttk.Label(
                scroll_frame,
                text=f"A temporada {ano_atual} ainda não possui jogos registrados."
            ).pack(anchor="w")
            return

        jogos_equivalentes_anterior = jogos_anterior[:len(jogos_atual)]
        stats_atual = self._resumir_jogos(jogos_atual)
        stats_anterior = self._resumir_jogos(jogos_equivalentes_anterior)
        series_atual = self._montar_series_evolucao(jogos_atual)
        series_anterior = self._montar_series_evolucao(jogos_equivalentes_anterior) if jogos_equivalentes_anterior else None

        nb = ttk.Notebook(scroll_frame)
        nb.pack(fill="both", expand=True)

        frame_totais = ttk.Frame(nb, padding=10)
        nb.add(frame_totais, text="Totais")
        self._render_tab_totais(
            frame_totais,
            stats_atual,
            stats_anterior,
            series_atual,
            series_anterior,
            ano_atual,
            ano_anterior,
            len(jogos_anterior)
        )

        comps_por_ano = self._agrupar_competicoes_por_ano(temporadas)
        comps_atual = comps_por_ano.get(ano_atual, {})
        comps_anterior = comps_por_ano.get(ano_anterior, {})
        todas_competicoes = sorted(set(list(comps_atual.keys()) + list(comps_anterior.keys())),
                                   key=lambda nome: (0 if self._competicao_usa_posicao(nome) else 1, nome.casefold()))

        if not todas_competicoes:
            aviso = ttk.Label(
                frame_totais,
                text="Nenhuma competição específica encontrada para as temporadas comparadas."
            )
            aviso.pack(anchor="w", pady=(10, 0))
            return

        for nome_comp in todas_competicoes:
            frame_comp = ttk.Frame(nb, padding=10)
            nb.add(frame_comp, text=nome_comp)
            self._render_tab_competicao(
                frame_comp,
                nome_comp,
                comps_por_ano,
                ano_atual,
                ano_anterior
            )

    def _render_tab_totais(self, container, stats_atual, stats_anterior, series_atual, series_anterior, ano_atual, ano_anterior, total_jogos_anterior):
        geral_section = ttk.Labelframe(
            container,
            text=f"Temporada {ano_atual} x {ano_anterior} (mesmo número de jogos)",
            padding=10
        )
        geral_section.pack(fill="both", expand=True)
        resumo_lbl = ttk.Label(
            geral_section,
            text=f"{stats_atual['jogos']} jogo(s) comparados com os primeiros {stats_anterior['jogos']} jogo(s) de {ano_anterior}."
        )
        resumo_lbl.pack(anchor="w", pady=(0, 6))
        if total_jogos_anterior < stats_atual["jogos"]:
            ttk.Label(
                geral_section,
                text="Aviso: existem menos partidas registradas na temporada anterior; a comparação foi ajustada para a quantidade disponível.",
                foreground="#b45309",
                wraplength=900
            ).pack(anchor="w", pady=(0, 6))

        metricas_gerais = [
            ("Jogos", "jogos"),
            ("Vitórias", "vitorias"),
            ("Empates", "empates"),
            ("Derrotas", "derrotas"),
            ("Gols Pró", "gols_pro"),
            ("Gols Contra", "gols_contra"),
            ("Saldo", "saldo"),
            ("Aproveitamento (%)", "aproveitamento"),
            ("Média Gols Pró", "media_gols_pro"),
            ("Média Gols Contra", "media_gols_contra"),
        ]
        self._montar_tabela_comparativo(
            geral_section,
            metricas_gerais,
            stats_atual,
            stats_anterior,
            f"{ano_atual}",
            f"{ano_anterior}"
        )

        if MATPLOTLIB_OK and series_atual.get("x"):
            graficos_gerais = ttk.Frame(geral_section)
            graficos_gerais.pack(fill="x", pady=(12, 0))
            self._plot_linhas_comparativo(
                graficos_gerais,
                series_atual,
                ["gols_pro_acum", "gols_contra_acum"],
                ["Gols pró (acum.)", "Gols contra (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução de gols",
                ylabel="Gols"
            )
            self._plot_linhas_comparativo(
                graficos_gerais,
                series_atual,
                ["saldo_acum"],
                ["Saldo (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução do saldo",
                ylabel="Saldo"
            )
            self._plot_linhas_comparativo(
                graficos_gerais,
                series_atual,
                ["vit_acum"],
                ["Vitórias (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução das vitórias",
                ylabel="Qtd.",
                color_override={
                    "vit_acum": ("#15803d", "#86efac"),
                }
            )
            self._plot_linhas_comparativo(
                graficos_gerais,
                series_atual,
                ["emp_acum"],
                ["Empates (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução dos empates",
                ylabel="Qtd.",
                color_override={
                    "emp_acum": ("#ca8a04", "#fde047"),
                }
            )
            self._plot_linhas_comparativo(
                graficos_gerais,
                series_atual,
                ["der_acum"],
                ["Derrotas (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução das derrotas",
                ylabel="Qtd.",
                color_override={
                    "der_acum": ("#b91c1c", "#fca5a5"),
                }
            )
        elif not MATPLOTLIB_OK:
            ttk.Label(
                geral_section,
                text="Matplotlib não disponível: os gráficos do comparativo geral estão desativados."
            ).pack(anchor="w", pady=(8, 0))

    def _render_tab_competicao(self, container, competicao, comps_por_ano, ano_atual, ano_anterior):
        jogos_atual = list(comps_por_ano.get(ano_atual, {}).get(competicao, []))
        competicao_anterior = competicao
        comps_ano_anterior = comps_por_ano.get(ano_anterior, {})
        if self._competicao_eh_brasileiro_serie_a_ou_b(competicao):
            competicao_anterior = self._encontrar_competicao_brasileira_para_comparativo(comps_ano_anterior, competicao)
        jogos_anterior = list(comps_ano_anterior.get(competicao_anterior, []))

        if not jogos_atual:
            ttk.Label(
                container,
                text=f"Não há jogos de {competicao} na temporada {ano_atual}."
            ).pack(anchor="w")
            return

        jogos_equivalentes_anterior = jogos_anterior[:len(jogos_atual)]
        stats_atual = self._resumir_jogos(jogos_atual)
        stats_anterior = self._resumir_jogos(jogos_equivalentes_anterior)
        series_atual = self._montar_series_evolucao(jogos_atual)
        series_anterior = self._montar_series_evolucao(jogos_equivalentes_anterior) if jogos_equivalentes_anterior else None

        titulo = ttk.Label(
            container,
            text=f"{competicao} — temporada {ano_atual} vs {ano_anterior}",
            font=("Segoe UI", 12, "bold")
        )
        titulo.pack(anchor="w")
        detalhes = ttk.Label(
            container,
            text=(
                f"Rodada atual registrada: {stats_atual['jogos']} jogo(s) "
                f"| Temporada anterior usada até o jogo {stats_anterior['jogos']}."
            )
        )
        detalhes.pack(anchor="w", pady=(0, 6))
        if competicao_anterior != competicao:
            ttk.Label(
                container,
                text=f"Comparação da temporada anterior usando {competicao_anterior}.",
                foreground="#475569",
            ).pack(anchor="w", pady=(0, 6))
        if len(jogos_anterior) < len(jogos_atual):
            ttk.Label(
                container,
                text="Atenção: a temporada anterior possui menos partidas registradas para esta competição.",
                foreground="#b45309",
                wraplength=900
            ).pack(anchor="w", pady=(0, 6))

        mostra_posicao = self._competicao_usa_posicao(competicao)
        if mostra_posicao:
            posicoes = ttk.Frame(container)
            posicoes.pack(fill="x", pady=(0, 8))
            pos_atual = stats_atual.get("posicao")
            pos_anterior = stats_anterior.get("posicao")
            ttk.Label(
                posicoes,
                text=f"Posição atual: {pos_atual if pos_atual is not None else '—'}"
            ).pack(side="left", padx=(0, 18))
            ttk.Label(
                posicoes,
                text=f"Posição na mesma rodada do ano anterior: {pos_anterior if pos_anterior is not None else '—'}"
            ).pack(side="left")

        metricas_comp = [
            ("Jogos", "jogos"),
            ("Vitórias", "vitorias"),
            ("Empates", "empates"),
            ("Derrotas", "derrotas"),
            ("Gols Pró", "gols_pro"),
            ("Gols Contra", "gols_contra"),
            ("Saldo", "saldo"),
            ("Aproveitamento (%)", "aproveitamento"),
        ]
        if mostra_posicao:
            metricas_comp.insert(1, ("Pontos", "pontos"))
            metricas_comp.append(("Posição", "posicao"))
        self._montar_tabela_comparativo(
            container,
            metricas_comp,
            stats_atual,
            stats_anterior,
            f"{ano_atual}",
            f"{ano_anterior}"
        )

        if MATPLOTLIB_OK and series_atual.get("x"):
            graf_frame = ttk.Frame(container)
            graf_frame.pack(fill="x", pady=(10, 0))
            keys_totais = ["gols_pro_acum", "gols_contra_acum"]
            labels_totais = ["Gols pró (acum.)", "Gols contra (acum.)"]
            if mostra_posicao:
                keys_totais.insert(0, "pontos_acum")
                labels_totais.insert(0, "Pontos (acum.)")
            self._plot_linhas_comparativo(
                graf_frame,
                series_atual,
                keys_totais,
                labels_totais,
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução dos indicadores",
                ylabel="Valores"
            )
            self._plot_linhas_comparativo(
                graf_frame,
                series_atual,
                ["saldo_acum"],
                ["Saldo (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução do saldo",
                ylabel="Saldo"
            )
            self._plot_linhas_comparativo(
                graf_frame,
                series_atual,
                ["vit_acum"],
                ["Vitórias (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução das vitórias",
                ylabel="Qtd.",
                color_override={
                    "vit_acum": ("#15803d", "#86efac"),
                }
            )
            self._plot_linhas_comparativo(
                graf_frame,
                series_atual,
                ["emp_acum"],
                ["Empates (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução dos empates",
                ylabel="Qtd.",
                color_override={
                    "emp_acum": ("#ca8a04", "#fde047"),
                }
            )
            self._plot_linhas_comparativo(
                graf_frame,
                series_atual,
                ["der_acum"],
                ["Derrotas (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução das derrotas",
                ylabel="Qtd.",
                color_override={
                    "der_acum": ("#b91c1c", "#fca5a5"),
                }
            )
            if self._competicao_usa_grafico_posicao(competicao):
                self._plot_linhas_comparativo(
                    graf_frame,
                    series_atual,
                    ["posicao_rodada"],
                    ["Posição na tabela"],
                    ano_atual,
                    ano_anterior,
                    prev_series=series_anterior,
                    titulo="Evolução da posição na tabela",
                    ylabel="Posição",
                    color_override={
                        "posicao_rodada": ("#7c3aed", "#c4b5fd"),
                    },
                    invert_y=True,
                    integer_x_ticks=True,
                )
        elif not MATPLOTLIB_OK:
            ttk.Label(
                container,
                text="Matplotlib não disponível: gráficos da competição desativados."
            ).pack(anchor="w", pady=(8, 0))

    def _agrupar_por_temporada(self, jogos):
        temporadas = defaultdict(list)
        for jogo in jogos:
            data_txt = jogo.get("data")
            if not data_txt:
                continue
            try:
                ano = _parse_data_ptbr(data_txt).year
            except Exception:
                continue
            temporadas[ano].append(jogo)
        for ano in temporadas:
            temporadas[ano].sort(key=lambda j: _parse_data_ptbr(j["data"]))
        return dict(sorted(temporadas.items()))

    def _agrupar_competicoes_por_ano(self, temporadas):
        agrupado = {}
        for ano, jogos in temporadas.items():
            comp_dict = defaultdict(list)
            for jogo in jogos:
                nome = jogo.get("competicao") or "Competição desconhecida"
                comp_dict[nome].append(jogo)
            for nome in comp_dict:
                comp_dict[nome].sort(key=lambda j: _parse_data_ptbr(j["data"]))
            agrupado[ano] = comp_dict
        return agrupado

    def _resumir_jogos(self, jogos):
        stats = {
            "jogos": len(jogos),
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_pro": 0,
            "gols_contra": 0,
            "pontos": 0,
            "saldo": 0,
            "aproveitamento": 0.0,
            "media_gols_pro": 0.0,
            "media_gols_contra": 0.0,
            "posicao": None,
        }
        for jogo in jogos:
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            vasco = placar.get("vasco", 0)
            adv = placar.get("adversario", 0)
            stats["gols_pro"] += vasco
            stats["gols_contra"] += adv
            if vasco > adv:
                stats["vitorias"] += 1
            elif vasco == adv:
                stats["empates"] += 1
            else:
                stats["derrotas"] += 1
        stats["pontos"] = stats["vitorias"] * 3 + stats["empates"]
        stats["saldo"] = stats["gols_pro"] - stats["gols_contra"]
        if stats["jogos"]:
            stats["aproveitamento"] = round((stats["pontos"] / (stats["jogos"] * 3)) * 100, 1)
            stats["media_gols_pro"] = round(stats["gols_pro"] / stats["jogos"], 2)
            stats["media_gols_contra"] = round(stats["gols_contra"] / stats["jogos"], 2)
        stats["posicao"] = self._posicao_mais_recente(jogos)
        return stats

    def _posicao_mais_recente(self, jogos):
        posicao = None
        for jogo in jogos:
            valor = jogo.get("posicao_tabela")
            if valor in (None, ""):
                continue
            try:
                posicao = int(valor)
            except (ValueError, TypeError):
                continue
        return posicao

    def _montar_tabela_comparativo(self, parent, metricas, stats_atual, stats_anterior, cabec_atual, cabec_anterior):
        cols = ("metrica", "anterior", "atual", "diferenca")
        tv = ttk.Treeview(parent, columns=cols, show="headings", height=len(metricas))
        tv.heading("metrica", text="Métrica")
        tv.heading("anterior", text=cabec_anterior)
        tv.heading("atual", text=cabec_atual)
        tv.heading("diferenca", text="Diferença")
        tv.column("metrica", width=220, anchor="w")
        tv.column("anterior", width=160, anchor="center")
        tv.column("atual", width=140, anchor="center")
        tv.column("diferenca", width=120, anchor="center")
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])

        def fmt(valor):
            if valor in (None, ""):
                return "—"
            if isinstance(valor, float):
                texto = f"{valor:.2f}"
                if "." in texto:
                    texto = texto.rstrip("0").rstrip(".")
                return texto
            return str(valor)

        def diff(val_atual, val_anterior):
            if isinstance(val_atual, (int, float)) and isinstance(val_anterior, (int, float)):
                delta = val_atual - val_anterior
                if isinstance(delta, float) and not delta.is_integer():
                    texto = f"{delta:+.2f}".rstrip("0").rstrip(".")
                else:
                    texto = f"{int(delta):+d}"
                return texto
            return "—"

        for i, (titulo, chave) in enumerate(metricas, start=1):
            atual = stats_atual.get(chave)
            anterior = stats_anterior.get(chave)
            tv.insert(
                "",
                "end",
                values=(titulo, fmt(anterior), fmt(atual), diff(atual, anterior)),
                tags=("odd" if i % 2 else "",)
            )
        tv.pack(fill="x", pady=(4, 0))
        return tv

    # --------------------- Técnicos ---------------------
    def _carregar_tecnicos(self):
        for widget in self.frame_tecnicos.winfo_children():
            widget.destroy()
        self._limpar_tecnicos_cell_overlays()

        jogos = carregar_dados_jogos()
        self._tecnicos_jogos = list(jogos)

        stats = defaultdict(_criar_stats_tecnico)

        for tecnico in self.listas.get("tecnicos", []):
            nome = _normalizar_nome_tecnico(tecnico)
            if nome:
                _ = stats[nome]

        for jogo in jogos:
            tecnico = _normalizar_nome_tecnico(jogo.get("tecnico"))
            info = stats[tecnico]
            _acumular_stats_tecnico(info, jogo)

        if not stats:
            ttk.Label(self.frame_tecnicos, text="Nenhum técnico cadastrado.").pack(anchor="w")
            return

        container = ttk.Frame(self.frame_tecnicos)
        container.pack(fill="both", expand=True)
        resumo = ttk.Label(
            container,
            text="Dê dois cliques no nome de um técnico para abrir as passagens separadas por sequências contínuas de jogos.",
            foreground=self.colors["tree_head_fg"],
        )
        resumo.pack(anchor="w", pady=(0, 8))

        tabela_wrap = ttk.Frame(container)
        tabela_wrap.pack(fill="both", expand=True)
        cols = ("tecnico", "jogos", "casa", "fora", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo", "aproveitamento", "artilheiro")
        tv = ttk.Treeview(tabela_wrap, columns=cols, show="headings", height=min(18, max(6, len(stats))))
        headings = {
            "tecnico": "Técnico",
            "jogos": "Jogos",
            "casa": "Casa",
            "fora": "Fora",
            "vitorias": "Vitórias",
            "empates": "Empates",
            "derrotas": "Derrotas",
            "gols_pro": "Gols Pró",
            "gols_contra": "Gols Contra",
            "saldo": "Saldo",
            "aproveitamento": "Aproveitamento",
            "artilheiro": "Maior Goleador",
        }
        widths = {
            "tecnico": 220,
            "jogos": 60,
            "casa": 60,
            "fora": 60,
            "vitorias": 80,
            "empates": 80,
            "derrotas": 80,
            "gols_pro": 90,
            "gols_contra": 100,
            "saldo": 70,
            "aproveitamento": 110,
            "artilheiro": 180,
        }
        for col in cols:
            tv.heading(col, text=headings[col], command=lambda c=col: self._ordenar_coluna_tecnicos(c))
            tv.column(col, width=widths[col], anchor="center" if col != "tecnico" else "w")

        def _on_tecnicos_scroll(*args):
            tv.yview(*args)
            self._agendar_repintura_tecnicos()

        sy = ttk.Scrollbar(tabela_wrap, orient="vertical", command=_on_tecnicos_scroll)
        tv.configure(yscrollcommand=lambda first, last: (sy.set(first, last), self._agendar_repintura_tecnicos()))
        tv.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.tag_configure("tecnico_atual", background="#cfe8ff", foreground="#0b3d91")
        self._tecnicos_colunas_coloridas = {
            "vitorias": {"bg": "#d9f4dd", "fg": "#14532d"},
            "empates": {"bg": "#fff3bf", "fg": "#7a5a00"},
            "derrotas": {"bg": "#ffd9d6", "fg": "#8a1c16"},
            "gols_pro": {"bg": "#c9f7d2", "fg": "#0f5132"},
            "gols_contra": {"bg": "#ffcfcf", "fg": "#7f1d1d"},
            "aproveitamento": {"bg": "#dbeafe", "fg": "#1d4ed8"},
        }
        self._tv_tecnicos = tv
        self._tecnicos_cell_overlays = []
        self._tecnicos_overlay_after = None
        tv.bind("<Configure>", lambda _e: self._agendar_repintura_tecnicos())
        tv.bind("<Double-1>", self._abrir_modal_tecnico_evento)
        self._tecnicos_rows = []
        self._tecnicos_iid_para_nome = {}
        for tecnico, info in stats.items():
            saldo = info["gols_pro"] - info["gols_contra"]
            self._tecnicos_rows.append({
                "tecnico": tecnico,
                "jogos": info["jogos"],
                "casa": info["casa"],
                "fora": info["fora"],
                "vitorias": info["vitorias"],
                "empates": info["empates"],
                "derrotas": info["derrotas"],
                "gols_pro": info["gols_pro"],
                "gols_contra": info["gols_contra"],
                "saldo": saldo,
                "aproveitamento": _calcular_aproveitamento_stats(info),
                "artilheiro": _texto_artilheiro_counter(info["artilheiros"]),
            })

        self._tecnicos_sort_col = "jogos"
        self._tecnicos_sort_reverse = True
        self._render_tecnicos_ordenado()

    def _limpar_tecnicos_cell_overlays(self):
        if getattr(self, "_tecnicos_overlay_after", None):
            try:
                self.root.after_cancel(self._tecnicos_overlay_after)
            except Exception:
                pass
            self._tecnicos_overlay_after = None
        for lbl in getattr(self, "_tecnicos_cell_overlays", []):
            try:
                lbl.destroy()
            except Exception:
                pass
        self._tecnicos_cell_overlays = []

    def _agendar_repintura_tecnicos(self):
        if not getattr(self, "_tv_tecnicos", None):
            return
        if getattr(self, "_tecnicos_overlay_after", None):
            try:
                self.root.after_cancel(self._tecnicos_overlay_after)
            except Exception:
                pass
        self._tecnicos_overlay_after = self.root.after(15, self._repintar_colunas_tecnicos)

    def _repintar_colunas_tecnicos(self):
        self._tecnicos_overlay_after = None
        tv = getattr(self, "_tv_tecnicos", None)
        if not tv or not tv.winfo_exists():
            return
        self._limpar_tecnicos_cell_overlays()

        palette = getattr(self, "_tecnicos_colunas_coloridas", {})
        if not palette:
            return

        for iid in tv.get_children():
            tags = tv.item(iid, "tags") or ()
            if "tecnico_atual" in tags:
                continue
            for coluna, colors in palette.items():
                bbox = tv.bbox(iid, coluna)
                if not bbox:
                    continue
                x, y, w, h = bbox
                if w <= 2 or h <= 2:
                    continue
                txt = tv.set(iid, coluna)
                lbl = tk.Label(
                    tv,
                    text=txt,
                    bg=colors["bg"],
                    fg=colors["fg"],
                    bd=0,
                    padx=0,
                    pady=0,
                    font=("Segoe UI", 9),
                )
                lbl.place(x=x + 1, y=y + 1, width=w - 2, height=h - 2)
                self._tecnicos_cell_overlays.append(lbl)

    def _chave_ordenacao_tecnicos(self, row, coluna):
        if coluna in {"jogos", "casa", "fora", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo"}:
            return int(row.get(coluna, 0))
        if coluna == "aproveitamento":
            return float(row.get(coluna, 0.0))
        return str(row.get(coluna, "")).casefold()

    def _render_tecnicos_ordenado(self):
        if not getattr(self, "_tv_tecnicos", None):
            return
        tv = self._tv_tecnicos
        self._limpar_tecnicos_cell_overlays()
        for iid in tv.get_children():
            tv.delete(iid)
        self._tecnicos_iid_para_nome = {}
        rows = sorted(
            self._tecnicos_rows,
            key=lambda r: (self._chave_ordenacao_tecnicos(r, self._tecnicos_sort_col), str(r.get("tecnico", "")).casefold()),
            reverse=self._tecnicos_sort_reverse
        )
        tecnico_destacado = self._obter_tecnico_destacado()
        iid_selecionado = None
        for i, row in enumerate(rows, start=1):
            tags = ["odd"] if i % 2 else []
            if str(row.get("tecnico", "")).strip().casefold() == tecnico_destacado.casefold():
                tags.append("tecnico_atual")
            iid = tv.insert(
                "",
                "end",
                values=(
                    row["tecnico"],
                    row["jogos"],
                    row["casa"],
                    row["fora"],
                    row["vitorias"],
                    row["empates"],
                    row["derrotas"],
                    row["gols_pro"],
                    row["gols_contra"],
                    row["saldo"],
                    f"{float(row['aproveitamento']):.1f}%",
                    row["artilheiro"],
                ),
                tags=tuple(tags)
            )
            self._tecnicos_iid_para_nome[iid] = row["tecnico"]
            if iid_selecionado is None and str(row.get("tecnico", "")).strip().casefold() == tecnico_destacado.casefold():
                iid_selecionado = iid
        self._agendar_repintura_tecnicos()
        if iid_selecionado is None:
            filhos = tv.get_children()
            iid_selecionado = filhos[0] if filhos else None
        if iid_selecionado:
            tv.selection_set(iid_selecionado)
            tv.focus(iid_selecionado)

    def _ordenar_coluna_tecnicos(self, coluna):
        if not getattr(self, "_tecnicos_rows", None):
            return
        if getattr(self, "_tecnicos_sort_col", None) == coluna:
            self._tecnicos_sort_reverse = not self._tecnicos_sort_reverse
        else:
            self._tecnicos_sort_col = coluna
            self._tecnicos_sort_reverse = False
        self._render_tecnicos_ordenado()

    def _abrir_modal_tecnico_evento(self, _event=None):
        tv = getattr(self, "_tv_tecnicos", None)
        if not tv:
            return
        selecionados = tv.selection()
        if not selecionados:
            foco = tv.focus()
            if foco:
                selecionados = (foco,)
        if not selecionados:
            return
        tecnico = self._tecnicos_iid_para_nome.get(selecionados[0], "")
        if tecnico:
            self._abrir_modal_detalhes_tecnico(tecnico)

    def _ao_selecionar_passagem_tecnico_modal(self, _event=None):
        tv = getattr(self, "_modal_tecnico_passagens_resumo", None)
        if not tv:
            return
        selecionados = tv.selection()
        if not selecionados:
            return
        row = self._modal_tecnico_passagens_iid_map.get(selecionados[0])
        if row:
            self._render_detalhe_passagem_tecnico_modal(row)

    def _abrir_modal_detalhes_tecnico(self, tecnico_nome: str):
        tecnico = _normalizar_nome_tecnico(tecnico_nome)
        self.root.update_idletasks()
        largura = max(900, int(self.root.winfo_width() or 0))
        altura = max(600, int(self.root.winfo_height() or 0))
        pos_x = int(self.root.winfo_rootx() or 0)
        pos_y = int(self.root.winfo_rooty() or 0)
        top = tk.Toplevel(self.root)
        top.title(f"Passagens de {tecnico}")
        top.transient(self.root)
        top.grab_set()
        top.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        frame = ttk.Frame(top, padding=10)
        frame.pack(fill="both", expand=True)
        cabecalho = tk.Frame(frame, bg=self.colors["bg"], highlightthickness=0)
        cabecalho.pack(fill="x", pady=(0, 10))
        titulo_var = tk.StringVar(value=tecnico)
        subtitulo_var = tk.StringVar(value="")
        tk.Label(
            cabecalho,
            textvariable=titulo_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 18, "bold"),
            anchor="center",
            justify="center",
        ).pack(fill="x")
        tk.Label(
            cabecalho,
            textvariable=subtitulo_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            font=("Segoe UI", 10, "bold"),
            anchor="center",
            justify="center",
        ).pack(fill="x", pady=(2, 0))
        resumo_var = tk.StringVar()
        ttk.Label(frame, textvariable=resumo_var, justify="left", wraplength=1220).pack(anchor="w", fill="x", pady=(0, 8))

        resumo_wrap = ttk.Frame(frame)
        resumo_wrap.pack(fill="x", pady=(0, 8))
        cols = ("passagem", "jogos", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo", "aproveitamento", "artilheiro")
        tv = ttk.Treeview(resumo_wrap, columns=cols, show="headings", height=6)
        headings = {
            "passagem": "Passagem",
            "jogos": "Jogos",
            "vitorias": "Vitórias",
            "empates": "Empates",
            "derrotas": "Derrotas",
            "gols_pro": "Gols Pró",
            "gols_contra": "Gols Contra",
            "saldo": "Saldo",
            "aproveitamento": "Aproveitamento",
            "artilheiro": "Artilheiro",
        }
        widths = {
            "passagem": 100,
            "jogos": 90,
            "vitorias": 100,
            "empates": 100,
            "derrotas": 100,
            "gols_pro": 100,
            "gols_contra": 120,
            "saldo": 90,
            "aproveitamento": 120,
            "artilheiro": 220,
        }
        for col in cols:
            tv.heading(col, text=headings[col])
            anchor = "w" if col == "artilheiro" else "center"
            tv.column(col, width=widths[col], anchor=anchor, stretch=True)
        sy_resumo = ttk.Scrollbar(resumo_wrap, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy_resumo.set)
        tv.pack(side="left", fill="x", expand=True)
        sy_resumo.pack(side="right", fill="y")
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.bind("<<TreeviewSelect>>", self._ao_selecionar_passagem_tecnico_modal)

        tabela_wrap = ttk.Frame(frame)
        tabela_wrap.pack(fill="both", expand=True)
        cols_jogos = ("data", "local", "competicao", "adversario", "resultado", "placar")
        tv_jogos = ttk.Treeview(tabela_wrap, columns=cols_jogos, show="headings", height=14)
        larguras = {
            "data": 90,
            "local": 80,
            "competicao": 190,
            "adversario": 170,
            "resultado": 110,
            "placar": 250,
        }
        for col in cols_jogos:
            titulo = col.capitalize() if col != "placar" else "Placar"
            tv_jogos.heading(col, text=titulo)
            tv_jogos.column(col, anchor="w", width=larguras[col], stretch=True)
        sy_jogos = ttk.Scrollbar(tabela_wrap, orient="vertical", command=tv_jogos.yview)
        sx_jogos = ttk.Scrollbar(frame, orient="horizontal", command=tv_jogos.xview)
        tv_jogos.configure(yscrollcommand=sy_jogos.set, xscrollcommand=sx_jogos.set)
        tv_jogos.pack(side="left", fill="both", expand=True)
        sy_jogos.pack(side="right", fill="y")
        sx_jogos.pack(fill="x", pady=(6, 0))
        tv_jogos.tag_configure("odd", background=self.colors["row_alt_bg"])

        self._modal_tecnico_passagens_resumo = tv
        self._modal_tecnico_passagem_jogos = tv_jogos
        self._modal_tecnico_passagens_iid_map = {}

        passagens = _gerar_passagens_tecnico(getattr(self, "_tecnicos_jogos", []), tecnico)
        total_jogos = sum(int(item.get("jogos", 0)) for item in passagens)
        total_vitorias = sum(int(item.get("vitorias", 0)) for item in passagens)
        total_empates = sum(int(item.get("empates", 0)) for item in passagens)
        total_derrotas = sum(int(item.get("derrotas", 0)) for item in passagens)
        subtitulo_var.set(
            f"Jogos: {total_jogos} | Vitórias: {total_vitorias} | "
            f"Empates: {total_empates} | Derrotas: {total_derrotas}"
        )
        resumo_txt = f"{tecnico} sem jogos registrados."
        if passagens:
            resumo_txt = (
                f"{tecnico} teve {len(passagens)} passagem(ns) pelo Vasco, somando {total_jogos} jogo(s). "
                "Selecione uma passagem para ver os jogos."
            )
        resumo_var.set(resumo_txt)

        iid_selecionado = None
        for idx, row in enumerate(passagens, start=1):
            tags = ("odd",) if idx % 2 else ()
            iid = tv.insert(
                "",
                "end",
                values=(
                    row["passagem"],
                    row["jogos"],
                    row["vitorias"],
                    row["empates"],
                    row["derrotas"],
                    row["gols_pro"],
                    row["gols_contra"],
                    row["saldo"],
                    f"{float(row['aproveitamento']):.1f}%",
                    row["artilheiro"],
                ),
                tags=tags,
            )
            self._modal_tecnico_passagens_iid_map[iid] = row
            if iid_selecionado is None:
                iid_selecionado = iid

        if iid_selecionado:
            tv.selection_set(iid_selecionado)
            tv.focus(iid_selecionado)
            self._render_detalhe_passagem_tecnico_modal(self._modal_tecnico_passagens_iid_map[iid_selecionado])

    def _render_detalhe_passagem_tecnico_modal(self, row: dict):
        tv_jogos = getattr(self, "_modal_tecnico_passagem_jogos", None)
        if not tv_jogos:
            return
        for iid in tv_jogos.get_children():
            tv_jogos.delete(iid)

        for idx, jogo in enumerate(row["jogos_lista"], start=1):
            tags = ("odd",) if idx % 2 else ()
            tv_jogos.insert(
                "",
                "end",
                values=(
                    str(jogo.get("data", "")).strip(),
                    str(jogo.get("local", "desconhecido")).capitalize(),
                    str(jogo.get("competicao", "Competição Desconhecida")).strip(),
                    str(jogo.get("adversario", "")).strip(),
                    self._formatar_resultado_com_bolinha(_resultado_jogo_tecnico(jogo)),
                    _placar_jogo_tecnico(jogo),
                ),
                tags=tags,
            )

    # --------------------- Árbitros ---------------------
    def _carregar_arbitros(self):
        for widget in self.frame_arbitros.winfo_children():
            widget.destroy()

        jogos = carregar_dados_jogos()
        container = ttk.Frame(self.frame_arbitros)
        container.pack(fill="both", expand=True)
        ttk.Label(
            container,
            text="Oficiais de arbitragem em jogos do Vasco.",
            foreground=self.colors["tree_head_fg"],
        ).pack(anchor="w", pady=(0, 8))

        filtros = ttk.Frame(container)
        filtros.pack(fill="x", pady=(0, 8))
        ttk.Label(filtros, text="Local:").pack(side="left")
        self._arbitros_local_var = tk.StringVar(value="todos")
        ttk.Radiobutton(filtros, text="Todos", variable=self._arbitros_local_var, value="todos").pack(side="left", padx=(8, 6))
        ttk.Radiobutton(filtros, text="Casa", variable=self._arbitros_local_var, value="casa").pack(side="left", padx=6)
        ttk.Radiobutton(filtros, text="Fora", variable=self._arbitros_local_var, value="fora").pack(side="left", padx=6)
        ttk.Label(filtros, text="Ano:").pack(side="left", padx=(14, 0))
        anos_disponiveis = sorted({
            str(j.get("data", "")).strip()[-4:]
            for j in jogos
            if str(j.get("data", "")).strip()[-4:].isdigit()
        })
        self._arbitros_ano_var = tk.StringVar(value="Todos")
        combo_ano = ttk.Combobox(
            filtros,
            textvariable=self._arbitros_ano_var,
            values=["Todos"] + anos_disponiveis,
            state="readonly",
            width=10,
        )
        combo_ano.pack(side="left", padx=(8, 0))

        self._arbitragem_tvs = {}
        self._arbitragem_headings = {}
        self._arbitragem_iid_maps = {}
        self._arbitragem_total_vars = {}
        self._arbitragem_rows = {}
        self._arbitragem_sort_cols = {}
        self._arbitragem_sort_reverse = {}
        self._arbitros_jogos = list(jogos)

        abas = ttk.Notebook(container)
        abas.pack(fill="both", expand=True)
        for papel, spec in self._arbitragem_papeis().items():
            self._criar_subaba_arbitragem(abas, papel, spec)
        self._criar_subaba_combinacoes_arbitragem(abas)

        self._arbitros_local_var.trace_add("write", lambda *_: self._aplicar_filtros_arbitros())
        self._arbitros_ano_var.trace_add("write", lambda *_: self._aplicar_filtros_arbitros())
        self._aplicar_filtros_arbitros()

    def _arbitragem_papeis(self):
        return {
            "arbitro": {
                "aba": "Árbitros",
                "coluna_nome": "Árbitro",
                "total": "árbitros listados",
                "descricao": "árbitro principal",
            },
            "auxiliar": {
                "aba": "Auxiliares",
                "coluna_nome": "Auxiliar",
                "total": "auxiliares listados",
                "descricao": "auxiliar",
            },
            "var": {
                "aba": "VARs",
                "coluna_nome": "VAR",
                "total": "VARs listados",
                "descricao": "VAR",
            },
        }

    def _criar_subaba_arbitragem(self, notebook, papel, spec):
        frame = ttk.Frame(notebook, padding=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        notebook.add(frame, text=spec["aba"])

        ttk.Label(
            frame,
            text=f"Lista de {spec['total']} em jogos do Vasco.",
            foreground=self.colors["tree_head_fg"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        total_var = tk.StringVar(value=f"Total de {spec['total']}: 0")
        ttk.Label(frame, textvariable=total_var, foreground=self.colors["tree_head_fg"]).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 8),
        )

        tabela_wrap = ttk.Frame(frame)
        tabela_wrap.grid(row=2, column=0, sticky="nsew")
        tabela_wrap.columnconfigure(0, weight=1)
        tabela_wrap.rowconfigure(0, weight=1)

        cols = (
            "nome",
            "jogos",
            "primeiro_jogo",
            "ultimo_jogo",
            "vitorias",
            "empates",
            "derrotas",
            "gols_pro",
            "gols_contra",
            "saldo",
        )
        headings = {
            "nome": spec["coluna_nome"],
            "jogos": "Jogos",
            "primeiro_jogo": "Primeiro Jogo",
            "ultimo_jogo": "Último Jogo",
            "vitorias": "Vitórias",
            "empates": "Empates",
            "derrotas": "Derrotas",
            "gols_pro": "Gols Feitos",
            "gols_contra": "Gols Tomados",
            "saldo": "Saldo",
        }
        widths = {
            "nome": 220,
            "jogos": 60,
            "primeiro_jogo": 260,
            "ultimo_jogo": 260,
            "vitorias": 80,
            "empates": 80,
            "derrotas": 80,
            "gols_pro": 100,
            "gols_contra": 110,
            "saldo": 70,
        }
        tv = ttk.Treeview(tabela_wrap, columns=cols, show="headings", height=12)
        for col in cols:
            tv.heading(col, text=headings[col], command=lambda c=col, p=papel: self._ordenar_coluna_arbitragem(p, c))
            tv.column(col, width=widths[col], anchor="center" if col != "nome" else "w", stretch=True)

        sy = ttk.Scrollbar(tabela_wrap, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tv.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.bind("<Double-1>", lambda event, p=papel: self._abrir_modal_arbitragem_evento(event, p))

        self._arbitragem_tvs[papel] = tv
        self._arbitragem_headings[papel] = headings
        self._arbitragem_iid_maps[papel] = {}
        self._arbitragem_total_vars[papel] = total_var
        self._arbitragem_rows[papel] = []
        self._arbitragem_sort_cols[papel] = "jogos"
        self._arbitragem_sort_reverse[papel] = True

    def _criar_subaba_combinacoes_arbitragem(self, notebook):
        frame = ttk.Frame(notebook, padding=8)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        notebook.add(frame, text="Combinações")

        ttk.Label(
            frame,
            text="Combinações de árbitro, auxiliares e VAR em jogos do Vasco.",
            foreground=self.colors["tree_head_fg"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self._arbitragem_combinacoes_total_var = tk.StringVar(value="Total de combinações listadas: 0")
        ttk.Label(
            frame,
            textvariable=self._arbitragem_combinacoes_total_var,
            foreground=self.colors["tree_head_fg"],
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        tabela_wrap = ttk.Frame(frame)
        tabela_wrap.grid(row=2, column=0, sticky="nsew")
        tabela_wrap.columnconfigure(0, weight=1)
        tabela_wrap.rowconfigure(0, weight=1)

        cols = (
            "arbitro",
            "auxiliares",
            "var",
            "jogos",
            "primeiro_jogo",
            "ultimo_jogo",
            "vitorias",
            "empates",
            "derrotas",
            "gols_pro",
            "gols_contra",
            "saldo",
        )
        headings = {
            "arbitro": "Árbitro",
            "auxiliares": "Auxiliares",
            "var": "VAR",
            "jogos": "Jogos",
            "primeiro_jogo": "Primeiro Jogo",
            "ultimo_jogo": "Último Jogo",
            "vitorias": "Vitórias",
            "empates": "Empates",
            "derrotas": "Derrotas",
            "gols_pro": "Gols Feitos",
            "gols_contra": "Gols Tomados",
            "saldo": "Saldo",
        }
        widths = {
            "arbitro": 190,
            "auxiliares": 300,
            "var": 180,
            "jogos": 60,
            "primeiro_jogo": 230,
            "ultimo_jogo": 230,
            "vitorias": 80,
            "empates": 80,
            "derrotas": 80,
            "gols_pro": 100,
            "gols_contra": 110,
            "saldo": 70,
        }
        tv = ttk.Treeview(tabela_wrap, columns=cols, show="headings", height=12)
        for col in cols:
            tv.heading(col, text=headings[col], command=lambda c=col: self._ordenar_coluna_combinacoes_arbitragem(c))
            tv.column(
                col,
                width=widths[col],
                anchor="center" if col not in {"arbitro", "auxiliares", "var", "primeiro_jogo", "ultimo_jogo"} else "w",
                stretch=True,
            )

        sy = ttk.Scrollbar(tabela_wrap, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        tv.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.bind("<Double-1>", self._abrir_modal_combinacao_arbitragem_evento)

        paginacao = ttk.Frame(frame)
        paginacao.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        paginacao.columnconfigure(1, weight=1)
        self._arbitragem_combinacoes_pagina_anterior_btn = ttk.Button(
            paginacao,
            text="Anterior",
            command=lambda: self._mudar_pagina_combinacoes_arbitragem(-1),
        )
        self._arbitragem_combinacoes_pagina_anterior_btn.grid(row=0, column=0, sticky="w")
        self._arbitragem_combinacoes_paginacao_var = tk.StringVar(value="Linhas 0-0 de 0  |  Página 1/1")
        ttk.Label(
            paginacao,
            textvariable=self._arbitragem_combinacoes_paginacao_var,
            foreground=self.colors["tree_head_fg"],
        ).grid(row=0, column=1, padx=10)
        self._arbitragem_combinacoes_pagina_proxima_btn = ttk.Button(
            paginacao,
            text="Próxima",
            command=lambda: self._mudar_pagina_combinacoes_arbitragem(1),
        )
        self._arbitragem_combinacoes_pagina_proxima_btn.grid(row=0, column=2, sticky="e")

        self._tv_arbitragem_combinacoes = tv
        self._arbitragem_combinacoes_headings = headings
        self._arbitragem_combinacoes_rows = []
        self._arbitragem_combinacoes_iid_map = {}
        self._arbitragem_combinacoes_sort_col = "jogos"
        self._arbitragem_combinacoes_sort_reverse = True
        self._arbitragem_combinacoes_page = 0
        self._arbitragem_combinacoes_page_size = 50

    def _aplicar_filtros_arbitros(self):
        jogos = list(getattr(self, "_arbitros_jogos", []))
        local_sel = str(getattr(self, "_arbitros_local_var", tk.StringVar(value="todos")).get() or "todos").strip().casefold()
        ano_sel = str(getattr(self, "_arbitros_ano_var", tk.StringVar(value="Todos")).get() or "Todos").strip()

        if local_sel in {"casa", "fora"}:
            jogos = [j for j in jogos if str(j.get("local", "")).strip().casefold() == local_sel]
        if ano_sel and ano_sel != "Todos":
            jogos = [j for j in jogos if str(j.get("data", "")).strip().endswith(ano_sel)]

        for papel, spec in self._arbitragem_papeis().items():
            self._arbitragem_rows[papel] = self._montar_rows_arbitragem(jogos, papel)
            total_var = self._arbitragem_total_vars.get(papel)
            if total_var is not None:
                total_var.set(f"Total de {spec['total']}: {len(self._arbitragem_rows[papel])}")
            self._render_arbitragem_ordenado(papel)

        self._arbitragem_combinacoes_rows = self._montar_rows_combinacoes_arbitragem(jogos)
        self._arbitragem_combinacoes_page = 0
        if hasattr(self, "_arbitragem_combinacoes_total_var"):
            self._arbitragem_combinacoes_total_var.set(
                f"Total de combinações listadas: {len(self._arbitragem_combinacoes_rows)}"
            )
        self._render_combinacoes_arbitragem_ordenado()

    def _nomes_arbitragem_por_papel(self, arbitragem: dict, papel: str) -> list:
        if papel == "arbitro":
            nomes = [arbitragem.get("arbitro", "")]
        elif papel == "auxiliar":
            nomes = arbitragem.get("auxiliares", [])
            if not isinstance(nomes, list):
                nomes = []
        elif papel == "var":
            nomes = [arbitragem.get("var", "")]
        else:
            nomes = []

        normalizados = []
        vistos = set()
        for nome in nomes:
            nome_limpo = _normalizar_nome_arbitragem(nome)
            chave = _chave_nome_arbitragem(nome_limpo)
            if not chave or chave in vistos:
                continue
            vistos.add(chave)
            normalizados.append(nome_limpo)
        return normalizados

    def _montar_rows_arbitragem(self, jogos, papel: str) -> list:
        stats = defaultdict(_criar_stats_arbitro)
        for jogo in jogos:
            arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
            for nome in self._nomes_arbitragem_por_papel(arbitragem, papel):
                _acumular_stats_arbitro(stats[nome], jogo)

        rows = []
        for nome, info in stats.items():
            rows.append({
                "nome": nome,
                "jogos": info["jogos"],
                "primeiro_jogo": info["primeiro_jogo_txt"],
                "ultimo_jogo": info["ultimo_jogo_txt"],
                "primeiro_jogo_data": info["primeiro_jogo_data"],
                "ultimo_jogo_data": info["ultimo_jogo_data"],
                "vitorias": info["vitorias"],
                "empates": info["empates"],
                "derrotas": info["derrotas"],
                "gols_pro": info["gols_pro"],
                "gols_contra": info["gols_contra"],
                "saldo": info["gols_pro"] - info["gols_contra"],
            })
        return rows

    def _chave_combinacao_arbitragem(self, arbitragem: dict):
        arbitragem = _normalizar_arbitragem(arbitragem)
        arbitro = _normalizar_nome_arbitragem(arbitragem.get("arbitro", ""))
        auxiliares = tuple(self._nomes_arbitragem_por_papel(arbitragem, "auxiliar"))
        var = _normalizar_nome_arbitragem(arbitragem.get("var", ""))
        if not arbitro and not auxiliares and not var:
            return None
        return (arbitro, auxiliares, var)

    def _montar_rows_combinacoes_arbitragem(self, jogos) -> list:
        stats = {}
        for jogo in jogos:
            chave = self._chave_combinacao_arbitragem(jogo.get("arbitragem", {}))
            if not chave:
                continue
            if chave not in stats:
                stats[chave] = _criar_stats_arbitro()
            _acumular_stats_arbitro(stats[chave], jogo)

        rows = []
        for chave, info in stats.items():
            arbitro, auxiliares, var = chave
            rows.append({
                "chave": chave,
                "arbitro": arbitro,
                "auxiliares": list(auxiliares),
                "auxiliares_txt": self._texto_detalhe_partida(auxiliares),
                "var": var,
                "jogos": info["jogos"],
                "primeiro_jogo": info["primeiro_jogo_txt"],
                "ultimo_jogo": info["ultimo_jogo_txt"],
                "primeiro_jogo_data": info["primeiro_jogo_data"],
                "ultimo_jogo_data": info["ultimo_jogo_data"],
                "vitorias": info["vitorias"],
                "empates": info["empates"],
                "derrotas": info["derrotas"],
                "gols_pro": info["gols_pro"],
                "gols_contra": info["gols_contra"],
                "saldo": info["gols_pro"] - info["gols_contra"],
            })
        return rows

    def _chave_ordenacao_arbitros(self, row, coluna):
        if coluna in {"jogos", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo"}:
            return int(row.get(coluna, 0))
        if coluna == "primeiro_jogo":
            return row.get("primeiro_jogo_data") or datetime.min
        if coluna == "ultimo_jogo":
            return row.get("ultimo_jogo_data") or datetime.min
        return str(row.get(coluna, "")).casefold()

    def _chave_ordenacao_combinacoes_arbitragem(self, row, coluna):
        if coluna == "auxiliares":
            return str(row.get("auxiliares_txt", "")).casefold()
        if coluna in {"arbitro", "var"}:
            return str(row.get(coluna, "")).casefold()
        return self._chave_ordenacao_arbitros(row, coluna)

    def _render_arbitragem_ordenado(self, papel: str):
        tv = getattr(self, "_arbitragem_tvs", {}).get(papel)
        if not tv:
            return
        headings = getattr(self, "_arbitragem_headings", {}).get(papel, {})
        sort_col = getattr(self, "_arbitragem_sort_cols", {}).get(papel, "jogos")
        reverse = bool(getattr(self, "_arbitragem_sort_reverse", {}).get(papel, False))
        for col, titulo in headings.items():
            indicador = ""
            if col == sort_col:
                indicador = " ▼" if reverse else " ▲"
            tv.heading(col, text=f"{titulo}{indicador}", command=lambda c=col, p=papel: self._ordenar_coluna_arbitragem(p, c))
        for iid in tv.get_children():
            tv.delete(iid)
        self._arbitragem_iid_maps[papel] = {}

        rows = sorted(
            self._arbitragem_rows.get(papel, []),
            key=lambda r: (self._chave_ordenacao_arbitros(r, sort_col), str(r.get("nome", "")).casefold()),
            reverse=reverse,
        )
        for idx, row in enumerate(rows, start=1):
            tags = ("odd",) if idx % 2 else ()
            iid = tv.insert(
                "",
                "end",
                values=(
                    row["nome"],
                    row["jogos"],
                    row["primeiro_jogo"],
                    row["ultimo_jogo"],
                    row["vitorias"],
                    row["empates"],
                    row["derrotas"],
                    row["gols_pro"],
                    row["gols_contra"],
                    row["saldo"],
                ),
                tags=tags,
            )
            self._arbitragem_iid_maps[papel][iid] = row

    def _ordenar_coluna_arbitragem(self, papel: str, coluna: str):
        if not getattr(self, "_arbitragem_rows", {}).get(papel):
            return
        if self._arbitragem_sort_cols.get(papel) == coluna:
            self._arbitragem_sort_reverse[papel] = not self._arbitragem_sort_reverse.get(papel, False)
        else:
            self._arbitragem_sort_cols[papel] = coluna
            self._arbitragem_sort_reverse[papel] = False
        self._render_arbitragem_ordenado(papel)

    def _render_combinacoes_arbitragem_ordenado(self):
        tv = getattr(self, "_tv_arbitragem_combinacoes", None)
        if not tv:
            return
        headings = getattr(self, "_arbitragem_combinacoes_headings", {})
        sort_col = getattr(self, "_arbitragem_combinacoes_sort_col", "jogos")
        reverse = bool(getattr(self, "_arbitragem_combinacoes_sort_reverse", False))
        for col, titulo in headings.items():
            indicador = ""
            if col == sort_col:
                indicador = " ▼" if reverse else " ▲"
            tv.heading(col, text=f"{titulo}{indicador}", command=lambda c=col: self._ordenar_coluna_combinacoes_arbitragem(c))
        for iid in tv.get_children():
            tv.delete(iid)
        self._arbitragem_combinacoes_iid_map = {}

        rows = sorted(
            getattr(self, "_arbitragem_combinacoes_rows", []),
            key=lambda r: (
                self._chave_ordenacao_combinacoes_arbitragem(r, sort_col),
                str(r.get("arbitro", "")).casefold(),
                str(r.get("auxiliares_txt", "")).casefold(),
                str(r.get("var", "")).casefold(),
            ),
            reverse=reverse,
        )
        total = len(rows)
        page_size = max(1, int(getattr(self, "_arbitragem_combinacoes_page_size", 50)))
        total_pages = max(1, (total + page_size - 1) // page_size)
        page_idx = int(getattr(self, "_arbitragem_combinacoes_page", 0))
        page_idx = max(0, min(page_idx, total_pages - 1))
        self._arbitragem_combinacoes_page = page_idx
        ini = page_idx * page_size
        fim = min(ini + page_size, total)
        rows_pagina = rows[ini:fim]

        self._atualizar_paginacao_combinacoes_arbitragem(total, ini, fim, page_idx, total_pages)

        for idx, row in enumerate(rows_pagina, start=1):
            tags = ("odd",) if idx % 2 else ()
            iid = tv.insert(
                "",
                "end",
                values=(
                    self._texto_detalhe_partida(row.get("arbitro", "")),
                    row.get("auxiliares_txt", "—"),
                    self._texto_detalhe_partida(row.get("var", "")),
                    row["jogos"],
                    row["primeiro_jogo"],
                    row["ultimo_jogo"],
                    row["vitorias"],
                    row["empates"],
                    row["derrotas"],
                    row["gols_pro"],
                    row["gols_contra"],
                    row["saldo"],
                ),
                tags=tags,
            )
            self._arbitragem_combinacoes_iid_map[iid] = row

    def _atualizar_paginacao_combinacoes_arbitragem(self, total: int, ini: int, fim: int, page_idx: int, total_pages: int):
        info_var = getattr(self, "_arbitragem_combinacoes_paginacao_var", None)
        if info_var is not None:
            if total:
                info_var.set(f"Linhas {ini + 1}-{fim} de {total}  |  Página {page_idx + 1}/{total_pages}")
            else:
                info_var.set("Linhas 0-0 de 0  |  Página 1/1")

        anterior = getattr(self, "_arbitragem_combinacoes_pagina_anterior_btn", None)
        if anterior is not None:
            anterior.configure(state=("normal" if page_idx > 0 else "disabled"))

        proxima = getattr(self, "_arbitragem_combinacoes_pagina_proxima_btn", None)
        if proxima is not None:
            proxima.configure(state=("normal" if page_idx < total_pages - 1 else "disabled"))

    def _mudar_pagina_combinacoes_arbitragem(self, delta: int):
        total = len(getattr(self, "_arbitragem_combinacoes_rows", []))
        page_size = max(1, int(getattr(self, "_arbitragem_combinacoes_page_size", 50)))
        total_pages = max(1, (total + page_size - 1) // page_size)
        page_idx = int(getattr(self, "_arbitragem_combinacoes_page", 0))
        novo_idx = max(0, min(total_pages - 1, page_idx + int(delta)))
        if novo_idx == page_idx:
            return
        self._arbitragem_combinacoes_page = novo_idx
        self._render_combinacoes_arbitragem_ordenado()

    def _ordenar_coluna_combinacoes_arbitragem(self, coluna: str):
        if not getattr(self, "_arbitragem_combinacoes_rows", None):
            return
        if getattr(self, "_arbitragem_combinacoes_sort_col", None) == coluna:
            self._arbitragem_combinacoes_sort_reverse = not bool(getattr(self, "_arbitragem_combinacoes_sort_reverse", False))
        else:
            self._arbitragem_combinacoes_sort_col = coluna
            self._arbitragem_combinacoes_sort_reverse = False
        self._arbitragem_combinacoes_page = 0
        self._render_combinacoes_arbitragem_ordenado()

    def _partidas_da_arbitragem(self, nome_oficial: str, papel: str) -> list:
        alvo = _chave_nome_arbitragem(nome_oficial)
        if not alvo:
            return []
        jogos = list(getattr(self, "_arbitros_jogos", [])) or carregar_dados_jogos()
        partidas = []
        for idx, jogo in enumerate(jogos):
            arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
            chaves_papel = {_chave_nome_arbitragem(nome) for nome in self._nomes_arbitragem_por_papel(arbitragem, papel)}
            if alvo not in chaves_papel:
                continue
            data_ord = _parse_data_ptbr_safe(str(jogo.get("data", "")).strip()) or datetime.min
            partidas.append((idx, jogo, data_ord))
        return sorted(
            partidas,
            key=lambda item: (item[2], str(item[1].get("adversario", "")).casefold()),
            reverse=True,
        )

    def _partidas_da_combinacao_arbitragem(self, chave) -> list:
        if not chave:
            return []
        jogos = list(getattr(self, "_arbitros_jogos", [])) or carregar_dados_jogos()
        partidas = []
        for idx, jogo in enumerate(jogos):
            chave_jogo = self._chave_combinacao_arbitragem(jogo.get("arbitragem", {}))
            if chave_jogo != chave:
                continue
            data_ord = _parse_data_ptbr_safe(str(jogo.get("data", "")).strip()) or datetime.min
            partidas.append((idx, jogo, data_ord))
        return sorted(
            partidas,
            key=lambda item: (item[2], str(item[1].get("adversario", "")).casefold()),
            reverse=True,
        )

    def _abrir_modal_arbitragem_evento(self, event=None, papel: str = "arbitro"):
        tv = event.widget if event is not None else getattr(self, "_arbitragem_tvs", {}).get(papel)
        if not tv:
            return
        iid = tv.identify_row(event.y) if event is not None else (tv.selection()[0] if tv.selection() else "")
        if not iid:
            return
        tv.selection_set(iid)
        tv.focus(iid)
        row = getattr(self, "_arbitragem_iid_maps", {}).get(papel, {}).get(iid)
        if not row:
            values = tv.item(iid, "values")
            row = {"nome": values[0] if values else ""}
        self._abrir_modal_detalhes_arbitragem(row.get("nome", ""), papel)

    def _abrir_modal_combinacao_arbitragem_evento(self, event=None):
        tv = event.widget if event is not None else getattr(self, "_tv_arbitragem_combinacoes", None)
        if not tv:
            return
        iid = tv.identify_row(event.y) if event is not None else (tv.selection()[0] if tv.selection() else "")
        if not iid:
            return
        tv.selection_set(iid)
        tv.focus(iid)
        row = getattr(self, "_arbitragem_combinacoes_iid_map", {}).get(iid)
        if not row:
            return
        self._abrir_modal_detalhes_combinacao_arbitragem(row)

    def _abrir_modal_detalhes_combinacao_arbitragem(self, row: dict):
        chave = row.get("chave")
        partidas = self._partidas_da_combinacao_arbitragem(chave)
        if not partidas:
            messagebox.showinfo("Combinação", "Não há partidas registradas para esta combinação.")
            return

        titulo = "Combinação de arbitragem"
        detalhes = (
            f"Árbitro: {self._texto_detalhe_partida(row.get('arbitro', ''))} | "
            f"Auxiliares: {row.get('auxiliares_txt', '—')} | "
            f"VAR: {self._texto_detalhe_partida(row.get('var', ''))}"
        )
        self._abrir_modal_lista_jogos_arbitragem(titulo, detalhes, partidas)

    def _abrir_modal_detalhes_arbitragem(self, nome_oficial: str, papel: str):
        specs = self._arbitragem_papeis()
        spec = specs.get(papel, specs["arbitro"])
        nome = _normalizar_nome_arbitragem(nome_oficial)
        partidas = self._partidas_da_arbitragem(nome, papel)
        if not nome or not partidas:
            messagebox.showinfo(spec["coluna_nome"], f"Não há partidas registradas para este {spec['descricao']}.")
            return

        stats = _criar_stats_arbitro()
        for _idx, jogo, _data_ord in partidas:
            _acumular_stats_arbitro(stats, jogo)
        aproveitamento = _calcular_aproveitamento_stats(stats)

        titulo = f"Jogos de {nome} como {spec['descricao']}"
        detalhes = (
            f"{stats['jogos']} jogos | V/E/D {stats['vitorias']}/{stats['empates']}/{stats['derrotas']} | "
            f"Gols {stats['gols_pro']} x {stats['gols_contra']} | Aproveitamento {aproveitamento:.1f}%"
        )
        self._abrir_modal_lista_jogos_arbitragem(titulo, detalhes, partidas)

    def _abrir_modal_lista_jogos_arbitragem(self, titulo: str, subtitulo: str, partidas: list):
        if not partidas:
            messagebox.showinfo("Arbitragem", "Não há partidas registradas para este recorte.")
            return

        top = tk.Toplevel(self.root)
        top.title(titulo)
        top.transient(self.root)
        top.lift()
        top.focus_force()
        top.minsize(1280, 640)
        top.configure(bg=self.colors["bg"])

        container = ttk.Frame(top, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        ttk.Label(
            container,
            text=titulo,
            font=("Segoe UI", 15, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            container,
            text=subtitulo,
            foreground=self.colors["tree_head_fg"],
        ).grid(row=1, column=0, sticky="w", pady=(4, 10))

        tabela_wrap = ttk.Frame(container)
        tabela_wrap.grid(row=2, column=0, sticky="nsew")
        tabela_wrap.columnconfigure(0, weight=1)
        tabela_wrap.rowconfigure(0, weight=1)

        cols = (
            "data",
            "local",
            "competicao",
            "adversario",
            "resultado",
            "placar",
            "arbitro",
            "auxiliares",
            "var",
            "estadio",
            "horario",
            "tecnico",
        )
        headings = {
            "data": "Data",
            "local": "Local",
            "competicao": "Competição",
            "adversario": "Adversário",
            "resultado": "Resultado",
            "placar": "Placar",
            "arbitro": "Árbitro",
            "auxiliares": "Auxiliares",
            "var": "VAR",
            "estadio": "Estádio",
            "horario": "Horário",
            "tecnico": "Técnico",
        }
        widths = {
            "data": 90,
            "local": 70,
            "competicao": 170,
            "adversario": 160,
            "resultado": 110,
            "placar": 230,
            "arbitro": 190,
            "auxiliares": 300,
            "var": 190,
            "estadio": 170,
            "horario": 80,
            "tecnico": 160,
        }
        tv = ttk.Treeview(tabela_wrap, columns=cols, show="headings", height=18, selectmode="extended")
        for col in cols:
            tv.heading(col, text=headings[col])
            tv.column(col, width=widths[col], anchor="w", stretch=True)
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        tv.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(tabela_wrap, orient="vertical", command=tv.yview)
        sx = ttk.Scrollbar(container, orient="horizontal", command=tv.xview)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        item_to_idx = {}
        for i, (idx_global, jogo, _data_ord) in enumerate(partidas, start=1):
            arbitragem = _normalizar_arbitragem(jogo.get("arbitragem", {}))
            local_raw = str(jogo.get("local", "") or "").strip().casefold()
            local_txt = "Fora" if local_raw == "fora" else "Casa"
            iid = tv.insert(
                "",
                "end",
                values=(
                    str(jogo.get("data", "")).strip(),
                    local_txt,
                    str(jogo.get("competicao", "")).strip() or "—",
                    str(jogo.get("adversario", "")).strip() or "—",
                    self._formatar_resultado_com_bolinha(self._resultado_detalhe_partida(jogo)),
                    self._placar_detalhe_partida(jogo),
                    self._texto_detalhe_partida(arbitragem.get("arbitro", "")),
                    self._texto_detalhe_partida(arbitragem.get("auxiliares", [])),
                    self._texto_detalhe_partida(arbitragem.get("var", "")),
                    str(jogo.get("estadio", "")).strip() or "—",
                    str(jogo.get("horario", "")).strip() or "—",
                    str(jogo.get("tecnico", "")).strip() or "—",
                ),
                tags=("odd",) if i % 2 else (),
            )
            item_to_idx[iid] = idx_global

        tv._item_to_idx = item_to_idx
        tv.bind("<Double-1>", self._on_tree_double_click)
        tv.bind("<Button-3>", self._abrir_menu_contexto_temporadas)
        tv.bind("<Control-Button-1>", self._abrir_menu_contexto_temporadas)

        botoes = ttk.Frame(container)
        botoes.grid(row=4, column=0, sticky="e", pady=(10, 0))
        ttk.Button(botoes, text="Fechar", command=top.destroy).pack(side="left")

        top.update_idletasks()
        self._centralizar_modal_no_app(top)

    # --------------------- Títulos ---------------------
    def _carregar_titulos(self):
        for widget in self.frame_titulos.winfo_children():
            widget.destroy()

        jogos = carregar_dados_jogos()
        if not jogos:
            ttk.Label(self.frame_titulos, text="Ainda não há jogos registrados.").pack(anchor="w")
            return

        nb = ttk.Notebook(self.frame_titulos)
        nb.pack(fill="both", expand=True)

        tab_campanhas = ttk.Frame(nb, padding=8)
        tab_gerenciar = ttk.Frame(nb, padding=8)
        nb.add(tab_campanhas, text="Titulos")
        nb.add(tab_gerenciar, text="Gerenciar Títulos")

        self._render_tab_campanhas_titulos(tab_campanhas, jogos)
        self._render_tab_gerenciar_titulos(tab_gerenciar)

    def _render_tab_campanhas_titulos(self, parent, jogos):
        ttk.Label(
            parent,
            text="Números das campanhas campeãs: vitórias, empates, derrotas e artilheiro do Vasco.",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)

        cols = ("campeonato", "ano", "vitorias", "empates", "derrotas", "artilheiro")
        tv = ttk.Treeview(wrap, columns=cols, show="headings", height=min(16, max(8, len(self.titulos_vasco))))
        tv.heading("campeonato", text="Campeonato")
        tv.heading("ano", text="Ano")
        tv.heading("vitorias", text="Vitórias")
        tv.heading("empates", text="Empates")
        tv.heading("derrotas", text="Derrotas")
        tv.heading("artilheiro", text="Artilheiro do Vasco")
        tv.column("campeonato", width=320, anchor="w")
        tv.column("ano", width=90, anchor="center")
        tv.column("vitorias", width=90, anchor="center")
        tv.column("empates", width=90, anchor="center")
        tv.column("derrotas", width=90, anchor="center")
        tv.column("artilheiro", width=280, anchor="w")
        tv.tag_configure("odd", background=self.colors["row_alt_bg"])

        campanhas = []
        for item in self.titulos_vasco:
            campanhas.append(self._resumir_campanha_titulo(jogos, item["campeonato"], item["ano"]))
        campanhas.sort(key=lambda x: (x["ano"], x["campeonato"].casefold()))

        for i, info in enumerate(campanhas, start=1):
            tv.insert(
                "",
                "end",
                values=(
                    info["campeonato"],
                    info["ano"],
                    info["vitorias"],
                    info["empates"],
                    info["derrotas"],
                    info["artilheiro"],
                ),
                tags=("odd",) if i % 2 else ()
            )

        sy = ttk.Scrollbar(wrap, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        tv.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

    def _render_tab_gerenciar_titulos(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        form = ttk.Labelframe(parent, text="Cadastrar / Editar título", padding=10)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        form.columnconfigure(1, weight=1)

        self.titulo_campeonato_var = tk.StringVar()
        self.titulo_ano_var = tk.StringVar()
        competicoes_historicas = self._listar_competicoes_historicas()

        ttk.Label(form, text="Campeonato:").grid(row=0, column=0, sticky="w")
        self.entry_titulo_campeonato = ttk.Combobox(
            form,
            textvariable=self.titulo_campeonato_var,
            values=competicoes_historicas,
        )
        self.entry_titulo_campeonato.grid(row=0, column=1, sticky="ew", padx=(6, 10))
        self._forcar_cursor_visivel(self.entry_titulo_campeonato)

        ttk.Label(form, text="Ano:").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.titulo_ano_var, width=10).grid(row=0, column=3, sticky="w", padx=(6, 0))

        botoes = ttk.Frame(form)
        botoes.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        ttk.Button(botoes, text="Cadastrar", command=self._cadastrar_titulo_vasco).pack(side="left")
        ttk.Button(botoes, text="Salvar Edição", command=self._editar_titulo_vasco).pack(side="left", padx=(8, 0))
        ttk.Button(botoes, text="Excluir Selecionado", command=self._excluir_titulo_vasco).pack(side="left", padx=(8, 0))
        ttk.Button(botoes, text="Limpar", command=self._limpar_form_titulo_vasco).pack(side="left", padx=(8, 0))

        table_wrap = ttk.Frame(parent)
        table_wrap.grid(row=1, column=0, sticky="nsew")
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)

        cols = ("campeonato", "ano")
        self.tv_titulos_gerenciar = ttk.Treeview(
            table_wrap,
            columns=cols,
            show="headings",
            height=min(16, max(8, len(self.titulos_vasco))),
        )
        self.tv_titulos_gerenciar.heading("campeonato", text="Campeonato")
        self.tv_titulos_gerenciar.heading("ano", text="Ano")
        self.tv_titulos_gerenciar.column("campeonato", width=420, anchor="w")
        self.tv_titulos_gerenciar.column("ano", width=110, anchor="center")
        self.tv_titulos_gerenciar.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_titulos_gerenciar.grid(row=0, column=0, sticky="nsew")
        self.tv_titulos_gerenciar.bind("<<TreeviewSelect>>", self._on_select_titulo_vasco)

        sy = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tv_titulos_gerenciar.yview)
        sy.grid(row=0, column=1, sticky="ns")
        self.tv_titulos_gerenciar.configure(yscrollcommand=sy.set)
        self._render_tabela_titulos_gerenciar()

    def _listar_competicoes_historicas(self):
        competicoes = set()
        for jogo in carregar_dados_jogos():
            nome = str(jogo.get("competicao", "")).strip()
            if nome:
                competicoes.add(nome)
        for nome in self.listas.get("competicoes", []) if isinstance(self.listas, dict) else []:
            nome_txt = str(nome).strip()
            if nome_txt:
                competicoes.add(nome_txt)
        return sorted(competicoes, key=str.casefold)

    def _render_tabela_titulos_gerenciar(self):
        if not getattr(self, "tv_titulos_gerenciar", None):
            return
        tv = self.tv_titulos_gerenciar
        tv.delete(*tv.get_children())
        for i, item in enumerate(self.titulos_vasco, start=1):
            tv.insert("", "end", values=(item["campeonato"], item["ano"]), tags=("odd",) if i % 2 else ())

    def _on_select_titulo_vasco(self, _event=None):
        if not getattr(self, "tv_titulos_gerenciar", None):
            return
        sel = self.tv_titulos_gerenciar.selection()
        if not sel:
            return
        vals = self.tv_titulos_gerenciar.item(sel[0], "values")
        if len(vals) < 2:
            return
        self.titulo_campeonato_var.set(str(vals[0]))
        self.titulo_ano_var.set(str(vals[1]))

    def _limpar_form_titulo_vasco(self):
        if hasattr(self, "titulo_campeonato_var"):
            self.titulo_campeonato_var.set("")
        if hasattr(self, "titulo_ano_var"):
            self.titulo_ano_var.set("")
        if getattr(self, "tv_titulos_gerenciar", None):
            self.tv_titulos_gerenciar.selection_remove(self.tv_titulos_gerenciar.selection())

    def _ler_form_titulo_vasco(self):
        campeonato = str(self.titulo_campeonato_var.get()).strip() if hasattr(self, "titulo_campeonato_var") else ""
        ano_txt = str(self.titulo_ano_var.get()).strip() if hasattr(self, "titulo_ano_var") else ""
        if not campeonato:
            messagebox.showwarning("Campo obrigatório", "Informe o campeonato.")
            return None
        try:
            ano = int(ano_txt)
        except Exception:
            messagebox.showwarning("Campo inválido", "Ano inválido.")
            return None
        if ano < 1900 or ano > 2100:
            messagebox.showwarning("Campo inválido", "Ano fora do intervalo válido.")
            return None
        return {"campeonato": campeonato, "ano": ano}

    def _cadastrar_titulo_vasco(self):
        novo = self._ler_form_titulo_vasco()
        if not novo:
            return
        chave = (novo["campeonato"].casefold(), novo["ano"])
        existentes = {(t["campeonato"].casefold(), int(t["ano"])) for t in self.titulos_vasco}
        if chave in existentes:
            messagebox.showwarning("Título já existe", "Esse título já está cadastrado.")
            return
        self.titulos_vasco.append(novo)
        salvar_titulos_vasco(self.titulos_vasco)
        self.titulos_vasco = carregar_titulos_vasco()
        self._carregar_titulos()
        messagebox.showinfo("Sucesso", "Título cadastrado com sucesso.")

    def _editar_titulo_vasco(self):
        if not getattr(self, "tv_titulos_gerenciar", None):
            return
        sel = self.tv_titulos_gerenciar.selection()
        if not sel:
            messagebox.showwarning("Seleção obrigatória", "Selecione um título para editar.")
            return
        atual_vals = self.tv_titulos_gerenciar.item(sel[0], "values")
        if len(atual_vals) < 2:
            messagebox.showerror("Erro", "Não foi possível ler o título selecionado.")
            return
        try:
            ano_atual = int(str(atual_vals[1]).strip())
        except Exception:
            messagebox.showerror("Erro", "Ano atual inválido na seleção.")
            return
        campeonato_atual = str(atual_vals[0]).strip()
        novo = self._ler_form_titulo_vasco()
        if not novo:
            return

        chave_antiga = (campeonato_atual.casefold(), ano_atual)
        chave_nova = (novo["campeonato"].casefold(), novo["ano"])

        for item in self.titulos_vasco:
            chave_item = (item["campeonato"].casefold(), int(item["ano"]))
            if chave_item == chave_nova and chave_nova != chave_antiga:
                messagebox.showwarning("Título já existe", "Já existe um título com esse campeonato e ano.")
                return

        alterou = False
        for item in self.titulos_vasco:
            chave_item = (item["campeonato"].casefold(), int(item["ano"]))
            if chave_item == chave_antiga:
                item["campeonato"] = novo["campeonato"]
                item["ano"] = novo["ano"]
                alterou = True
                break
        if not alterou:
            messagebox.showerror("Erro", "Título selecionado não foi encontrado.")
            return

        salvar_titulos_vasco(self.titulos_vasco)
        self.titulos_vasco = carregar_titulos_vasco()
        self._carregar_titulos()
        messagebox.showinfo("Sucesso", "Título atualizado com sucesso.")

    def _excluir_titulo_vasco(self):
        if not getattr(self, "tv_titulos_gerenciar", None):
            return
        sel = self.tv_titulos_gerenciar.selection()
        if not sel:
            messagebox.showwarning("Seleção obrigatória", "Selecione um título para excluir.")
            return
        vals = self.tv_titulos_gerenciar.item(sel[0], "values")
        if len(vals) < 2:
            messagebox.showerror("Erro", "Não foi possível ler o título selecionado.")
            return
        campeonato = str(vals[0]).strip()
        try:
            ano = int(str(vals[1]).strip())
        except Exception:
            messagebox.showerror("Erro", "Ano inválido na seleção.")
            return

        if not messagebox.askyesno("Excluir título", f"Deseja excluir o título?\n\n{campeonato} ({ano})"):
            return

        chave = (campeonato.casefold(), ano)
        antes = len(self.titulos_vasco)
        self.titulos_vasco = [
            t for t in self.titulos_vasco
            if (t["campeonato"].casefold(), int(t["ano"])) != chave
        ]
        if len(self.titulos_vasco) == antes:
            messagebox.showerror("Erro", "Título não encontrado para exclusão.")
            return

        salvar_titulos_vasco(self.titulos_vasco)
        self.titulos_vasco = carregar_titulos_vasco()
        self._carregar_titulos()
        messagebox.showinfo("Sucesso", "Título excluído com sucesso.")

    def _resumir_campanha_titulo(self, jogos, campeonato, ano):
        jogos_titulo = []
        camp_cf = str(campeonato).strip().casefold()
        for jogo in jogos:
            data_txt = str(jogo.get("data", "")).strip()
            dt = _parse_data_ptbr_safe(data_txt)
            if not dt or dt.year != int(ano):
                continue
            comp = str(jogo.get("competicao", "")).strip().casefold()
            if comp != camp_cf:
                continue
            jogos_titulo.append(jogo)

        if not jogos_titulo:
            return {
                "campeonato": campeonato,
                "ano": int(ano),
                "vitorias": "Sem registro",
                "empates": "Sem registro",
                "derrotas": "Sem registro",
                "artilheiro": "Sem registro",
            }

        vitorias = empates = derrotas = 0
        artilheiros = Counter()

        for jogo in jogos_titulo:
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            gols_vasco = int(placar.get("vasco", 0))
            gols_adv = int(placar.get("adversario", 0))
            if gols_vasco > gols_adv:
                vitorias += 1
            elif gols_vasco == gols_adv:
                empates += 1
            else:
                derrotas += 1

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    nome = str(g.get("nome", "")).strip()
                    if not nome:
                        continue
                    artilheiros[nome] += int(g.get("gols", 0))
                elif isinstance(g, str):
                    nome = g.strip()
                    if nome:
                        artilheiros[nome] += 1

        if not artilheiros:
            artilheiro_txt = "—"
        else:
            max_gols = max(artilheiros.values())
            nomes = sorted([nome for nome, gols in artilheiros.items() if gols == max_gols], key=str.casefold)
            artilheiro_txt = " / ".join(nomes) + f" ({max_gols})"

        return {
            "campeonato": campeonato,
            "ano": int(ano),
            "vitorias": vitorias,
            "empates": empates,
            "derrotas": derrotas,
            "artilheiro": artilheiro_txt,
        }

    # --------------------- Gráficos ---------------------
    def _carregar_graficos(self):
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        if not MATPLOTLIB_OK:
            ttk.Label(self.frame_graficos, text="Matplotlib não disponível. Instale para ver os gráficos (pip install matplotlib).").pack(anchor="w")
            return

        jogos = carregar_dados_jogos()
        if not jogos:
            ttk.Label(self.frame_graficos, text="Sem dados para exibir gráficos.").pack(anchor="w")
            return

        temporadas = self._agrupar_por_temporada(jogos)
        nb_root = ttk.Notebook(self.frame_graficos)
        nb_root.pack(fill="both", expand=True)

        frame_resumo_anual = ttk.Frame(nb_root, padding=6)
        nb_root.add(frame_resumo_anual, text="Resumo Anual")
        self._render_graficos_barras_por_ano(frame_resumo_anual, temporadas)

        frame_geral = ttk.Frame(nb_root, padding=6)
        nb_root.add(frame_geral, text="Geral")
        self._render_graficos_para_dataset(frame_geral, jogos, is_geral=True)

        anos_ordenados = sorted(temporadas.keys())
        limite_abas = 10
        abas_fixas = 2
        limite_temporadas_visiveis = max(1, limite_abas - abas_fixas) if len(anos_ordenados) <= (limite_abas - abas_fixas) else max(1, limite_abas - abas_fixas - 1)
        anos_visiveis = anos_ordenados[-limite_temporadas_visiveis:]
        anos_ocultos = anos_ordenados[:-limite_temporadas_visiveis]

        if anos_ocultos:
            frame_mais = ttk.Frame(nb_root, padding=6)
            nb_root.add(frame_mais, text="Mais")

            topo = ttk.Frame(frame_mais)
            topo.pack(fill="x", pady=(0, 8))
            ttk.Label(
                topo,
                text="Temporadas antigas ficam aqui para manter no máximo 10 abas visíveis.",
            ).pack(side="left")

            seletor_wrap = ttk.Frame(frame_mais)
            seletor_wrap.pack(fill="x", pady=(0, 8))
            ttk.Label(seletor_wrap, text="Carregar temporada:").pack(side="left")
            evolucao_antiga_var = tk.StringVar(value=str(anos_ocultos[-1]))
            combo_evolucao_antiga = ttk.Combobox(
                seletor_wrap,
                textvariable=evolucao_antiga_var,
                values=list(reversed(anos_ocultos)),
                state="readonly",
                width=10,
            )
            combo_evolucao_antiga.pack(side="left", padx=(8, 8))

            container_evolucao_antiga = ttk.Frame(frame_mais)
            container_evolucao_antiga.pack(fill="both", expand=True)

            def _render_evolucao_antiga(_event=None):
                ano_sel = evolucao_antiga_var.get().strip()
                if not ano_sel:
                    return
                try:
                    ano_int = int(ano_sel)
                except Exception:
                    return
                if ano_int not in temporadas:
                    return
                for child in container_evolucao_antiga.winfo_children():
                    child.destroy()
                self._montar_aba_evolucao_ano(container_evolucao_antiga, temporadas, ano_int)

            combo_evolucao_antiga.bind("<<ComboboxSelected>>", _render_evolucao_antiga)
            ttk.Button(seletor_wrap, text="Carregar", command=_render_evolucao_antiga).pack(side="left")
            _render_evolucao_antiga()

        for ano in anos_visiveis:
            frame_ano = ttk.Frame(nb_root, padding=6)
            nb_root.add(frame_ano, text=str(ano))
            self._montar_aba_evolucao_ano(frame_ano, temporadas, ano)

        ttk.Button(self.frame_graficos, text="Recarregar Gráficos", command=self._carregar_graficos).pack(pady=8)

    def _configurar_tabs_evolucao(self, notebook):
        tabs = notebook.tabs()
        if not tabs:
            return
        idx = getattr(self, "_evolucao_subtab_index", 0)
        idx = max(0, min(idx, len(tabs) - 1))
        notebook.select(tabs[idx])

        def on_change(event, self=self):
            try:
                self._evolucao_subtab_index = event.widget.index("current")
            except Exception:
                pass

        notebook.bind("<<NotebookTabChanged>>", on_change)

    def _montar_aba_evolucao_ano(self, container, temporadas, ano):
        prev = temporadas.get(ano - 1)
        prev_label = str(ano - 1) if prev else None
        self._render_graficos_para_dataset(
            container,
            temporadas[ano],
            is_geral=False,
            prev_jogos=prev,
            prev_label=prev_label,
        )

    def _render_graficos_barras_por_ano(self, container, temporadas):
        if not temporadas:
            ttk.Label(container, text="Sem temporadas para resumir.").pack(anchor="w")
            return

        canvas = tk.Canvas(container, highlightthickness=0, bg=self.colors["bg"])
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame = ttk.Frame(canvas, padding=4)
        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _update_scroll_region(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _resize_window(event):
            canvas.itemconfigure(window_id, width=event.width)

        def _scroll_canvas(event):
            try:
                if getattr(event, "num", None) == 4:
                    canvas.yview_scroll(-1, "units")
                elif getattr(event, "num", None) == 5:
                    canvas.yview_scroll(1, "units")
                else:
                    delta = int(-1 * (event.delta / 120))
                    if delta:
                        canvas.yview_scroll(delta, "units")
            except Exception:
                return "break"
            return "break"

        scroll_frame.bind("<Configure>", _update_scroll_region)
        canvas.bind("<Configure>", _resize_window)
        for widget in (canvas, scroll_frame):
            widget.bind("<MouseWheel>", _scroll_canvas, add="+")
            widget.bind("<Button-4>", _scroll_canvas, add="+")
            widget.bind("<Button-5>", _scroll_canvas, add="+")

        ttk.Label(
            scroll_frame,
            text="Totais por temporada do Vasco em gráficos de barras.",
        ).pack(anchor="w", pady=(0, 8))

        anos = sorted(temporadas.keys(), reverse=True)
        labels = [str(ano) for ano in anos]
        resumo_por_ano = []
        for ano in anos:
            jogos_ano = temporadas.get(ano, [])
            stats = self._resumir_jogos(jogos_ano)
            resumo_por_ano.append(stats)

        graficos = [
            ("Gols Pró por Ano", "Gols Pró", [item.get("gols_pro", 0) for item in resumo_por_ano]),
            ("Gols Contra por Ano", "Gols Contra", [item.get("gols_contra", 0) for item in resumo_por_ano]),
            ("Saldo por Ano", "Saldo", [item.get("saldo", 0) for item in resumo_por_ano]),
            ("Vitórias por Ano", "Vitórias", [item.get("vitorias", 0) for item in resumo_por_ano]),
            ("Empates por Ano", "Empates", [item.get("empates", 0) for item in resumo_por_ano]),
            ("Derrotas por Ano", "Derrotas", [item.get("derrotas", 0) for item in resumo_por_ano]),
        ]

        for titulo, eixo_x, valores in graficos:
            frame_grafico = ttk.Frame(scroll_frame)
            frame_grafico.pack(fill="both", expand=True, pady=(0, 12))
            graf_widget = self._plot_barras_h(frame_grafico, labels, valores, titulo, eixo_x, top_to_bottom=True)
            for widget in (frame_grafico, graf_widget):
                widget.bind("<MouseWheel>", _scroll_canvas, add="+")
                widget.bind("<Button-4>", _scroll_canvas, add="+")
                widget.bind("<Button-5>", _scroll_canvas, add="+")

    def _render_graficos_para_dataset(self, container, jogos, is_geral=False, prev_jogos=None, prev_label=None):
        if not jogos:
            ttk.Label(container, text="Sem partidas registradas neste contexto.").pack(anchor="w")
            return

        series = self._montar_series_evolucao(jogos)
        if not series["x"]:
            ttk.Label(container, text="Sem dados suficientes para montar a evolução.").pack(anchor="w")
            return

        artilheiros = self._contar_artilheiros(jogos)
        prev_series = None
        if prev_jogos and not is_geral:
            prev_series = self._montar_series_evolucao(prev_jogos)
        overlay_label = prev_label or "Ano anterior"

        nb = ttk.Notebook(container)
        nb.pack(fill="both", expand=True)

        # Artilheiros
        tab_art = ttk.Frame(nb, padding=8)
        nb.add(tab_art, text="Artilheiros")
        if artilheiros:
            top = sorted(artilheiros.items(), key=lambda item: (-item[1], item[0].casefold()))
            top_plot = top
            if is_geral:
                page_size = max(1, int(getattr(self, "_evolucao_geral_art_page_size", 20)))
                total = len(top)
                total_pages = max(1, (total + page_size - 1) // page_size)
                page_idx = int(getattr(self, "_evolucao_geral_art_page", 0))
                page_idx = max(0, min(page_idx, total_pages - 1))
                self._evolucao_geral_art_page = page_idx
                ini = page_idx * page_size
                fim = min(ini + page_size, total)

                controles = ttk.Frame(tab_art)
                controles.pack(fill="x", pady=(0, 8))

                def mudar_pagina_art(delta):
                    novo_idx = max(0, min(total_pages - 1, self._evolucao_geral_art_page + delta))
                    if novo_idx == self._evolucao_geral_art_page:
                        return
                    self._evolucao_geral_art_page = novo_idx
                    for widget in container.winfo_children():
                        widget.destroy()
                    self._render_graficos_para_dataset(
                        container,
                        jogos,
                        is_geral=True,
                        prev_jogos=prev_jogos,
                        prev_label=prev_label,
                    )

                ttk.Button(
                    controles,
                    text="Anterior",
                    command=lambda: mudar_pagina_art(-1),
                    state=("normal" if page_idx > 0 else "disabled"),
                ).pack(side="left")
                ttk.Label(
                    controles,
                    text=f"Nomes {ini + 1}-{fim} de {total}  |  Página {page_idx + 1}/{total_pages}",
                ).pack(side="left", padx=10)
                ttk.Button(
                    controles,
                    text="Próxima",
                    command=lambda: mudar_pagina_art(1),
                    state=("normal" if page_idx < total_pages - 1 else "disabled"),
                ).pack(side="left")

                top_plot = top[ini:fim]

            labels = [n for n, _ in top_plot]
            values = [q for _, q in top_plot]
            self._plot_barras_h(tab_art, labels, values, "Artilheiros (Gols válidos)", "Gols", top_to_bottom=True)
        else:
            ttk.Label(tab_art, text="Ainda não há artilheiros registrados.").pack(anchor="w")

        # Gols acumulados
        tab_gols = ttk.Frame(nb, padding=8)
        nb.add(tab_gols, text="Gols (Acum.)")
        comparativo_gols = None
        if prev_series:
            comparativo_gols = self._criar_overlay_series(series, prev_series,
                                                          ["gols_pro_acum", "gols_contra_acum"],
                                                          overlay_label,
                                                          ["Gols pró (acum.)", "Gols contra (acum.)"],
                                                          color_override=["#15803d", "#b91c1c"])
        self._plot_linhas(tab_gols, series["x"],
                          [series["gols_pro_acum"], series["gols_contra_acum"]],
                          ["Gols pró (acum.)", "Gols contra (acum.)"],
                          "Gols Acumulados", "Jogo", "Gols",
                          comparativos=[comparativo_gols] if comparativo_gols else None,
                          line_colors=["#15803d", "#b91c1c"])

        # Saldo acumulado
        tab_saldo = ttk.Frame(nb, padding=8)
        nb.add(tab_saldo, text="Saldo")
        comparativo_saldo = None
        if prev_series:
            comparativo_saldo = self._criar_overlay_series(series, prev_series,
                                                           ["saldo_acum"],
                                                           overlay_label,
                                                           ["Saldo (acum.)"])
        self._plot_linhas(tab_saldo, series["x"], [series["saldo_acum"]],
                          ["Saldo (acum.)"], "Saldo de Gols (Acum.)", "Jogo", "Saldo",
                          comparativos=[comparativo_saldo] if comparativo_saldo else None)

        # V/E/D acumulados
        tab_ved = ttk.Frame(nb, padding=8)
        nb.add(tab_ved, text="VED (Totais)")
        v_total = series["vit_acum"][-1] if series["vit_acum"] else 0
        e_total = series["emp_acum"][-1] if series["emp_acum"] else 0
        d_total = series["der_acum"][-1] if series["der_acum"] else 0
        self._plot_barras_v(tab_ved, ["Vitórias", "Empates", "Derrotas"], [v_total, e_total, d_total],
                            "Totais de Resultados", "Categoria", "Quantidade",
                            colors=["green", "yellow", "red"])

        self._configurar_tabs_evolucao(nb)
    def _criar_overlay_series(self, base_series, prev_series, keys, label_prefix, labels_desc, color_override=None):
        if not prev_series or not base_series:
            return None
        base_len = len(base_series.get("x", []))
        prev_len = len(prev_series.get("x", []))
        if not base_len or not prev_len:
            return None
        max_len = min(base_len, prev_len)
        if max_len == 0:
            return None
        comparativo = {
            "x": base_series["x"][:max_len],
            "series": [],
            "labels": [],
            "color": "#6b7280",
            "alpha": 1.0,
            "linestyle": "--",
            "linewidth": 1.9,
            "colors": [],
        }
        color_map_default = {
            "gols_pro_acum": "#86efac",
            "gols_contra_acum": "#fca5a5",
            "saldo_acum": "#fdba74",
            "vit_acum": "#86efac",
            "emp_acum": "#fde047",
            "der_acum": "#fca5a5",
            "pontos_acum": "#60a5fa",
        }
        for idx, (key, desc) in enumerate(zip(keys, labels_desc)):
            valores_prev = prev_series.get(key, [])
            if not valores_prev:
                return None
            comparativo["series"].append(valores_prev[:max_len])
            comparativo["labels"].append(f"{label_prefix} - {desc}")
            cor = None
            if color_override and idx < len(color_override):
                cor = color_override[idx]
            else:
                cor = color_map_default.get(key)
            comparativo["colors"].append(cor)
        return comparativo

    def _contar_artilheiros(self, jogos=None) -> Counter:
        if jogos is None:
            jogos = carregar_dados_jogos()
        c = Counter()
        nomes_exibicao = {}

        def chave_nome(nome):
            nome_limpo = re.sub(r"\s+", " ", str(nome or "").strip())
            nome_sem_acentos = "".join(
                ch for ch in unicodedata.normalize("NFKD", nome_limpo)
                if not unicodedata.combining(ch)
            )
            return nome_sem_acentos.casefold()

        def preferir_exibicao(atual, novo):
            if not atual:
                return novo
            if atual.isascii() and not novo.isascii():
                return novo
            if len(novo) > len(atual):
                return novo
            return atual

        for jogo in jogos:
            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    nome = re.sub(r"\s+", " ", str(g.get("nome", "Desconhecido")).strip()) or "Desconhecido"
                    try:
                        qtd = int(g.get("gols", 0))
                    except Exception:
                        qtd = 0
                    if qtd <= 0:
                        continue
                    chave = chave_nome(nome)
                    nomes_exibicao[chave] = preferir_exibicao(nomes_exibicao.get(chave), nome)
                    c[chave] += qtd
                elif isinstance(g, str):
                    nome = re.sub(r"\s+", " ", g.strip())
                    if not nome:
                        continue
                    chave = chave_nome(nome)
                    nomes_exibicao[chave] = preferir_exibicao(nomes_exibicao.get(chave), nome)
                    c[chave] += 1

        c_final = Counter()
        for chave, gols in c.items():
            if gols > 0:
                c_final[nomes_exibicao.get(chave, chave)] = gols
        return c_final

    def _montar_series_evolucao(self, jogos=None):
        if jogos is None:
            jogos = carregar_dados_jogos()
        if not jogos:
            return {"x": []}

        jogos_ordenados = sorted(jogos, key=lambda j: _parse_data_ptbr(j["data"]))

        x = []
        gols_pro_acum = []
        gols_contra_acum = []
        saldo_acum = []
        vit_acum = []
        emp_acum = []
        der_acum = []
        pontos_acum = []
        posicao_rodada = []

        gp = gc = s = v = e = d = p = 0

        for i, jogo in enumerate(jogos_ordenados, start=1):
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            vasco = placar.get("vasco", 0)
            adv = placar.get("adversario", 0)

            gp += vasco
            gc += adv
            s = gp - gc

            if vasco > adv:
                v += 1
            elif vasco == adv:
                e += 1
            else:
                d += 1

            p = v * 3 + e

            x.append(i)
            gols_pro_acum.append(gp)
            gols_contra_acum.append(gc)
            saldo_acum.append(s)
            vit_acum.append(v)
            emp_acum.append(e)
            der_acum.append(d)
            pontos_acum.append(p)
            try:
                posicao_rodada.append(int(jogo.get("posicao_tabela")))
            except (TypeError, ValueError):
                posicao_rodada.append(None)

        return {
            "x": x,
            "gols_pro_acum": gols_pro_acum,
            "gols_contra_acum": gols_contra_acum,
            "saldo_acum": saldo_acum,
            "vit_acum": vit_acum,
            "emp_acum": emp_acum,
            "der_acum": der_acum,
            "pontos_acum": pontos_acum,
            "posicao_rodada": posicao_rodada,
        }

    # --------- Helpers de plot ---------
    def _plot_linhas(self, container, x, series_list, labels, titulo, xlabel, ylabel, comparativos=None, line_colors=None, invert_y=False, integer_x_ticks=False):
        fig = Figure(figsize=(8.5, 5.0), dpi=100)
        ax = fig.add_subplot(111)
        for idx, (serie, label) in enumerate(zip(series_list, labels)):
            if not serie:
                continue
            color = None
            if line_colors and idx < len(line_colors):
                color = line_colors[idx]
            plot_kwargs = {"label": label, "linewidth": 2}
            if color:
                plot_kwargs["color"] = color
            ax.plot(x, serie, **plot_kwargs)
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if integer_x_ticks:
            ax.set_xticks(x)
        if invert_y:
            ax.invert_yaxis()
        ax.grid(True, linestyle="--", alpha=0.4)
        if comparativos:
            for comp in comparativos:
                if not comp:
                    continue
                comp_x = comp.get("x", x)
                comp_series = comp.get("series", [])
                comp_labels = comp.get("labels", [])
                default_color = comp.get("color", "#888888")
                alpha = comp.get("alpha", 1.0)
                linestyle = comp.get("linestyle", "--")
                linewidth = comp.get("linewidth", 1.4)
                comp_colors = comp.get("colors")
                for idx, (serie, label) in enumerate(zip(comp_series, comp_labels)):
                    if not serie:
                        continue
                    lim = min(len(comp_x), len(serie))
                    if lim == 0:
                        continue
                    cor = default_color
                    if comp_colors and idx < len(comp_colors) and comp_colors[idx]:
                        cor = comp_colors[idx]
                    ax.plot(
                        comp_x[:lim],
                        serie[:lim],
                        label=label,
                        linewidth=linewidth,
                        linestyle=linestyle,
                        color=cor,
                        alpha=alpha,
                    )
        handles, labels_text = ax.get_legend_handles_labels()
        if handles:
            fig.subplots_adjust(bottom=0.22)
            ncol = min(4, max(1, len(handles)))
            ax.legend(
                handles,
                labels_text,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.18),
                ncol=ncol
            )
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _plot_linhas_comparativo(self, container, series_atual, keys, labels, ano_atual, ano_anterior, prev_series=None, titulo="", xlabel="Jogo", ylabel="", color_override=None, invert_y=False, integer_x_ticks=False):
        color_override = color_override or {}
        base_x = series_atual.get("x", [])
        if not base_x:
            ttk.Label(container, text="Sem dados suficientes para este gráfico.").pack(anchor="w", pady=(4, 6))
            return
        linhas = []
        nomes = []
        line_colors = []
        present = []
        color_map = {
            "pontos_acum": ("#1d4ed8", "#60a5fa"),
            "gols_pro_acum": ("#15803d", "#15803d"),
            "gols_contra_acum": ("#b91c1c", "#b91c1c"),
            "saldo_acum": ("#f97316", "#fdba74"),
            "posicao_rodada": ("#7c3aed", "#c4b5fd"),
        }
        ano_atual_txt = str(ano_atual)
        ano_ant_txt = str(ano_anterior) if ano_anterior is not None else "Ano anterior"
        for key, label in zip(keys, labels):
            valores = series_atual.get(key)
            if not valores:
                continue
            linhas.append(valores)
            nomes.append(f"{ano_atual_txt} - {label}")
            base_color, light_color = color_override.get(key, color_map.get(key, (None, None)))
            line_colors.append(base_color)
            present.append({"key": key, "label": label, "light_color": light_color})
        if not linhas:
            ttk.Label(container, text="Sem métricas disponíveis para exibir.").pack(anchor="w", pady=(4, 6))
            return
        comparativos = None
        if prev_series and prev_series.get("x"):
            comparativo = {
                "x": base_x,
                "series": [],
                "labels": [],
                "color": "#6b7280",
                "alpha": 1.0,
                "linestyle": "--",
                "linewidth": 1.9,
                "colors": [],
            }
            prev_x = prev_series.get("x", [])
            lim_x = min(len(base_x), len(prev_x))
            if lim_x > 0:
                comparativo["x"] = base_x[:lim_x]
                for idx_present, info in enumerate(present):
                    key = info["key"]
                    label = info["label"]
                    valores_prev = prev_series.get(key)
                    if not valores_prev:
                        continue
                    comparativo["series"].append(valores_prev[:lim_x])
                    comparativo["labels"].append(f"{ano_ant_txt} - {label}")
                    cor_clara = info.get("light_color")
                    comparativo["colors"].append(cor_clara)
                if comparativo["series"]:
                    comparativos = [comparativo]
        self._plot_linhas(
            container,
            base_x,
            linhas,
            nomes,
            titulo or "Evolução",
            xlabel,
            ylabel,
            comparativos=comparativos,
            line_colors=line_colors,
            invert_y=invert_y,
            integer_x_ticks=integer_x_ticks,
        )

    def _plot_barras_h(self, container, labels, values, titulo, xlabel, top_to_bottom=True):
        fig = Figure(figsize=(9.2, 6.0), dpi=100)
        ax = fig.add_subplot(111)
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        if top_to_bottom:
            ax.invert_yaxis()  # primeiro item no topo
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        maxv = max(values) if values else 0
        minv = min(values) if values else 0
        max_abs = max([abs(v) for v in values], default=0)
        texto_offset = 0.01 * max_abs if max_abs else 0.2
        label_artists = []
        default_bar_colors = []
        for rect, val in zip(bars, values):
            default_bar_colors.append(rect.get_facecolor())
            if val < 0:
                txt = ax.text(
                    rect.get_width() + texto_offset,
                    rect.get_y() + rect.get_height() / 2,
                    str(val),
                    va="center",
                    ha="right",
                    color="white",
                    fontweight="bold",
                )
            else:
                txt = ax.text(
                    rect.get_width() + texto_offset,
                    rect.get_y() + rect.get_height() / 2,
                    str(val),
                    va="center",
                    ha="left",
                    color="#111111",
                )
            label_artists.append(txt)
            rect.set_picker(True)
        if minv < 0:
            ax.set_xlim(minv - (0.08 * max_abs if max_abs else 1), ax.get_xlim()[1])

        selected = {"index": None}

        def _aplicar_destaque(indice):
            selected["index"] = indice
            for idx, rect in enumerate(bars):
                if idx == indice:
                    rect.set_edgecolor("#f59e0b")
                    rect.set_linewidth(3)
                    rect.set_alpha(1.0)
                else:
                    rect.set_edgecolor("none")
                    rect.set_linewidth(0)
                    rect.set_alpha(0.9)
                if idx < len(label_artists):
                    label_artists[idx].set_fontweight("bold" if idx == indice else "normal")
            canvas.draw_idle()

        def _on_pick(event):
            if event.artist not in bars:
                return
            for idx, rect in enumerate(bars):
                if rect == event.artist:
                    _aplicar_destaque(idx)
                    break

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)
        canvas.mpl_connect("pick_event", _on_pick)
        return widget

    def _plot_barras_v(self, container, labels, values, titulo, xlabel, ylabel, colors=None):
        fig = Figure(figsize=(8.5, 5.0), dpi=100)
        ax = fig.add_subplot(111)
        x_pos = range(len(labels))
        ax.bar(x_pos, values, color=colors)
        ax.set_xticks(list(x_pos))
        ax.set_xticklabels(labels)
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        maxv = max(values) if values else 0
        for i, v in enumerate(values):
            ax.text(i, v + (0.02 * maxv if maxv else 0.1), str(v), ha="center", va="bottom")
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    _gerar_backup_jsons_inicio()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
