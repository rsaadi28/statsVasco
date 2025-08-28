import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict, Counter
import json
import os
from tkcalendar import DateEntry
import tkinter.font as tkFont
from datetime import datetime

# --- Matplotlib (gráficos) ---
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False

ARQUIVO_JOGOS = "jogos_vasco.json"
ARQUIVO_LISTAS = "listas_auxiliares.json"


def carregar_dados_jogos():
    if os.path.exists(ARQUIVO_JOGOS):
        with open(ARQUIVO_JOGOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def carregar_listas():
    if os.path.exists(ARQUIVO_LISTAS):
        with open(ARQUIVO_LISTAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "clubes_adversarios": [],
        "jogadores_vasco": [],
        "jogadores_contra": [],
        "competicoes": []
    }


def salvar_listas(data):
    with open(ARQUIVO_LISTAS, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def salvar_jogo(jogo):
    if os.path.exists(ARQUIVO_JOGOS):
        with open(ARQUIVO_JOGOS, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = []
    dados.append(jogo)
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

        self.listas = carregar_listas()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frame_registro = ttk.Frame(self.notebook, padding=10)
        self.frame_temporadas = ttk.Frame(self.notebook, padding=10)
        self.frame_geral = ttk.Frame(self.notebook, padding=10)
        self.frame_graficos = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_temporadas, text="Temporadas")
        self.notebook.add(self.frame_geral, text="Geral")
        self.notebook.add(self.frame_graficos, text="Evolução")

        self._criar_formulario(self.frame_registro)
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_graficos()

    # --------------------- Formulário ---------------------
    def _criar_formulario(self, frame):
        for i in range(4):
            frame.columnconfigure(i, weight=1)

        ttk.Label(frame, text="Data da Partida:").grid(row=0, column=0, sticky="w", pady=4)
        self.data_entry = DateEntry(frame, width=12, date_pattern='dd/mm/yyyy')
        self.data_entry.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frame, text="Adversário:").grid(row=1, column=0, sticky="w", pady=4)
        self.adversario_var = tk.StringVar()
        self.adversario_entry = ttk.Combobox(frame, textvariable=self.adversario_var)
        self.adversario_entry['values'] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))

        ttk.Label(frame, text="Placar (Vasco x Adversário):").grid(row=2, column=0, sticky="w", pady=4)
        self.placar_vasco = ttk.Entry(frame, width=6)
        self.placar_vasco.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="x").grid(row=2, column=2, sticky="w", pady=4)
        self.placar_adversario = ttk.Entry(frame, width=6)
        self.placar_adversario.grid(row=2, column=3, sticky="w", pady=4)

        ttk.Label(frame, text="Local:").grid(row=3, column=0, sticky="w", pady=4)
        self.local_var = tk.StringVar(value="casa")
        local_wrap = ttk.Frame(frame)
        local_wrap.grid(row=3, column=1, columnspan=3, sticky="w", pady=4)
        ttk.Radiobutton(local_wrap, text="Casa", variable=self.local_var, value="casa").pack(side="left", padx=(0, 12))
        ttk.Radiobutton(local_wrap, text="Fora", variable=self.local_var, value="fora").pack(side="left")

        ttk.Label(frame, text="Competição:").grid(row=4, column=0, sticky="w", pady=4)
        self.competicao_var = tk.StringVar()
        self.competicao_entry = ttk.Combobox(frame, textvariable=self.competicao_var)
        self.competicao_entry['values'] = self.listas.get("competicoes", [])
        self.competicao_entry.grid(row=4, column=1, columnspan=3, sticky="ew", pady=4)
        self.competicao_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "competicoes"))

        # Gols do Vasco
        ttk.Label(frame, text="Gols do Vasco (pressione Enter para adicionar):").grid(row=5, column=0, sticky="nw", pady=(10, 4))
        col_vasco = ttk.Frame(frame)
        col_vasco.grid(row=5, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.entry_gol_vasco = ttk.Combobox(col_vasco)
        self.entry_gol_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_gol_vasco.bind("<Return>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vasco"))
        self.entry_gol_vasco.pack(fill="x")
        self.lista_gols_vasco = tk.Listbox(frame, height=5)
        self.lista_gols_vasco.grid(row=6, column=1, columnspan=3, sticky="ew")
        self.lista_gols_vasco.bind("<Delete>", self.remover_gol_vasco)

        # Gols do Adversário
        ttk.Label(frame, text="Gols do Adversário (pressione Enter para adicionar):").grid(row=7, column=0, sticky="nw", pady=(10, 4))
        col_contra = ttk.Frame(frame)
        col_contra.grid(row=7, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.entry_gol_contra = ttk.Combobox(col_contra)
        self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self.entry_gol_contra.bind("<Return>", self.adicionar_gol_contra)
        self.entry_gol_contra.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "contra"))
        self.entry_gol_contra.pack(fill="x")
        self.lista_gols_contra = tk.Listbox(frame, height=5)
        self.lista_gols_contra.grid(row=8, column=1, columnspan=3, sticky="ew")
        self.lista_gols_contra.bind("<Delete>", self.remover_gol_contra)

        # Observações
        ttk.Label(frame, text="Observações da Partida:").grid(row=9, column=0, sticky="nw", pady=(10, 4))
        self.obs_text = tk.Text(frame, height=4, wrap="word")
        self.obs_text.grid(row=9, column=1, columnspan=3, sticky="ew", pady=(10, 4))

        # Botões
        botoes = ttk.Frame(frame)
        botoes.grid(row=10, column=0, columnspan=4, pady=12)
        ttk.Button(botoes, text="Salvar Partida", command=self.salvar_partida).pack(side="left", padx=6)
        ttk.Button(botoes, text="Atualizar Abas", command=self._atualizar_abas).pack(side="left", padx=6)

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

    def remover_gol_vasco(self, event):
        sel = self.lista_gols_vasco.curselection()
        if sel:
            self.lista_gols_vasco.delete(sel[0])

    def remover_gol_contra(self, event):
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

        # Gols (contados)
        nomes_vasco = list(self.lista_gols_vasco.get(0, tk.END))
        contagem_vasco = Counter(nomes_vasco)
        gols_vasco = [{"nome": nome, "gols": qtd} for nome, qtd in contagem_vasco.items()]

        nomes_contra = list(self.lista_gols_contra.get(0, tk.END))
        contagem_contra = Counter(nomes_contra)
        gols_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_contra.items()]

        if not (data and adversario and placar_vasco and placar_adv and competicao):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        if adversario not in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].append(adversario)
            self.adversario_entry['values'] = self.listas["clubes_adversarios"]

        if competicao not in self.listas.get("competicoes", []):
            self.listas.setdefault("competicoes", []).append(competicao)
            self.competicao_entry['values'] = self.listas["competicoes"]

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
        }

        salvar_jogo(jogo)
        messagebox.showinfo("Sucesso", "Partida registrada com sucesso!")
        self._limpar_formulario()
        self._atualizar_abas()

    def _limpar_formulario(self):
        self.adversario_var.set("")
        self.competicao_var.set("")
        self.placar_vasco.delete(0, tk.END)
        self.placar_adversario.delete(0, tk.END)
        self.lista_gols_vasco.delete(0, tk.END)
        self.lista_gols_contra.delete(0, tk.END)
        self.entry_gol_vasco.delete(0, tk.END)
        self.entry_gol_contra.delete(0, tk.END)
        self.obs_text.delete("1.0", "end")
        self.local_var.set("casa")

    def _atualizar_abas(self):
        self._carregar_temporadas()
        self._carregar_geral()
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

    # --------------------- Temporadas ---------------------
    def _carregar_temporadas(self):
        # limpa a aba
        for widget in self.frame_temporadas.winfo_children():
            widget.destroy()

        # Canvas + Scrollbar
        canvas = tk.Canvas(self.frame_temporadas, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_temporadas, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Frame interno que contém tudo
        scroll_frame = ttk.Frame(canvas, padding=(8, 8))
        # cria a janela e guarda o id
        window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # 1) sempre atualiza a scrollregion
        def on_frame_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind("<Configure>", on_frame_configure)

        # 2) força o frame a ter a MESMA largura do canvas (ocupa toda a largura!)
        def on_canvas_configure(e):
            canvas.itemconfigure(window_id, width=e.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # scroll com a roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)


        jogos = carregar_dados_jogos()
        temporadas = defaultdict(list)
        for jogo in jogos:
            ano = jogo["data"][-4:]  # dd/mm/aaaa
            temporadas[ano].append(jogo)

        for ano in sorted(temporadas.keys(), reverse=True):
            frame_ano = ttk.LabelFrame(scroll_frame, text=f"Temporada {ano}", padding=10)
            frame_ano.pack(fill="x", padx=8, pady=14)  # mais espaçamento vertical

            jogos_ano = temporadas[ano]
            vitorias = empates = derrotas = 0
            gols_pro = gols_contra = 0
            artilheiros = Counter()
            carrascos = Counter()

            rows = []
            for jogo in sorted(jogos_ano, key=lambda j: _parse_data_ptbr(j["data"])):
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
                    "adversario": adversario, "raw": jogo
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
            table_wrap.pack(fill="x")

            cols = ("data", "local", "competicao", "adversario", "placar")
            tv = ttk.Treeview(table_wrap, columns=cols, show="headings",
                              height=min(12, max(6, len(rows))))
            # larguras para caber placar estendido
            for c, w in zip(cols, (90, 80, 240, 220, 320)):
                tv.heading(c, text=c.capitalize() if c != "placar" else "Placar")
                tv.column(c, anchor="w", width=w, stretch=True)

            sx = ttk.Scrollbar(table_wrap, orient="horizontal", command=tv.xview)
            tv.configure(xscrollcommand=sx.set)
            tv.pack(fill="both", expand=True)   # em vez de apenas fill="x"

            if len(rows) > 12:
                sx.pack(fill="x")

            tv.tag_configure("odd", background="#f6f6f6")

            tooltip_map = {}
            obs_map = {}

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

            # Tooltip nos gols (mouse hover)
            self._bind_treeview_tooltips(tv, tooltip_map)

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

            # separador entre temporadas
            sep = ttk.Separator(scroll_frame, orient="horizontal")
            sep.pack(fill="x", padx=4, pady=(6, 2))


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
        tv_art.tag_configure("odd", background="#f3f3f3")
        tv_art.pack(fill="both", expand=True)

        frame_carr = ttk.Labelframe(tables, text="Carrascos (Gols contra o Vasco)", padding=8)
        frame_carr.pack(side="left", fill="both", expand=True, padx=(6, 0))
        tv_carr = ttk.Treeview(frame_carr, columns=("jogador", "gols"), show="headings", height=12)
        tv_carr.heading("jogador", text="Jogador (Adversário)")
        tv_carr.heading("gols", text="Gols")
        tv_carr.column("jogador", anchor="w", width=260)
        tv_carr.column("gols", anchor="center", width=80)
        tv_carr.tag_configure("odd", background="#f3f3f3")
        tv_carr.pack(fill="both", expand=True)

        for i, (nome, qtd) in enumerate(artilheiros.most_common(), start=1):
            tv_art.insert("", "end", values=(nome, qtd), tags=("odd" if i % 2 else "",))
        for i, (nome, qtd) in enumerate(carrascos.most_common(), start=1):
            tv_carr.insert("", "end", values=(nome, qtd), tags=("odd" if i % 2 else "",))

    # --------------------- Gráficos ---------------------
    def _carregar_graficos(self):
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()

        if not MATPLOTLIB_OK:
            ttk.Label(self.frame_graficos, text="Matplotlib não disponível. Instale para ver os gráficos (pip install matplotlib).").pack(anchor="w")
            return

        series = self._montar_series_evolucao()
        if not series["x"]:
            ttk.Label(self.frame_graficos, text="Sem dados para exibir gráficos.").pack(anchor="w")
            return

        artilheiros = self._contar_artilheiros()
        nb = ttk.Notebook(self.frame_graficos)
        nb.pack(fill="both", expand=True)

        # 1) Artilheiros (barras horizontais) — decrescente
        f1 = ttk.Frame(nb, padding=8)
        nb.add(f1, text="Artilheiros")
        if artilheiros:
            top = artilheiros.most_common(15)
            labels = [n for n, _ in top]   # já em ordem decrescente
            values = [q for _, q in top]
            self._plot_barras_h(f1, labels, values, "Artilheiros (Gols válidos)", "Gols", top_to_bottom=True)
        else:
            ttk.Label(f1, text="Ainda não há artilheiros registrados.").pack(anchor="w")

        # 2) Gols Pró x Contra (Acum.) - linhas
        f2 = ttk.Frame(nb, padding=8)
        nb.add(f2, text="Gols (Acum.)")
        self._plot_linhas(f2, series["x"],
                          [series["gols_pro_acum"], series["gols_contra_acum"]],
                          ["Gols pró (acum.)", "Gols contra (acum.)"],
                          "Gols Acumulados", "Jogo", "Gols")

        # 3) Saldo de gols (Acum.) - linhas
        f3 = ttk.Frame(nb, padding=8)
        nb.add(f3, text="Saldo")
        self._plot_linhas(f3, series["x"], [series["saldo_acum"]],
                          ["Saldo (acum.)"], "Saldo de Gols (Acum.)", "Jogo", "Saldo")

        # 4) V/E/D (Totais) - barras coloridas
        f4 = ttk.Frame(nb, padding=8)
        nb.add(f4, text="VED (Totais)")
        v_total = series["vit_acum"][-1] if series["vit_acum"] else 0
        e_total = series["emp_acum"][-1] if series["emp_acum"] else 0
        d_total = series["der_acum"][-1] if series["der_acum"] else 0
        self._plot_barras_v(f4, ["Vitórias", "Empates", "Derrotas"], [v_total, e_total, d_total],
                            "Totais de Resultados", "Categoria", "Quantidade",
                            colors=["green", "yellow", "red"])

        ttk.Button(self.frame_graficos, text="Recarregar Gráficos", command=self._carregar_graficos).pack(pady=8)

    def _contar_artilheiros(self) -> Counter:
        jogos = carregar_dados_jogos()
        c = Counter()
        for jogo in jogos:
            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    c[g.get("nome", "Desconhecido")] += int(g.get("gols", 0))
                elif isinstance(g, str):
                    c[g] += 1
        return c

    def _montar_series_evolucao(self):
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

        gp = gc = s = v = e = d = 0

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

            x.append(i)
            gols_pro_acum.append(gp)
            gols_contra_acum.append(gc)
            saldo_acum.append(s)
            vit_acum.append(v)
            emp_acum.append(e)
            der_acum.append(d)

        return {
            "x": x,
            "gols_pro_acum": gols_pro_acum,
            "gols_contra_acum": gols_contra_acum,
            "saldo_acum": saldo_acum,
            "vit_acum": vit_acum,
            "emp_acum": emp_acum,
            "der_acum": der_acum,
        }

    # --------- Helpers de plot ---------
    def _plot_linhas(self, container, x, series_list, labels, titulo, xlabel, ylabel):
        fig = Figure(figsize=(8.5, 5.0), dpi=100)
        ax = fig.add_subplot(111)
        for serie, label in zip(series_list, labels):
            ax.plot(x, serie, label=label, linewidth=2)
        ax.set_title(titulo)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc="best")
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
