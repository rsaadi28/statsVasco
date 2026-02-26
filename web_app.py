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

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
ARQUIVO_JOGOS = os.path.join(PROJECT_ROOT, "jogos_vasco.json")
ARQUIVO_FUTUROS = os.path.join(PROJECT_ROOT, "jogos_futuros.json")
ARQUIVO_LISTAS = os.path.join(PROJECT_ROOT, "listas_auxiliares.json")
ARQUIVO_ELENCO_ATUAL = os.path.join(PROJECT_ROOT, "elenco_atual.json")
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
CONDICOES_ELENCO = ["Titular", "Reserva", "Não Relacionado", "Lesionado"]
CATEGORIAS_ESCALACAO_EXTRAS = (
    ("reservas", "Reservas"),
    ("nao_relacionados", "Não Relacionados"),
    ("lesionados", "Lesionados"),
)


def _load_json_safe(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return json.loads(content) if content else default
    except Exception:
        return default


def carregar_jogos():
    return _load_json_safe(ARQUIVO_JOGOS, [])


def carregar_futuros():
    return _load_json_safe(ARQUIVO_FUTUROS, [])


def carregar_listas():
    return _load_json_safe(
        ARQUIVO_LISTAS,
        {
            "clubes_adversarios": [],
            "jogadores_vasco": [],
            "jogadores_contra": [],
            "competicoes": [],
            "tecnicos": [],
            "tecnico_atual": "",
        },
    )


def salvar_listas(dados: dict):
    with open(ARQUIVO_LISTAS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def salvar_lista_jogos(dados: list):
    with open(ARQUIVO_JOGOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


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
    dados = _load_json_safe(ARQUIVO_ELENCO_ATUAL, {"jogadores": [], "tecnico": ""})
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
        "nao_relacionados": [],
        "lesionados": [],
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
    return base


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
        else:
            base["lesionados"].append(nome)
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
        if isinstance(j, dict) and str(j.get("nome", "")).strip()
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
        return False, "Todos os jogadores do elenco precisam estar em alguma lista da escalação.", escalacao
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


def _salvar_ou_atualizar_partida_web(payload: dict, edit_idx: int | None = None):
    if not isinstance(payload, dict):
        return False, "Payload inválido.", None

    data = str(payload.get("data", "")).strip()
    adversario = str(payload.get("adversario", "")).strip()
    competicao = str(payload.get("competicao", "")).strip()
    local = str(payload.get("local", "casa")).strip() or "casa"
    observacao = str(payload.get("observacao", "")).strip()
    tecnico = str(payload.get("tecnico", "")).strip()
    if not tecnico:
        tecnico = str(carregar_listas().get("tecnico_atual", "") or "Fernando Diniz")

    placar = payload.get("placar") or {}
    try:
        placar_vasco = int(placar.get("vasco"))
        placar_adv = int(placar.get("adversario"))
    except Exception:
        return False, "Placar inválido. Informe números inteiros.", None
    if placar_vasco < 0 or placar_adv < 0:
        return False, "Placar inválido. Não use números negativos.", None

    if not (data and adversario and competicao and tecnico):
        return False, "Preencha todos os campos obrigatórios.", None
    if not _parse_data_br_strita(data):
        return False, "Data inválida. Use o formato dd/mm/aaaa.", None
    if local not in ("casa", "fora"):
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
    if len(nomes_vasco) != placar_vasco:
        return (
            False,
            f"Informe exatamente {placar_vasco} nome(s) para os gols do Vasco (um por gol).",
            None,
        )
    if len(nomes_contra) != placar_adv:
        return (
            False,
            f"Informe exatamente {placar_adv} nome(s) para os gols do adversário (um por gol).",
            None,
        )

    escalacao_payload = payload.get("escalacao_partida") or {}
    elenco = carregar_elenco_atual()
    ok_esc, msg_esc, escalacao_partida = validar_escalacao_partida(escalacao_payload, elenco)
    if not ok_esc:
        return False, msg_esc, None

    titulares_cf = set()
    reservas_cf = set()
    for pos in POSICOES_ELENCO:
        for nome in escalacao_partida["titulares_por_posicao"].get(pos, []):
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
    if competicao not in listas.get("competicoes", []):
        listas.setdefault("competicoes", []).append(competicao)
        listas["competicoes"] = sorted(listas["competicoes"], key=str.casefold)
    if tecnico not in listas.get("tecnicos", []):
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
    listas["tecnico_atual"] = tecnico
    salvar_listas(listas)

    jogo = {
        "data": data,
        "adversario": adversario,
        "competicao": competicao,
        "local": local,
        "placar": {"vasco": placar_vasco, "adversario": placar_adv},
        "gols_vasco": gols_vasco,
        "gols_adversario": gols_contra,
        "observacao": observacao,
        "tecnico": tecnico,
        "posicao_tabela": posicao_tabela,
        "escalacao_partida": escalacao_partida,
    }

    jogos = carregar_jogos()
    if edit_idx is None:
        jogos.append(jogo)
        msg_ok = "Partida registrada com sucesso!"
    else:
        if not (0 <= edit_idx < len(jogos)):
            return False, "Não foi possível localizar o jogo para edição.", None
        jogos[edit_idx] = jogo
        msg_ok = "Partida atualizada com sucesso!"
    salvar_lista_jogos(jogos)
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
        "tecnico": jogo.get("tecnico", ""),
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


INDEX_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>StatsVasco Web (MVP)</title>
  <style>
    :root {
      --bg: #eef3f7;
      --card: #ffffff;
      --ink: #0f172a;
      --muted: #5b6473;
      --line: #d8e0e8;
      --accent: #0b5ed7;
      --accent-2: #0a3f8f;
      --ok: #0f8a3f;
      --warn: #b67700;
      --bad: #c32f27;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 15% -10%, #cfe3ff 0 25%, transparent 26%),
        radial-gradient(circle at 90% 0%, #d6f3ec 0 18%, transparent 19%),
        var(--bg);
    }
    .wrap { max-width: 1200px; margin: 0 auto; padding: 20px; }
    .hero {
      background: linear-gradient(135deg, #0b5ed7, #0a3f8f);
      color: white;
      border-radius: 18px;
      padding: 18px 20px;
      box-shadow: 0 10px 28px rgba(11, 94, 215, .18);
    }
    .hero h1 { margin: 0; font-size: 1.35rem; }
    .hero p { margin: 6px 0 0; opacity: .9; }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
      box-shadow: 0 4px 16px rgba(16,24,40,.04);
    }
    .metric .label { color: var(--muted); font-size: .8rem; }
    .metric .value { font-size: 1.35rem; font-weight: 700; margin-top: 4px; }
    .row {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 12px;
      margin-top: 12px;
    }
    .toolbar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 10px;
      align-items: center;
    }
    input, select, button {
      border: 1px solid var(--line);
      background: #fff;
      border-radius: 10px;
      padding: 9px 11px;
      font-size: .95rem;
    }
    button {
      cursor: pointer;
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }
    button.secondary {
      background: white;
      color: var(--ink);
      border-color: var(--line);
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); font-size: .92rem; }
    th { color: var(--muted); font-weight: 600; position: sticky; top: 0; background: white; }
    .table-wrap { max-height: 520px; overflow: auto; }
    .pill {
      display: inline-flex; align-items: center; justify-content: center;
      min-width: 24px; height: 24px; border-radius: 999px; font-weight: 700; font-size: .8rem;
      color: white;
    }
    .V { background: var(--ok); }
    .E { background: var(--warn); }
    .D { background: var(--bad); }
    .muted { color: var(--muted); }
    ul.clean { list-style: none; padding: 0; margin: 0; }
    ul.clean li {
      display: flex; justify-content: space-between; gap: 8px;
      padding: 8px 0; border-bottom: 1px solid var(--line);
      font-size: .92rem;
    }
    .section-title { margin: 0 0 10px; font-size: 1rem; }
    .tabs { display: flex; gap: 8px; margin: 12px 0 8px; flex-wrap: wrap; }
    .tab-btn.active { background: var(--accent-2); color: #fff; border-color: var(--accent-2); }
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
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 24px 60px rgba(15, 23, 42, .25);
      padding: 16px;
    }
    .modal-card.lg { width: min(1100px, 100%); }
    .modal-head {
      display: flex; justify-content: space-between; align-items: center; gap: 10px;
      position: sticky; top: 0; background: #fff; padding-bottom: 10px; z-index: 1;
    }
    .kv { display: grid; grid-template-columns: 180px 1fr; gap: 6px 10px; }
    .kv div:nth-child(odd) { color: var(--muted); }
    .score-box {
      display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 12px;
      background: linear-gradient(180deg, #f8fbff, #eef5ff);
      border: 1px solid #dbe7ff; border-radius: 14px; padding: 14px; margin: 10px 0 14px;
    }
    .score-num { font-size: 2rem; font-weight: 800; text-align: center; }
    .mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .chip { display:inline-block; border:1px solid var(--line); padding:4px 8px; border-radius:999px; margin:2px 4px 2px 0; font-size:.85rem; }
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
        #0f6a35;
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
      background: #fbfcfe;
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
      border-radius: 12px;
      padding: 10px;
      background: #fcfdff;
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
      border: 1px dashed #cfd8e3;
      border-radius: 10px;
      padding: 8px;
      background: #fff;
    }
    .goal-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid #bdd0ea;
      border-radius: 999px;
      padding: 4px 8px;
      margin: 3px 4px 3px 0;
      background: #eef5ff;
      font-size: .88rem;
    }
    .goal-chip button {
      border: 0;
      background: transparent;
      color: #365b8f;
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
      border-radius: 10px;
      padding: 10px;
      min-height: 88px;
      font: inherit;
    }
    @media (max-width: 900px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .row { grid-template-columns: 1fr; }
      .mini-grid { grid-template-columns: 1fr; }
      .kv { grid-template-columns: 130px 1fr; }
      .goal-builder .goal-controls { grid-template-columns: 1fr; }
      .pitch-wrap { grid-template-columns: 1fr; }
      .edit-grid { grid-template-columns: 1fr; }
    }
    @media (max-width: 560px) {
      .grid { grid-template-columns: 1fr; }
      .hero h1 { font-size: 1.1rem; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>StatsVasco Web (MVP)</h1>
      <p>Dados consolidados e atualizados</p>
    </section>

    <section class="grid" id="metrics"></section>

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
        </div>
        <div id="retro-resumo" class="muted" style="margin-bottom:10px;">
          Selecione um adversário para ver o retrospecto.
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Competição</th>
                <th>Local</th>
                <th>Placar</th>
                <th>Res.</th>
                <th>Gols do Vasco</th>
                <th>Gols do Adversário</th>
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
            Mesmas regras do desktop para validação: 11 titulares, 1 goleiro titular, mínimo 4 reservas e todos do elenco em alguma lista.
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
        <div class="field"><label>Local</label><select id="edit-local"><option value="casa">Casa</option><option value="fora">Fora</option></select></div>
        <div class="field"><label>Competição</label><input id="edit-competicao" list="dl-competicoes"></div>
        <div class="field"><label>Posição na tabela (Brasileirão)</label><input id="edit-posicao_tabela"></div>
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
      };
    }

    function carregarEscalacaoNoForm(esc) {
      const data = esc || {};
      const tit = data.titulares_por_posicao || {};
      ["Goleiro","Lateral-Direito","Zagueiro","Lateral-Esquerdo","Volante","Meio-Campista","Atacante"].forEach(pos => {
        const el = document.getElementById(`esc-${pos}`);
        if (el) el.value = (tit[pos] || []).join("\\n");
      });
      const extras = ["reservas", "nao_relacionados", "lesionados"];
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
      $("#escalacao-resumo-web").textContent =
        `Titulares: ${titulares}/11 | Reservas: ${reservas} (mín. 4) | Não Relac.: ${naoRel} | Lesionados: ${lesionados}`;
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
          ["jogos","futuros","listas","registro"].forEach(id => {
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
        $("#edit-local").value = j.local || "casa";
        $("#edit-competicao").value = j.competicao || "";
        $("#edit-posicao_tabela").value = j.posicao_tabela == null ? "" : String(j.posicao_tabela);
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
        posicao_tabela: $("#edit-posicao_tabela").value.trim(),
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
