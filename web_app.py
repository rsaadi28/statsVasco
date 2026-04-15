#!/usr/bin/env python3
"""MVP web para visualizar dados do StatsVasco no navegador.

Sem dependências externas: usa apenas biblioteca padrão.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from storage_sqlite import (
    bootstrap_database,
    db_path_for,
    load_current_squad as db_load_current_squad,
    load_future_matches as db_load_future_matches,
    load_historic_players as db_load_historic_players,
    load_listas as db_load_listas,
    load_matches as db_load_matches,
    save_historic_players as db_save_historic_players,
    save_listas as db_save_listas,
    save_matches as db_save_matches,
)

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
ARQUIVO_JOGOS = os.path.join(PROJECT_ROOT, "jogos_vasco.json")
ARQUIVO_FUTUROS = os.path.join(PROJECT_ROOT, "jogos_futuros.json")
ARQUIVO_LISTAS = os.path.join(PROJECT_ROOT, "listas_auxiliares.json")
ARQUIVO_ELENCO_ATUAL = os.path.join(PROJECT_ROOT, "elenco_atual.json")
DB_PATH = db_path_for(PROJECT_ROOT)
bootstrap_database(
    DB_PATH,
    json_paths={
        "jogos": ARQUIVO_JOGOS,
        "listas": ARQUIVO_LISTAS,
        "futuros": ARQUIVO_FUTUROS,
        "elenco": ARQUIVO_ELENCO_ATUAL,
        "historico": os.path.join(PROJECT_ROOT, "jogadores_historico.json"),
    },
)
COMPETICAO_BRASILEIRAO = "Brasileirão Série A"
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


def carregar_jogos():
    return db_load_matches(DB_PATH)


def carregar_futuros():
    return db_load_future_matches(DB_PATH)


def carregar_listas():
    return db_load_listas(DB_PATH)


def salvar_listas(dados: dict):
    db_save_listas(DB_PATH, dados)


def salvar_lista_jogos(dados: list):
    db_save_matches(DB_PATH, dados)


def _normalizar_posicao_elenco(posicao: str) -> str:
    pos = str(posicao or "").strip()
    if pos.casefold() == "goleiros":
        pos = "Goleiro"
    return pos if pos in POSICOES_ELENCO else "Meio-Campista"


def _normalizar_condicao_elenco(condicao: str) -> str:
    cond = str(condicao or "").strip()
    return cond if cond in CONDICOES_ELENCO else "Reserva"


def _normalizar_jogador_elenco(item):
    if not isinstance(item, dict):
        return None
    nome = str(item.get("nome", "")).strip()
    if not nome:
        return None
    return {
        "nome": nome,
        "posicao": _normalizar_posicao_elenco(item.get("posicao")),
        "condicao": _normalizar_condicao_elenco(item.get("condicao")),
    }


def carregar_elenco_atual():
    dados = db_load_current_squad(DB_PATH)
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
    for item in jogadores:
        jogador = _normalizar_jogador_elenco(item)
        if not jogador:
            continue
        cf = jogador["nome"].casefold()
        if cf in vistos:
            continue
        vistos.add(cf)
        normalizados.append(jogador)
    return {"jogadores": normalizados, "tecnico": tecnico}


def _competicao_usa_posicao(nome: str) -> bool:
    return bool(nome and nome.strip().casefold() == COMPETICAO_BRASILEIRAO.casefold())


def _escalacao_partida_base():
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


def _normalizar_escalacao_partida(escalacao: dict | None) -> dict:
    base = _escalacao_partida_base()
    if not isinstance(escalacao, dict):
        return base

    tit_por_pos = escalacao.get("titulares_por_posicao")
    if isinstance(tit_por_pos, dict):
        for pos in POSICOES_ELENCO:
            nomes = tit_por_pos.get(pos, [])
            if isinstance(nomes, list):
                base["titulares_por_posicao"][pos] = [str(n).strip() for n in nomes if str(n).strip()]

    for chave, _ in CATEGORIAS_ESCALACAO_EXTRAS:
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
        base["titulares_por_posicao"][pos] = filtrados
    for chave, _ in CATEGORIAS_ESCALACAO_EXTRAS:
        filtrados = []
        for nome in base[chave]:
            cf = nome.casefold()
            if cf in vistos:
                continue
            vistos.add(cf)
            filtrados.append(nome)
        base[chave] = filtrados
    reservas_cf = {str(nome).strip().casefold() for nome in base["reservas"] if str(nome).strip()}
    substituicoes = escalacao.get("substituicoes", [])
    if isinstance(substituicoes, list):
        base["substituicoes"] = [item for item in substituicoes if isinstance(item, dict)]
    if base["substituicoes"]:
        bruto_entraram = [item.get("jogador_entrou", "") for item in base["substituicoes"]]
    elif "reservas_que_entraram" in escalacao:
        bruto_entraram = escalacao.get("reservas_que_entraram")
    else:
        bruto_entraram = list(base["reservas"])
    vistos_entraram = set()
    for nome in bruto_entraram:
        nome_limpo = str(nome).strip()
        chave = nome_limpo.casefold()
        if not nome_limpo or chave in vistos_entraram or chave not in reservas_cf:
            continue
        vistos_entraram.add(chave)
        base["reservas_que_entraram"].append(nome_limpo)
    return base


def _chave_nome_jogador(nome: str) -> str:
    return str(nome or "").strip().casefold()


def _jogadores_que_participaram_do_jogo(jogo: dict) -> set[str]:
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


def _ajustar_jogos_pelo_vasco_historico(participantes_antes: set[str], participantes_depois: set[str]) -> None:
    dados = db_load_historic_players(DB_PATH)
    jogadores = dados.get("jogadores", []) if isinstance(dados, dict) else []
    if not isinstance(jogadores, list):
        jogadores = []
    alterou = False
    atualizados = []
    for item in jogadores:
        if not isinstance(item, dict):
            continue
        jogador = dict(item)
        chave = _chave_nome_jogador(jogador.get("nome", ""))
        valor_atual = jogador.get("jogos_pelo_vasco")
        try:
            valor_atual = int(valor_atual)
            if valor_atual < 0:
                valor_atual = None
        except (TypeError, ValueError):
            valor_atual = None
        novo_valor = valor_atual
        if chave in participantes_antes and chave not in participantes_depois:
            novo_valor = max(0, (valor_atual or 0) - 1)
        elif chave in participantes_depois and chave not in participantes_antes:
            novo_valor = (valor_atual or 0) + 1
        if novo_valor != valor_atual:
            jogador["jogos_pelo_vasco"] = novo_valor
            alterou = True
        atualizados.append(jogador)
    if alterou:
        db_save_historic_players(DB_PATH, {"jogadores": atualizados})


def escalacao_padrao_do_elenco(elenco: dict) -> dict:
    base = _escalacao_partida_base()
    for jogador in elenco.get("jogadores", []):
        nome = str(jogador.get("nome", "")).strip()
        if not nome:
            continue
        cond = _normalizar_condicao_elenco(jogador.get("condicao"))
        pos = _normalizar_posicao_elenco(jogador.get("posicao"))
        if cond == "Titular":
            base["titulares_por_posicao"][pos].append(nome)
        elif cond == "Reserva":
            base["reservas"].append(nome)
        elif cond == "Não Relacionado":
            base["nao_relacionados"].append(nome)
        elif cond == "Lesionado":
            base["lesionados"].append(nome)
        elif cond == "Suspenso":
            base["suspensos"].append(nome)
        elif cond == "Servindo a seleção":
            base["servindo_selecao"].append(nome)
        # Emprestados ficam fora da escalação padrão da partida.
    return _normalizar_escalacao_partida(base)


def validar_escalacao_partida(escalacao: dict, elenco: dict):
    escalacao = _normalizar_escalacao_partida(escalacao)
    titulares = sum(len(escalacao["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
    goleiros_titulares = len(escalacao["titulares_por_posicao"].get("Goleiro", []))
    reservas = len(escalacao.get("reservas", []))
    if titulares != 11:
        return False, "A escalação precisa ter exatamente 11 titulares.", escalacao
    if goleiros_titulares != 1:
        return False, "A escalação precisa ter exatamente 1 goleiro titular.", escalacao
    if reservas < 4:
        return False, "A escalação precisa ter pelo menos 4 reservas.", escalacao

    nomes_elenco = {
        str(j.get("nome", "")).strip().casefold()
        for j in elenco.get("jogadores", [])
        if (
            isinstance(j, dict)
            and str(j.get("nome", "")).strip()
            and _normalizar_condicao_elenco(j.get("condicao")) != "Emprestado"
        )
    }
    nomes_escalados = set()
    for pos in POSICOES_ELENCO:
        for nome in escalacao["titulares_por_posicao"].get(pos, []):
            n = str(nome).strip()
            if n:
                nomes_escalados.add(n.casefold())
    for chave, _ in CATEGORIAS_ESCALACAO_EXTRAS:
        for nome in escalacao.get(chave, []):
            n = str(nome).strip()
            if n:
                nomes_escalados.add(n.casefold())
    faltando = sorted(nomes_elenco - nomes_escalados)
    if faltando:
        return False, "Todos os jogadores do elenco (exceto emprestados) precisam estar em alguma lista da escalação.", escalacao
    return True, "", escalacao


def _split_nomes_livres(valor: str) -> list[str]:
    bruto = str(valor or "")
    partes = []
    for trecho in bruto.replace(";", "\n").splitlines():
        for item in trecho.split(","):
            nome = item.strip()
            if nome:
                partes.append(nome)
    return partes


def _parse_data_br_strita(valor: str) -> bool:
    try:
        datetime.strptime(str(valor or "").strip(), "%d/%m/%Y")
        return True
    except Exception:
        return False


def _escalacao_partida_vazia(escalacao: dict | None) -> bool:
    if not isinstance(escalacao, dict):
        return True
    tit = escalacao.get("titulares_por_posicao")
    if isinstance(tit, dict):
        for nomes in tit.values():
            if isinstance(nomes, list) and any(str(nome).strip() for nome in nomes):
                return False
    for chave, _ in CATEGORIAS_ESCALACAO_EXTRAS:
        nomes = escalacao.get(chave)
        if isinstance(nomes, list) and any(str(nome).strip() for nome in nomes):
            return False
    return True


def _parse_optional_int(valor, campo: str):
    txt = str(valor or "").strip()
    if not txt:
        return None, None
    try:
        return int(txt), None
    except ValueError:
        return None, f"Informe apenas números inteiros para {campo}."


def _parse_optional_float(valor, campo: str):
    txt = str(valor or "").strip()
    if not txt:
        return None, None
    txt = txt.replace(" ", "")
    if "," in txt and "." in txt:
        txt = txt.replace(".", "").replace(",", ".")
    elif "," in txt:
        txt = txt.replace(",", ".")
    try:
        return float(txt), None
    except ValueError:
        return None, f"Informe um número válido para {campo}."


def _salvar_ou_atualizar_partida_web(payload: dict, edit_idx: int | None = None):
    if not isinstance(payload, dict):
        return False, "Payload inválido.", None

    jogos = carregar_jogos()
    jogo_base = {}
    participantes_antes = set()
    if edit_idx is not None:
        if not (0 <= edit_idx < len(jogos)):
            return False, "Não foi possível localizar o jogo para edição.", None
        jogo_base = jogos[edit_idx] if isinstance(jogos[edit_idx], dict) else {}
        participantes_antes = _jogadores_que_participaram_do_jogo(jogo_base)

    data = str(payload.get("data", "")).strip()
    adversario = str(payload.get("adversario", "")).strip()
    competicao = str(payload.get("competicao", "")).strip()
    local = str(payload.get("local", "")).strip()
    estadio = str(payload.get("estadio", "")).strip()
    horario = str(payload.get("horario", "")).strip()
    capitao = str(payload.get("capitao", "")).strip()
    observacao = str(payload.get("observacao", "")).strip()
    tecnico = str(payload.get("tecnico", "")).strip()
    publico_pagante, err = _parse_optional_int(payload.get("publico_pagante", ""), "o público pagante")
    if err:
        return False, err, None
    publico_presente, err = _parse_optional_int(payload.get("publico_presente", ""), "o público presente")
    if err:
        return False, err, None
    renda, err = _parse_optional_float(payload.get("renda", ""), "a renda")
    if err:
        return False, err, None

    placar = payload.get("placar") or {}
    try:
        placar_vasco = int(placar.get("vasco"))
        placar_adv = int(placar.get("adversario"))
    except Exception:
        return False, "Placar inválido. Informe números inteiros.", None
    if placar_vasco < 0 or placar_adv < 0:
        return False, "Placar inválido. Não use números negativos.", None

    if not (data and adversario):
        return False, "Preencha os campos obrigatórios: data, adversário e placar.", None
    if not _parse_data_br_strita(data):
        return False, "Data inválida. Use o formato dd/mm/aaaa.", None
    if local and local not in ("casa", "fora"):
        return False, "Local inválido (use 'casa' ou 'fora').", None

    posicao_tabela = None
    posicao_txt = str(payload.get("posicao_tabela", "")).strip()
    if _competicao_usa_posicao(competicao):
        if posicao_txt:
            try:
                posicao_tabela = int(posicao_txt)
            except ValueError:
                return False, "Informe apenas números inteiros para a posição na tabela.", None
    else:
        posicao_txt = ""

    nomes_vasco = _split_nomes_livres(payload.get("gols_vasco_lista", ""))
    nomes_contra = _split_nomes_livres(payload.get("gols_contra_lista", ""))
    if len(nomes_vasco) > placar_vasco:
        return (
            False,
            f"Você informou mais autores ({len(nomes_vasco)}) do que gols do Vasco no placar ({placar_vasco}).",
            None,
        )
    if len(nomes_contra) > placar_adv:
        return (
            False,
            f"Você informou mais autores ({len(nomes_contra)}) do que gols do adversário no placar ({placar_adv}).",
            None,
        )

    escalacao_payload = payload.get("escalacao_partida") or {}
    if _escalacao_partida_vazia(escalacao_payload):
        escalacao_partida = {}
    else:
        elenco = carregar_elenco_atual()
        ok_esc, msg_esc, escalacao_partida = validar_escalacao_partida(escalacao_payload, elenco)
        if not ok_esc:
            return False, msg_esc, None

    titulares_cf = set()
    reservas_cf = set()
    titulares_por_posicao = escalacao_partida.get("titulares_por_posicao", {})
    for pos in POSICOES_ELENCO:
        for nome in titulares_por_posicao.get(pos, []):
            n = str(nome).strip()
            if n:
                titulares_cf.add(n.casefold())
    for nome in escalacao_partida.get("reservas", []):
        n = str(nome).strip()
        if n:
            reservas_cf.add(n.casefold())

    contagem_vasco = Counter(nomes_vasco)
    gols_vasco = []
    for nome, qtd in contagem_vasco.items():
        nome_cf = str(nome).strip().casefold()
        gols_vasco.append({
            "nome": nome,
            "gols": qtd,
            "saiu_do_banco": (nome_cf in reservas_cf and nome_cf not in titulares_cf),
        })

    contagem_contra = Counter(nomes_contra)
    gols_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_contra.items()]

    listas = carregar_listas()
    if adversario not in listas.get("clubes_adversarios", []):
        listas.setdefault("clubes_adversarios", []).append(adversario)
        listas["clubes_adversarios"] = sorted(listas["clubes_adversarios"], key=str.casefold)
    if competicao and competicao not in listas.get("competicoes", []):
        listas.setdefault("competicoes", []).append(competicao)
        listas["competicoes"] = sorted(listas["competicoes"], key=str.casefold)
    if tecnico and tecnico not in listas.get("tecnicos", []):
        listas.setdefault("tecnicos", []).append(tecnico)
        listas["tecnicos"] = sorted(listas["tecnicos"], key=str.casefold)

    for nome in nomes_vasco:
        if nome not in listas.get("jogadores_vasco", []):
            listas.setdefault("jogadores_vasco", []).append(nome)
    listas["jogadores_vasco"] = sorted(listas.get("jogadores_vasco", []), key=str.casefold)

    for nome in nomes_contra:
        if nome not in listas.get("jogadores_contra", []):
            listas.setdefault("jogadores_contra", []).append(nome)
    listas["jogadores_contra"] = sorted(listas.get("jogadores_contra", []), key=str.casefold)
    salvar_listas(listas)

    jogo = {
        **jogo_base,
        "data": data,
        "adversario": adversario,
        "competicao": competicao,
        "local": local,
        "estadio": estadio,
        "horario": horario,
        "placar": {"vasco": placar_vasco, "adversario": placar_adv},
        "gols_vasco": gols_vasco,
        "gols_adversario": gols_contra,
        "observacao": observacao,
        "tecnico": tecnico,
        "capitao": capitao,
        "publico_pagante": publico_pagante,
        "publico_presente": publico_presente,
        "renda": renda,
        "posicao_tabela": posicao_tabela,
        "escalacao_partida": escalacao_partida,
    }
    participantes_depois = _jogadores_que_participaram_do_jogo(jogo)

    if edit_idx is None:
        jogos.append(jogo)
        msg_ok = "Partida registrada com sucesso!"
    else:
        jogos[edit_idx] = jogo
        msg_ok = "Partida atualizada com sucesso!"
    salvar_lista_jogos(jogos)
    _ajustar_jogos_pelo_vasco_historico(participantes_antes, participantes_depois)
    return True, msg_ok, jogo


def registrar_partida_web(payload: dict):
    return _salvar_ou_atualizar_partida_web(payload, edit_idx=None)


def editar_partida_web(idx: int, payload: dict):
    return _salvar_ou_atualizar_partida_web(payload, edit_idx=idx)


def _parse_data_br(valor: str):
    try:
        return datetime.strptime((valor or "").strip(), "%d/%m/%Y")
    except Exception:
        return None


def _resultado_jogo(jogo: dict) -> str:
    placar = jogo.get("placar") or {}
    v = placar.get("vasco")
    a = placar.get("adversario")
    if not isinstance(v, int) or not isinstance(a, int):
        return "?"
    if v > a:
        return "V"
    if v < a:
        return "D"
    return "E"


def resumo_geral(jogos: list[dict]) -> dict:
    total = 0
    vitorias = empates = derrotas = 0
    gols_pro = gols_contra = 0
    por_comp = Counter()

    for jogo in jogos:
        placar = jogo.get("placar") or {}
        gp = placar.get("vasco")
        gc = placar.get("adversario")
        if not isinstance(gp, int) or not isinstance(gc, int):
            continue
        total += 1
        gols_pro += gp
        gols_contra += gc
        if gp > gc:
            vitorias += 1
        elif gp < gc:
            derrotas += 1
        else:
            empates += 1
        comp = (jogo.get("competicao") or "Sem competição").strip()
        por_comp[comp] += 1

    return {
        "total_jogos": total,
        "vitorias": vitorias,
        "empates": empates,
        "derrotas": derrotas,
        "gols_pro": gols_pro,
        "gols_contra": gols_contra,
        "saldo": gols_pro - gols_contra,
        "competicoes_top": por_comp.most_common(10),
    }


def serializar_jogos(jogos: list[dict], limite: int | None = None, busca: str = "") -> list[dict]:
    busca_cf = busca.strip().casefold()
    itens = []
    for idx, jogo in enumerate(jogos):
        adversario = str(jogo.get("adversario") or "")
        competicao = str(jogo.get("competicao") or "")
        tecnico = str(jogo.get("tecnico") or "")
        if busca_cf and busca_cf not in " | ".join([adversario, competicao, tecnico]).casefold():
            continue
        placar = jogo.get("placar") or {}
        itens.append(
            {
                "data": jogo.get("data", ""),
                "adversario": adversario,
                "competicao": competicao,
                "local": jogo.get("local", ""),
                "vasco": placar.get("vasco"),
                "adversario_gols": placar.get("adversario"),
                "resultado": _resultado_jogo(jogo),
                "tecnico": tecnico,
                "idx": idx,
                "_sort_data": _parse_data_br(str(jogo.get("data") or "")),
            }
        )
    itens.sort(key=lambda x: (x["_sort_data"] is None, x["_sort_data"] or datetime.min), reverse=True)
    for item in itens:
        item.pop("_sort_data", None)
    return itens[:limite] if limite else itens


def detalhe_jogo_por_indice(idx: int):
    jogos = carregar_jogos()
    if not (0 <= idx < len(jogos)):
        return None
    jogo = jogos[idx]
    placar = jogo.get("placar") or {}
    escalacao = _normalizar_escalacao_partida(
        jogo.get("escalacao_partida") if isinstance(jogo.get("escalacao_partida"), dict) else {}
    )
    return {
        "idx": idx,
        "data": jogo.get("data", ""),
        "adversario": jogo.get("adversario", ""),
        "competicao": jogo.get("competicao", ""),
        "local": jogo.get("local", ""),
        "estadio": jogo.get("estadio", ""),
        "horario": jogo.get("horario", ""),
        "tecnico": jogo.get("tecnico", ""),
        "capitao": jogo.get("capitao", ""),
        "publico_pagante": jogo.get("publico_pagante"),
        "publico_presente": jogo.get("publico_presente"),
        "renda": jogo.get("renda"),
        "observacao": jogo.get("observacao", ""),
        "posicao_tabela": jogo.get("posicao_tabela"),
        "placar": {
            "vasco": placar.get("vasco"),
            "adversario": placar.get("adversario"),
        },
        "resultado": _resultado_jogo(jogo),
        "gols_vasco": jogo.get("gols_vasco", []),
        "gols_adversario": jogo.get("gols_adversario", []),
        "escalacao_partida": escalacao,
    }


def serializar_futuros(futuros: list[dict]) -> list[dict]:
    itens = []
    for j in futuros:
        itens.append(
            {
                "jogo": j.get("jogo", ""),
                "data": j.get("data", ""),
                "em_casa": bool(j.get("em_casa", False)),
                "campeonato": j.get("campeonato", ""),
                "_sort_data": _parse_data_br(str(j.get("data") or "")),
            }
        )
    itens.sort(key=lambda x: (x["_sort_data"] is None, x["_sort_data"] or datetime.max))
    for item in itens:
        item.pop("_sort_data", None)
    return itens


def _contagem_goleadores(lista) -> Counter:
    contagem = Counter()
    if not isinstance(lista, list):
        return contagem
    for item in lista:
        if isinstance(item, dict):
            nome = str(item.get("nome", "")).strip()
            try:
                qtd = int(item.get("gols", 1))
            except (TypeError, ValueError):
                qtd = 1
            if nome:
                contagem[nome] += max(1, qtd)
        elif isinstance(item, str):
            nome = item.strip()
            if nome:
                contagem[nome] += 1
    return contagem


def _formatar_goleadores(contagem: Counter) -> str:
    if not contagem:
        return "—"
    partes = []
    for nome, qtd in contagem.most_common():
        partes.append(f"{nome} x{qtd}" if qtd > 1 else nome)
    return ", ".join(partes)


def coletar_retro_por_adversario(adversario: str) -> dict:
    retro = {
        "adversario": str(adversario or "").strip(),
        "partidas": [],
        "vitorias": 0,
        "empates": 0,
        "derrotas": 0,
        "gols_vasco": 0,
        "gols_adversario": 0,
        "artilheiros_vasco": Counter(),
        "artilheiros_adversario": Counter(),
    }
    if not retro["adversario"]:
        return {
            **retro,
            "artilheiros_vasco": "—",
            "artilheiros_adversario": "—",
            "total_partidas": 0,
        }

    alvo = retro["adversario"].casefold()
    for jogo in carregar_jogos():
        adv_jogo = str(jogo.get("adversario", "")).strip()
        if not adv_jogo or adv_jogo.casefold() != alvo:
            continue

        placar = jogo.get("placar") or {}
        try:
            gols_vasco = int(placar.get("vasco", 0))
        except (TypeError, ValueError):
            gols_vasco = 0
        try:
            gols_adv = int(placar.get("adversario", 0))
        except (TypeError, ValueError):
            gols_adv = 0

        if gols_vasco > gols_adv:
            resultado_txt = "Vitória"
            resultado_sigla = "V"
            retro["vitorias"] += 1
        elif gols_vasco < gols_adv:
            resultado_txt = "Derrota"
            resultado_sigla = "D"
            retro["derrotas"] += 1
        else:
            resultado_txt = "Empate"
            resultado_sigla = "E"
            retro["empates"] += 1

        retro["gols_vasco"] += gols_vasco
        retro["gols_adversario"] += gols_adv

        goleadores_vasco = _contagem_goleadores(jogo.get("gols_vasco", []))
        goleadores_adv = _contagem_goleadores(jogo.get("gols_adversario", []))
        retro["artilheiros_vasco"].update(goleadores_vasco)
        retro["artilheiros_adversario"].update(goleadores_adv)

        data_txt = str(jogo.get("data", "")).strip() or "—"
        data_ord = _parse_data_br(data_txt)
        retro["partidas"].append(
            {
                "data": data_txt,
                "competicao": str(jogo.get("competicao", "")).strip() or "—",
                "local": "Casa" if str(jogo.get("local", "casa")).strip() == "casa" else "Fora",
                "placar": f"{gols_vasco} x {gols_adv}",
                "resultado": resultado_sigla,
                "resultado_texto": resultado_txt,
                "gols_vasco": _formatar_goleadores(goleadores_vasco),
                "gols_adversario": _formatar_goleadores(goleadores_adv),
                "_sort_data": data_ord,
            }
        )

    retro["partidas"].sort(key=lambda p: (p["_sort_data"] is None, p["_sort_data"] or datetime.min), reverse=True)
    for partida in retro["partidas"]:
        partida.pop("_sort_data", None)

    return {
        "adversario": retro["adversario"],
        "partidas": retro["partidas"],
        "total_partidas": len(retro["partidas"]),
        "vitorias": retro["vitorias"],
        "empates": retro["empates"],
        "derrotas": retro["derrotas"],
        "gols_vasco": retro["gols_vasco"],
        "gols_adversario": retro["gols_adversario"],
        "artilheiros_vasco": _formatar_goleadores(retro["artilheiros_vasco"]),
        "artilheiros_adversario": _formatar_goleadores(retro["artilheiros_adversario"]),
    }


def listar_adversarios_com_historico() -> list[str]:
    return sorted(
        {
            str(jogo.get("adversario", "")).strip()
            for jogo in carregar_jogos()
            if str(jogo.get("adversario", "")).strip()
        },
        key=lambda s: s.casefold(),
    )


INDEX_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>StatsVasco Web (MVP)</title>
  <style>
    :root {
      --bg: #f3efe6;
      --bg-soft: #e6ddcb;
      --card: rgba(255, 252, 246, 0.94);
      --card-strong: #fffdf8;
      --ink: #111111;
      --muted: #655b4e;
      --line: rgba(17, 17, 17, 0.14);
      --line-strong: rgba(17, 17, 17, 0.34);
      --accent: #111111;
      --accent-soft: #2a2a2a;
      --gold: #b89b63;
      --gold-soft: #d9c7a0;
      --ok: #0f6b39;
      --warn: #9b6b13;
      --bad: #8f1f1f;
      --shadow: 0 18px 50px rgba(17, 17, 17, 0.1);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(135deg, rgba(17, 17, 17, 0.06) 0 14%, transparent 14% 100%),
        radial-gradient(circle at top right, rgba(184, 155, 99, 0.22), transparent 30%),
        radial-gradient(circle at left center, rgba(17, 17, 17, 0.08), transparent 28%),
        var(--bg);
      min-height: 100vh;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(90deg, transparent 0 86%, rgba(17,17,17,0.035) 86% 100%),
        repeating-linear-gradient(
          -45deg,
          rgba(17,17,17,0.02) 0 14px,
          transparent 14px 48px
        );
      opacity: .8;
    }
    .site-shell { position: relative; z-index: 1; }
    .wrap { max-width: 1320px; margin: 0 auto; padding: 24px; }
    .topbar {
      border-bottom: 1px solid rgba(255,255,255,.08);
      background:
        linear-gradient(90deg, rgba(255,255,255,.06), transparent 45%),
        linear-gradient(135deg, #090909, #1c1c1c);
      color: #f8f3e8;
      box-shadow: inset 0 -1px 0 rgba(184, 155, 99, 0.35);
    }
    .topbar-inner {
      max-width: 1320px;
      margin: 0 auto;
      padding: 14px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    .brand-block { display: flex; align-items: center; gap: 14px; }
    .brand-mark {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      position: relative;
      background:
        linear-gradient(135deg, #efe4cb, #b89b63);
      box-shadow: inset 0 0 0 1px rgba(17,17,17,.18);
      overflow: hidden;
    }
    .brand-mark::before {
      content: "";
      position: absolute;
      inset: -6px 20px;
      background: #111;
      transform: rotate(45deg);
    }
    .brand-mark::after {
      content: "+";
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      color: #efe4cb;
      font-size: 1.45rem;
      font-weight: 700;
    }
    .brand-copy small,
    .masthead-notes {
      display: block;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      font-size: .72rem;
      color: rgba(248, 243, 232, 0.72);
    }
    .brand-copy strong {
      display: block;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: 1.45rem;
      letter-spacing: .02em;
      font-weight: 700;
    }
    .masthead-notes {
      text-align: right;
      max-width: 320px;
      line-height: 1.5;
    }
    .hero {
      position: relative;
      overflow: hidden;
      border-radius: 28px;
      padding: 28px;
      background:
        linear-gradient(140deg, rgba(255,255,255,0.08), transparent 42%),
        linear-gradient(125deg, rgba(184,155,99,.2), transparent 58%),
        linear-gradient(135deg, #0f0f0f 0%, #202020 65%, #121212 100%);
      color: #f7f1e5;
      box-shadow: var(--shadow);
      border: 1px solid rgba(255,255,255,.08);
    }
    .hero::before {
      content: "";
      position: absolute;
      right: -10%;
      top: -24%;
      width: 420px;
      height: 420px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(184,155,99,.26), transparent 62%);
    }
    .hero::after {
      content: "";
      position: absolute;
      inset: auto -40px 40px auto;
      width: 280px;
      height: 280px;
      border: 1px solid rgba(255,255,255,.08);
      transform: rotate(45deg);
    }
    .hero-grid {
      position: relative;
      z-index: 1;
      display: grid;
      grid-template-columns: minmax(0, 1.45fr) minmax(260px, .75fr);
      gap: 20px;
      align-items: stretch;
    }
    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin: 0 0 12px;
      text-transform: uppercase;
      letter-spacing: .18em;
      font-size: .78rem;
      color: #d8c7a1;
    }
    .eyebrow::before {
      content: "";
      width: 42px;
      height: 1px;
      background: currentColor;
    }
    .hero h1 {
      margin: 0;
      max-width: 10ch;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: clamp(2.35rem, 5vw, 4.75rem);
      line-height: .95;
      letter-spacing: -.03em;
    }
    .hero p { margin: 0; }
    .hero-text {
      max-width: 62ch;
      margin-top: 16px;
      color: rgba(247, 241, 229, 0.82);
      font-size: 1rem;
      line-height: 1.7;
    }
    .hero-meta {
      margin-top: 20px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    .hero-meta span {
      display: inline-flex;
      align-items: center;
      min-height: 38px;
      padding: 0 14px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(255,255,255,.04);
      color: #f7f1e5;
      font-size: .83rem;
      text-transform: uppercase;
      letter-spacing: .12em;
    }
    .hero-side {
      position: relative;
      min-height: 280px;
      border-radius: 24px;
      padding: 22px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.02)),
        rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.08);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      backdrop-filter: blur(4px);
    }
    .hero-side::before {
      content: "";
      position: absolute;
      inset: 18px;
      background:
        linear-gradient(135deg, transparent 0 47%, rgba(184,155,99,.95) 47% 53%, transparent 53% 100%);
      opacity: .5;
      border-radius: 18px;
    }
    .hero-side::after {
      content: "";
      position: absolute;
      right: 28px;
      top: 24px;
      width: 86px;
      height: 86px;
      border-radius: 22px;
      background: rgba(255,255,255,.06);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.08);
    }
    .hero-side-copy {
      position: relative;
      z-index: 1;
      max-width: 260px;
      margin-top: auto;
    }
    .hero-side-copy strong {
      display: block;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: 1.3rem;
      margin-bottom: 8px;
    }
    .hero-side-copy p {
      color: rgba(247, 241, 229, 0.78);
      line-height: 1.65;
      font-size: .95rem;
    }
    .section-band {
      margin-top: 18px;
      background: rgba(255, 251, 244, 0.76);
      border: 1px solid rgba(17, 17, 17, 0.08);
      border-radius: 24px;
      padding: 16px;
      box-shadow: 0 12px 28px rgba(17,17,17,.05);
      backdrop-filter: blur(6px);
    }
    .section-band-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .section-kicker {
      margin: 0;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .18em;
      font-size: .72rem;
    }
    .section-band-title {
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: 1.3rem;
      margin: 4px 0 0;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .card {
      position: relative;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 16px;
      box-shadow: 0 10px 24px rgba(17,17,17,.05);
      overflow: hidden;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 auto auto 0;
      width: 100%;
      height: 4px;
      background: linear-gradient(90deg, var(--gold), transparent 80%);
    }
    .metric {
      min-height: 136px;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      background:
        linear-gradient(180deg, rgba(255,255,255,.3), transparent 56%),
        var(--card);
    }
    .metric .label {
      color: var(--muted);
      font-size: .76rem;
      text-transform: uppercase;
      letter-spacing: .14em;
    }
    .metric .value {
      font-size: clamp(1.5rem, 2vw, 2rem);
      font-weight: 800;
      line-height: 1.02;
      margin-top: 10px;
      letter-spacing: -.03em;
    }
    .row {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 14px;
      margin-top: 14px;
    }
    .toolbar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 12px;
      align-items: center;
    }
    input, select, button, textarea {
      font: inherit;
    }
    input, select, textarea {
      border: 1px solid rgba(17, 17, 17, 0.14);
      background: rgba(255,255,255,.8);
      border-radius: 14px;
      padding: 11px 13px;
      font-size: .95rem;
      color: var(--ink);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.7);
    }
    input::placeholder,
    textarea::placeholder {
      color: #8a7e70;
    }
    input:focus,
    select:focus,
    textarea:focus {
      outline: none;
      border-color: rgba(184, 155, 99, 0.95);
      box-shadow: 0 0 0 4px rgba(184, 155, 99, 0.16);
    }
    button {
      cursor: pointer;
      background: var(--accent);
      color: #f7f1e5;
      border: 1px solid var(--accent);
      border-radius: 999px;
      padding: 11px 15px;
      font-size: .9rem;
      letter-spacing: .04em;
      text-transform: uppercase;
      transition: transform .18s ease, background-color .18s ease, border-color .18s ease;
    }
    button:hover {
      transform: translateY(-1px);
      background: var(--accent-soft);
      border-color: var(--accent-soft);
    }
    button.secondary {
      background: rgba(255,255,255,.65);
      color: var(--ink);
      border-color: rgba(17, 17, 17, 0.12);
    }
    button.secondary:hover {
      background: rgba(255,255,255,.92);
      border-color: rgba(17,17,17,.2);
    }
    table { width: 100%; border-collapse: collapse; }
    th, td {
      text-align: left;
      padding: 12px 8px;
      border-bottom: 1px solid rgba(17,17,17,.08);
      font-size: .92rem;
    }
    th {
      color: var(--muted);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .08em;
      position: sticky;
      top: 0;
      background: rgba(255, 252, 246, 0.96);
      backdrop-filter: blur(4px);
    }
    .table-wrap {
      max-height: 520px;
      overflow: auto;
      border: 1px solid rgba(17,17,17,.08);
      border-radius: 18px;
      background: rgba(255,255,255,.55);
    }
    .pill {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 28px; height: 28px; border-radius: 999px; font-weight: 700; font-size: .8rem;
      color: white;
    }
    .V { background: var(--ok); }
    .E { background: var(--warn); }
    .D { background: var(--bad); }
    .muted { color: var(--muted); }
    ul.clean { list-style: none; padding: 0; margin: 0; }
    ul.clean li {
      display: flex; justify-content: space-between; gap: 8px;
      padding: 10px 0; border-bottom: 1px solid rgba(17,17,17,.08);
      font-size: .92rem;
    }
    .section-title {
      margin: 0 0 12px;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      font-size: 1.18rem;
      letter-spacing: -.02em;
    }
    .tabs {
      display: flex;
      gap: 10px;
      margin: 18px 0 10px;
      flex-wrap: wrap;
      padding: 10px;
      background: rgba(17,17,17,.92);
      border-radius: 24px;
      box-shadow: var(--shadow);
      position: sticky;
      top: 12px;
      z-index: 10;
    }
    .tab-btn {
      background: transparent;
      color: rgba(247, 241, 229, 0.74);
      border-color: transparent;
      padding-inline: 18px;
    }
    .tab-btn.secondary { background: transparent; color: rgba(247, 241, 229, 0.74); border-color: transparent; }
    .tab-btn.active {
      background: linear-gradient(135deg, #f1e3c4, #c8ab72);
      color: #111;
      border-color: rgba(255,255,255,.22);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.18);
    }
    .hidden { display: none; }
    .modal-backdrop {
      position: fixed; inset: 0; background: rgba(15, 23, 42, .45);
      display: none; align-items: center; justify-content: center; padding: 20px; z-index: 50;
    }
    .modal-backdrop.show { display: flex; }
    .modal-card {
      width: min(980px, 100%);
      max-height: min(90vh, 900px);
      overflow: auto;
      background: var(--card-strong);
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: 0 24px 60px rgba(15, 23, 42, .25);
      padding: 20px;
    }
    .modal-card.lg { width: min(1100px, 100%); }
    .modal-head {
      display: flex; justify-content: space-between; align-items: center; gap: 10px;
      position: sticky; top: 0; background: var(--card-strong); padding-bottom: 10px; z-index: 1;
    }
    .kv { display: grid; grid-template-columns: 180px 1fr; gap: 6px 10px; }
    .kv div:nth-child(odd) { color: var(--muted); }
    .score-box {
      display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 12px;
      background:
        linear-gradient(135deg, rgba(17,17,17,.98), rgba(41,41,41,.98)),
        linear-gradient(90deg, rgba(184,155,99,.16), transparent 70%);
      color: #f7f1e5;
      border: 1px solid rgba(17,17,17,.9);
      border-radius: 22px;
      padding: 18px;
      margin: 10px 0 14px;
    }
    .score-num { font-size: 2rem; font-weight: 800; text-align: center; }
    .mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .chip {
      display:inline-block;
      border:1px solid rgba(17,17,17,.12);
      padding:6px 10px;
      border-radius:999px;
      margin:2px 4px 2px 0;
      font-size:.85rem;
      background: rgba(255,255,255,.76);
    }
    .pitch-wrap {
      display: grid;
      grid-template-columns: 1fr 260px;
      gap: 12px;
      align-items: stretch;
    }
    .pitch {
      position: relative;
      min-height: 420px;
      border-radius: 14px;
      background:
        linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02)),
        #173d25;
      border: 2px solid #d8f0de;
      overflow: hidden;
    }
    .pitch::before {
      content: "";
      position: absolute;
      inset: 14px;
      border: 2px solid #e9f7ed;
      border-radius: 8px;
      pointer-events: none;
    }
    .pitch::after {
      content: "";
      position: absolute;
      left: 16px; right: 16px; top: 50%;
      border-top: 2px solid #e9f7ed;
      transform: translateY(-1px);
      pointer-events: none;
    }
    .pitch-center-circle {
      position: absolute;
      left: 50%; top: 50%;
      width: 72px; height: 72px;
      border: 2px solid #e9f7ed; border-radius: 999px;
      transform: translate(-50%, -50%);
      pointer-events: none;
    }
    .pitch-line-label {
      position: absolute;
      left: 14px;
      color: #d8f0de;
      font-size: .75rem;
      font-weight: 700;
      letter-spacing: .04em;
      text-transform: uppercase;
      opacity: .95;
      transform: translateY(-50%);
    }
    .pitch-player {
      position: absolute;
      transform: translate(-50%, -50%);
      text-align: center;
      max-width: 130px;
    }
    .pitch-dot {
      width: 30px;
      height: 30px;
      border-radius: 999px;
      margin: 0 auto 6px;
      background: #f5f8f6;
      color: #133b23;
      border: 1px solid #0b3d24;
      display: grid;
      place-items: center;
      font-weight: 700;
      font-size: .82rem;
    }
    .pitch-name {
      color: #eef9f1;
      font-size: .78rem;
      line-height: 1.15;
      font-weight: 700;
      text-shadow: 0 1px 1px rgba(0,0,0,.35);
      background: rgba(7, 35, 20, .28);
      border-radius: 8px;
      padding: 2px 5px;
      display: inline-block;
    }
    .pitch-name .goal-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: #ffd54a;
      box-shadow: 0 0 0 1px rgba(0,0,0,.18);
      margin-left: 6px;
      vertical-align: middle;
    }
    .pitch-legend {
      margin-top: 8px;
      color: #d8f0de;
      font-size: .78rem;
      display: flex;
      align-items: center;
      gap: 6px;
      padding-left: 8px;
    }
    .pitch-legend .goal-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: #ffd54a;
      box-shadow: 0 0 0 1px rgba(0,0,0,.18);
    }
    .reserve-list {
      background: rgba(255,255,255,.76);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px;
    }
    .reserve-list ul {
      margin: 0;
      padding-left: 18px;
      max-height: 380px;
      overflow: auto;
    }
    .goal-builder {
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.56);
    }
    .goal-builder .goal-controls {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      margin-bottom: 8px;
    }
    .goal-builder .goal-controls .full-row {
      grid-column: 1 / -1;
    }
    .goal-list {
      min-height: 46px;
      border: 1px dashed rgba(17,17,17,.18);
      border-radius: 14px;
      padding: 8px;
      background: rgba(255,255,255,.84);
    }
    .goal-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid rgba(17,17,17,.12);
      border-radius: 999px;
      padding: 6px 10px;
      margin: 3px 4px 3px 0;
      background: rgba(184, 155, 99, 0.14);
      font-size: .88rem;
    }
    .goal-chip button {
      border: 0;
      background: transparent;
      color: #5a4220;
      padding: 0;
      line-height: 1;
      cursor: pointer;
      font-weight: 700;
    }
    .goal-help {
      color: var(--muted);
      font-size: .82rem;
      margin-top: 6px;
    }
    .edit-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .edit-grid .full { grid-column: 1 / -1; }
    .edit-grid .field label {
      display: block;
      color: var(--muted);
      font-size: .85rem;
      margin-bottom: 4px;
    }
    .edit-grid .field input,
    .edit-grid .field select {
      width: 100%;
    }
    .edit-grid textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px;
      min-height: 88px;
    }
    #tab-jogos,
    #tab-futuros,
    #tab-retrospecto,
    #tab-listas,
    #tab-registro {
      animation: fadeUp .28s ease;
    }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
    @media (max-width: 900px) {
      .topbar-inner { align-items: flex-start; flex-direction: column; }
      .masthead-notes { text-align: left; max-width: none; }
      .hero-grid { grid-template-columns: 1fr; }
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .row { grid-template-columns: 1fr; }
      .mini-grid { grid-template-columns: 1fr; }
      .kv { grid-template-columns: 130px 1fr; }
      .goal-builder .goal-controls { grid-template-columns: 1fr; }
      .pitch-wrap { grid-template-columns: 1fr; }
      .edit-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 560px) {
      .wrap { padding: 16px; }
      .topbar-inner { padding: 14px 16px; }
      .hero { padding: 22px 18px; }
      .grid { grid-template-columns: 1fr; }
      .hero h1 { font-size: 2.5rem; }
      .tabs {
        position: static;
        border-radius: 20px;
      }
    }
  </style>
</head>
<body>
  <div class="site-shell">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand-block">
          <div class="brand-mark" aria-hidden="true"></div>
          <div class="brand-copy">
            <small>Club de Regatas Vasco da Gama</small>
            <strong>StatsVasco Web</strong>
          </div>
        </div>
        <div class="masthead-notes">Base histórica, jogos, retrospectos e registro inspirados na atualização da identidade visual cruzmaltina.</div>
      </div>
    </header>

    <div class="wrap">
    <section class="hero">
      <div class="hero-grid">
        <div>
          <p class="eyebrow">Um só Vasco</p>
          <h1>StatsVasco Web</h1>
          <p class="hero-text">Dados consolidados do clube em uma interface editorial, sóbria e direta, com contraste forte, diagonais marcantes e acabamento inspirado no site institucional do Vasco.</p>
          <div class="hero-meta">
            <span>Jogos</span>
            <span>Retrospecto</span>
            <span>Elenco</span>
            <span>Registro</span>
          </div>
        </div>
        <aside class="hero-side">
          <div class="hero-side-copy">
            <strong>Memória, contexto e jogo.</strong>
            <p>Uma leitura mais clara do histórico vascaíno, com visual alinhado ao escudo, à faixa diagonal e à sobriedade preto, branco e dourado.</p>
          </div>
        </aside>
      </div>
    </section>

    <section class="section-band">
      <div class="section-band-header">
        <div>
          <p class="section-kicker">Panorama</p>
          <div class="section-band-title">Resumo do acervo</div>
        </div>
      </div>
      <section class="grid" id="metrics"></section>
    </section>

    <div class="tabs">
      <button class="tab-btn active" data-tab="jogos">Jogos</button>
      <button class="tab-btn secondary" data-tab="futuros">Jogos Futuros</button>
      <button class="tab-btn secondary" data-tab="retrospecto">Retrospecto</button>
      <button class="tab-btn secondary" data-tab="listas">Listas Auxiliares</button>
      <button class="tab-btn secondary" data-tab="registro">Registrar Jogo</button>
    </div>

    <section id="tab-jogos">
      <div class="row">
        <div class="card">
          <div class="toolbar">
            <input id="busca-jogos" type="search" placeholder="Buscar por adversário, competição ou técnico" style="min-width: 320px; flex: 1;">
            <button id="btn-buscar">Buscar</button>
            <button id="btn-limpar" class="secondary">Limpar</button>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Adversário</th>
                  <th>Competição</th>
                  <th>Local</th>
                  <th>Placar</th>
                  <th>Res.</th>
                  <th>Técnico</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-jogos"></tbody>
            </table>
          </div>
        </div>
        <div class="card">
          <h3 class="section-title">Top Competições</h3>
          <ul class="clean" id="competicoes-top"></ul>
        </div>
      </div>
    </section>

    <section id="tab-futuros" class="hidden">
      <div class="card">
        <h3 class="section-title">Próximos Jogos</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Jogo</th>
                <th>Campeonato</th>
                <th>Mando</th>
              </tr>
            </thead>
            <tbody id="tbody-futuros"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="tab-retrospecto" class="hidden">
      <div class="card">
        <h3 class="section-title">Retrospecto por Adversário</h3>
        <div class="toolbar">
          <select id="retro-adversario-select" style="min-width:320px; flex:1;">
            <option value="">Selecione um adversário...</option>
          </select>
          <button id="retro-atualizar" class="secondary" type="button">Atualizar</button>
        </div>
        <div id="retro-resumo" class="muted" style="margin-bottom:10px;">
          Selecione um adversário para ver o retrospecto.
        </div>
        <div class="card" style="margin-bottom:10px;">
          <div class="muted">Gols somados</div>
          <div id="retro-gols-somados" class="value" style="font-size:1.25rem; font-weight:700;">Vasco 0 x 0 Adversário</div>
        </div>
        <div class="mini-grid" style="margin-bottom:10px;">
          <div class="card">
            <div class="muted">Jogos</div>
            <div id="retro-total" class="value" style="font-size:1.3rem; font-weight:700;">0</div>
          </div>
          <div class="card">
            <div class="muted">Aproveitamento</div>
            <div id="retro-aproveitamento" class="value" style="font-size:1.3rem; font-weight:700;">0%</div>
          </div>
          <div class="card">
            <div class="muted">V / E / D</div>
            <div id="retro-ved" class="value" style="font-size:1.3rem; font-weight:700;">0 / 0 / 0</div>
          </div>
          <div class="card">
            <div class="muted">Saldo</div>
            <div id="retro-saldo" class="value" style="font-size:1.3rem; font-weight:700;">0</div>
          </div>
        </div>
        <div class="mini-grid" style="margin-bottom:10px;">
          <div class="card">
            <div class="muted">Placar mais elástico (Vasco)</div>
            <div id="retro-elastico-vasco">—</div>
          </div>
          <div class="card">
            <div class="muted" id="retro-elastico-adv-titulo">Placar mais elástico (Adversário)</div>
            <div id="retro-elastico-adv">—</div>
          </div>
          <div class="card">
            <div class="muted" id="retro-jejum-adv-titulo">Adversário sem vencer</div>
            <div id="retro-jejum-adv">—</div>
          </div>
          <div class="card">
            <div class="muted">Vasco sem vencer</div>
            <div id="retro-jejum-vasco">—</div>
          </div>
        </div>
        <div class="mini-grid" style="margin-bottom:10px;">
          <div class="card">
            <div class="muted">Artilheiros do Vasco</div>
            <div id="retro-art-vasco">—</div>
          </div>
          <div class="card">
            <div class="muted" id="retro-art-adv-titulo">Artilheiros do adversário</div>
            <div id="retro-art-adv">—</div>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead id="retro-head">
              <tr>
                <th data-col="data" style="cursor:pointer">Data</th>
                <th data-col="competicao" style="cursor:pointer">Competição</th>
                <th data-col="local" style="cursor:pointer">Local</th>
                <th data-col="placar" style="cursor:pointer">Placar</th>
                <th data-col="resultado" style="cursor:pointer">Res.</th>
                <th data-col="gols_vasco" style="cursor:pointer">Gols do Vasco</th>
                <th data-col="gols_adversario" style="cursor:pointer">Gols do Adversário</th>
              </tr>
            </thead>
            <tbody id="tbody-retro"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="tab-listas" class="hidden">
      <div class="row">
        <div class="card">
          <h3 class="section-title">Resumo das Listas</h3>
          <ul class="clean" id="listas-resumo"></ul>
        </div>
        <div class="card">
          <h3 class="section-title">Técnicos</h3>
          <ul class="clean" id="lista-tecnicos"></ul>
        </div>
      </div>
    </section>

    <section id="tab-registro" class="hidden">
      <div class="row">
        <div class="card">
          <h3 class="section-title">Dados da Partida</h3>
          <div class="toolbar">
            <input id="reg-data" placeholder="dd/mm/aaaa" style="width:140px">
            <input id="reg-tecnico" placeholder="Técnico" list="dl-tecnicos" style="min-width:240px; flex:1">
            <input id="reg-adversario" placeholder="Adversário" list="dl-clubes" style="min-width:220px; flex:1">
            <select id="reg-local">
              <option value="">Sem informação</option>
              <option value="casa">Casa</option>
              <option value="fora">Fora</option>
            </select>
          </div>
          <div class="toolbar">
            <input id="reg-competicao" placeholder="Competição" list="dl-competicoes" style="min-width:280px; flex:1">
            <input id="reg-posicao" placeholder="Posição na tabela (Brasileirão)" style="width:240px">
            <input id="reg-placar-vasco" type="number" min="0" placeholder="Gols Vasco" style="width:130px">
            <input id="reg-placar-adv" type="number" min="0" placeholder="Gols Adv" style="width:130px">
          </div>

          <h3 class="section-title" style="margin-top:16px">Gols da Partida</h3>
          <div class="row" style="margin-top:0; grid-template-columns:1fr 1fr;">
            <div>
              <label class="muted">Gols do Vasco</label>
              <div class="goal-builder" id="goal-builder-vasco">
                <div class="goal-controls">
                  <select id="reg-gol-vasco-select">
                    <option value="">Selecionar titular/reserva...</option>
                  </select>
                  <button id="reg-gol-vasco-add" type="button">Adicionar</button>
                  <input id="reg-gol-vasco-input" class="full-row" type="text" placeholder="Nome livre (ex.: gol contra)">
                </div>
                <div id="reg-gols-vasco-list" class="goal-list"></div>
                <div class="goal-help">Selecionar adiciona automaticamente. Digitando, aperte Enter para adicionar.</div>
                <textarea id="reg-gols-vasco" hidden></textarea>
              </div>
            </div>
            <div>
              <label class="muted">Gols do Adversário</label>
              <div class="goal-builder" id="goal-builder-contra">
                <div class="goal-controls">
                  <select id="reg-gol-contra-select">
                    <option value="">Selecionar jogador adversário...</option>
                  </select>
                  <button id="reg-gol-contra-add" type="button">Adicionar</button>
                  <input id="reg-gol-contra-input" class="full-row" type="text" placeholder="Nome livre do adversário">
                </div>
                <div id="reg-gols-contra-list" class="goal-list"></div>
                <div class="goal-help">Selecionar adiciona automaticamente. Digitando, aperte Enter para adicionar.</div>
                <textarea id="reg-gols-contra" hidden></textarea>
              </div>
            </div>
          </div>

          <h3 class="section-title" style="margin-top:16px">Observações</h3>
          <textarea id="reg-observacao" rows="4" style="width:100%; border:1px solid var(--line); border-radius:10px; padding:10px;" placeholder="Observações da partida"></textarea>

          <div class="toolbar" style="margin-top:12px">
            <button id="btn-salvar-partida">Salvar Partida</button>
            <button id="btn-reset-registro" class="secondary">Limpar</button>
            <button id="btn-carregar-escalacao" class="secondary">Carregar Escalação Padrão do Elenco</button>
          </div>
          <div id="registro-status" class="muted"></div>
        </div>

        <div class="card">
          <h3 class="section-title">Escalação da Partida (simplificada)</h3>
          <p class="muted" style="margin-top:0">
            Mesmas regras do desktop para validação: 11 titulares, 1 goleiro titular, mínimo 4 reservas e todos do elenco (exceto emprestados) em alguma lista.
          </p>
          <div id="escalacao-resumo-web" class="muted" style="margin-bottom:10px"></div>
          <div class="table-wrap" style="max-height:620px; overflow:auto;">
            <div id="escalacao-editor"></div>
          </div>
        </div>
      </div>

      <datalist id="dl-clubes"></datalist>
      <datalist id="dl-tecnicos"></datalist>
      <datalist id="dl-competicoes"></datalist>
    </section>
  </div>
  </div>

  <div id="jogo-modal" class="modal-backdrop" aria-hidden="true">
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="jogo-modal-title">
      <div class="modal-head">
        <h3 id="jogo-modal-title" class="section-title" style="margin:0">Detalhes do Jogo</h3>
        <button id="jogo-modal-close" class="secondary" type="button">Fechar</button>
      </div>
      <div id="jogo-modal-content"></div>
    </div>
  </div>

  <div id="edit-jogo-modal" class="modal-backdrop" aria-hidden="true">
    <div class="modal-card lg" role="dialog" aria-modal="true" aria-labelledby="edit-jogo-modal-title">
      <div class="modal-head">
        <h3 id="edit-jogo-modal-title" class="section-title" style="margin:0">Editar Jogo</h3>
        <button id="edit-jogo-modal-close" class="secondary" type="button">Fechar</button>
      </div>
      <div id="edit-jogo-status" class="muted" style="margin-bottom:10px"></div>
      <div class="edit-grid">
        <div class="field"><label>Data</label><input id="edit-data" placeholder="dd/mm/aaaa"></div>
        <div class="field"><label>Técnico</label><input id="edit-tecnico" list="dl-tecnicos"></div>
        <div class="field"><label>Adversário</label><input id="edit-adversario" list="dl-clubes"></div>
        <div class="field"><label>Local</label><select id="edit-local"><option value="">Sem informação</option><option value="casa">Casa</option><option value="fora">Fora</option></select></div>
        <div class="field"><label>Competição</label><input id="edit-competicao" list="dl-competicoes"></div>
        <div class="field"><label>Horário</label><input id="edit-horario" placeholder="Ex.: 21:30"></div>
        <div class="field"><label>Estádio</label><input id="edit-estadio" placeholder="Local da partida"></div>
        <div class="field"><label>Capitão</label><input id="edit-capitao" placeholder="Capitão do jogo"></div>
        <div class="field"><label>Posição na tabela (Brasileirão)</label><input id="edit-posicao_tabela"></div>
        <div class="field"><label>Público pagante</label><input id="edit-publico-pagante" type="number" min="0"></div>
        <div class="field"><label>Público presente</label><input id="edit-publico-presente" type="number" min="0"></div>
        <div class="field"><label>Renda</label><input id="edit-renda" placeholder="Ex.: 1250000,50"></div>
        <div class="field"><label>Gols Vasco</label><input id="edit-placar-vasco" type="number" min="0"></div>
        <div class="field"><label>Gols Adversário</label><input id="edit-placar-adv" type="number" min="0"></div>
        <div class="field"><label>Gols do Vasco (1 nome por linha)</label><textarea id="edit-gols-vasco"></textarea></div>
        <div class="field"><label>Gols do Adversário (1 nome por linha)</label><textarea id="edit-gols-contra"></textarea></div>
        <div class="field full"><label>Observações</label><textarea id="edit-observacao" style="min-height:100px"></textarea></div>
        <div class="field full">
          <label>Escalação da Partida (simplificada)</label>
          <div class="edit-grid" id="edit-escalacao-grid"></div>
        </div>
        <div class="field full" style="display:flex; gap:8px; justify-content:flex-end">
          <button id="edit-jogo-carregar-padrao" class="secondary" type="button">Carregar Escalação Padrão</button>
          <button id="edit-jogo-salvar" type="button">Salvar Alterações</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    const $ = (sel) => document.querySelector(sel);
    const escapeHtml = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));

    async function getJSON(url) {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    }

    async function postJSON(url, payload) {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.erro || data.message || `HTTP ${res.status}`);
      return data;
    }

    function renderMetrics(resumo) {
      const items = [
        ["Jogos", resumo.total_jogos],
        ["Vitórias / Empates / Derrotas", `${resumo.vitorias} / ${resumo.empates} / ${resumo.derrotas}`],
        ["Gols Pró / Contra", `${resumo.gols_pro} / ${resumo.gols_contra}`],
        ["Saldo", resumo.saldo],
      ];
      $("#metrics").innerHTML = items.map(([label, value]) => `
        <div class="card metric">
          <div class="label">${escapeHtml(label)}</div>
          <div class="value">${escapeHtml(value)}</div>
        </div>
      `).join("");
      $("#competicoes-top").innerHTML = (resumo.competicoes_top || []).map(([nome, qtd]) => `
        <li><span>${escapeHtml(nome)}</span><strong>${qtd}</strong></li>
      `).join("") || `<li><span class="muted">Sem dados</span></li>`;
    }

    function renderJogos(items) {
      $("#tbody-jogos").innerHTML = items.map(j => `
        <tr>
          <td>${escapeHtml(j.data)}</td>
          <td>${escapeHtml(j.adversario)}</td>
          <td>${escapeHtml(j.competicao)}</td>
          <td>${escapeHtml(j.local)}</td>
          <td>${escapeHtml(j.vasco)} x ${escapeHtml(j.adversario_gols)}</td>
          <td><span class="pill ${escapeHtml(j.resultado)}">${escapeHtml(j.resultado)}</span></td>
          <td>${escapeHtml(j.tecnico)}</td>
          <td>
            <button class="btn-ver-jogo" data-idx="${escapeHtml(j.idx)}" type="button">Ver</button>
            <button class="secondary btn-editar-jogo" data-idx="${escapeHtml(j.idx)}" type="button">Editar</button>
          </td>
        </tr>
      `).join("") || `<tr><td colspan="8" class="muted">Nenhum jogo encontrado.</td></tr>`;
    }

    function fmtGoleadores(lista, isVasco = true) {
      if (!Array.isArray(lista) || !lista.length) return `<span class="muted">Nenhum gol informado</span>`;
      return lista.map(g => {
        if (typeof g === "string") return `<li>${escapeHtml(g)}</li>`;
        const nome = g?.nome ?? "";
        const gols = g?.gols ?? 0;
        const extra = isVasco && g?.saiu_do_banco ? " (saiu do banco)" : "";
        return `<li><strong>${escapeHtml(nome)}</strong> - ${escapeHtml(gols)} gol(s)${escapeHtml(extra)}</li>`;
      }).join("");
    }

    function chipsFromList(list) {
      if (!Array.isArray(list) || !list.length) return `<span class="muted">Nenhum</span>`;
      return list.map(n => `<span class="chip">${escapeHtml(n)}</span>`).join("");
    }

    function renderEscalacaoDetalhe(esc, golsVasco = []) {
      const tit = esc?.titulares_por_posicao || {};
      const goleadoresVasco = new Set(
        (Array.isArray(golsVasco) ? golsVasco : [])
          .map(g => (typeof g === "string" ? g : g?.nome))
          .map(n => String(n || "").trim().toLowerCase())
          .filter(Boolean)
      );
      const lineDefs = [
        { sigla: "ATA", y: 16, nomes: (tit["Atacante"] || []) },
        { sigla: "MEI", y: 34, nomes: (tit["Meio-Campista"] || []) },
        { sigla: "VOL", y: 50, nomes: (tit["Volante"] || []) },
        { sigla: "DEF", y: 68, nomes: [...(tit["Lateral-Esquerdo"] || []), ...(tit["Zagueiro"] || []), ...(tit["Lateral-Direito"] || [])] },
        { sigla: "GOL", y: 84, nomes: (tit["Goleiro"] || []) },
      ];

      const pitchPlayers = [];
      lineDefs.forEach((line) => {
        const nomes = Array.isArray(line.nomes) ? line.nomes : [];
        nomes.forEach((nome, i) => {
          const x = ((i + 1) / (nomes.length + 1)) * 100;
          const marcou = goleadoresVasco.has(String(nome || "").trim().toLowerCase());
          pitchPlayers.push(`
            <div class="pitch-player" style="left:${x}%; top:${line.y}%;">
              <div class="pitch-dot">${i + 1}</div>
              <div class="pitch-name">${escapeHtml(nome)}${marcou ? '<span class="goal-dot" title="Marcou gol"></span>' : ''}</div>
            </div>
          `);
        });
      });

      const lineLabels = lineDefs.map(line => `
        <div class="pitch-line-label" style="top:${line.y}%;">${escapeHtml(line.sigla)}</div>
      `).join("");

      const reservas = Array.isArray(esc?.reservas) ? esc.reservas : [];
      const reservasHtml = reservas.length
        ? `<ul>${reservas.map(n => `<li>${escapeHtml(n)}</li>`).join("")}</ul>`
        : `<span class="muted">Nenhum reserva informado</span>`;

      return `
        <div class="pitch-wrap">
          <div class="pitch">
            <div class="pitch-center-circle"></div>
            ${lineLabels}
            ${pitchPlayers.join("") || `<div class="muted" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);color:#eef9f1">Sem titulares</div>`}
          </div>
          <div class="reserve-list">
            <h5 class="section-title" style="margin:0 0 8px">Reservas</h5>
            ${reservasHtml}
          </div>
        </div>
        <div class="pitch-legend"><span class="goal-dot"></span><span>Jogador que marcou gol</span></div>
        <div class="mini-grid" style="margin-top:12px">
          <div class="card" style="padding:10px"><div class="muted" style="margin-bottom:6px">Não Relacionados</div>${chipsFromList(esc?.nao_relacionados || [])}</div>
          <div class="card" style="padding:10px"><div class="muted" style="margin-bottom:6px">Lesionados</div>${chipsFromList(esc?.lesionados || [])}</div>
          <div class="card" style="padding:10px"><div class="muted" style="margin-bottom:6px">Suspensos</div>${chipsFromList(esc?.suspensos || [])}</div>
          <div class="card" style="padding:10px"><div class="muted" style="margin-bottom:6px">Servindo a seleção</div>${chipsFromList(esc?.servindo_selecao || [])}</div>
        </div>
      `;
    }

    function openJogoModal() {
      $("#jogo-modal").classList.add("show");
      $("#jogo-modal").setAttribute("aria-hidden", "false");
    }

    function closeJogoModal() {
      $("#jogo-modal").classList.remove("show");
      $("#jogo-modal").setAttribute("aria-hidden", "true");
    }

    async function verDetalhesJogo(idx) {
      try {
        const j = await getJSON(`/api/jogos/${idx}`);
        $("#jogo-modal-title").textContent = `Detalhes: Vasco x ${j.adversario || ""}`;
        $("#jogo-modal-content").innerHTML = `
          <div class="score-box">
            <div style="text-align:center"><div class="muted">Vasco</div><div class="score-num">${escapeHtml(j.placar?.vasco ?? "-")}</div></div>
            <div style="font-weight:700; color:var(--muted)">x</div>
            <div style="text-align:center"><div class="muted">${escapeHtml(j.adversario || "Adversário")}</div><div class="score-num">${escapeHtml(j.placar?.adversario ?? "-")}</div></div>
          </div>

          <div class="card" style="margin-bottom:12px">
            <div class="kv">
              <div>Data</div><div>${escapeHtml(j.data || "")}</div>
              <div>Competição</div><div>${escapeHtml(j.competicao || "")}</div>
              <div>Local</div><div>${escapeHtml(j.local || "")}</div>
              <div>Resultado</div><div><span class="pill ${escapeHtml(j.resultado || '?')}">${escapeHtml(j.resultado || "?")}</span></div>
              <div>Técnico</div><div>${escapeHtml(j.tecnico || "")}</div>
              <div>Posição na tabela</div><div>${j.posicao_tabela == null ? '<span class="muted">-</span>' : escapeHtml(j.posicao_tabela)}</div>
            </div>
          </div>

          <div class="mini-grid">
            <div class="card">
              <h4 class="section-title" style="margin:0 0 8px">Gols do Vasco</h4>
              <ul>${fmtGoleadores(j.gols_vasco, true)}</ul>
            </div>
            <div class="card">
              <h4 class="section-title" style="margin:0 0 8px">Gols do Adversário</h4>
              <ul>${fmtGoleadores(j.gols_adversario, false)}</ul>
            </div>
          </div>

          <div class="card" style="margin-top:12px">
            <h4 class="section-title" style="margin:0 0 8px">Escalação da Partida</h4>
            ${renderEscalacaoDetalhe(j.escalacao_partida || {}, j.gols_vasco || [])}
          </div>

          <div class="card" style="margin-top:12px">
            <h4 class="section-title" style="margin:0 0 8px">Observações</h4>
            <div>${j.observacao ? escapeHtml(j.observacao).replaceAll("\\n","<br>") : '<span class="muted">Sem observações</span>'}</div>
          </div>
        `;
        openJogoModal();
      } catch (err) {
        alert(`Erro ao carregar detalhes do jogo: ${err.message}`);
      }
    }

    function renderFuturos(items) {
      $("#tbody-futuros").innerHTML = items.map(j => `
        <tr>
          <td>${escapeHtml(j.data)}</td>
          <td>${escapeHtml(j.jogo)}</td>
          <td>${escapeHtml(j.campeonato)}</td>
          <td>${j.em_casa ? "Casa" : "Fora"}</td>
        </tr>
      `).join("") || `<tr><td colspan="4" class="muted">Nenhum jogo futuro.</td></tr>`;
    }

    function renderListas(dados) {
      const keys = [
        ["clubes_adversarios", "Clubes adversários"],
        ["jogadores_vasco", "Jogadores Vasco"],
        ["jogadores_contra", "Jogadores adversários"],
        ["competicoes", "Competições"],
        ["tecnicos", "Técnicos"],
      ];
      $("#listas-resumo").innerHTML = keys.map(([k, label]) => `
        <li>
          <span>${escapeHtml(label)}</span>
          <strong>${Array.isArray(dados[k]) ? dados[k].length : 0}</strong>
        </li>
      `).join("");
      $("#lista-tecnicos").innerHTML = (dados.tecnicos || []).map(nome => `
        <li>
          <span>${escapeHtml(nome)}</span>
          <strong>${nome === dados.tecnico_atual ? "Atual" : ""}</strong>
        </li>
      `).join("") || `<li><span class="muted">Sem técnicos</span></li>`;
    }

    const registroState = {
      listas: null,
      elenco: null,
      escalacaoPadrao: null,
      gols: { vasco: [], contra: [] },
    };
    const editState = { idx: null, escalacaoPadrao: null };
    const retroState = { adversario: "", partidas: [], sortCol: "data", sortReverse: true };

    function parseDataBR(txt) {
      const m = String(txt || "").trim().match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
      if (!m) return null;
      const d = Number(m[1]);
      const mo = Number(m[2]) - 1;
      const y = Number(m[3]);
      const dt = new Date(y, mo, d);
      return Number.isNaN(dt.getTime()) ? null : dt;
    }

    function parsePlacar(txt) {
      const m = String(txt || "").trim().match(/^(\d+)\s*x\s*(\d+)$/i);
      if (!m) return [0, 0];
      return [Number(m[1]), Number(m[2])];
    }

    function chaveOrdenacaoRetro(partida, coluna) {
      if (coluna === "data") return parseDataBR(partida?.data) || new Date(0);
      if (coluna === "placar") {
        const [v, a] = parsePlacar(partida?.placar);
        return `${String(v).padStart(3, "0")}-${String(a).padStart(3, "0")}`;
      }
      return String(partida?.[coluna] || "").toLowerCase();
    }

    function renderRetroPartidasOrdenado() {
      const partidas = [...(retroState.partidas || [])].sort((a, b) => {
        const ka = chaveOrdenacaoRetro(a, retroState.sortCol);
        const kb = chaveOrdenacaoRetro(b, retroState.sortCol);
        if (ka < kb) return retroState.sortReverse ? 1 : -1;
        if (ka > kb) return retroState.sortReverse ? -1 : 1;
        return 0;
      });
      $("#tbody-retro").innerHTML = partidas.map((p) => `
        <tr>
          <td>${escapeHtml(p.data || "")}</td>
          <td>${escapeHtml(p.competicao || "")}</td>
          <td>${escapeHtml(p.local || "")}</td>
          <td>${escapeHtml(p.placar || "")}</td>
          <td><span class="pill ${escapeHtml(p.resultado || "?")}">${escapeHtml(p.resultado || "?")}</span></td>
          <td>${escapeHtml(p.gols_vasco || "—")}</td>
          <td>${escapeHtml(p.gols_adversario || "—")}</td>
        </tr>
      `).join("") || `<tr><td colspan="7" class="muted">Nenhuma partida encontrada.</td></tr>`;
    }

    function maiorElastico(partidas, lado = "vasco") {
      let best = null;
      let diff = -1;
      (partidas || []).forEach((p) => {
        const [v, a] = parsePlacar(p.placar);
        const d = lado === "vasco" ? (v - a) : (a - v);
        if (d <= 0) return;
        if (d > diff) {
          diff = d;
          best = p;
        }
      });
      if (!best) return "—";
      return `${best.placar} | Data: ${best.data}`;
    }

    function maiorJejum(partidas, semVencer) {
      let maxLen = 0;
      let curLen = 0;
      let ini = null;
      let fim = null;
      let curIni = null;
      let emAndamento = false;
      const asc = [...(partidas || [])].sort((a, b) => {
        const da = parseDataBR(a.data) || new Date(0);
        const db = parseDataBR(b.data) || new Date(0);
        return da - db;
      });
      asc.forEach((p) => {
        const rt = String(p.resultado_texto || "").trim();
        if (semVencer.has(rt)) {
          curLen += 1;
          if (!curIni) curIni = p;
          if (curLen > maxLen) {
            maxLen = curLen;
            ini = curIni;
            fim = p;
            emAndamento = false;
          }
        } else {
          curLen = 0;
          curIni = null;
        }
      });
      const ultimo = asc.length ? asc[asc.length - 1] : null;
      if (ultimo && fim && String(ultimo.data || "") === String(fim.data || "") && semVencer.has(String(ultimo.resultado_texto || ""))) {
        emAndamento = true;
      }
      return { qtd: maxLen, inicio: ini, fim, em_andamento: emAndamento };
    }

    function fmtJejumCard(info) {
      if (!info || !info.qtd) return "0 jogo(s) | Período: —";
      const ini = info.inicio?.data || "—";
      const fim = info.em_andamento ? "hoje" : (info.fim?.data || "—");
      return `${info.qtd} jogo(s) | ${ini} até ${fim}`;
    }

    function limparRetro(msg) {
      retroState.partidas = [];
      retroState.sortCol = "data";
      retroState.sortReverse = true;
      $("#retro-resumo").textContent = msg || "Selecione um adversário para ver o retrospecto.";
      $("#retro-total").textContent = "0";
      $("#retro-aproveitamento").textContent = "0%";
      $("#retro-ved").textContent = "0 / 0 / 0";
      $("#retro-saldo").textContent = "0";
      $("#retro-gols-somados").textContent = "Vasco 0 x 0 Adversário";
      $("#retro-elastico-vasco").textContent = "—";
      $("#retro-elastico-adv").textContent = "—";
      $("#retro-jejum-adv").textContent = "—";
      $("#retro-jejum-vasco").textContent = "—";
      $("#retro-art-vasco").textContent = "—";
      $("#retro-art-adv").textContent = "—";
      $("#retro-elastico-adv-titulo").textContent = "Placar mais elástico (Adversário)";
      $("#retro-jejum-adv-titulo").textContent = "Adversário sem vencer";
      $("#retro-art-adv-titulo").textContent = "Artilheiros do adversário";
      renderRetroPartidasOrdenado();
    }

    function renderRetroDados(retro) {
      const total = Number(retro?.total_partidas || 0);
      const adversario = String(retro?.adversario || "").trim();
      if (!adversario || total === 0) {
        limparRetro(adversario ? `${adversario}: sem partidas registradas contra o Vasco.` : "Selecione um adversário para ver o retrospecto.");
        return;
      }
      const v = Number(retro.vitorias || 0);
      const e = Number(retro.empates || 0);
      const d = Number(retro.derrotas || 0);
      const gv = Number(retro.gols_vasco || 0);
      const ga = Number(retro.gols_adversario || 0);
      const aproveitamento = total ? (((v * 3 + e) / (total * 3)) * 100) : 0;
      const resumo = `${adversario} | Jogos: ${total} | V/E/D: ${v}/${e}/${d} | Gols totais: Vasco ${gv} x ${ga} ${adversario}`;

      $("#retro-resumo").textContent = resumo;
      $("#retro-total").textContent = String(total);
      $("#retro-aproveitamento").textContent = `${Math.round(aproveitamento)}%`;
      $("#retro-ved").textContent = `${v} / ${e} / ${d}`;
      $("#retro-saldo").textContent = String(gv - ga);
      $("#retro-gols-somados").textContent = `Vasco ${gv} x ${ga} ${adversario}`;
      $("#retro-art-vasco").textContent = retro.artilheiros_vasco || "—";
      $("#retro-art-adv").textContent = retro.artilheiros_adversario || "—";
      $("#retro-elastico-adv-titulo").textContent = `Placar mais elástico (${adversario})`;
      $("#retro-jejum-adv-titulo").textContent = `${adversario} sem vencer`;
      $("#retro-art-adv-titulo").textContent = `Artilheiros do ${adversario}`;

      retroState.partidas = Array.isArray(retro.partidas) ? retro.partidas : [];
      retroState.sortCol = "data";
      retroState.sortReverse = true;
      $("#retro-elastico-vasco").textContent = maiorElastico(retroState.partidas, "vasco");
      $("#retro-elastico-adv").textContent = maiorElastico(retroState.partidas, "adversario");
      $("#retro-jejum-adv").textContent = fmtJejumCard(maiorJejum(retroState.partidas, new Set(["Vitória", "Empate"])));
      $("#retro-jejum-vasco").textContent = fmtJejumCard(maiorJejum(retroState.partidas, new Set(["Derrota", "Empate"])));
      renderRetroPartidasOrdenado();
    }

    async function carregarRetroAdversario(adversario) {
      const alvo = String(adversario || "").trim();
      retroState.adversario = alvo;
      if (!alvo) {
        limparRetro("Selecione um adversário para ver o retrospecto.");
        return;
      }
      const retro = await getJSON(`/api/retrospecto?adversario=${encodeURIComponent(alvo)}`);
      renderRetroDados(retro);
    }

    async function carregarOpcoesRetro(preferido = "") {
      const res = await getJSON("/api/retrospecto/opcoes");
      const items = Array.isArray(res?.items) ? res.items : [];
      const select = $("#retro-adversario-select");
      const atual = String(preferido || select.value || "").trim();
      select.innerHTML = `<option value="">Selecione um adversário...</option>` +
        items.map(n => `<option value="${escapeHtml(n)}">${escapeHtml(n)}</option>`).join("");
      if (atual && items.includes(atual)) {
        select.value = atual;
      } else {
        select.value = "";
      }
    }

    function setupRetrospecto() {
      $("#retro-adversario-select").addEventListener("change", (e) => carregarRetroAdversario(e.target.value));
      $("#retro-atualizar").addEventListener("click", () => carregarRetroAdversario($("#retro-adversario-select").value));
      $("#retro-head").addEventListener("click", (e) => {
        const th = e.target.closest("th[data-col]");
        if (!th || !retroState.partidas.length) return;
        const col = th.dataset.col;
        if (retroState.sortCol === col) {
          retroState.sortReverse = !retroState.sortReverse;
        } else {
          retroState.sortCol = col;
          retroState.sortReverse = false;
        }
        renderRetroPartidasOrdenado();
      });
    }

    function fillDataLists(listas) {
      const setOptions = (id, arr) => {
        $(id).innerHTML = (arr || []).map(v => `<option value="${escapeHtml(v)}"></option>`).join("");
      };
      setOptions("#dl-clubes", listas?.clubes_adversarios || []);
      setOptions("#dl-tecnicos", listas?.tecnicos || []);
      setOptions("#dl-competicoes", listas?.competicoes || []);
    }

    function linhaTextareaEscalacao(label, id, placeholder = "") {
      return `
        <div style="margin-bottom:10px">
          <label for="${id}" class="muted">${label}</label>
          <textarea id="${id}" rows="3" style="width:100%; margin-top:4px; border:1px solid var(--line); border-radius:10px; padding:10px;" placeholder="${placeholder}"></textarea>
        </div>`;
    }

    function renderEscalacaoEditor() {
      const wrap = $("#escalacao-editor");
      if (!wrap) return;
      const rows = [];
      rows.push('<h4 style="margin:0 0 8px">Titulares por posição</h4>');
      rows.push(linhaTextareaEscalacao("Goleiro", "esc-Goleiro"));
      rows.push(linhaTextareaEscalacao("Lateral-Direito", "esc-Lateral-Direito"));
      rows.push(linhaTextareaEscalacao("Zagueiro", "esc-Zagueiro"));
      rows.push(linhaTextareaEscalacao("Lateral-Esquerdo", "esc-Lateral-Esquerdo"));
      rows.push(linhaTextareaEscalacao("Volante", "esc-Volante"));
      rows.push(linhaTextareaEscalacao("Meio-Campista", "esc-Meio-Campista"));
      rows.push(linhaTextareaEscalacao("Atacante", "esc-Atacante"));
      rows.push('<h4 style="margin:14px 0 8px">Extras</h4>');
      rows.push(linhaTextareaEscalacao("Reservas", "esc-reservas"));
      rows.push(linhaTextareaEscalacao("Não Relacionados", "esc-nao_relacionados"));
      rows.push(linhaTextareaEscalacao("Lesionados", "esc-lesionados"));
      rows.push(linhaTextareaEscalacao("Suspensos", "esc-suspensos"));
      rows.push(linhaTextareaEscalacao("Servindo a seleção", "esc-servindo_selecao"));
      wrap.innerHTML = rows.join("");
      ["change","input"].forEach(evt => wrap.addEventListener(evt, atualizarResumoEscalacaoWeb));
    }

    function uniqueSorted(arr) {
      return Array.from(new Set((arr || []).filter(Boolean).map(v => String(v).trim()).filter(Boolean)))
        .sort((a, b) => a.localeCompare(b, "pt-BR", { sensitivity: "base" }));
    }

    function parseTextareaNames(value) {
      return String(value || "")
        .replaceAll(";", "\\n")
        .split(/\\n|,/)
        .map(s => s.trim())
        .filter(Boolean);
    }

    function linesFromGoalObjects(arr) {
      if (!Array.isArray(arr)) return "";
      const out = [];
      arr.forEach((g) => {
        if (typeof g === "string") {
          if (g.trim()) out.push(g.trim());
          return;
        }
        const nome = String(g?.nome || "").trim();
        const qtd = Number(g?.gols || 0);
        if (!nome) return;
        for (let i = 0; i < Math.max(1, qtd); i++) out.push(nome);
      });
      return out.join("\\n");
    }

    function coletarEscalacaoForm() {
      const titulares_por_posicao = {};
      ["Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo","Volante","Meio-Campista","Atacante"].forEach(pos => {
        titulares_por_posicao[pos] = parseTextareaNames(document.getElementById(`esc-${pos}`)?.value);
      });
      return {
        titulares_por_posicao,
        reservas: parseTextareaNames($("#esc-reservas")?.value),
        nao_relacionados: parseTextareaNames($("#esc-nao_relacionados")?.value),
        lesionados: parseTextareaNames($("#esc-lesionados")?.value),
        suspensos: parseTextareaNames($("#esc-suspensos")?.value),
        servindo_selecao: parseTextareaNames($("#esc-servindo_selecao")?.value),
      };
    }

    function carregarEscalacaoNoForm(esc) {
      const data = esc || {};
      const tit = data.titulares_por_posicao || {};
      ["Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo","Volante","Meio-Campista","Atacante"].forEach(pos => {
        const el = document.getElementById(`esc-${pos}`);
        if (el) el.value = (tit[pos] || []).join("\\n");
      });
      const extras = ["reservas", "nao_relacionados", "lesionados", "suspensos", "servindo_selecao"];
      extras.forEach(k => {
        const el = document.getElementById(`esc-${k}`);
        if (el) el.value = (data[k] || []).join("\\n");
      });
      atualizarResumoEscalacaoWeb();
      atualizarOpcoesGolsVasco();
    }

    function atualizarResumoEscalacaoWeb() {
      const esc = coletarEscalacaoForm();
      const titulares = Object.values(esc.titulares_por_posicao || {}).reduce((s, arr) => s + (arr?.length || 0), 0);
      const reservas = (esc.reservas || []).length;
      const naoRel = (esc.nao_relacionados || []).length;
      const lesionados = (esc.lesionados || []).length;
      const suspensos = (esc.suspensos || []).length;
      const servindoSelecao = (esc.servindo_selecao || []).length;
      $("#escalacao-resumo-web").textContent =
        `Titulares: ${titulares}/11 | Reservas: ${reservas} (mín. 4) | Não Relac.: ${naoRel} | Lesionados: ${lesionados} | Suspensos: ${suspensos} | Seleção: ${servindoSelecao}`;
      atualizarOpcoesGolsVasco();
    }

    function applyRegistroDefaults(prefill) {
      registroState.listas = prefill.listas || {};
      registroState.elenco = prefill.elenco || {};
      registroState.escalacaoPadrao = prefill.escalacao_padrao || {};
      fillDataLists(registroState.listas);
      $("#reg-data").value = prefill.data_hoje || "";
      $("#reg-tecnico").value = (registroState.listas?.tecnico_atual || "");
      $("#reg-local").value = "casa";
      registroState.gols = { vasco: [], contra: [] };
      renderGoalList("vasco");
      renderGoalList("contra");
      carregarEscalacaoNoForm(registroState.escalacaoPadrao);
      atualizarOpcoesGolsContra();
      atualizarCampoPosicao();
    }

    function atualizarCampoPosicao() {
      const comp = ($("#reg-competicao").value || "").trim().toLowerCase();
      const usa = comp === "brasileirão série a".toLowerCase();
      $("#reg-posicao").disabled = !usa;
      if (!usa) $("#reg-posicao").value = "";
    }

    function limparFormularioRegistro() {
      $("#reg-adversario").value = "";
      $("#reg-competicao").value = "";
      $("#reg-local").value = "casa";
      $("#reg-placar-vasco").value = "";
      $("#reg-placar-adv").value = "";
      registroState.gols = { vasco: [], contra: [] };
      renderGoalList("vasco");
      renderGoalList("contra");
      $("#reg-gol-vasco-input").value = "";
      $("#reg-gol-contra-input").value = "";
      $("#reg-gol-vasco-select").value = "";
      $("#reg-gol-contra-select").value = "";
      $("#reg-observacao").value = "";
      $("#reg-posicao").value = "";
      $("#reg-tecnico").value = (registroState.listas?.tecnico_atual || $("#reg-tecnico").value || "");
      $("#registro-status").textContent = "";
      carregarEscalacaoNoForm(registroState.escalacaoPadrao || {});
      atualizarOpcoesGolsContra();
      atualizarCampoPosicao();
    }

    function getGoalLimit(side) {
      const raw = side === "vasco" ? $("#reg-placar-vasco").value : $("#reg-placar-adv").value;
      const n = Number(raw);
      return Number.isFinite(n) && n >= 0 ? n : 0;
    }

    function setRegistroInfo(msg, color = "var(--muted)") {
      $("#registro-status").textContent = msg || "";
      $("#registro-status").style.color = color;
    }

    function syncGoalHiddenFields() {
      $("#reg-gols-vasco").value = (registroState.gols.vasco || []).join("\\n");
      $("#reg-gols-contra").value = (registroState.gols.contra || []).join("\\n");
    }

    function renderGoalList(side) {
      const listEl = side === "vasco" ? $("#reg-gols-vasco-list") : $("#reg-gols-contra-list");
      const items = registroState.gols[side] || [];
      const limit = getGoalLimit(side);
      listEl.innerHTML = items.length
        ? items.map((nome, idx) => `
            <span class="goal-chip">
              <span>${escapeHtml(nome)}</span>
              <button type="button" data-side="${side}" data-idx="${idx}" aria-label="Remover">x</button>
            </span>
          `).join("")
        : `<span class="muted">Nenhum gol informado</span>`;
      syncGoalHiddenFields();
      const lado = side === "vasco" ? "Vasco" : "Adversário";
      setRegistroInfo(`${lado}: ${items.length} gol(s) listado(s)` + (limit || limit === 0 ? ` / placar ${limit}` : ""), "var(--muted)");
    }

    function addGoal(side, nome) {
      const clean = String(nome || "").trim();
      if (!clean) return;
      const current = registroState.gols[side] || [];
      const limit = getGoalLimit(side);
      if (current.length >= limit && Number.isFinite(limit)) {
        const label = side === "vasco" ? "Vasco" : "adversário";
        setRegistroInfo(`Limite atingido: o ${label} só fez ${limit} gol(s).`, "var(--bad)");
        return;
      }
      current.push(clean);
      registroState.gols[side] = current;
      renderGoalList(side);
    }

    function removeGoal(side, idx) {
      const arr = registroState.gols[side] || [];
      if (idx < 0 || idx >= arr.length) return;
      arr.splice(idx, 1);
      renderGoalList(side);
    }

    function atualizarOpcoesGolsVasco() {
      const esc = coletarEscalacaoForm();
      const tit = esc.titulares_por_posicao || {};
      const nomesEscalados = [
        ...(tit["Goleiro"] || []),
        ...(tit["Lateral-Direito"] || []),
        ...(tit["Zagueiro"] || []),
        ...(tit["Lateral-Esquerdo"] || []),
        ...(tit["Volante"] || []),
        ...(tit["Meio-Campista"] || []),
        ...(tit["Atacante"] || []),
        ...(esc.reservas || []),
      ];
      const fallback = registroState.listas?.jogadores_vasco || [];
      const opts = uniqueSorted([...nomesEscalados, ...fallback]);
      const select = $("#reg-gol-vasco-select");
      const current = select.value;
      select.innerHTML = `<option value="">Selecionar titular/reserva...</option>` +
        opts.map(n => `<option value="${escapeHtml(n)}">${escapeHtml(n)}</option>`).join("");
      if (opts.includes(current)) select.value = current;
    }

    function atualizarOpcoesGolsContra() {
      const opts = uniqueSorted(registroState.listas?.jogadores_contra || []);
      const select = $("#reg-gol-contra-select");
      const current = select.value;
      select.innerHTML = `<option value="">Selecionar jogador adversário...</option>` +
        opts.map(n => `<option value="${escapeHtml(n)}">${escapeHtml(n)}</option>`).join("");
      if (opts.includes(current)) select.value = current;
    }

    function setupGoalBuilders() {
      $("#reg-gol-vasco-select").addEventListener("change", (e) => {
        if (!e.target.value) return;
        addGoal("vasco", e.target.value);
        e.target.value = "";
      });
      $("#reg-gol-contra-select").addEventListener("change", (e) => {
        if (!e.target.value) return;
        addGoal("contra", e.target.value);
        e.target.value = "";
      });

      $("#reg-gol-vasco-add").addEventListener("click", () => {
        const el = $("#reg-gol-vasco-input");
        addGoal("vasco", el.value);
        el.value = "";
        el.focus();
      });
      $("#reg-gol-contra-add").addEventListener("click", () => {
        const el = $("#reg-gol-contra-input");
        addGoal("contra", el.value);
        el.value = "";
        el.focus();
      });

      $("#reg-gol-vasco-input").addEventListener("keydown", (e) => {
        if (e.key !== "Enter") return;
        e.preventDefault();
        addGoal("vasco", e.currentTarget.value);
        e.currentTarget.value = "";
      });
      $("#reg-gol-contra-input").addEventListener("keydown", (e) => {
        if (e.key !== "Enter") return;
        e.preventDefault();
        addGoal("contra", e.currentTarget.value);
        e.currentTarget.value = "";
      });

      $("#reg-gols-vasco-list").addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-idx]");
        if (!btn) return;
        removeGoal("vasco", Number(btn.dataset.idx));
      });
      $("#reg-gols-contra-list").addEventListener("click", (e) => {
        const btn = e.target.closest("button[data-idx]");
        if (!btn) return;
        removeGoal("contra", Number(btn.dataset.idx));
      });

      ["#reg-placar-vasco", "#reg-placar-adv"].forEach(sel => {
        $(sel).addEventListener("input", () => {
          renderGoalList("vasco");
          renderGoalList("contra");
        });
      });
    }

    function commitPendingGoalInputs() {
      const vascoInput = $("#reg-gol-vasco-input");
      const contraInput = $("#reg-gol-contra-input");
      if (vascoInput && vascoInput.value.trim()) {
        addGoal("vasco", vascoInput.value);
        vascoInput.value = "";
      }
      if (contraInput && contraInput.value.trim()) {
        addGoal("contra", contraInput.value);
        contraInput.value = "";
      }
    }

    async function salvarPartidaWeb() {
      // Garante que o último nome digitado entre na lista mesmo sem apertar Enter.
      commitPendingGoalInputs();
      const payload = {
        data: $("#reg-data").value.trim(),
        tecnico: $("#reg-tecnico").value.trim(),
        adversario: $("#reg-adversario").value.trim(),
        local: $("#reg-local").value,
        competicao: $("#reg-competicao").value.trim(),
        posicao_tabela: $("#reg-posicao").value.trim(),
        placar: {
          vasco: $("#reg-placar-vasco").value,
          adversario: $("#reg-placar-adv").value,
        },
        gols_vasco_lista: $("#reg-gols-vasco").value,
        gols_contra_lista: $("#reg-gols-contra").value,
        observacao: $("#reg-observacao").value,
        escalacao_partida: coletarEscalacaoForm(),
      };
      $("#registro-status").textContent = "Salvando...";
      try {
        const res = await postJSON("/api/jogos", payload);
        $("#registro-status").textContent = res.message || "Partida registrada.";
        $("#registro-status").style.color = "var(--ok)";
        const prefill = await getJSON("/api/registro/prefill");
        applyRegistroDefaults(prefill);
        await carregarTudo($("#busca-jogos").value || "");
        const tabJogos = document.querySelector('.tab-btn[data-tab="jogos"]');
        if (tabJogos) tabJogos.click();
      } catch (err) {
        $("#registro-status").textContent = err.message;
        $("#registro-status").style.color = "var(--bad)";
      }
    }

    async function carregarTudo(busca = "") {
      const retroSelecionado = ($("#retro-adversario-select")?.value || "").trim();
      const [resumo, jogos, futuros, listas, prefill] = await Promise.all([
        getJSON("/api/resumo"),
        getJSON(`/api/jogos?limit=300&busca=${encodeURIComponent(busca)}`),
        getJSON("/api/futuros"),
        getJSON("/api/listas"),
        getJSON("/api/registro/prefill"),
      ]);
      renderMetrics(resumo);
      renderJogos(jogos.items || []);
      renderFuturos(futuros.items || []);
      renderListas(listas);
      applyRegistroDefaults(prefill);
      await carregarOpcoesRetro(retroSelecionado);
      const alvo = ($("#retro-adversario-select")?.value || "").trim();
      if (alvo) {
        await carregarRetroAdversario(alvo);
      } else {
        limparRetro("Selecione um adversário para ver o retrospecto.");
      }
    }

    function setupTabs() {
      document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          document.querySelectorAll(".tab-btn").forEach(b => {
            b.classList.remove("active");
            if (!b.classList.contains("secondary")) b.classList.add("secondary");
          });
          btn.classList.add("active");
          btn.classList.remove("secondary");
          const tab = btn.dataset.tab;
          ["jogos","futuros","retrospecto","listas","registro"].forEach(id => {
            document.querySelector(`#tab-${id}`).classList.toggle("hidden", id !== tab);
          });
        });
      });
    }

    function setupJogoModal() {
      $("#jogo-modal-close").addEventListener("click", closeJogoModal);
      $("#jogo-modal").addEventListener("click", (e) => {
        if (e.target.id === "jogo-modal") closeJogoModal();
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeJogoModal();
      });
      $("#tbody-jogos").addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-ver-jogo");
        if (!btn) return;
        const idx = Number(btn.dataset.idx);
        if (Number.isInteger(idx)) verDetalhesJogo(idx);
      });
    }

    function editEscalacaoField(id, label) {
      return `
        <div class="field">
          <label>${escapeHtml(label)}</label>
          <textarea id="${id}" style="min-height:70px"></textarea>
        </div>`;
    }

    function renderEditEscalacaoGrid() {
      $("#edit-escalacao-grid").innerHTML = [
        editEscalacaoField("edit-esc-Goleiro", "Goleiro"),
        editEscalacaoField("edit-esc-Lateral-Direito", "Lateral-Direito"),
        editEscalacaoField("edit-esc-Zagueiro", "Zagueiro"),
        editEscalacaoField("edit-esc-Lateral-Esquerdo", "Lateral-Esquerdo"),
        editEscalacaoField("edit-esc-Volante", "Volante"),
        editEscalacaoField("edit-esc-Meio-Campista", "Meio-Campista"),
        editEscalacaoField("edit-esc-Atacante", "Atacante"),
        editEscalacaoField("edit-esc-reservas", "Reservas"),
        editEscalacaoField("edit-esc-nao_relacionados", "Não Relacionados"),
        editEscalacaoField("edit-esc-lesionados", "Lesionados"),
        editEscalacaoField("edit-esc-suspensos", "Suspensos"),
        editEscalacaoField("edit-esc-servindo_selecao", "Servindo a seleção"),
      ].join("");
    }

    function setEditStatus(msg, color = "var(--muted)") {
      $("#edit-jogo-status").textContent = msg || "";
      $("#edit-jogo-status").style.color = color;
    }

    function coletarEditEscalacao() {
      const get = (id) => parseTextareaNames(document.getElementById(id)?.value);
      return {
        titulares_por_posicao: {
          "Goleiro": get("edit-esc-Goleiro"),
          "Lateral-Direito": get("edit-esc-Lateral-Direito"),
          "Zagueiro": get("edit-esc-Zagueiro"),
          "Lateral-Esquerdo": get("edit-esc-Lateral-Esquerdo"),
          "Volante": get("edit-esc-Volante"),
          "Meio-Campista": get("edit-esc-Meio-Campista"),
          "Atacante": get("edit-esc-Atacante"),
        },
        reservas: get("edit-esc-reservas"),
        nao_relacionados: get("edit-esc-nao_relacionados"),
        lesionados: get("edit-esc-lesionados"),
        suspensos: get("edit-esc-suspensos"),
        servindo_selecao: get("edit-esc-servindo_selecao"),
      };
    }

    function carregarEditEscalacao(esc) {
      const data = esc || {};
      const tit = data.titulares_por_posicao || {};
      const setv = (id, arr) => { const el = document.getElementById(id); if (el) el.value = (arr || []).join("\\n"); };
      setv("edit-esc-Goleiro", tit["Goleiro"]);
      setv("edit-esc-Lateral-Direito", tit["Lateral-Direito"]);
      setv("edit-esc-Zagueiro", tit["Zagueiro"]);
      setv("edit-esc-Lateral-Esquerdo", tit["Lateral-Esquerdo"]);
      setv("edit-esc-Volante", tit["Volante"]);
      setv("edit-esc-Meio-Campista", tit["Meio-Campista"]);
      setv("edit-esc-Atacante", tit["Atacante"]);
      setv("edit-esc-reservas", data.reservas);
      setv("edit-esc-nao_relacionados", data.nao_relacionados);
      setv("edit-esc-lesionados", data.lesionados);
      setv("edit-esc-suspensos", data.suspensos);
      setv("edit-esc-servindo_selecao", data.servindo_selecao);
    }

    function updateEditPosicaoField() {
      const comp = ($("#edit-competicao").value || "").trim().toLowerCase();
      const usa = comp === "brasileirão série a".toLowerCase();
      $("#edit-posicao_tabela").disabled = !usa;
      if (!usa) $("#edit-posicao_tabela").value = "";
    }

    function openEditJogoModal() {
      $("#edit-jogo-modal").classList.add("show");
      $("#edit-jogo-modal").setAttribute("aria-hidden", "false");
    }

    function closeEditJogoModal() {
      $("#edit-jogo-modal").classList.remove("show");
      $("#edit-jogo-modal").setAttribute("aria-hidden", "true");
      editState.idx = null;
    }

    async function abrirEditarJogo(idx) {
      try {
        const j = await getJSON(`/api/jogos/${idx}`);
        editState.idx = idx;
        editState.escalacaoPadrao = registroState.escalacaoPadrao || {};
        $("#edit-jogo-modal-title").textContent = `Editar Jogo: Vasco x ${j.adversario || ""}`;
        $("#edit-data").value = j.data || "";
        $("#edit-tecnico").value = j.tecnico || "";
        $("#edit-adversario").value = j.adversario || "";
        $("#edit-local").value = j.local || "";
        $("#edit-competicao").value = j.competicao || "";
        $("#edit-horario").value = j.horario || "";
        $("#edit-estadio").value = j.estadio || "";
        $("#edit-capitao").value = j.capitao || "";
        $("#edit-posicao_tabela").value = j.posicao_tabela == null ? "" : String(j.posicao_tabela);
        $("#edit-publico-pagante").value = j.publico_pagante == null ? "" : String(j.publico_pagante);
        $("#edit-publico-presente").value = j.publico_presente == null ? "" : String(j.publico_presente);
        $("#edit-renda").value = j.renda == null ? "" : String(j.renda);
        $("#edit-placar-vasco").value = j.placar?.vasco ?? "";
        $("#edit-placar-adv").value = j.placar?.adversario ?? "";
        $("#edit-gols-vasco").value = linesFromGoalObjects(j.gols_vasco);
        $("#edit-gols-contra").value = linesFromGoalObjects(j.gols_adversario);
        $("#edit-observacao").value = j.observacao || "";
        carregarEditEscalacao(j.escalacao_partida || {});
        updateEditPosicaoField();
        setEditStatus("");
        openEditJogoModal();
      } catch (err) {
        alert(`Erro ao abrir edição: ${err.message}`);
      }
    }

    async function salvarEdicaoJogo() {
      if (!Number.isInteger(editState.idx)) return;
      setEditStatus("Salvando...");
      const payload = {
        data: $("#edit-data").value.trim(),
        tecnico: $("#edit-tecnico").value.trim(),
        adversario: $("#edit-adversario").value.trim(),
        local: $("#edit-local").value,
        competicao: $("#edit-competicao").value.trim(),
        horario: $("#edit-horario").value.trim(),
        estadio: $("#edit-estadio").value.trim(),
        capitao: $("#edit-capitao").value.trim(),
        posicao_tabela: $("#edit-posicao_tabela").value.trim(),
        publico_pagante: $("#edit-publico-pagante").value.trim(),
        publico_presente: $("#edit-publico-presente").value.trim(),
        renda: $("#edit-renda").value.trim(),
        placar: { vasco: $("#edit-placar-vasco").value, adversario: $("#edit-placar-adv").value },
        gols_vasco_lista: $("#edit-gols-vasco").value,
        gols_contra_lista: $("#edit-gols-contra").value,
        observacao: $("#edit-observacao").value,
        escalacao_partida: coletarEditEscalacao(),
      };
      try {
        const res = await fetch(`/api/jogos/${editState.idx}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.erro || `HTTP ${res.status}`);
        setEditStatus(data.message || "Partida atualizada.", "var(--ok)");
        await carregarTudo($("#busca-jogos").value || "");
        closeEditJogoModal();
      } catch (err) {
        setEditStatus(err.message, "var(--bad)");
        const statusEl = $("#edit-jogo-status");
        if (statusEl) statusEl.scrollIntoView({ behavior: "smooth", block: "center" });
        console.error("Erro ao editar jogo:", err);
        alert(`Erro ao editar jogo: ${err.message}`);
      }
    }

    function setupEditJogoModal() {
      renderEditEscalacaoGrid();
      $("#edit-jogo-modal-close").addEventListener("click", closeEditJogoModal);
      $("#edit-jogo-modal").addEventListener("click", (e) => {
        if (e.target.id === "edit-jogo-modal") closeEditJogoModal();
      });
      $("#edit-competicao").addEventListener("input", updateEditPosicaoField);
      $("#edit-jogo-salvar").addEventListener("click", salvarEdicaoJogo);
      $("#edit-jogo-carregar-padrao").addEventListener("click", () => carregarEditEscalacao(editState.escalacaoPadrao || {}));
      $("#tbody-jogos").addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-editar-jogo");
        if (!btn) return;
        const idx = Number(btn.dataset.idx);
        if (Number.isInteger(idx)) abrirEditarJogo(idx);
      });
    }

    window.addEventListener("DOMContentLoaded", async () => {
      setupTabs();
      setupRetrospecto();
      setupJogoModal();
      setupEditJogoModal();
      renderEscalacaoEditor();
      setupGoalBuilders();
      $("#btn-buscar").addEventListener("click", () => carregarTudo($("#busca-jogos").value));
      $("#btn-limpar").addEventListener("click", () => {
        $("#busca-jogos").value = "";
        carregarTudo("");
      });
      $("#reg-competicao").addEventListener("input", atualizarCampoPosicao);
      $("#btn-reset-registro").addEventListener("click", limparFormularioRegistro);
      $("#btn-carregar-escalacao").addEventListener("click", () => carregarEscalacaoNoForm(registroState.escalacaoPadrao || {}));
      $("#btn-salvar-partida").addEventListener("click", salvarPartidaWeb);
      $("#busca-jogos").addEventListener("keydown", (e) => {
        if (e.key === "Enter") carregarTudo($("#busca-jogos").value);
      });
      try {
        await carregarTudo();
      } catch (err) {
        document.body.insertAdjacentHTML("afterbegin",
          `<div style="background:#fee2e2;color:#7f1d1d;padding:10px;text-align:center">Erro ao carregar dados: ${escapeHtml(err.message)}</div>`);
      }
    });
  </script>
</body>
</html>
"""


