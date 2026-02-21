import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict, Counter
import json
import os
import shutil
import sys
import ast
import glob
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
ELENCO_POSICAO_PLACEHOLDER = "Selecione..."
ELENCO_CONDICAO_PLACEHOLDER = "Selecione..."
ICONE_STATUS_ESCALACAO = {
    "titulares": "T",
    "reservas": "R",
    "nao_relacionados": "N",
    "lesionados": "L",
    "sem_lista": "!",
}


def _json_tem_dados(path):
    """Retorna True se o JSON existir e contiver dados úteis."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return False
        data = json.loads(content)
        if data in (None, "", [], {}):
            return False
        return True
    except Exception:
        return False


def _bootstrap_jsons():
    """Garante JSONs na pasta de produção com fallback nos JSONs do app."""
    if DATA_DIR == PROJECT_ROOT:
        return
    os.makedirs(DATA_DIR, exist_ok=True)

    defaults = {
        "jogos_vasco.json": [],
        "jogos_futuros.json": [],
        "elenco_atual.json": {"jogadores": []},
        "jogadores_historico.json": {"jogadores": []},
        "listas_auxiliares.json": {
            "clubes_adversarios": [],
            "jogadores_vasco": [],
            "jogadores_contra": [],
            "competicoes": [],
            "tecnicos": ["Fernando Diniz"],
            "tecnico_atual": "Fernando Diniz",
        },
    }

    for nome in ("jogos_vasco.json", "listas_auxiliares.json", "jogos_futuros.json", "elenco_atual.json", "jogadores_historico.json"):
        destino = os.path.join(DATA_DIR, nome)
        if _json_tem_dados(destino):
            continue

        origem = os.path.join(PROJECT_ROOT, nome)
        if _json_tem_dados(origem):
            shutil.copy2(origem, destino)
            continue

        if os.path.exists(origem):
            shutil.copy2(origem, destino)
            continue

        with open(destino, "w", encoding="utf-8") as f:
            json.dump(defaults[nome], f, ensure_ascii=False, indent=2)


_bootstrap_jsons()


def _gerar_backup_jsons_inicio():
    """Gera backup snapshot dos JSONs ao abrir o app (mantém somente o mais recente de cada arquivo)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivos = (
        ("jogos_vasco", ARQUIVO_JOGOS),
        ("jogos_futuros", ARQUIVO_FUTUROS),
        ("listas_auxiliares", ARQUIVO_LISTAS),
        ("elenco_atual", ARQUIVO_ELENCO_ATUAL),
        ("jogadores_historico", ARQUIVO_JOGADORES_HISTORICO),
    )
    for prefixo, origem in arquivos:
        if not os.path.exists(origem):
            continue
        padrao_antigos = os.path.join(DATA_DIR, f"{prefixo}.backup_*.json")
        for antigo in glob.glob(padrao_antigos):
            try:
                os.remove(antigo)
            except Exception:
                pass
        destino = os.path.join(DATA_DIR, f"{prefixo}.backup_{timestamp}.json")
        try:
            shutil.copy2(origem, destino)
        except Exception:
            pass


def _ordenar_listas(dados: dict) -> dict:
    """Ordena, alfabeticamente (case-insensitive), as listas auxiliares."""
    if not isinstance(dados, dict):
        return dados
    chaves = ("clubes_adversarios", "jogadores_vasco", "jogadores_contra", "competicoes", "tecnicos")
    for k in chaves:
        lista = dados.get(k)
        if isinstance(lista, list):
            dados[k] = sorted(lista, key=lambda s: s.casefold())
    return dados


