import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict, Counter
import json
import os
import shutil
import sys
try:
    from tkcalendar import Calendar
    TKCALENDAR_OK = True
except Exception:
    Calendar = None
    TKCALENDAR_OK = False
import tkinter.font as tkFont
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
APP_SUPPORT_DIR = os.path.join(
    os.path.expanduser("~/Library/Application Support"),
    APP_NAME
)


def _definir_diretorio_dados():
    """Usa Application Support quando empacotado (PyInstaller)."""
    if sys.platform == "darwin" and getattr(sys, "frozen", False):
        os.makedirs(APP_SUPPORT_DIR, exist_ok=True)
        return APP_SUPPORT_DIR
    return PROJECT_ROOT


DATA_DIR = _definir_diretorio_dados()
ARQUIVO_JOGOS = os.path.join(DATA_DIR, "jogos_vasco.json")
ARQUIVO_LISTAS = os.path.join(DATA_DIR, "listas_auxiliares.json")
COMPETICAO_BRASILEIRAO = "Brasileirão Série A"


def _bootstrap_jsons():
    """Copia JSONs originais para Application Support no primeiro uso."""
    if DATA_DIR == PROJECT_ROOT:
        return
    for nome in ("jogos_vasco.json", "listas_auxiliares.json"):
        destino = os.path.join(DATA_DIR, nome)
        if os.path.exists(destino):
            continue
        origem = os.path.join(PROJECT_ROOT, nome)
        if os.path.exists(origem):
            shutil.copy2(origem, destino)


_bootstrap_jsons()


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