class StatsVascoWebHandler(BaseHTTPRequestHandler):
    server_version = "StatsVascoWeb/0.1"

    def _json_response(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html_response(self, html: str, status=HTTPStatus.OK):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        raw = self.rfile.read(max(0, length)) if length > 0 else b""
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def log_message(self, fmt, *args):
        # Mantém logs úteis no terminal sem muito ruído.
        print(f"[web] {self.address_string()} - {fmt % args}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/":
            return self._html_response(INDEX_HTML)

        if path == "/health":
            return self._json_response({"ok": True})

        if path == "/api/resumo":
            jogos = carregar_jogos()
            return self._json_response(resumo_geral(jogos))

        if path == "/api/jogos":
            jogos = carregar_jogos()
            busca = (qs.get("busca") or [""])[0]
            try:
                limit = int((qs.get("limit") or ["200"])[0])
            except ValueError:
                limit = 200
            limit = max(1, min(limit, 5000))
            items = serializar_jogos(jogos, limite=limit, busca=busca)
            return self._json_response({"items": items, "total_filtrado": len(items)})

        if path.startswith("/api/jogos/"):
            try:
                idx = int(path.rsplit("/", 1)[-1])
            except ValueError:
                return self._json_response({"erro": "Índice inválido"}, status=HTTPStatus.BAD_REQUEST)
            detalhe = detalhe_jogo_por_indice(idx)
            if detalhe is None:
                return self._json_response({"erro": "Jogo não encontrado"}, status=HTTPStatus.NOT_FOUND)
            return self._json_response(detalhe)

        if path == "/api/futuros":
            return self._json_response({"items": serializar_futuros(carregar_futuros())})

        if path == "/api/retrospecto/opcoes":
            return self._json_response({"items": listar_adversarios_com_historico()})

        if path == "/api/retrospecto":
            adversario = (qs.get("adversario") or [""])[0]
            return self._json_response(coletar_retro_por_adversario(adversario))

        if path == "/api/listas":
            return self._json_response(carregar_listas())

        if path == "/api/elenco":
            return self._json_response(carregar_elenco_atual())

        if path == "/api/registro/prefill":
            listas = carregar_listas()
            elenco = carregar_elenco_atual()
            return self._json_response(
                {
                    "data_hoje": datetime.now().strftime("%d/%m/%Y"),
                    "listas": listas,
                    "elenco": elenco,
                    "escalacao_padrao": escalacao_padrao_do_elenco(elenco),
                }
            )

        return self._json_response({"erro": "Rota não encontrada"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/jogos":
            payload = self._read_json_body()
            if payload is None:
                return self._json_response({"erro": "JSON inválido."}, status=HTTPStatus.BAD_REQUEST)
            ok, msg, jogo = registrar_partida_web(payload)
            if not ok:
                return self._json_response({"erro": msg}, status=HTTPStatus.BAD_REQUEST)
            return self._json_response({"ok": True, "message": msg, "jogo": jogo}, status=HTTPStatus.CREATED)

        return self._json_response({"erro": "Rota não encontrada"}, status=HTTPStatus.NOT_FOUND)

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/jogos/"):
            try:
                idx = int(parsed.path.rsplit("/", 1)[-1])
            except ValueError:
                return self._json_response({"erro": "Índice inválido"}, status=HTTPStatus.BAD_REQUEST)
            payload = self._read_json_body()
            if payload is None:
                return self._json_response({"erro": "JSON inválido."}, status=HTTPStatus.BAD_REQUEST)
            ok, msg, jogo = editar_partida_web(idx, payload)
            if not ok:
                return self._json_response({"erro": msg}, status=HTTPStatus.BAD_REQUEST)
            return self._json_response({"ok": True, "message": msg, "jogo": jogo})
        return self._json_response({"erro": "Rota não encontrada"}, status=HTTPStatus.NOT_FOUND)


def main():
    host = os.environ.get("STATSVASCO_WEB_HOST", "127.0.0.1")
    try:
        port = int(os.environ.get("STATSVASCO_WEB_PORT", "8000"))
    except ValueError:
        port = 8000

    server = ThreadingHTTPServer((host, port), StatsVascoWebHandler)
    print(f"StatsVasco Web (MVP) em http://{host}:{port}")
    print("Use Ctrl+C para parar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