def _load_json_safe(path, default):
    """Carrega JSON com segurança, retornando default se ausente/corrompido."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except Exception:
        return default


def carregar_dados_jogos():
    return _load_json_safe(ARQUIVO_JOGOS, [])


def carregar_jogos_futuros():
    return _load_json_safe(ARQUIVO_FUTUROS, [])


def carregar_listas():
    dados = _load_json_safe(ARQUIVO_LISTAS, {
        "clubes_adversarios": [],
        "jogadores_vasco": [],
        "jogadores_contra": [],
        "competicoes": [],
        "tecnicos": ["Fernando Diniz"],
        "tecnico_atual": "Fernando Diniz",
    })
    dados = _ordenar_listas(dados)
    if not dados.get("tecnicos"):
        dados["tecnicos"] = ["Fernando Diniz"]
    if not dados.get("tecnico_atual"):
        dados["tecnico_atual"] = dados["tecnicos"][0]
    elif dados["tecnico_atual"] not in dados["tecnicos"]:
        dados["tecnicos"].append(dados["tecnico_atual"])
        dados = _ordenar_listas(dados)
    return dados


def salvar_listas(data):
    data = _ordenar_listas(data)
    with open(ARQUIVO_LISTAS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def salvar_jogo(jogo):
    dados = carregar_dados_jogos()
    dados.append(jogo)
    salvar_lista_jogos(dados)


def salvar_lista_jogos(dados):
    with open(ARQUIVO_JOGOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def salvar_lista_futuros(dados):
    with open(ARQUIVO_FUTUROS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _normalizar_posicao_elenco(posicao: str) -> str:
    posicao_txt = str(posicao or "").strip()
    if posicao_txt.casefold() == "goleiros":
        posicao_txt = "Goleiro"
    return posicao_txt if posicao_txt in POSICOES_ELENCO else "Meio-Campista"


def _normalizar_condicao_elenco(condicao: str) -> str:
    condicao_txt = str(condicao or "").strip()
    return condicao_txt if condicao_txt in CONDICOES_ELENCO else "Reserva"


def _normalizar_jogador_elenco(item):
    if isinstance(item, str):
        nome = item.strip()
        if not nome:
            return None
        return {
            "nome": nome,
            "posicao": "Meio-Campista",
            "condicao": "Reserva",
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
    dados = _load_json_safe(ARQUIVO_ELENCO_ATUAL, {"jogadores": []})
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
        jogador = _normalizar_jogador_elenco(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(jogador)

    normalizados = _ordenar_jogadores_elenco(normalizados)
    return {"jogadores": normalizados}


def salvar_elenco_atual(dados):
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
        jogador = _normalizar_jogador_elenco(item)
        if not jogador:
            continue
        chave = jogador["nome"].casefold()
        if chave in vistos:
            continue
        vistos.add(chave)
        normalizados.append(jogador)

    jogadores_limpos = _ordenar_jogadores_elenco(normalizados)
    with open(ARQUIVO_ELENCO_ATUAL, "w", encoding="utf-8") as f:
        json.dump({"jogadores": jogadores_limpos}, f, ensure_ascii=False, indent=2)


def _normalizar_jogador_historico(item):
    if isinstance(item, str):
        nome = item.strip()
        if not nome:
            return None
        return {
            "nome": nome,
            "posicao": "Meio-Campista",
        }
    if not isinstance(item, dict):
        return None
    nome = str(item.get("nome", "")).strip()
    if not nome:
        return None
    return {
        "nome": nome,
        "posicao": _normalizar_posicao_elenco(item.get("posicao")),
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
    dados = _load_json_safe(ARQUIVO_JOGADORES_HISTORICO, {"jogadores": []})
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

    with open(ARQUIVO_JOGADORES_HISTORICO, "w", encoding="utf-8") as f:
        json.dump({"jogadores": _ordenar_jogadores_historico(normalizados)}, f, ensure_ascii=False, indent=2)


def _chave_nome_jogador(nome):
    nome_limpo = re.sub(r"\s+", " ", str(nome or "").strip())
    nome_sem_acentos = "".join(
        ch for ch in unicodedata.normalize("NFKD", nome_limpo)
        if not unicodedata.combining(ch)
    )
    return nome_sem_acentos.casefold()


def _parse_data_ptbr(s: str) -> datetime:
    # dd/mm/aaaa
    return datetime.strptime(s, "%d/%m/%Y")


def _parse_data_ptbr_safe(s: str):
    try:
        return _parse_data_ptbr(s)
    except Exception:
        return None


def _extrair_adversario_de_jogo(jogo_txt: str) -> str:
    if not jogo_txt:
        return ""
    jogo_clean = jogo_txt.replace("×", "x")
    partes = re.split(r"\s*(?:x|vs\.?)\s*", jogo_clean, maxsplit=1, flags=re.IGNORECASE)
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
        "campeonato": campeonato,
    }


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
        tw.attributes("-topmost", True)
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
        self.root.geometry("1500x1000")
        self.root.minsize(1000, 700)
        self.root.after(10, self._centralizar_janela)
        
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
        self.elenco_atual = carregar_elenco_atual()
        self.jogadores_historico = carregar_jogadores_historico()
        jogadores_elenco = [j.get("nome", "") for j in self.elenco_atual.get("jogadores", []) if j.get("nome")]
        jogadores_vasco = list(self.listas.get("jogadores_vasco", []))
        if jogadores_elenco:
            self.listas["jogadores_vasco"] = jogadores_elenco
            salvar_listas(self.listas)
        elif jogadores_vasco:
            self.elenco_atual = {
                "jogadores": [
                    {"nome": nome, "posicao": "Meio-Campista", "condicao": "Reserva"}
                    for nome in jogadores_vasco
                ]
            }
            salvar_elenco_atual(self.elenco_atual)
            self.elenco_atual = carregar_elenco_atual()
        self._evolucao_subtab_index = 0
        self._evolucao_geral_art_page = 0
        self._evolucao_geral_art_page_size = 20
        self._calendar_popup = None
        self._elenco_info_por_nome_cf = {}

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frame_futuros = ttk.Frame(self.notebook, padding=10)
        self.frame_elenco_atual = ttk.Frame(self.notebook, padding=10)
        self.frame_registro = ttk.Frame(self.notebook, padding=10)
        self.frame_temporadas = ttk.Frame(self.notebook, padding=10)
        self.frame_geral = ttk.Frame(self.notebook, padding=10)
        self.frame_comparativo = ttk.Frame(self.notebook, padding=10)
        self.frame_tecnicos = ttk.Frame(self.notebook, padding=10)
        self.frame_graficos = ttk.Frame(self.notebook, padding=10)
        self.frame_jogadores_historico = ttk.Frame(self.notebook, padding=10)

        self.notebook.insert(0, self.frame_futuros, text="Jogos Futuros")
        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_temporadas, text="Temporadas")
        self.notebook.add(self.frame_geral, text="Geral")
        self.notebook.add(self.frame_comparativo, text="Comparativo")
        self.notebook.add(self.frame_tecnicos, text="Técnicos")
        self.notebook.add(self.frame_graficos, text="Evolução")
        self.notebook.add(self.frame_elenco_atual, text="Elenco Atual")
        self.notebook.add(self.frame_jogadores_historico, text="Jogadores")

        self._criar_aba_futuros(self.frame_futuros)
        self._criar_aba_elenco_atual(self.frame_elenco_atual)
        self._criar_aba_jogadores_historico(self.frame_jogadores_historico)
        self._criar_formulario(self.frame_registro)
        self._sincronizar_jogadores_historico()
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_comparativo()
        self._carregar_graficos()
        self._carregar_tecnicos()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_notebook_tab_changed, add="+")
        self.notebook.select(self.frame_registro)

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
        self.fut_manual_em_casa_var = tk.BooleanVar(value=True)
        self.fut_manual_campeonato_var = tk.StringVar()

        ttk.Label(manual_frame, text="Adversário:").grid(row=0, column=0, sticky="w", pady=3)
        adversarios_disputados = sorted({
            str(j.get("adversario", "")).strip()
            for j in carregar_dados_jogos()
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
            for j in carregar_dados_jogos()
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
        ttk.Checkbutton(manual_frame, text="Vasco em casa (em_casa = true)", variable=self.fut_manual_em_casa_var).grid(
            row=2, column=2, columnspan=2, sticky="w", pady=3, padx=(10, 0)
        )

        ttk.Button(manual_frame, text="Adicionar Jogo", command=self._adicionar_jogo_futuro_manual).grid(
            row=3, column=0, columnspan=4, sticky="e", pady=(6, 0)
        )

        ttk.Label(frame, text="Jogos futuros cadastrados:").grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 6))

        list_wrap = ttk.Frame(frame)
        list_wrap.grid(row=4, column=0, columnspan=2, sticky="nsew")
        list_wrap.rowconfigure(0, weight=1)
        list_wrap.columnconfigure(0, weight=1)

        cols = ("data", "jogo", "local", "campeonato")
        self.tv_futuros = ttk.Treeview(list_wrap, columns=cols, show="headings", height=10)
        self.tv_futuros.heading("data", text="Data")
        self.tv_futuros.heading("jogo", text="Jogo")
        self.tv_futuros.heading("local", text="Em casa?")
        self.tv_futuros.heading("campeonato", text="Campeonato")
        self.tv_futuros.column("data", width=100, anchor="center")
        self.tv_futuros.column("jogo", width=320, anchor="w")
        self.tv_futuros.column("local", width=90, anchor="center")
        self.tv_futuros.column("campeonato", width=240, anchor="w")
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
        self.tv_retro_futuros.column("resultado", width=90, anchor="center")
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
                str(item.get("jogo", "")).strip(),
                item.get("em_casa"),
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

    def _copiar_exemplo_json_futuros(self):
        exemplo = [
            {
                "jogo": "Vasco x Time adversario",
                "data": "18/02/2026",
                "em_casa": True,
                "campeonato": "Campeonato Carioca"
            },
            {
                "jogo": "Time adversario x Vasco",
                "data": "22/02/2026",
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
        self.fut_manual_em_casa_var.set(True)

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
        adversario = self.fut_manual_adversario_var.get().strip()
        data_txt = self.fut_manual_data_var.get().strip()
        campeonato = self.fut_manual_campeonato_var.get().strip()
        em_casa = bool(self.fut_manual_em_casa_var.get())

        if not adversario or not data_txt:
            messagebox.showerror("Erro", "Preencha pelo menos os campos Adversário e Data.")
            return

        jogo = f"Vasco x {adversario}" if em_casa else f"{adversario} x Vasco"
        item = {
            "jogo": jogo,
            "data": data_txt,
            "em_casa": em_casa,
            "campeonato": campeonato,
        }
        normalizado = _normalizar_futuro_item(item)
        if not normalizado:
            messagebox.showerror("Erro", "Não foi possível normalizar o jogo informado.")
            return
        if not _parse_data_ptbr_safe(normalizado["data"]):
            messagebox.showerror("Erro", "Data inválida. Use o formato dd/mm/aaaa.")
            return

        jogos = carregar_jogos_futuros()
        jogos.append(normalizado)
        salvar_lista_futuros(jogos)
        self._render_lista_futuros()
        self.fut_manual_adversario_var.set("")
        self.fut_manual_campeonato_var.set("")
        messagebox.showinfo("Sucesso", "Jogo futuro adicionado.")

    def _render_lista_futuros(self):
        for iid in self.tv_futuros.get_children():
            self.tv_futuros.delete(iid)

        jogos = carregar_jogos_futuros()
        jogos_validos = []
        for item in jogos:
            normalizado = _normalizar_futuro_item(item)
            if not normalizado:
                continue
            data_obj = _parse_data_ptbr_safe(normalizado["data"])
            if not data_obj:
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
                values=(jogo.get("data"), jogo.get("jogo"), local, jogo.get("campeonato") or "-"),
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
        alvo = adversario.casefold()
        for jogo in jogos:
            adv_jogo = str(jogo.get("adversario", "")).strip()
            if not adv_jogo or adv_jogo.casefold() != alvo:
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
        if len(values) < 2:
            self._retro_partidas_atual = []
            self.retro_resumo_var.set("Não foi possível identificar o adversário.")
            return

        jogo_txt = str(values[1]).strip()
        adversario = _extrair_adversario_de_jogo(jogo_txt).replace("Vasco", "").strip()
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
                    partida["resultado"],
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

    def _abrir_menu_contexto_futuros(self, event):
        iid = self.tv_futuros.identify_row(event.y)
        if not iid:
            return
        self.tv_futuros.selection_set(iid)
        self.tv_futuros.focus(iid)

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Excluir jogo futuro", command=self._excluir_jogo_futuro_selecionado)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _excluir_jogo_futuro_selecionado(self):
        sel = self.tv_futuros.selection()
        if not sel:
            return
        values = self.tv_futuros.item(sel[0], "values")
        if len(values) < 4:
            return
        data_txt, jogo_txt, local_txt, campeonato_txt = values
        desc = f"{data_txt} | {jogo_txt}"
        if not messagebox.askyesno("Excluir jogo futuro", f"Deseja excluir este jogo futuro?\n\n{desc}"):
            return

        futuros = carregar_jogos_futuros()
        novos = []
        removido = False
        for item in futuros:
            normalizado = _normalizar_futuro_item(item)
            if not normalizado or removido:
                novos.append(item)
                continue

            mesmo_jogo = (
                str(normalizado.get("data", "")) == str(data_txt)
                and str(normalizado.get("jogo", "")) == str(jogo_txt)
                and self._local_futuro_txt(normalizado.get("em_casa")) == str(local_txt)
                and str(normalizado.get("campeonato") or "-") == str(campeonato_txt)
            )
            if mesmo_jogo:
                removido = True
                continue
            novos.append(item)

        if not removido:
            messagebox.showwarning("Não encontrado", "Não foi possível localizar o jogo futuro para exclusão.")
            return

        salvar_lista_futuros(novos)
        self._render_lista_futuros()

    def _importar_futuro_para_registro(self, _event=None):
        sel = self.tv_futuros.selection()
        if not sel:
            return
        values = self.tv_futuros.item(sel[0], "values")
        if len(values) < 4:
            return
        data_txt, jogo_txt, local_txt, campeonato_txt = values
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

        self.elenco_nome_var = tk.StringVar()
        self.elenco_posicao_var = tk.StringVar(value=ELENCO_POSICAO_PLACEHOLDER)
        self.elenco_condicao_var = tk.StringVar(value=ELENCO_CONDICAO_PLACEHOLDER)
        self.elenco_modo_var = tk.StringVar(value="")
        self.elenco_botao_var = tk.StringVar(value="Adicionar")
        self.elenco_resumo_var = tk.StringVar(value="")
        self._elenco_edit_nome_cf = None

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

        ttk.Button(
            entrada_wrap, textvariable=self.elenco_botao_var, command=self._adicionar_jogador_elenco
        ).grid(row=0, column=6)

        ttk.Label(frame, textvariable=self.elenco_resumo_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        list_wrap = ttk.Frame(frame)
        list_wrap.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        list_wrap.rowconfigure(0, weight=1)
        list_wrap.columnconfigure(0, weight=1)

        cols = ("posicao", "jogador", "condicao")
        self.tv_elenco_atual = ttk.Treeview(list_wrap, columns=cols, show="headings", height=14)
        self.tv_elenco_atual.heading("posicao", text="Posição")
        self.tv_elenco_atual.heading("jogador", text="Jogador")
        self.tv_elenco_atual.heading("condicao", text="Condição")
        self.tv_elenco_atual.column("posicao", width=180, anchor="w")
        self.tv_elenco_atual.column("jogador", width=340, anchor="w")
        self.tv_elenco_atual.column("condicao", width=150, anchor="center")
        self.tv_elenco_atual.tag_configure("status_titulares", background="#dff5e6", foreground="#173a23")
        self.tv_elenco_atual.tag_configure("status_reservas", background="#fff4cf", foreground="#4a3a06")
        self.tv_elenco_atual.tag_configure("status_nao_relacionados", background="#ffe3c2", foreground="#4f2a09")
        self.tv_elenco_atual.tag_configure("status_lesionados", background="#ffd6d6", foreground="#5a1414")
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
        cont = {"Titular": 0, "Reserva": 0, "Não Relacionado": 0, "Lesionado": 0}
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
            else:
                tag = "status_sem_lista"
            self.tv_elenco_atual.insert(
                "",
                "end",
                values=(jogador.get("posicao", ""), jogador.get("nome", ""), jogador.get("condicao", "")),
                tags=(tag,)
            )
        if hasattr(self, "elenco_resumo_var"):
            self.elenco_resumo_var.set(
                f"Titulares: {cont['Titular']} | Reservas: {cont['Reserva']} | "
                f"Não Relacionados: {cont['Não Relacionado']} | Lesionados: {cont['Lesionado']}"
            )
        self._render_campinho_elenco()

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
        self.elenco_atual = carregar_elenco_atual()
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
            _pos, nome_iid, _cond = self.tv_elenco_atual.item(iid, "values")
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
        posicao, nome, condicao = self.tv_elenco_atual.item(selecao[0], "values")
        nome = str(nome).strip()
        if not nome:
            return
        self._elenco_edit_nome_cf = nome.casefold()
        self.elenco_nome_var.set(nome)
        self.elenco_posicao_var.set(_normalizar_posicao_elenco(posicao))
        self.elenco_condicao_var.set(_normalizar_condicao_elenco(condicao))
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

    def _salvar_elenco_da_interface(self):
        jogadores = []
        for iid in self.tv_elenco_atual.get_children():
            posicao, nome, condicao = self.tv_elenco_atual.item(iid, "values")
            jogadores.append(
                {"nome": str(nome).strip(), "posicao": str(posicao).strip(), "condicao": str(condicao).strip()}
            )
        self.elenco_atual = {"jogadores": jogadores}
        salvar_elenco_atual(self.elenco_atual)
        self.elenco_atual = carregar_elenco_atual()
        self._render_elenco_atual()
        self._sincronizar_jogadores_vasco_com_elenco()

    def _sincronizar_jogadores_vasco_com_elenco(self):
        self._atualizar_opcoes_gol_vasco(persistir=True)
        self._sincronizar_jogadores_historico()
        if hasattr(self, "_render_elenco_atual"):
            self._render_elenco_atual()
        if hasattr(self, "_render_aba_jogadores_historico"):
            self._render_aba_jogadores_historico()
        self._atualizar_elenco_disponivel_partida()
        if hasattr(self, "escalacao_partida"):
            self._inicializar_escalacao_partida()

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
        self.listas["jogadores_vasco"] = opcoes
        if hasattr(self, "entry_gol_vasco"):
            self.entry_gol_vasco["values"] = opcoes
        if persistir:
            salvar_listas(self.listas)

    def _on_notebook_tab_changed(self, event):
        if event.widget is not self.notebook:
            return
        atual = self.notebook.select()
        if str(atual) != str(self.frame_registro):
            return
        # Sempre espelha o que estiver salvo no Elenco Atual ao entrar na aba de registro.
        self.elenco_atual = carregar_elenco_atual()
        self._sincronizar_jogadores_vasco_com_elenco()

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
            nova_condicao = nomes_por_condicao.get(nome.casefold(), "Não Relacionado")
            if jogador.get("condicao") != nova_condicao:
                jogador["condicao"] = nova_condicao
                alterou = True

        if alterou:
            salvar_elenco_atual(self.elenco_atual)
            self.elenco_atual = carregar_elenco_atual()
            self._sincronizar_jogadores_vasco_com_elenco()

    def _adicionar_jogador_elenco(self, _event=None):
        nome = self.elenco_nome_var.get().strip()
        posicao_raw = self.elenco_posicao_var.get().strip()
        condicao_raw = self.elenco_condicao_var.get().strip()
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
            _pos_atual, nome_atual, cond_atual = self.tv_elenco_atual.item(iid, "values")
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
                self.tv_elenco_atual.item(iid_edit, values=(posicao, nome, condicao))
            else:
                self.tv_elenco_atual.insert("", "end", values=(posicao, nome, condicao))
        elif nome.casefold() in nomes_atuais:
            messagebox.showwarning("Duplicado", f"'{nome}' já está no elenco atual.")
            return
        else:
            self.tv_elenco_atual.insert("", "end", values=(posicao, nome, condicao))

        self._resetar_modo_edicao_elenco()
        self.elenco_nome_var.set("")
        self.elenco_posicao_var.set(ELENCO_POSICAO_PLACEHOLDER)
        self.elenco_condicao_var.set(ELENCO_CONDICAO_PLACEHOLDER)
        self._salvar_elenco_da_interface()

    def _remover_jogador_elenco(self, _event=None):
        selecao = self.tv_elenco_atual.selection()
        if not selecao:
            return
        pos_removida, nome_removido, _ = self.tv_elenco_atual.item(selecao[0], "values")
        self._adicionar_jogadores_historico([{"nome": str(nome_removido).strip(), "posicao": str(pos_removida).strip()}])
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
            posicao, nome, _cond = self.tv_elenco_atual.item(iid, "values")
            removidos.append({"nome": str(nome).strip(), "posicao": str(posicao).strip()})
        self._adicionar_jogadores_historico(removidos)
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
        for item in jogadores:
            jogador = _normalizar_jogador_historico(item)
            if not jogador:
                continue
            chave = jogador["nome"].casefold()
            atual = mapa.get(chave)
            if not atual:
                mapa[chave] = jogador
                alterou = True
                continue
            pos_atual = _normalizar_posicao_elenco(atual.get("posicao"))
            pos_nova = _normalizar_posicao_elenco(jogador.get("posicao"))
            if pos_atual == "Meio-Campista" and pos_nova != "Meio-Campista":
                atual["posicao"] = pos_nova
                mapa[chave] = atual
                alterou = True
        if not alterou:
            return
        self.jogadores_historico = {"jogadores": _ordenar_jogadores_historico(list(mapa.values()))}
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
        if hasattr(self, "_render_aba_jogadores_historico"):
            self._render_aba_jogadores_historico()

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
        ttk.Button(filtros, text="Limpar", command=self._limpar_busca_jogadores_historico).pack(side="left")
        self.jogadores_hist_busca_var.trace_add("write", lambda *_: self._render_aba_jogadores_historico())

        cols = ("posicao", "jogador", "status")
        self.tv_jogadores_historico = ttk.Treeview(esquerda, columns=cols, show="headings", height=16)
        self.tv_jogadores_historico.heading("posicao", text="Posição")
        self.tv_jogadores_historico.heading("jogador", text="Jogador")
        self.tv_jogadores_historico.heading("status", text="Status")
        self.tv_jogadores_historico.column("posicao", width=150, anchor="w")
        self.tv_jogadores_historico.column("jogador", width=280, anchor="w")
        self.tv_jogadores_historico.column("status", width=130, anchor="center")
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

        self.tv_detalhes_jogador_historico = ttk.Treeview(
            direita,
            columns=("metrica", "valor"),
            show="headings",
            height=16,
        )
        self.tv_detalhes_jogador_historico.heading("metrica", text="Métrica")
        self.tv_detalhes_jogador_historico.heading("valor", text="Valor")
        self.tv_detalhes_jogador_historico.column("metrica", width=320, anchor="w")
        self.tv_detalhes_jogador_historico.column("valor", width=180, anchor="w")
        self.tv_detalhes_jogador_historico.tag_configure("odd", background=self.colors["row_alt_bg"])
        self.tv_detalhes_jogador_historico.grid(row=1, column=0, sticky="nsew")

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

        atuais = {
            str(j.get("nome", "")).strip().casefold(): _normalizar_condicao_elenco(j.get("condicao"))
            for j in self.elenco_atual.get("jogadores", [])
            if isinstance(j, dict) and str(j.get("nome", "")).strip()
        }
        self.tv_jogadores_historico.delete(*self.tv_jogadores_historico.get_children())
        novo_sel = None
        for i, jogador in enumerate(_ordenar_jogadores_historico(list(self.jogadores_historico.get("jogadores", []))), start=1):
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            posicao = _normalizar_posicao_elenco(jogador.get("posicao"))
            cond = atuais.get(nome.casefold())
            status = cond if cond else "Ex-jogador"
            if termo:
                haystack = f"{posicao} {nome} {status}".casefold()
                if termo not in haystack:
                    continue
            iid = self.tv_jogadores_historico.insert(
                "",
                "end",
                values=(posicao, nome, status),
                tags=("odd",) if i % 2 else (),
            )
            if selecionado_cf and nome.casefold() == selecionado_cf:
                novo_sel = iid
        if novo_sel:
            self.tv_jogadores_historico.selection_set(novo_sel)
            self.tv_jogadores_historico.focus(novo_sel)
            self._ao_selecionar_jogador_historico()

    def _limpar_busca_jogadores_historico(self):
        if hasattr(self, "jogadores_hist_busca_var"):
            self.jogadores_hist_busca_var.set("")

    def _ao_selecionar_jogador_historico(self, _event=None):
        if not hasattr(self, "tv_jogadores_historico") or not hasattr(self, "tv_detalhes_jogador_historico"):
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
        tv = self.tv_detalhes_jogador_historico
        tv.delete(*tv.get_children())
        for i, (metrica, valor) in enumerate(detalhes, start=1):
            tv.insert("", "end", values=(metrica, valor), tags=("odd",) if i % 2 else ())

    def _coletar_detalhes_jogador_historico(self, nome):
        alvo = _chave_nome_jogador(nome)
        jogos = carregar_dados_jogos()
        jogos_total = len(jogos)
        jogos_com_escalacao = 0
        jogos_com_participacao = 0
        jogos_titular = 0
        jogos_reserva = 0
        jogos_nao_rel = 0
        jogos_lesionado = 0
        gols = 0
        partidas_com_gol = 0
        gols_banco = 0
        gols_titular = 0
        vitorias = empates = derrotas = 0

        for jogo in jogos:
            participou = False
            gol_no_jogo = 0
            gol_banco_jogo = 0
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
                    if bool(g.get("saiu_do_banco", False)):
                        gol_banco_jogo += qtd
                elif isinstance(g, str):
                    nome_g = g.strip()
                    if _chave_nome_jogador(nome_g) == alvo:
                        gol_no_jogo += 1

            if gol_no_jogo > 0:
                participou = True
                gols += gol_no_jogo
                partidas_com_gol += 1
                gols_banco += gol_banco_jogo
                gols_titular += max(0, gol_no_jogo - gol_banco_jogo)

            esc = jogo.get("escalacao")
            if isinstance(esc, dict):
                jogos_com_escalacao += 1
                em_titulares = False
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
                if em_titulares:
                    jogos_titular += 1
                    participou = True
                elif any(_chave_nome_jogador(nm) == alvo for nm in esc.get("reservas", [])):
                    jogos_reserva += 1
                    participou = True
                elif any(_chave_nome_jogador(nm) == alvo for nm in esc.get("nao_relacionados", [])):
                    jogos_nao_rel += 1
                elif any(_chave_nome_jogador(nm) == alvo for nm in esc.get("lesionados", [])):
                    jogos_lesionado += 1

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
        detalhes = [
            ("Jogos do Vasco registrados", jogos_total),
            ("Jogos com participação do jogador", jogos_com_participacao),
            ("Jogos como titular (com escalação salva)", jogos_titular),
            ("Jogos como reserva (com escalação salva)", jogos_reserva),
            ("Jogos como não relacionado", jogos_nao_rel),
            ("Jogos como lesionado", jogos_lesionado),
            ("Gols pelo Vasco", gols),
            ("Partidas em que marcou", partidas_com_gol),
            ("Gols como titular", gols_titular),
            ("Gols saindo do banco", gols_banco),
            ("Média de gols por jogo com participação", media_gols),
            ("Participação (V/E/D)", f"{vitorias}/{empates}/{derrotas}"),
            ("Jogos com escalação disponível", jogos_com_escalacao),
        ]
        return detalhes

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
        posicao, nome, status = vals
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
            }
        )
        salvar_elenco_atual(self.elenco_atual)
        self.elenco_atual = carregar_elenco_atual()
        self._sincronizar_jogadores_vasco_com_elenco()
        self._render_aba_jogadores_historico()

    def _abrir_menu_contexto_elenco_atual(self, event):
        iid = self.tv_elenco_atual.identify_row(event.y)
        if not iid:
            return
        self.tv_elenco_atual.selection_set(iid)
        self.tv_elenco_atual.focus(iid)

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
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _enviar_jogador_elenco_para(self, destino):
        sel = self.tv_elenco_atual.selection()
        if not sel:
            return
        iid = sel[0]
        posicao_atual, nome, condicao_atual = self.tv_elenco_atual.item(iid, "values")
        nome = str(nome).strip()
        if not nome:
            return

        tipo, chave = destino
        nova_posicao = str(posicao_atual).strip()
        nova_condicao = _normalizar_condicao_elenco(condicao_atual)
        if tipo == "titulares":
            nova_posicao = _normalizar_posicao_elenco(chave)
            nova_condicao = "Titular"
            titulares_atuais = 0
            for row_iid in self.tv_elenco_atual.get_children():
                _p, row_nome, row_cond = self.tv_elenco_atual.item(row_iid, "values")
                if _normalizar_condicao_elenco(row_cond) == "Titular" and str(row_nome).strip().casefold() != nome.casefold():
                    titulares_atuais += 1
            if titulares_atuais >= 11:
                messagebox.showerror("Limite de titulares", "Não é possível ter mais de 11 titulares no elenco atual.")
                return
        else:
            if chave == "reservas":
                nova_condicao = "Reserva"
            elif chave == "nao_relacionados":
                nova_condicao = "Não Relacionado"
            elif chave == "lesionados":
                nova_condicao = "Lesionado"

        self.tv_elenco_atual.item(iid, values=(nova_posicao, nome, nova_condicao))
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
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=0)

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

        ttk.Label(topo, text="Data:").grid(row=0, column=0, sticky="w", pady=3)
        data_wrap = ttk.Frame(topo)
        data_wrap.grid(row=0, column=1, sticky="w", pady=3)
        self.data_entry = ttk.Entry(data_wrap, width=12, textvariable=self.data_var)
        self.data_entry.pack(side="left")
        self._forcar_cursor_visivel(self.data_entry)
        ttk.Button(data_wrap, text="Calendário", command=self._abrir_calendario_popup).pack(side="left", padx=(8, 0))

        ttk.Label(topo, text="Técnico:").grid(row=0, column=2, sticky="w", padx=(12, 4), pady=3)
        self.tecnico_entry = ttk.Combobox(topo, textvariable=self.tecnico_var, width=24)
        self.tecnico_entry["values"] = self.listas.get("tecnicos", [])
        self.tecnico_entry.grid(row=0, column=3, sticky="ew", pady=3)
        self.tecnico_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "tecnicos"))
        self._forcar_cursor_visivel(self.tecnico_entry)

        ttk.Label(topo, text="Adversário:").grid(row=0, column=4, sticky="w", padx=(12, 4), pady=3)
        self.adversario_entry = ttk.Combobox(topo, textvariable=self.adversario_var)
        self.adversario_entry["values"] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=0, column=5, sticky="ew", pady=3)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))
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

        placar_card = ttk.Labelframe(frame, text="Placar", padding=10)
        placar_card.grid(row=1, column=0, sticky="ew", pady=(10, 0))
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
        meio.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        meio.columnconfigure(0, weight=1)
        meio.columnconfigure(1, weight=1)
        meio.rowconfigure(0, weight=1)

        # Coluna esquerda: gols
        gols_card = ttk.Labelframe(meio, text="Gols da Partida", padding=10)
        gols_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        gols_card.columnconfigure(0, weight=1)
        gols_card.rowconfigure(1, weight=1)
        gols_card.rowconfigure(3, weight=1)

        ttk.Label(gols_card, text="Gols do Vasco (Enter para adicionar):").grid(row=0, column=0, sticky="w")
        col_vasco = ttk.Frame(gols_card)
        col_vasco.grid(row=1, column=0, sticky="nsew", pady=(4, 8))
        col_vasco.columnconfigure(0, weight=1)
        col_vasco.rowconfigure(1, weight=1)
        self.entry_gol_vasco = ttk.Combobox(col_vasco)
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
        self.entry_gol_contra = ttk.Combobox(col_contra)
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

        # Coluna direita: escalação em modal
        escalacao_card = ttk.Labelframe(meio, text="Escalação da Partida", padding=10)
        escalacao_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        escalacao_card.columnconfigure(0, weight=1)
        escalacao_card.rowconfigure(3, weight=1)

        ttk.Label(
            escalacao_card,
            text="Configure titulares por posição e banco em uma tela dedicada."
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(
            escalacao_card,
            text="Abrir Modal de Escalação",
            command=self._abrir_modal_escalacao_partida
        ).grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.escalacao_resumo_var = tk.StringVar(value="")
        ttk.Label(escalacao_card, textvariable=self.escalacao_resumo_var).grid(row=2, column=0, sticky="w")

        preview_wrap = ttk.Frame(escalacao_card)
        preview_wrap.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
        preview_wrap.columnconfigure(0, weight=1)
        preview_wrap.columnconfigure(1, weight=0)
        preview_wrap.rowconfigure(0, weight=1)

        self.canvas_campinho_preview = tk.Canvas(
            preview_wrap,
            background="#0f6a35",
            highlightthickness=1,
            highlightbackground="#1a1a1a"
        )
        self.canvas_campinho_preview.grid(row=0, column=0, sticky="nsew")
        self.canvas_campinho_preview.bind("<Configure>", lambda _e: self._render_preview_escalacao())

        reservas_wrap = ttk.Labelframe(preview_wrap, text="Reservas", padding=6)
        reservas_wrap.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        reservas_wrap.columnconfigure(0, weight=1)
        reservas_wrap.rowconfigure(0, weight=1)
        self.lista_reservas_preview = tk.Listbox(
            reservas_wrap,
            width=24,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_reservas_preview.grid(row=0, column=0, sticky="ns")

        # Observações
        obs_card = ttk.Labelframe(frame, text="Observações da Partida", padding=10)
        obs_card.grid(row=3, column=0, sticky="nsew", pady=(10, 0))
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
        botoes.grid(row=4, column=0, pady=12, sticky="ew")
        ttk.Label(botoes, textvariable=self.modo_edicao_var, foreground=self.colors["accent"]).pack(side="left", padx=(0, 12))
        self.btn_salvar = ttk.Button(botoes, textvariable=self.salvar_btn_label, command=self.salvar_partida)
        self.btn_salvar.pack(side="left", padx=6)
        ttk.Button(botoes, text="Limpar Campos", command=self._limpar_formulario).pack(side="left", padx=6)
        self.btn_cancelar_edicao = ttk.Button(botoes, text="Cancelar Edição", command=self._cancelar_edicao)
        self.btn_cancelar_edicao.pack(side="left", padx=6)
        self.btn_cancelar_edicao.state(["disabled"])
        ttk.Button(botoes, text="Atualizar Abas", command=self._atualizar_abas).pack(side="left", padx=6)

        self._inicializar_escalacao_partida()

    def _render_preview_escalacao(self):
        if not hasattr(self, "canvas_campinho_preview"):
            return
        canvas = self.canvas_campinho_preview
        canvas.delete("all")
        self._preview_hit_players = []

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
                nome_curto = nome if len(nome) <= 21 else (nome[:20] + "…")
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
            for nome in esc.get("reservas", []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    self.lista_reservas_preview.insert(tk.END, nome_limpo)

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

    def _atualizar_elenco_disponivel_partida(self):
        self._elenco_info_por_nome_cf = {}
        jogadores = _ordenar_jogadores_elenco(list(self.elenco_atual.get("jogadores", [])))
        for jogador in jogadores:
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            self._elenco_info_por_nome_cf[nome.casefold()] = {
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
            "nao_relacionados": [],
            "lesionados": [],
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
        return base

    def _atualizar_resumo_escalacao(self):
        esc = getattr(self, "escalacao_partida", self._escalacao_partida_base())
        titulares = sum(len(esc["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        reservas = len(esc.get("reservas", []))
        nao_rel = len(esc.get("nao_relacionados", []))
        lesionados = len(esc.get("lesionados", []))
        self.escalacao_resumo_var.set(
            f"Titulares: {titulares}/11 | Reservas: {reservas} (mín. 4) | "
            f"Não Relac.: {nao_rel} | Lesionados: {lesionados}"
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
            else:
                base["lesionados"].append(nome)
        self._carregar_escalacao_partida(base)

    def _coletar_escalacao_partida(self):
        return self._normalizar_escalacao_partida(getattr(self, "escalacao_partida", self._escalacao_partida_base()))

    def _validar_escalacao_partida(self, escalacao):
        titulares = sum(len(escalacao["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        goleiros_titulares = len(escalacao["titulares_por_posicao"].get("Goleiro", []))
        reservas = len(escalacao.get("reservas", []))
        if titulares != 11:
            return False, "A escalação precisa ter exatamente 11 titulares."
        if goleiros_titulares != 1:
            return False, "A escalação precisa ter exatamente 1 goleiro titular."
        if reservas < 4:
            return False, "A escalação precisa ter pelo menos 4 reservas."

        nomes_elenco = {
            str(j.get("nome", "")).strip().casefold()
            for j in self.elenco_atual.get("jogadores", [])
            if isinstance(j, dict) and str(j.get("nome", "")).strip()
        }
        nomes_escalados = set()
        for pos in POSICOES_ELENCO:
            for nome in escalacao["titulares_por_posicao"].get(pos, []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    nomes_escalados.add(nome_limpo.casefold())
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            for nome in escalacao.get(chave, []):
                nome_limpo = str(nome).strip()
                if nome_limpo:
                    nomes_escalados.add(nome_limpo.casefold())

        faltando = sorted(nomes_elenco - nomes_escalados)
        if faltando:
            return False, "Todos os jogadores do elenco precisam estar em alguma lista da escalação."
        return True, ""

    def _carregar_escalacao_partida(self, escalacao):
        self.escalacao_partida = self._normalizar_escalacao_partida(escalacao)
        self._atualizar_resumo_escalacao()
        self._render_preview_escalacao()
        self._atualizar_opcoes_gol_vasco()

    def _abrir_modal_escalacao_partida(self):
        existente = getattr(self, "_modal_escalacao_partida", None)
        if existente and existente.winfo_exists():
            existente.lift()
            existente.focus_force()
            return

        self._atualizar_elenco_disponivel_partida()
        draft = self._coletar_escalacao_partida()

        top = tk.Toplevel(self.root)
        top.title("Escalação da Partida")
        top.transient(self.root)
        top.grab_set()
        top.lift()
        top.focus_force()
        modal_w = 1200
        modal_h = 780
        self.root.update_idletasks()
        try:
            root_x = self.root.winfo_rootx()
            root_y = self.root.winfo_rooty()
            root_w = self.root.winfo_width()
            root_h = self.root.winfo_height()
            modal_w, modal_h = root_w, root_h
            top.geometry(f"{modal_w}x{modal_h}+{root_x}+{root_y}")
        except Exception:
            top.geometry("1200x780")
        self._modal_escalacao_partida = top

        largura_esquerda = max(360, min(440, int(modal_w * 0.30)))
        top.columnconfigure(0, weight=0, minsize=largura_esquerda)
        top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)

        esquerda = ttk.Labelframe(top, text="Elenco Atual (lista geral)", padding=8)
        esquerda.grid(row=0, column=0, sticky="nsew", padx=(10, 6), pady=10)
        esquerda.grid_propagate(False)
        esquerda.columnconfigure(0, weight=1)
        esquerda.rowconfigure(0, weight=1)

        self._modal_tv_elenco = ttk.Treeview(esquerda, columns=("nome", "posicao"), show="headings")
        self._modal_tv_elenco.heading("nome", text="Jogador")
        self._modal_tv_elenco.heading("posicao", text="Posição")
        largura_nome = 220
        largura_posicao = 150
        self._modal_tv_elenco.column("nome", width=largura_nome, minwidth=220, anchor="w", stretch=False)
        self._modal_tv_elenco.column("posicao", width=largura_posicao, minwidth=120, anchor="w", stretch=False)
        self._modal_tv_elenco.tag_configure("status_titulares", background="#dff5e6", foreground="#173a23")
        self._modal_tv_elenco.tag_configure("status_reservas", background="#fff4cf", foreground="#4a3a06")
        self._modal_tv_elenco.tag_configure("status_nao_relacionados", background="#ffe3c2", foreground="#4f2a09")
        self._modal_tv_elenco.tag_configure("status_lesionados", background="#ffd6d6", foreground="#5a1414")
        self._modal_tv_elenco.tag_configure("status_sem_lista", background="#e6e7eb", foreground="#2f3136")
        self._modal_tv_elenco.tag_configure("sep_posicao", background=self.colors["bg2"], foreground=self.colors["bg2"])
        self._modal_tv_elenco.grid(row=0, column=0, sticky="nsew")
        sy = ttk.Scrollbar(esquerda, orient="vertical", command=self._modal_tv_elenco.yview)
        sy.grid(row=0, column=1, sticky="ns")
        self._modal_tv_elenco.configure(yscrollcommand=sy.set)
        self._modal_tv_elenco.bind(
            "<Button-3>",
            lambda e: self._abrir_menu_contexto_escalacao_modal(e, ("elenco", None))
        )
        self._modal_tv_elenco.bind(
            "<Control-Button-1>",
            lambda e: self._abrir_menu_contexto_escalacao_modal(e, ("elenco", None))
        )

        self._modal_tv_elenco.delete(*self._modal_tv_elenco.get_children())

        direita = ttk.Frame(top)
        direita.grid(row=0, column=1, sticky="nsew", padx=(6, 10), pady=10)
        direita.columnconfigure(0, weight=1)
        direita.rowconfigure(1, weight=1)

        header = ttk.Frame(direita)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self._modal_resumo_var = tk.StringVar(value="")
        ttk.Label(header, textvariable=self._modal_resumo_var).grid(row=0, column=0, sticky="w")

        conteudo = ttk.Frame(direita)
        conteudo.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        conteudo.columnconfigure(0, weight=1)
        conteudo.columnconfigure(1, weight=1)
        conteudo.rowconfigure(0, weight=5, minsize=320)
        conteudo.rowconfigure(1, weight=1, minsize=140)
        conteudo.rowconfigure(2, weight=1, minsize=140)

        titulares_frame = ttk.Labelframe(conteudo, text="Titulares no Campinho", padding=10)
        titulares_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(4, 4), pady=(4, 10))
        titulares_frame.columnconfigure(0, weight=1)
        titulares_frame.rowconfigure(0, weight=1)

        self._modal_canvas_campinho = tk.Canvas(
            titulares_frame,
            background="#0f6a35",
            highlightthickness=1,
            highlightbackground="#1a1a1a",
            height=340,
        )
        self._modal_canvas_campinho.grid(row=0, column=0, sticky="nsew")
        self._modal_canvas_campinho.bind("<Configure>", lambda _e: self._modal_render_campinho())
        self._modal_canvas_campinho.bind("<ButtonPress-1>", self._modal_campinho_drag_start)
        self._modal_canvas_campinho.bind("<ButtonRelease-1>", self._modal_campinho_drag_end)
        self._modal_canvas_campinho.bind("<Button-3>", lambda e: self._abrir_menu_contexto_escalacao_modal(e, ("campinho", None)))
        self._modal_canvas_campinho.bind("<Control-Button-1>", lambda e: self._abrir_menu_contexto_escalacao_modal(e, ("campinho", None)))
        self._modal_titulares_por_posicao = {pos: [] for pos in POSICOES_ELENCO}

        self._modal_lb_extras = {}
        for idx, (chave, titulo) in enumerate(CATEGORIAS_ESCALACAO_EXTRAS):
            r, c = divmod(idx, 2)
            bloco = ttk.Labelframe(conteudo, text=titulo, padding=10)
            bloco.grid(
                row=1 + r, column=c, sticky="nsew",
                padx=(4 if c == 0 else 6, 6 if c == 0 else 4),
                pady=(4, 10 if r == 0 else 4)
            )
            bloco.columnconfigure(0, weight=1)
            bloco.rowconfigure(0, weight=1)
            if chave == "reservas":
                lb_bg, lb_fg = "#fff4cf", "#4a3a06"
            elif chave == "nao_relacionados":
                lb_bg, lb_fg = "#ffe3c2", "#4f2a09"
            else:  # lesionados
                lb_bg, lb_fg = "#ffd6d6", "#5a1414"
            lb = tk.Listbox(
                bloco, height=6,
                bg=lb_bg, fg=lb_fg,
                selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
            )
            lb.grid(row=0, column=0, sticky="nsew")
            lb.bind("<Delete>", lambda _e, k=chave: self._modal_remover_jogador(("extras", k)))
            lb.bind("<Button-3>", lambda e, k=chave: self._abrir_menu_contexto_escalacao_modal(e, ("extras", k)))
            lb.bind("<Control-Button-1>", lambda e, k=chave: self._abrir_menu_contexto_escalacao_modal(e, ("extras", k)))
            botoes = ttk.Frame(bloco)
            botoes.grid(row=1, column=0, sticky="ew", pady=(6, 0))
            ttk.Button(botoes, text="Adicionar", command=lambda k=chave: self._modal_adicionar_jogador(("extras", k))).pack(side="left")
            ttk.Button(botoes, text="Remover", command=lambda k=chave: self._modal_remover_jogador(("extras", k))).pack(side="right")
            self._modal_lb_extras[chave] = lb

        rodape = ttk.Frame(direita)
        rodape.grid(row=2, column=0, sticky="e", pady=(14, 14), padx=(0, 14))
        ttk.Button(rodape, text="Cancelar", command=self._fechar_modal_escalacao_partida).pack(side="left", padx=(0, 10))
        ttk.Button(rodape, text="Salvar Escalação", command=self._salvar_modal_escalacao_partida).pack(side="left")

        self._modal_carregar_escalacao(draft)
        self._modal_atualizar_resumo()
        self._modal_atualizar_lista_geral_com_status()
        top.protocol("WM_DELETE_WINDOW", self._fechar_modal_escalacao_partida)

    def _modal_coletar_escalacao(self):
        base = self._escalacao_partida_base()
        titulares = getattr(self, "_modal_titulares_por_posicao", {})
        for pos in POSICOES_ELENCO:
            nomes = titulares.get(pos, [])
            base["titulares_por_posicao"][pos] = list(nomes) if isinstance(nomes, list) else []
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            lb = self._modal_lb_extras.get(chave)
            base[chave] = list(lb.get(0, tk.END)) if lb else []
        return self._normalizar_escalacao_partida(base)

    def _modal_carregar_escalacao(self, escalacao):
        data = self._normalizar_escalacao_partida(escalacao)
        self._modal_titulares_por_posicao = {
            pos: list(data["titulares_por_posicao"].get(pos, []))
            for pos in POSICOES_ELENCO
        }
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            lb = self._modal_lb_extras.get(chave)
            if not lb:
                continue
            lb.delete(0, tk.END)
            for nome in data.get(chave, []):
                lb.insert(tk.END, nome)
        self._modal_render_campinho()

    def _modal_render_campinho(self):
        canvas = getattr(self, "_modal_canvas_campinho", None)
        if canvas is None:
            return
        canvas.delete("all")
        self._modal_campinho_hits = []

        w = max(360, canvas.winfo_width())
        h = max(240, canvas.winfo_height())
        m = 16
        canvas.create_rectangle(0, 0, w, h, fill="#0f6a35", outline="")
        canvas.create_rectangle(m, m, w - m, h - m, outline="#e9f7ed", width=2)
        meio_y = h / 2
        canvas.create_line(m, meio_y, w - m, meio_y, fill="#e9f7ed", width=2)
        canvas.create_oval(w / 2 - 36, meio_y - 36, w / 2 + 36, meio_y + 36, outline="#e9f7ed", width=2)

        tit = getattr(self, "_modal_titulares_por_posicao", {})
        linhas = [
            ("ATA", "Atacante", 0.16),
            ("MEI", "Meio-Campista", 0.34),
            ("VOL", "Volante", 0.50),
            ("DEF", "Lateral-Esquerdo", 0.68),
            ("GOL", "Goleiro", 0.84),
        ]

        for sigla, chave, rel_y in linhas:
            y = m + (h - 2 * m) * rel_y
            canvas.create_text(m + 18, y, text=sigla, fill="#d8f0de", font=("Segoe UI", 9, "bold"))
            if sigla == "DEF":
                nomes = (
                    list(tit.get("Lateral-Esquerdo", []))
                    + list(tit.get("Zagueiro", []))
                    + list(tit.get("Lateral-Direito", []))
                )
            else:
                nomes = list(tit.get(chave, []))
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
                self._modal_campinho_hits.append({
                    "nome": nome,
                    "linha": sigla,
                    "idx": i,
                    "n": n,
                    "x": x,
                    "y": y,
                    "r": r,
                })

    def _modal_campinho_drag_start(self, event):
        hit = None
        for item in getattr(self, "_modal_campinho_hits", []):
            dx = event.x - item["x"]
            dy = event.y - item["y"]
            if (dx * dx + dy * dy) <= (item["r"] + 4) ** 2:
                hit = item
                break
        self._modal_campinho_drag_state = hit
        if hit:
            self._modal_canvas_campinho.configure(cursor="hand2")

    def _modal_campinho_drag_end(self, event):
        state = getattr(self, "_modal_campinho_drag_state", None)
        self._modal_campinho_drag_state = None
        self._modal_canvas_campinho.configure(cursor="")
        if not state:
            return
        if state["n"] < 2:
            return

        linha = state["linha"]
        origem = state["idx"]
        n = state["n"]
        mesmos = sorted(
            [p for p in getattr(self, "_modal_campinho_hits", []) if p.get("linha") == linha],
            key=lambda p: p.get("idx", 0),
        )
        if len(mesmos) != n:
            return
        alvo = min(range(n), key=lambda i: abs(event.x - mesmos[i]["x"]))
        if alvo == origem:
            return

        if linha == "DEF":
            le = list(self._modal_titulares_por_posicao.get("Lateral-Esquerdo", []))
            zag = list(self._modal_titulares_por_posicao.get("Zagueiro", []))
            ld = list(self._modal_titulares_por_posicao.get("Lateral-Direito", []))
            combinado = le + zag + ld
            if len(combinado) != n:
                return
            jogador = combinado.pop(origem)
            combinado.insert(alvo, jogador)
            n_le = len(le)
            n_zag = len(zag)
            self._modal_titulares_por_posicao["Lateral-Esquerdo"] = combinado[:n_le]
            self._modal_titulares_por_posicao["Zagueiro"] = combinado[n_le:n_le + n_zag]
            self._modal_titulares_por_posicao["Lateral-Direito"] = combinado[n_le + n_zag:]
        else:
            mapa = {
                "ATA": "Atacante",
                "MEI": "Meio-Campista",
                "VOL": "Volante",
                "GOL": "Goleiro",
            }
            pos = mapa.get(linha)
            if not pos:
                return
            lista = list(self._modal_titulares_por_posicao.get(pos, []))
            if len(lista) != n:
                return
            jogador = lista.pop(origem)
            lista.insert(alvo, jogador)
            self._modal_titulares_por_posicao[pos] = lista

        self._modal_render_campinho()
        self._modal_atualizar_resumo()
        self._modal_atualizar_lista_geral_com_status()

    def _modal_status_por_jogador(self):
        esc = self._modal_coletar_escalacao()
        status = {}
        for pos in POSICOES_ELENCO:
            for nome in esc["titulares_por_posicao"].get(pos, []):
                status[str(nome).strip().casefold()] = "titulares"
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            for nome in esc.get(chave, []):
                status[str(nome).strip().casefold()] = chave
        return status

    def _modal_formatar_nome_com_status(self, nome, status):
        icone = ICONE_STATUS_ESCALACAO.get(status or "sem_lista", ICONE_STATUS_ESCALACAO["sem_lista"])
        return f"{icone} {nome}"

    def _modal_extrair_nome_raw(self, texto):
        txt = str(texto or "").strip()
        if len(txt) >= 2 and txt[1] == " " and txt[0] in set(ICONE_STATUS_ESCALACAO.values()):
            return txt[2:].strip()
        return txt

    def _modal_atualizar_lista_geral_com_status(self):
        if not hasattr(self, "_modal_tv_elenco"):
            return
        status_por_nome = self._modal_status_por_jogador()
        selecionado_cf = None
        self._modal_iids_separador = set()
        sel = self._modal_tv_elenco.selection()
        if sel:
            vals_sel = self._modal_tv_elenco.item(sel[0], "values")
            if vals_sel:
                selecionado_cf = self._modal_extrair_nome_raw(vals_sel[0]).casefold()

        self._modal_tv_elenco.delete(*self._modal_tv_elenco.get_children())
        novo_iid_selecionado = None
        posicao_anterior = None
        for jogador in _ordenar_jogadores_por_posicao(list(self.elenco_atual.get("jogadores", []))):
            nome = str(jogador.get("nome", "")).strip()
            if not nome:
                continue
            posicao_atual = str(jogador.get("posicao", "")).strip()
            if posicao_anterior is not None and posicao_atual != posicao_anterior:
                iid_sep = self._modal_tv_elenco.insert("", "end", values=("", ""), tags=("sep_posicao",))
                self._modal_iids_separador.add(iid_sep)
            cf = nome.casefold()
            status = status_por_nome.get(cf, "sem_lista")
            tag = f"status_{status}"
            iid = self._modal_tv_elenco.insert(
                "",
                "end",
                values=(self._modal_formatar_nome_com_status(nome, status), posicao_atual),
                tags=(tag,),
            )
            if selecionado_cf and cf == selecionado_cf:
                novo_iid_selecionado = iid
            posicao_anterior = posicao_atual
        if novo_iid_selecionado:
            self._modal_tv_elenco.selection_set(novo_iid_selecionado)
            self._modal_tv_elenco.focus(novo_iid_selecionado)

    def _modal_remover_nome_de_tudo(self, nome):
        alvo = nome.casefold()
        for pos in POSICOES_ELENCO:
            atuais = list(getattr(self, "_modal_titulares_por_posicao", {}).get(pos, []))
            self._modal_titulares_por_posicao[pos] = [
                i for i in atuais if str(i).strip().casefold() != alvo
            ]
        for chave, _titulo in CATEGORIAS_ESCALACAO_EXTRAS:
            lb = self._modal_lb_extras.get(chave)
            if not lb:
                continue
            itens = [i for i in lb.get(0, tk.END) if str(i).strip().casefold() != alvo]
            lb.delete(0, tk.END)
            for item in itens:
                lb.insert(tk.END, item)
        self._modal_render_campinho()

    def _modal_adicionar_jogador(self, destino):
        sel = self._modal_tv_elenco.selection()
        if not sel:
            messagebox.showwarning("Escalação", "Selecione um jogador da lista geral do elenco.")
            return
        vals = self._modal_tv_elenco.item(sel[0], "values")
        if len(vals) < 2:
            return
        nome = self._modal_extrair_nome_raw(vals[0])
        if not nome:
            return
        self._modal_enviar_jogador_para(nome, destino)

    def _modal_enviar_jogador_para(self, nome, destino):
        nome = str(nome).strip()
        if not nome:
            return
        tipo, chave = destino
        if tipo == "titulares":
            total_titulares = sum(len(self._modal_titulares_por_posicao.get(pos, [])) for pos in POSICOES_ELENCO)
            ja_era_titular = any(
                str(n).strip().casefold() == nome.casefold()
                for pos in POSICOES_ELENCO
                for n in self._modal_titulares_por_posicao.get(pos, [])
            )
            if not ja_era_titular and total_titulares >= 11:
                messagebox.showerror("Escalação inválida", "Não é possível escalar mais de 11 titulares.")
                return
            if chave == "Goleiro":
                goleiros_titulares = len(self._modal_titulares_por_posicao.get("Goleiro", []))
                if goleiros_titulares >= 1 and not any(
                    str(n).strip().casefold() == nome.casefold()
                    for n in self._modal_titulares_por_posicao.get("Goleiro", [])
                ):
                    messagebox.showerror("Escalação inválida", "Só é permitido 1 goleiro titular.")
                    return
        self._modal_remover_nome_de_tudo(nome)
        if tipo == "titulares":
            lista = self._modal_titulares_por_posicao.setdefault(chave, [])
            lista.append(nome)
            self._modal_render_campinho()
        else:
            lb = self._modal_lb_extras.get(chave)
            if not lb:
                return
            itens = list(lb.get(0, tk.END))
            itens.append(nome)
            lb.delete(0, tk.END)
            for item in itens:
                lb.insert(tk.END, item)
        self._modal_atualizar_resumo()
        self._modal_atualizar_lista_geral_com_status()

    def _abrir_menu_contexto_escalacao_modal(self, event, origem):
        nome = ""
        tipo, chave = origem
        if tipo == "elenco":
            iid = self._modal_tv_elenco.identify_row(event.y)
            if not iid:
                return
            if iid in getattr(self, "_modal_iids_separador", set()):
                return
            self._modal_tv_elenco.selection_set(iid)
            self._modal_tv_elenco.focus(iid)
            values = self._modal_tv_elenco.item(iid, "values")
            if len(values) >= 1:
                nome = self._modal_extrair_nome_raw(values[0])
        elif tipo == "campinho":
            hits = getattr(self, "_modal_campinho_hits", [])
            hit = None
            for item in hits:
                dx = event.x - item["x"]
                dy = event.y - item["y"]
                if (dx * dx + dy * dy) <= (item["r"] + 4) ** 2:
                    hit = item
                    break
            if not hit:
                return
            nome = str(hit.get("nome", "")).strip()
        elif tipo == "extras":
            lb = self._modal_lb_extras.get(chave)
            if not lb:
                return
            idx = lb.nearest(event.y)
            if idx < 0 or idx >= lb.size():
                return
            lb.selection_clear(0, tk.END)
            lb.selection_set(idx)
            nome = str(lb.get(idx)).strip()

        if not nome:
            return

        menu = tk.Menu(self._modal_escalacao_partida, tearoff=0)
        submenu_tit = tk.Menu(menu, tearoff=0)
        for pos in POSICOES_ELENCO:
            submenu_tit.add_command(
                label=f"Titular - {pos}",
                command=lambda n=nome, p=pos: self._modal_enviar_jogador_para(n, ("titulares", p))
            )
        menu.add_cascade(label="Enviar para Titulares", menu=submenu_tit)
        menu.add_separator()
        menu.add_command(
            label="Enviar para Reservas",
            command=lambda n=nome: self._modal_enviar_jogador_para(n, ("extras", "reservas"))
        )
        menu.add_command(
            label="Enviar para Não Relacionados",
            command=lambda n=nome: self._modal_enviar_jogador_para(n, ("extras", "nao_relacionados"))
        )
        menu.add_command(
            label="Enviar para Lesionados",
            command=lambda n=nome: self._modal_enviar_jogador_para(n, ("extras", "lesionados"))
        )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _modal_remover_jogador(self, origem):
        tipo, chave = origem
        lb = self._modal_lb_extras.get(chave) if tipo == "extras" else None
        if not lb:
            return
        sel = lb.curselection()
        if not sel:
            return
        nome_removido = str(lb.get(sel[0])).strip()
        lb.delete(sel[0])
        if tipo == "extras" and chave == "reservas" and nome_removido:
            lb_nao_rel = self._modal_lb_extras.get("nao_relacionados")
            if lb_nao_rel:
                atuais = [str(n).strip() for n in lb_nao_rel.get(0, tk.END) if str(n).strip()]
                if nome_removido.casefold() not in {n.casefold() for n in atuais}:
                    atuais.append(nome_removido)
                    lb_nao_rel.delete(0, tk.END)
                    for item in atuais:
                        lb_nao_rel.insert(tk.END, item)
        self._modal_atualizar_resumo()
        self._modal_atualizar_lista_geral_com_status()

    def _modal_atualizar_resumo(self):
        esc = self._modal_coletar_escalacao()
        titulares = sum(len(esc["titulares_por_posicao"].get(pos, [])) for pos in POSICOES_ELENCO)
        reservas = len(esc.get("reservas", []))
        self._modal_resumo_var.set(f"Titulares: {titulares}/11 | Reservas: {reservas} (mín. 4)")

    def _salvar_modal_escalacao_partida(self):
        escalacao = self._modal_coletar_escalacao()
        ok, msg = self._validar_escalacao_partida(escalacao)
        if not ok:
            messagebox.showerror("Escalação inválida", msg)
            return
        self._carregar_escalacao_partida(escalacao)
        self._fechar_modal_escalacao_partida()

    def _fechar_modal_escalacao_partida(self):
        modal = getattr(self, "_modal_escalacao_partida", None)
        if modal and modal.winfo_exists():
            try:
                modal.grab_release()
            except Exception:
                pass
            modal.destroy()
        self._modal_escalacao_partida = None

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
        top.attributes("-topmost", True)
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
    def adicionar_gol_vasco(self, event):
        jogador = self.entry_gol_vasco.get().strip()
        if not jogador:
            return
        limite = self._obter_limite_gols("vasco")
        if self.lista_gols_vasco.size() >= limite:
            messagebox.showwarning("Limite Atingido", f"O Vasco só fez {limite} gol(s).")
            return
        self.lista_gols_vasco.insert(tk.END, jogador)
        if jogador not in self.listas["jogadores_vasco"]:
            self.listas["jogadores_vasco"].append(jogador)
            self._atualizar_opcoes_gol_vasco()
        self.entry_gol_vasco.delete(0, tk.END)

    def adicionar_gol_contra(self, event):
        jogador = self.entry_gol_contra.get().strip()
        if not jogador:
            return
        limite = self._obter_limite_gols("adversario")
        if self.lista_gols_contra.size() >= limite:
            messagebox.showwarning("Limite Atingido", f"O adversário só fez {limite} gol(s).")
            return
        self.lista_gols_contra.insert(tk.END, jogador)
        if jogador not in self.listas["jogadores_contra"]:
            self.listas["jogadores_contra"].append(jogador)
            self.listas["jogadores_contra"] = sorted(self.listas["jogadores_contra"], key=lambda s: s.casefold())
            self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self.entry_gol_contra.delete(0, tk.END)

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
            self.lista_gols_vasco.delete(sel[0])

    def remover_gol_contra(self, event=None):
        sel = self.lista_gols_contra.curselection()
        if sel:
            self.lista_gols_contra.delete(sel[0])

    # --------------------- Salvar ---------------------
    def salvar_partida(self):
        data = self.data_entry.get()
        adversario = self.adversario_var.get().strip()
        competicao = self.competicao_var.get().strip()
        placar_vasco = self.placar_vasco.get().strip()
        placar_adv = self.placar_adversario.get().strip()
        local = self.local_var.get()
        observacao = self.obs_text.get("1.0", "end").strip()
        tecnico = self.tecnico_var.get().strip() or self.listas.get("tecnico_atual", "Fernando Diniz")
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
        escalacao_ok, escalacao_msg = self._validar_escalacao_partida(escalacao_partida)

        if not (data and adversario and placar_vasco and placar_adv and competicao and tecnico):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return
        if not escalacao_ok:
            messagebox.showerror("Escalação inválida", escalacao_msg)
            return

        # Gols (contados)
        nomes_vasco = list(self.lista_gols_vasco.get(0, tk.END))
        contagem_vasco = Counter(nomes_vasco)
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

        gols_vasco = []
        for nome, qtd in contagem_vasco.items():
            nome_cf = str(nome).strip().casefold()
            saiu_do_banco = nome_cf in reservas_cf and nome_cf not in titulares_cf
            gols_vasco.append({
                "nome": nome,
                "gols": qtd,
                "saiu_do_banco": saiu_do_banco,
            })

        nomes_contra = list(self.lista_gols_contra.get(0, tk.END))
        contagem_contra = Counter(nomes_contra)
        gols_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_contra.items()]

        if adversario not in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].append(adversario)
            self.listas["clubes_adversarios"] = sorted(self.listas["clubes_adversarios"], key=lambda s: s.casefold())
            self.adversario_entry['values'] = self.listas["clubes_adversarios"]

        if competicao not in self.listas.get("competicoes", []):
            self.listas.setdefault("competicoes", []).append(competicao)
            self.listas["competicoes"] = sorted(self.listas["competicoes"], key=lambda s: s.casefold())
            self.competicao_entry['values'] = self.listas["competicoes"]

        lista_tecnicos = self.listas.setdefault("tecnicos", [])
        if tecnico not in lista_tecnicos:
            lista_tecnicos.append(tecnico)
            self.listas["tecnicos"] = sorted(lista_tecnicos, key=lambda s: s.casefold())
        self.listas["tecnico_atual"] = tecnico
        self.tecnico_var.set(tecnico)
        self._atualizar_combo_tecnicos()
        salvar_listas(self.listas)

        jogo = {
            "data": data,
            "adversario": adversario,
            "competicao": competicao,
            "local": local,  # 'casa' | 'fora'
            "placar": {"vasco": int(placar_vasco), "adversario": int(placar_adv)},
            "gols_vasco": gols_vasco,
            "gols_adversario": gols_contra,
            "observacao": observacao,  # <<< novo campo
            "tecnico": tecnico,
            "posicao_tabela": posicao_tabela,
            "escalacao_partida": escalacao_partida,
        }

        jogos = carregar_dados_jogos()
        if self.editing_index is not None:
            if 0 <= self.editing_index < len(jogos):
                jogos[self.editing_index] = jogo
                salvar_lista_jogos(jogos)
                msg = "Partida atualizada com sucesso!"
            else:
                messagebox.showerror("Erro", "Não foi possível localizar o jogo selecionado para edição.")
                return
        else:
            jogos.append(jogo)
            salvar_lista_jogos(jogos)
            msg = "Partida registrada com sucesso!"

        self._atualizar_condicoes_elenco_por_escalacao(escalacao_partida)
        self._limpar_formulario()
        self._atualizar_abas()
        self.notebook.select(self.frame_temporadas)

    def _limpar_formulario(self):
        self.editing_index = None
        self._fechar_modal_escalacao_partida()
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
        if hasattr(self, "posicao_var"):
            self.posicao_var.set("")
        self._atualizar_estado_posicao()
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(self.listas.get("tecnico_atual", "Fernando Diniz"))
        self.placar_vasco.delete(0, tk.END)
        self.placar_adversario.delete(0, tk.END)
        self.lista_gols_vasco.delete(0, tk.END)
        self.lista_gols_contra.delete(0, tk.END)
        self.entry_gol_vasco.delete(0, tk.END)
        self.entry_gol_contra.delete(0, tk.END)
        self.obs_text.delete("1.0", "end")
        self.local_var.set("casa")
        self._atualizar_elenco_disponivel_partida()
        self._inicializar_escalacao_partida()

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

    def _preencher_listbox_gols(self, listbox, dados):
        listbox.delete(0, tk.END)
        for item in dados:
            if isinstance(item, dict):
                nome = item.get("nome", "")
                qtd = int(item.get("gols", 0))
                for _ in range(max(1, qtd)):
                    if nome:
                        listbox.insert(tk.END, nome)
            elif isinstance(item, str) and item:
                listbox.insert(tk.END, item)

    def _carregar_jogo_para_edicao(self, jogo_idx):
        jogos = carregar_dados_jogos()
        if not (0 <= jogo_idx < len(jogos)):
            messagebox.showerror("Erro", "Não foi possível carregar o jogo selecionado.")
            return

        jogo = jogos[jogo_idx]
        self.notebook.select(self.frame_registro)
        self.editing_index = jogo_idx
        adversario = jogo.get("adversario", "")
        data = jogo.get("data", "")
        self.salvar_btn_label.set("Salvar Alterações")
        self.modo_edicao_var.set(f"Editando: {adversario} ({data})")
        self.btn_cancelar_edicao.state(["!disabled"])

        self.data_var.set(data)
        self.adversario_var.set(adversario)
        self.competicao_var.set(jogo.get("competicao", ""))
        self._atualizar_estado_posicao()
        if hasattr(self, "posicao_var"):
            posicao = jogo.get("posicao_tabela")
            if posicao not in (None, "") and self._competicao_usa_posicao(self.competicao_var.get()):
                self.posicao_var.set(str(posicao))
            else:
                self.posicao_var.set("")
        self.local_var.set(jogo.get("local", "casa"))
        if hasattr(self, "tecnico_var"):
            self.tecnico_var.set(jogo.get("tecnico", self.listas.get("tecnico_atual", "Fernando Diniz")))

        placar = jogo.get("placar", {})
        self.placar_vasco.delete(0, tk.END)
        self.placar_vasco.insert(0, str(placar.get("vasco", "")))
        self.placar_adversario.delete(0, tk.END)
        self.placar_adversario.insert(0, str(placar.get("adversario", "")))

        self._preencher_listbox_gols(self.lista_gols_vasco, jogo.get("gols_vasco", []))
        self._preencher_listbox_gols(self.lista_gols_contra, jogo.get("gols_adversario", []))
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
        else:
            self._inicializar_escalacao_partida()

        self.obs_text.delete("1.0", "end")
        self.obs_text.insert("1.0", jogo.get("observacao", ""))

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
        self._carregar_jogo_para_edicao(jogo_idx)

    def _abrir_menu_contexto_temporadas(self, event):
        tree = event.widget
        iid = tree.identify_row(event.y)
        if not iid:
            return
        tree.selection_set(iid)
        tree.focus(iid)

        mapping = getattr(tree, "_item_to_idx", {})
        jogo_idx = mapping.get(iid)
        if jogo_idx is None:
            return

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Excluir jogo", command=lambda idx=jogo_idx: self._excluir_jogo_por_indice(idx))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _excluir_jogo_por_indice(self, jogo_idx):
        jogos = carregar_dados_jogos()
        if not (0 <= jogo_idx < len(jogos)):
            messagebox.showerror("Erro", "Não foi possível localizar o jogo para exclusão.")
            return

        jogo = jogos[jogo_idx]
        desc = f"{jogo.get('data', '')} - Vasco x {jogo.get('adversario', '')} ({jogo.get('competicao', '')})"
        if not messagebox.askyesno("Excluir jogo", f"Deseja excluir este jogo?\n\n{desc}"):
            return

        jogos.pop(jogo_idx)
        salvar_lista_jogos(jogos)

        if self.editing_index == jogo_idx:
            self._limpar_formulario()
        elif self.editing_index is not None and self.editing_index > jogo_idx:
            self.editing_index -= 1

        self._atualizar_abas()
        messagebox.showinfo("Sucesso", "Jogo excluído com sucesso.")

    def _atualizar_abas(self):
        self.elenco_atual = carregar_elenco_atual()
        self.jogadores_historico = carregar_jogadores_historico()
        self._sincronizar_jogadores_historico()
        self._atualizar_elenco_disponivel_partida()
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_comparativo()
        self._carregar_tecnicos()
        self._carregar_graficos()
        self._render_aba_jogadores_historico()

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

    def _competicao_usa_posicao(self, nome):
        if not nome:
            return False
        return nome.strip().casefold() == COMPETICAO_BRASILEIRAO.casefold()

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
        indice_atual = len(anos_ordenados) - 1

        for ano in anos_ordenados:
            frame_ano = ttk.Frame(nb, padding=10)
            nb.add(frame_ano, text=str(ano))

            jogos_ano = temporadas[ano]
            vitorias = empates = derrotas = 0
            gols_pro = gols_contra = 0
            artilheiros = Counter()
            carrascos = Counter()

            rows = []
            streak_inv = streak_der = 0
            invicto_max = derrota_max = 0
            for idx_global, jogo in sorted(jogos_ano, key=lambda j: _parse_data_ptbr(j[1]["data"])):
                local = jogo.get("local", "desconhecido").capitalize()
                placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
                competicao = jogo.get("competicao", "Competição Desconhecida")
                data = jogo["data"]
                adversario = jogo["adversario"]

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

                gols_pro += placar.get("vasco", 0)
                gols_contra += placar.get("adversario", 0)

                for g in jogo.get("gols_vasco", []):
                    if isinstance(g, dict):
                        artilheiros[g["nome"]] += g["gols"]
                for g in jogo.get("gols_adversario", []):
                    if isinstance(g, dict):
                        carrascos[g["nome"]] += g["gols"]

                rows.append({
                    "data": data, "local": local, "competicao": competicao,
                    "adversario": adversario, "raw": jogo, "idx": idx_global
                })

            # Cards
            jogos_disputados = len(jogos_ano)
            saldo = gols_pro - gols_contra
            aproveitamento = round(((vitorias * 3 + empates) / (jogos_disputados * 3)) * 100, 1) if jogos_disputados else 0.0
            media_gols_pro = round(gols_pro / jogos_disputados, 2) if jogos_disputados else 0.0
            media_gols_contra = round(gols_contra / jogos_disputados, 2) if jogos_disputados else 0.0
            cards = ttk.Frame(frame_ano)
            cards.pack(fill="x", pady=(0, 8))
            cards.columnconfigure((0, 1, 2, 3), weight=1)

            def make_card(parent, titulo, valor):
                lf = ttk.Labelframe(parent, text=titulo, style="Card.TLabelframe")
                ttk.Label(lf, text=str(valor), style="CardValue.TLabel").pack()
                return lf

            make_card(cards, "Jogos", len(jogos_ano)).grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Vitórias", vitorias).grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Empates", empates).grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Derrotas", derrotas).grid(row=0, column=3, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Gols Pró", gols_pro).grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Gols Contra", gols_contra).grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Saldo", saldo).grid(row=1, column=2, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Aproveitamento (%)", f"{aproveitamento}").grid(row=1, column=3, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Média gols pró", media_gols_pro).grid(row=2, column=0, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Média gols contra", media_gols_contra).grid(row=2, column=1, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Maior sequência invicta", invicto_max).grid(row=2, column=2, sticky="nsew", padx=4, pady=4)
            make_card(cards, "Maior sequência derrotas", derrota_max).grid(row=2, column=3, sticky="nsew", padx=4, pady=4)

            # ----- Tabela de partidas da temporada
            table_wrap = ttk.Frame(frame_ano)
            table_wrap.pack(fill="both", expand=True)

            cols = ("data", "local", "competicao", "adversario", "placar")
            tv = ttk.Treeview(table_wrap, columns=cols, show="headings",
                              height=min(16, max(8, len(rows))))
            # larguras para caber placar estendido
            for c, w in zip(cols, (90, 80, 240, 220, 320)):
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

            for i, r in enumerate(rows, start=1):
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

                iid = tv.insert(
                    "", "end",
                    values=(r["data"], local_disp, r["competicao"], adversario, placar_fmt),
                    tags=("odd" if i % 2 else "",),
                )
                tooltip_map[iid] = self._tooltip_gols_text(jogo_raw)
                obs_map[iid] = jogo_raw.get("observacao", "").strip()
                item_to_idx[iid] = r["idx"]

            # Tooltip nos gols (mouse hover)
            self._bind_treeview_tooltips(tv, tooltip_map)
            tv._item_to_idx = item_to_idx
            tv.bind("<Double-1>", self._on_tree_double_click)
            tv.bind("<Button-3>", self._abrir_menu_contexto_temporadas)
            tv.bind("<Control-Button-1>", self._abrir_menu_contexto_temporadas)

            # ----- Área de Observações (aparece só se houver texto) -----
            obs_frame = ttk.Frame(frame_ano)

            # header com título à esquerda e botão X à direita
            obs_header = ttk.Frame(obs_frame)
            obs_title = ttk.Label(obs_header, text="Observações:", font=("Segoe UI", 11, "bold"))
            obs_title.pack(side="left", pady=(8, 2))

            # botão fechar (✕) no canto direito
            btn_close = ttk.Button(
                obs_header,
                text="✕",
                width=3,
                command=lambda f=obs_frame: f.pack_forget()  # captura este obs_frame
            )
            btn_close.pack(side="right")
            # (não empacotar obs_frame ainda — só quando houver texto)
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
                        # monta só quando necessário (evita piscada)
                        if not obs_frame_ref.winfo_ismapped():
                            obs_frame_ref.pack(fill="x", padx=2, pady=(6, 0))
                            obs_header_ref.pack(fill="x")
                            obs_label_ref.pack(anchor="w", pady=(0, 6))
                        obs_label_ref.configure(text=txt)
                    else:
                        obs_frame_ref.pack_forget()
                return on_select

            # bind usando factory para não “colar” no último tv do loop
            tv.bind("<<TreeviewSelect>>",
                    on_select_factory(tv, obs_frame, obs_header, obs_label, obs_map))



        nb.select(indice_atual)

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
                    partes.append(f"{nome_fmt} x{qtd}" if qtd > 1 else nome_fmt)
                elif isinstance(g, str):
                    partes.append(g)
            return ", ".join(partes)

        gols_vasco = fmt_lista(jogo.get("gols_vasco", []))
        gols_adv = fmt_lista(jogo.get("gols_adversario", []))
        return (f"Gols do Vasco: {gols_vasco}\n"
                f"Gols do {jogo.get('adversario','Adversário')}: {gols_adv}")

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
                ["vit_acum", "emp_acum", "der_acum"],
                ["Vitórias (acum.)", "Empates (acum.)", "Derrotas (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução de resultados",
                ylabel="Qtd.",
                color_override={
                    "vit_acum": ("#15803d", "#86efac"),
                    "emp_acum": ("#ca8a04", "#fde047"),
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
        jogos_anterior = list(comps_por_ano.get(ano_anterior, {}).get(competicao, []))

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
                ["vit_acum", "emp_acum", "der_acum"],
                ["Vitórias (acum.)", "Empates (acum.)", "Derrotas (acum.)"],
                ano_atual,
                ano_anterior,
                prev_series=series_anterior,
                titulo="Evolução dos resultados",
                ylabel="Qtd.",
                color_override={
                    "vit_acum": ("#15803d", "#86efac"),
                    "emp_acum": ("#ca8a04", "#fde047"),
                    "der_acum": ("#b91c1c", "#fca5a5"),
                }
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

        jogos = carregar_dados_jogos()
        if not jogos:
            ttk.Label(self.frame_tecnicos, text="Ainda não há jogos registrados.").pack(anchor="w")
            return

        stats = defaultdict(lambda: {
            "jogos": 0,
            "casa": 0,
            "fora": 0,
            "vitorias": 0,
            "empates": 0,
            "derrotas": 0,
            "gols_pro": 0,
            "gols_contra": 0,
            "artilheiros": Counter(),
        })

        for jogo in jogos:
            tecnico = jogo.get("tecnico") or "(Sem Técnico)"
            info = stats[tecnico]
            info["jogos"] += 1
            local = jogo.get("local", "casa")
            if local == "fora":
                info["fora"] += 1
            else:
                info["casa"] += 1

            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            gols_vasco = placar.get("vasco", 0)
            gols_adv = placar.get("adversario", 0)
            info["gols_pro"] += gols_vasco
            info["gols_contra"] += gols_adv

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    nome = g.get("nome", "Desconhecido")
                    info["artilheiros"][nome] += int(g.get("gols", 0))
                elif isinstance(g, str):
                    info["artilheiros"][g] += 1

            if gols_vasco > gols_adv:
                info["vitorias"] += 1
            elif gols_vasco < gols_adv:
                info["derrotas"] += 1
            else:
                info["empates"] += 1

        container = ttk.Frame(self.frame_tecnicos)
        container.pack(fill="both", expand=True)
        cols = ("tecnico", "jogos", "casa", "fora", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo", "artilheiro")
        tv = ttk.Treeview(container, columns=cols, show="headings", height=min(18, max(6, len(stats))))
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
            "artilheiro": 180,
        }
        for col in cols:
            tv.heading(col, text=headings[col], command=lambda c=col: self._ordenar_coluna_tecnicos(c))
            tv.column(col, width=widths[col], anchor="center" if col != "tecnico" else "w")

        sy = ttk.Scrollbar(container, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        tv.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        self._tv_tecnicos = tv
        self._tecnicos_rows = []
        for tecnico, info in stats.items():
            saldo = info["gols_pro"] - info["gols_contra"]
            top = info["artilheiros"].most_common(1)
            artilheiro_txt = "—"
            if top:
                nome, gols = top[0]
                artilheiro_txt = f"{nome} ({gols})"
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
                "artilheiro": artilheiro_txt,
            })

        self._tecnicos_sort_col = "jogos"
        self._tecnicos_sort_reverse = True
        self._render_tecnicos_ordenado()

    def _chave_ordenacao_tecnicos(self, row, coluna):
        if coluna in {"jogos", "casa", "fora", "vitorias", "empates", "derrotas", "gols_pro", "gols_contra", "saldo"}:
            return int(row.get(coluna, 0))
        return str(row.get(coluna, "")).casefold()

    def _render_tecnicos_ordenado(self):
        if not getattr(self, "_tv_tecnicos", None):
            return
        tv = self._tv_tecnicos
        for iid in tv.get_children():
            tv.delete(iid)
        rows = sorted(
            self._tecnicos_rows,
            key=lambda r: (self._chave_ordenacao_tecnicos(r, self._tecnicos_sort_col), str(r.get("tecnico", "")).casefold()),
            reverse=self._tecnicos_sort_reverse
        )
        for i, row in enumerate(rows, start=1):
            tv.insert(
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
                    row["artilheiro"],
                ),
                tags=("odd",) if i % 2 else ()
            )

    def _ordenar_coluna_tecnicos(self, coluna):
        if not getattr(self, "_tecnicos_rows", None):
            return
        if getattr(self, "_tecnicos_sort_col", None) == coluna:
            self._tecnicos_sort_reverse = not self._tecnicos_sort_reverse
        else:
            self._tecnicos_sort_col = coluna
            self._tecnicos_sort_reverse = False
        self._render_tecnicos_ordenado()

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

        frame_geral = ttk.Frame(nb_root, padding=6)
        nb_root.add(frame_geral, text="Geral")
        self._render_graficos_para_dataset(frame_geral, jogos, is_geral=True)

        for ano in sorted(temporadas.keys()):
            frame_ano = ttk.Frame(nb_root, padding=6)
            nb_root.add(frame_ano, text=str(ano))
            prev = temporadas.get(ano - 1)
            prev_label = str(ano - 1) if prev else None
            self._render_graficos_para_dataset(frame_ano, temporadas[ano], is_geral=False,
                                               prev_jogos=prev, prev_label=prev_label)

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

        return {
            "x": x,
            "gols_pro_acum": gols_pro_acum,
            "gols_contra_acum": gols_contra_acum,
            "saldo_acum": saldo_acum,
            "vit_acum": vit_acum,
            "emp_acum": emp_acum,
            "der_acum": der_acum,
            "pontos_acum": pontos_acum,
        }

    # --------- Helpers de plot ---------
    def _plot_linhas(self, container, x, series_list, labels, titulo, xlabel, ylabel, comparativos=None, line_colors=None):
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

    def _plot_linhas_comparativo(self, container, series_atual, keys, labels, ano_atual, ano_anterior, prev_series=None, titulo="", xlabel="Jogo", ylabel="", color_override=None):
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
            line_colors=line_colors
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
        for rect, val in zip(bars, values):
            ax.text(rect.get_width() + (0.01 * maxv if maxv else 0.2),
                    rect.get_y() + rect.get_height()/2,
                    str(val), va="center")
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