def _parse_data_ptbr(s: str) -> datetime:
    # dd/mm/aaaa
    return datetime.strptime(s, "%d/%m/%Y")


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
        self.root.geometry("1150x800")
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
        self._calendar_popup = None

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frame_registro = ttk.Frame(self.notebook, padding=10)
        self.frame_temporadas = ttk.Frame(self.notebook, padding=10)
        self.frame_geral = ttk.Frame(self.notebook, padding=10)
        self.frame_comparativo = ttk.Frame(self.notebook, padding=10)
        self.frame_tecnicos = ttk.Frame(self.notebook, padding=10)
        self.frame_graficos = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_temporadas, text="Temporadas")
        self.notebook.add(self.frame_geral, text="Geral")
        self.notebook.add(self.frame_comparativo, text="Comparativo")
        self.notebook.add(self.frame_tecnicos, text="Técnicos")
        self.notebook.add(self.frame_graficos, text="Evolução")

        self._criar_formulario(self.frame_registro)
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_comparativo()
        self._carregar_graficos()
        self._carregar_tecnicos()

    # --------------------- Formulário ---------------------
    def _criar_formulario(self, frame):
        for i in range(4):
            frame.columnconfigure(i, weight=1)
        frame.rowconfigure(6, weight=1)
        frame.rowconfigure(8, weight=1)
        frame.rowconfigure(9, weight=1)

        ttk.Label(frame, text="Data da Partida:").grid(row=0, column=0, sticky="w", pady=4)
        data_picker = ttk.Frame(frame)
        data_picker.grid(row=0, column=1, columnspan=2, sticky="w", pady=4)
        self.data_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.tecnico_var = tk.StringVar(value=self.listas.get("tecnico_atual", "Fernando Diniz"))
        self.data_entry = ttk.Entry(data_picker, width=12, textvariable=self.data_var)
        self.data_entry.pack(side="left")
        self._forcar_cursor_visivel(self.data_entry)
        ttk.Button(data_picker, text="Calendário", command=self._abrir_calendario_popup).pack(side="left", padx=(8, 0))
        ttk.Label(data_picker, text="Técnico:").pack(side="left", padx=(12, 4))
        self.tecnico_entry = ttk.Combobox(data_picker, textvariable=self.tecnico_var, width=22)
        self.tecnico_entry['values'] = self.listas.get("tecnicos", [])
        self.tecnico_entry.pack(side="left")
        self.tecnico_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "tecnicos"))
        self._forcar_cursor_visivel(self.tecnico_entry)

        ttk.Label(frame, text="Adversário:").grid(row=1, column=0, sticky="w", pady=4)
        self.adversario_var = tk.StringVar()
        self.adversario_entry = ttk.Combobox(frame, textvariable=self.adversario_var)
        self.adversario_entry['values'] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))
        self._forcar_cursor_visivel(self.adversario_entry)

        ttk.Label(frame, text="Placar (Vasco x Adversário):").grid(row=2, column=0, sticky="w", pady=4)
        self.placar_vasco = ttk.Entry(frame, width=6)
        self.placar_vasco.grid(row=2, column=1, sticky="w", pady=4)
        self._forcar_cursor_visivel(self.placar_vasco)
        ttk.Label(frame, text="x").grid(row=2, column=2, sticky="w", pady=4)
        self.placar_adversario = ttk.Entry(frame, width=6)
        self.placar_adversario.grid(row=2, column=3, sticky="w", pady=4)
        self._forcar_cursor_visivel(self.placar_adversario)

        ttk.Label(frame, text="Local:").grid(row=3, column=0, sticky="w", pady=4)
        self.local_var = tk.StringVar(value="casa")
        local_wrap = ttk.Frame(frame)
        local_wrap.grid(row=3, column=1, columnspan=3, sticky="w", pady=4)
        ttk.Radiobutton(local_wrap, text="Casa", variable=self.local_var, value="casa").pack(side="left", padx=(0, 12))
        ttk.Radiobutton(local_wrap, text="Fora", variable=self.local_var, value="fora").pack(side="left")

        ttk.Label(frame, text="Competição:").grid(row=4, column=0, sticky="w", pady=4)
        self.competicao_var = tk.StringVar()
        comp_wrap = ttk.Frame(frame)
        comp_wrap.grid(row=4, column=1, columnspan=3, sticky="ew", pady=4)
        comp_wrap.columnconfigure(0, weight=1)
        self.competicao_entry = ttk.Combobox(comp_wrap, textvariable=self.competicao_var)
        self.competicao_entry['values'] = self.listas.get("competicoes", [])
        self.competicao_entry.grid(row=0, column=0, sticky="ew")
        self.competicao_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "competicoes"))
        self._forcar_cursor_visivel(self.competicao_entry)
        ttk.Label(comp_wrap, text="Posição na tabela:").grid(row=0, column=1, sticky="w", padx=(10, 4))
        self.posicao_var = tk.StringVar()
        self.posicao_entry = ttk.Entry(comp_wrap, width=6, textvariable=self.posicao_var)
        self.posicao_entry.grid(row=0, column=2, sticky="w")
        self._forcar_cursor_visivel(self.posicao_entry)
        self.competicao_var.trace_add("write", lambda *_: self._atualizar_estado_posicao())
        self._atualizar_estado_posicao()

        # Gols do Vasco
        ttk.Label(frame, text="Gols do Vasco (pressione Enter para adicionar):").grid(row=5, column=0, sticky="nw", pady=(10, 4))
        col_vasco = ttk.Frame(frame)
        col_vasco.grid(row=5, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.entry_gol_vasco = ttk.Combobox(col_vasco)
        self.entry_gol_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_gol_vasco.bind("<Return>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vasco"))
        self.entry_gol_vasco.pack(fill="x")
        self._forcar_cursor_visivel(self.entry_gol_vasco)
        lista_vasco_wrap = ttk.Frame(frame)
        lista_vasco_wrap.grid(row=6, column=1, columnspan=3, sticky="nsew")
        lista_vasco_wrap.rowconfigure(0, weight=1)
        lista_vasco_wrap.columnconfigure(0, weight=1)
        self.lista_gols_vasco = tk.Listbox(
            lista_vasco_wrap, height=5,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_gols_vasco.grid(row=0, column=0, sticky="nsew")
        self.lista_gols_vasco.bind("<Delete>", self.remover_gol_vasco)
        ttk.Button(lista_vasco_wrap, text="Remover Selecionado",
                   command=self.remover_gol_vasco).grid(row=1, column=0, sticky="e", pady=(6, 0))

        # Gols do Adversário
        ttk.Label(frame, text="Gols do Adversário (pressione Enter para adicionar):").grid(row=7, column=0, sticky="nw", pady=(10, 4))
        col_contra = ttk.Frame(frame)
        col_contra.grid(row=7, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.entry_gol_contra = ttk.Combobox(col_contra)
        self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self.entry_gol_contra.bind("<Return>", self.adicionar_gol_contra)
        self.entry_gol_contra.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "contra"))
        self.entry_gol_contra.pack(fill="x")
        self._forcar_cursor_visivel(self.entry_gol_contra)
        lista_contra_wrap = ttk.Frame(frame)
        lista_contra_wrap.grid(row=8, column=1, columnspan=3, sticky="nsew")
        lista_contra_wrap.rowconfigure(0, weight=1)
        lista_contra_wrap.columnconfigure(0, weight=1)
        self.lista_gols_contra = tk.Listbox(
            lista_contra_wrap, height=5,
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            selectbackground=self.colors["select_bg"], selectforeground=self.colors["select_fg"]
        )
        self.lista_gols_contra.grid(row=0, column=0, sticky="nsew")
        self.lista_gols_contra.bind("<Delete>", self.remover_gol_contra)
        ttk.Button(lista_contra_wrap, text="Remover Selecionado",
                   command=self.remover_gol_contra).grid(row=1, column=0, sticky="e", pady=(6, 0))

        # Observações
        ttk.Label(frame, text="Observações da Partida:").grid(row=9, column=0, sticky="nw", pady=(10, 4))
        self.obs_text = tk.Text(
            frame, height=4, wrap="word",
            bg=self.colors["entry_bg"], fg=self.colors["entry_fg"],
            insertbackground=self.colors["fg"]
        )
        self.obs_text.grid(row=9, column=1, columnspan=3, sticky="nsew", pady=(10, 4))
        self._forcar_cursor_visivel(self.obs_text)

        # Botões e status de edição
        self.salvar_btn_label = tk.StringVar(value="Salvar Partida")
        self.modo_edicao_var = tk.StringVar(value="")
        botoes = ttk.Frame(frame)
        botoes.grid(row=10, column=0, columnspan=4, pady=12)
        ttk.Label(botoes, textvariable=self.modo_edicao_var, foreground=self.colors["accent"]).pack(side="left", padx=(0, 12))
        self.btn_salvar = ttk.Button(botoes, textvariable=self.salvar_btn_label, command=self.salvar_partida)
        self.btn_salvar.pack(side="left", padx=6)
        self.btn_cancelar_edicao = ttk.Button(botoes, text="Cancelar Edição", command=self._cancelar_edicao)
        self.btn_cancelar_edicao.pack(side="left", padx=6)
        self.btn_cancelar_edicao.state(["disabled"])
        ttk.Button(botoes, text="Atualizar Abas", command=self._atualizar_abas).pack(side="left", padx=6)

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

    def _abrir_calendario_popup(self):
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

        try:
            data_atual = _parse_data_ptbr(self.data_var.get().strip())
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
                self.data_var.set(selecionada.strftime("%d/%m/%Y"))
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
            self.listas["jogadores_vasco"] = sorted(self.listas["jogadores_vasco"], key=lambda s: s.casefold())
            self.entry_gol_vasco['values'] = self.listas["jogadores_vasco"]
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

        # Gols (contados)
        nomes_vasco = list(self.lista_gols_vasco.get(0, tk.END))
        contagem_vasco = Counter(nomes_vasco)
        gols_vasco = [{"nome": nome, "gols": qtd} for nome, qtd in contagem_vasco.items()]

        nomes_contra = list(self.lista_gols_contra.get(0, tk.END))
        contagem_contra = Counter(nomes_contra)
        gols_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_contra.items()]

        if not (data and adversario and placar_vasco and placar_adv and competicao and tecnico):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

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

        messagebox.showinfo("Sucesso", msg)
        self._limpar_formulario()
        self._atualizar_abas()

    def _limpar_formulario(self):
        self.editing_index = None
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

    def _atualizar_abas(self):
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_comparativo()
        self._carregar_tecnicos()
        self._carregar_graficos()

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
        for idx, jogo in enumerate(jogos):
            ano = jogo["data"][-4:]
            temporadas[ano].append((idx, jogo))

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
            for idx_global, jogo in sorted(jogos_ano, key=lambda j: _parse_data_ptbr(j[1]["data"])):
                local = jogo.get("local", "desconhecido").capitalize()
                placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
                competicao = jogo.get("competicao", "Competição Desconhecida")
                data = jogo["data"]
                adversario = jogo["adversario"]

                if placar["vasco"] > placar["adversario"]:
                    vitorias += 1
                elif placar["vasco"] < placar["adversario"]:
                    derrotas += 1
                else:
                    empates += 1

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
            saldo = gols_pro - gols_contra
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
            sx = ttk.Scrollbar(table_wrap, orient="horizontal", command=tv.xview)
            tv.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
            tv.pack(side="left", fill="both", expand=True)
            sy.pack(side="right", fill="y")

            if len(rows) > 12:
                sx.pack(fill="x")

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



            # ----- Resumos curtos (top artilheiros/carrascos da temporada)
            bottom = ttk.Frame(frame_ano)
            bottom.pack(fill="x", pady=(8, 0))
            left = ttk.Labelframe(bottom, text="Artilheiros do Vasco (na temporada)", padding=6)
            left.pack(side="left", fill="x", expand=True, padx=(0, 4))
            right = ttk.Labelframe(bottom, text="Carrascos (na temporada)", padding=6)
            right.pack(side="left", fill="x", expand=True, padx=(4, 0))

            def fill_label_list(frame, counter):
                if counter:
                    txt = "\n".join([f"• {n}: {q}" for n, q in counter.most_common(8)])
                else:
                    txt = "—"
                ttk.Label(frame, text=txt, justify="left").pack(anchor="w")

        fill_label_list(left, artilheiros)
        fill_label_list(right, carrascos)

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
                    partes.append(f"{nome} x{qtd}" if qtd > 1 else nome)
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

        for jogo in jogos:
            placar = jogo.get("placar")
            if not placar:
                continue

            gols_pro += placar.get("vasco", 0)
            gols_contra += placar.get("adversario", 0)

            if placar["vasco"] > placar["adversario"]:
                vitorias += 1
            elif placar["vasco"] < placar["adversario"]:
                derrotas += 1
            else:
                empates += 1

            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    artilheiros[g["nome"]] += g["gols"]
            for g in jogo.get("gols_adversario", []):
                if isinstance(g, dict):
                    carrascos[g["nome"]] += g["gols"]

        saldo = gols_pro - gols_contra
        aproveitamento = round(((vitorias * 3 + empates) / (total * 3)) * 100, 1) if total else 0.0
        invicto = round(((vitorias + empates) / total) * 100, 1) if total else 0.0

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

        make_card(cards, "Invicto (%)", f"{invicto}").grid(row=2, column=0, sticky="nsew", padx=6, pady=6)

        # Tabelas
        tables = ttk.Frame(self.frame_geral)
        tables.pack(fill="both", expand=True)

        frame_art = ttk.Labelframe(tables, text="Artilheiros do Vasco", padding=8)
        frame_art.pack(side="left", fill="both", expand=True, padx=(0, 6))
        tv_art = ttk.Treeview(frame_art, columns=("jogador", "gols"), show="headings", height=12)
        tv_art.heading("jogador", text="Jogador")
        tv_art.heading("gols", text="Gols")
        tv_art.column("jogador", anchor="w", width=240)
        tv_art.column("gols", anchor="center", width=80)
        tv_art.tag_configure("odd", background=self.colors["row_alt_bg"]) 
        tv_art.pack(fill="both", expand=True)

        frame_carr = ttk.Labelframe(tables, text="Carrascos (Gols contra o Vasco)", padding=8)
        frame_carr.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tv_carr = ttk.Treeview(frame_carr, columns=("jogador", "gols"), show="headings", height=12)
        tv_carr.heading("jogador", text="Jogador (Adversário)")
        tv_carr.heading("gols", text="Gols")
        tv_carr.column("jogador", anchor="w", width=260)
        tv_carr.column("gols", anchor="center", width=80)
        tv_carr.tag_configure("odd", background=self.colors["row_alt_bg"]) 
        tv_carr.pack(fill="both", expand=True)

        for i, (nome, qtd) in enumerate(artilheiros.most_common(), start=1):
            tv_art.insert("", "end", values=(nome, qtd), tags=("odd" if i % 2 else "",))
        for i, (nome, qtd) in enumerate(carrascos.most_common(), start=1):
            tv_carr.insert("", "end", values=(nome, qtd), tags=("odd" if i % 2 else "",))

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
            tv.heading(col, text=headings[col])
            tv.column(col, width=widths[col], anchor="center" if col != "tecnico" else "w")

        sy = ttk.Scrollbar(container, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=sy.set)
        tv.pack(side="left", fill="both", expand=True)
        sy.pack(side="right", fill="y")

        tv.tag_configure("odd", background=self.colors["row_alt_bg"])
        for i, (tecnico, info) in enumerate(sorted(stats.items(), key=lambda kv: (-kv[1]["jogos"], kv[0].casefold())), start=1):
            saldo = info["gols_pro"] - info["gols_contra"]
            top = info["artilheiros"].most_common(1)
            artilheiro_txt = "—"
            if top:
                nome, gols = top[0]
                artilheiro_txt = f"{nome} ({gols})"
            tv.insert(
                "", "end",
                values=(
                    tecnico,
                    info["jogos"],
                    info["casa"],
                    info["fora"],
                    info["vitorias"],
                    info["empates"],
                    info["derrotas"],
                    info["gols_pro"],
                    info["gols_contra"],
                    saldo,
                    artilheiro_txt,
                ),
                tags=("odd" if i % 2 else "",),
            )

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
            top = artilheiros.most_common(15)
            labels = [n for n, _ in top]
            values = [q for _, q in top]
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
                                                          ["Gols pró (acum.)", "Gols contra (acum.)"])
        self._plot_linhas(tab_gols, series["x"],
                          [series["gols_pro_acum"], series["gols_contra_acum"]],
                          ["Gols pró (acum.)", "Gols contra (acum.)"],
                          "Gols Acumulados", "Jogo", "Gols",
                          comparativos=[comparativo_gols] if comparativo_gols else None)

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

    def _criar_overlay_series(self, base_series, prev_series, keys, label_prefix, labels_desc):
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
            "alpha": 0.45,
            "linestyle": "--",
            "linewidth": 1.7,
        }
        for key, desc in zip(keys, labels_desc):
            valores_prev = prev_series.get(key, [])
            if not valores_prev:
                return None
            comparativo["series"].append(valores_prev[:max_len])
            comparativo["labels"].append(f"{label_prefix} - {desc}")
        return comparativo

    def _contar_artilheiros(self, jogos=None) -> Counter:
        if jogos is None:
            jogos = carregar_dados_jogos()
        c = Counter()
        for jogo in jogos:
            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    c[g.get("nome", "Desconhecido")] += int(g.get("gols", 0))
                elif isinstance(g, str):
                    c[g] += 1
        return c

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
            "gols_pro_acum": ("#15803d", "#86efac"),
            "gols_contra_acum": ("#b91c1c", "#fca5a5"),
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
                for info in present:
                    key = info["key"]
                    label = info["label"]
                    valores_prev = prev_series.get(key)
                    if not valores_prev:
                        continue
                    comparativo["series"].append(valores_prev[:lim_x])
                    comparativo["labels"].append(f"{ano_ant_txt} - {label}")
                    comparativo["colors"].append(info.get("light_color"))
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
    root = tk.Tk()
    app = App(root)
    root.mainloop()
