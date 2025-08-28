import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
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
    # aceita dd/mm/aaaa
    return datetime.strptime(s, "%d/%m/%Y")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Estatísticas do Vasco")
        # Janela mais espaçosa
        self.root.geometry("1100x780")
        self.root.minsize(980, 680)

        # Aumenta fontes padrão (TTK)
        default_font = tkFont.nametofont("TkDefaultFont")
        text_font = tkFont.nametofont("TkTextFont")
        fixed_font = tkFont.nametofont("TkFixedFont")
        for f in (default_font, text_font, fixed_font):
            f.configure(size=11)

        # Estilo TTK
        style = ttk.Style()
        # Em alguns temas, "clam" dá um visual consistente
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TLabel", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"))
        style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"))
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"))

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

    # --------------------- UI: Formulário ---------------------
    def _criar_formulario(self, frame):
        for i in range(4):
            frame.columnconfigure(i, weight=1)

        # Linha 0
        ttk.Label(frame, text="Data da Partida:").grid(row=0, column=0, sticky="w", pady=4)
        self.data_entry = DateEntry(frame, width=12, date_pattern='dd/mm/yyyy')
        self.data_entry.grid(row=0, column=1, sticky="w", pady=4)

        # Linha 1
        ttk.Label(frame, text="Adversário:").grid(row=1, column=0, sticky="w", pady=4)
        self.adversario_var = tk.StringVar()
        self.adversario_entry = ttk.Combobox(frame, textvariable=self.adversario_var)
        self.adversario_entry['values'] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))

        # Linha 2: Placar
        ttk.Label(frame, text="Placar (Vasco x Adversário):").grid(row=2, column=0, sticky="w", pady=4)
        self.placar_vasco = ttk.Entry(frame, width=6)
        self.placar_vasco.grid(row=2, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="x").grid(row=2, column=2, sticky="w", pady=4)
        self.placar_adversario = ttk.Entry(frame, width=6)
        self.placar_adversario.grid(row=2, column=3, sticky="w", pady=4)

        # Linha 3: Local
        ttk.Label(frame, text="Local:").grid(row=3, column=0, sticky="w", pady=4)
        self.local_var = tk.StringVar(value="casa")
        local_wrap = ttk.Frame(frame)
        local_wrap.grid(row=3, column=1, columnspan=3, sticky="w", pady=4)
        ttk.Radiobutton(local_wrap, text="Casa", variable=self.local_var, value="casa").pack(side="left", padx=(0, 12))
        ttk.Radiobutton(local_wrap, text="Fora", variable=self.local_var, value="fora").pack(side="left")

        # Linha 4: Competição
        ttk.Label(frame, text="Competição:").grid(row=4, column=0, sticky="w", pady=4)
        self.competicao_var = tk.StringVar()
        self.competicao_entry = ttk.Combobox(frame, textvariable=self.competicao_var)
        self.competicao_entry['values'] = self.listas.get("competicoes", [])
        self.competicao_entry.grid(row=4, column=1, columnspan=3, sticky="ew", pady=4)
        self.competicao_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "competicoes"))

        # Linha 5-6: Gols do Vasco
        ttk.Label(frame, text="Gols do Vasco:").grid(row=5, column=0, sticky="nw", pady=(10, 4))
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

        # Linha 7-8: Gols do Adversário
        ttk.Label(frame, text="Gols do Adversário:").grid(row=7, column=0, sticky="nw", pady=(10, 4))
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

        # Linha 9-10: Anulados Vasco
        ttk.Label(frame, text="Gols do Vasco Anulados (VAR):").grid(row=9, column=0, sticky="nw", pady=(10, 4))
        self.entry_anulado_vasco = ttk.Combobox(frame)
        self.entry_anulado_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_anulado_vasco.bind("<Return>", self.adicionar_anulado_vasco)
        self.entry_anulado_vasco.grid(row=9, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.lista_anulados_vasco = tk.Listbox(frame, height=3)
        self.lista_anulados_vasco.grid(row=10, column=1, columnspan=3, sticky="ew")
        self.lista_anulados_vasco.bind("<Delete>", lambda e: self._del_sel(self.lista_anulados_vasco))

        # Linha 11-12: Anulados Adversário
        ttk.Label(frame, text="Gols do Adversário Anulados (VAR):").grid(row=11, column=0, sticky="nw", pady=(10, 4))
        self.entry_anulado_contra = ttk.Combobox(frame)
        self.entry_anulado_contra['values'] = self.listas["jogadores_contra"]
        self.entry_anulado_contra.bind("<Return>", self.adicionar_anulado_contra)
        self.entry_anulado_contra.grid(row=11, column=1, columnspan=3, sticky="ew", pady=(10, 4))
        self.lista_anulados_contra = tk.Listbox(frame, height=3)
        self.lista_anulados_contra.grid(row=12, column=1, columnspan=3, sticky="ew")
        self.lista_anulados_contra.bind("<Delete>", lambda e: self._del_sel(self.lista_anulados_contra))

        # Botões
        botoes = ttk.Frame(frame)
        botoes.grid(row=13, column=0, columnspan=4, pady=12)
        self.btn_salvar = ttk.Button(botoes, text="Salvar Partida", command=self.salvar_partida)
        self.btn_salvar.pack(side="left", padx=6)
        self.btn_atualizar = ttk.Button(botoes, text="Atualizar Abas", command=self._atualizar_abas)
        self.btn_atualizar.pack(side="left", padx=6)

    def _del_sel(self, listbox):
        sel = listbox.curselection()
        if sel:
            listbox.delete(sel[0])

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

    # --------------------- Salvar / Menu contexto ---------------------
    def salvar_partida(self):
        data = self.data_entry.get()
        adversario = self.adversario_var.get().strip()
        competicao = self.competicao_var.get().strip()
        placar_vasco = self.placar_vasco.get().strip()
        placar_adv = self.placar_adversario.get().strip()
        local = self.local_var.get()

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

        contagem_anulados_vasco = Counter(self.lista_anulados_vasco.get(0, tk.END))
        gols_anulados_vasco = [{"nome": nome, "gols": qtd} for nome, qtd in contagem_anulados_vasco.items()]

        contagem_anulados_contra = Counter(self.lista_anulados_contra.get(0, tk.END))
        gols_anulados_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_anulados_contra.items()]

        jogo = {
            "data": data,
            "adversario": adversario,
            "competicao": competicao,
            "local": local,
            "placar": {
                "vasco": int(placar_vasco),
                "adversario": int(placar_adv)
            },
            "gols_vasco": gols_vasco,
            "gols_adversario": gols_contra,
            "gols_anulados": {
                "vasco": gols_anulados_vasco,
                "adversario": gols_anulados_contra
            }
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
        self.lista_anulados_vasco.delete(0, tk.END)
        self.lista_anulados_contra.delete(0, tk.END)
        self.local_var.set("casa")

    def _atualizar_abas(self):
        self._carregar_temporadas()
        self._carregar_geral()
        self._carregar_graficos()

    def mostrar_menu_contexto(self, event, tipo):
        widget = event.widget
        selecionado = widget.get().strip()
        if not selecionado:
            return

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"Excluir '{selecionado}'", command=lambda: self.excluir_nome(selecionado, tipo, widget))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def excluir_nome(self, nome, tipo, widget):
        alterou = False
        if tipo == "vasco" and nome in self.listas["jogadores_vasco"]:
            self.listas["jogadores_vasco"].remove(nome)
            widget['values'] = self.listas["jogadores_vasco"]
            alterou = True
        elif tipo == "contra" and nome in self.listas["jogadores_contra"]:
            self.listas["jogadores_contra"].remove(nome)
            widget['values'] = self.listas["jogadores_contra"]
            alterou = True
        elif tipo == "clubes" and nome in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].remove(nome)
            widget['values'] = self.listas["clubes_adversarios"]
            alterou = True
        elif tipo == "competicoes" and nome in self.listas.get("competicoes", []):
            self.listas["competicoes"].remove(nome)
            widget['values'] = self.listas.get("competicoes", [])
            alterou = True

        if alterou:
            salvar_listas(self.listas)
            widget.set("")
        else:
            messagebox.showwarning("Não encontrado", f"'{nome}' não está na lista.")

    def adicionar_anulado_vasco(self, event):
        jogador = self.entry_anulado_vasco.get().strip()
        if jogador:
            self.lista_anulados_vasco.insert(tk.END, jogador)
            if jogador not in self.listas["jogadores_vasco"]:
                self.listas["jogadores_vasco"].append(jogador)
                self.entry_anulado_vasco['values'] = self.listas["jogadores_vasco"]
            self.entry_anulado_vasco.delete(0, tk.END)

    def adicionar_anulado_contra(self, event):
        jogador = self.entry_anulado_contra.get().strip()
        if jogador:
            self.lista_anulados_contra.insert(tk.END, jogador)
            if jogador not in self.listas["jogadores_contra"]:
                self.listas["jogadores_contra"].append(jogador)
                self.entry_anulado_contra['values'] = self.listas["jogadores_contra"]
            self.entry_anulado_contra.delete(0, tk.END)

    # --------------------- Temporadas ---------------------
    def _carregar_temporadas(self):
        for widget in self.frame_temporadas.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.frame_temporadas, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.frame_temporadas, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding=(5, 5))

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        jogos = carregar_dados_jogos()
        temporadas = defaultdict(list)
        for jogo in jogos:
            ano = jogo["data"][-4:]  # dd/mm/aaaa
            temporadas[ano].append(jogo)

        for ano in sorted(temporadas.keys(), reverse=True):
            frame_ano = ttk.LabelFrame(scroll_frame, text=f"Temporada {ano}", padding=8)
            frame_ano.pack(fill="x", padx=5, pady=6)

            jogos_ano = temporadas[ano]
            vitorias = empates = derrotas = 0
            gols_pro = gols_contra = 0
            anulados_vasco = anulados_contra = 0
            artilheiros = Counter()
            carrascos = Counter()

            for jogo in jogos_ano:
                local = jogo.get("local", "desconhecido").capitalize()
                placar = jogo.get("placar", {"vasco": "?", "adversario": "?"})
                competicao = jogo.get("competicao", "Competição Desconhecida")
                linha = f"{jogo['data']} - {local} - {competicao}: Vasco {placar['vasco']} x {placar['adversario']} {jogo['adversario']}"
                ttk.Label(frame_ano, text=linha).pack(anchor="w")

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

                for g in jogo.get("gols_anulados", {}).get("vasco", []):
                    anulados_vasco += g["gols"]
                for g in jogo.get("gols_anulados", {}).get("adversario", []):
                    anulados_contra += g["gols"]

            ttk.Separator(frame_ano, orient="horizontal").pack(fill="x", pady=5)

            resumo = f"""Total de jogos: {len(jogos_ano)}
Vitórias: {vitorias}
Empates: {empates}
Derrotas: {derrotas}
Gols Pró: {gols_pro}
Gols Contra: {gols_contra}
Gols Anulados do Vasco: {anulados_vasco}
Gols Anulados Contra: {anulados_contra}"""

            for linha in resumo.splitlines():
                ttk.Label(frame_ano, text=linha).pack(anchor="w")

            if artilheiros:
                ttk.Label(frame_ano, text="Artilheiros do Vasco:").pack(anchor="w", pady=(5, 0))
                for nome, qtd in artilheiros.most_common():
                    ttk.Label(frame_ano, text=f" - {nome}: {qtd} gol(s)").pack(anchor="w")

            if carrascos:
                ttk.Label(frame_ano, text="Carrascos (Gols contra o Vasco):").pack(anchor="w", pady=(5, 0))
                for nome, qtd in carrascos.most_common():
                    ttk.Label(frame_ano, text=f" - {nome}: {qtd} gol(s)").pack(anchor="w")

    # --------------------- Geral ---------------------
    def _carregar_geral(self):
        for widget in self.frame_geral.winfo_children():
            widget.destroy()

        jogos = carregar_dados_jogos()
        total = len(jogos)
        vitorias = empates = derrotas = 0
        gols_pro = gols_contra = 0
        anulados_vasco = anulados_contra = 0
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

            for g in jogo.get("gols_anulados", {}).get("vasco", []):
                anulados_vasco += g["gols"]
            for g in jogo.get("gols_anulados", {}).get("adversario", []):
                anulados_contra += g["gols"]

        texto = f"""Total de jogos: {total}
Vitórias: {vitorias}
Empates: {empates}
Derrotas: {derrotas}
Gols Pró: {gols_pro}
Gols Contra: {gols_contra}
Gols Anulados do Vasco: {anulados_vasco}
Gols Anulados Contra: {anulados_contra}"""

        frame_resumo = ttk.LabelFrame(self.frame_geral, text="Resumo Geral", padding=10)
        frame_resumo.pack(fill="x", padx=10, pady=6)
        for linha in texto.splitlines():
            ttk.Label(frame_resumo, text=linha).pack(anchor="w")

        frame_art = ttk.LabelFrame(self.frame_geral, text="Artilheiros do Vasco", padding=10)
        frame_art.pack(fill="x", padx=10, pady=6)
        for nome, qtd in artilheiros.most_common():
            ttk.Label(frame_art, text=f"{nome}: {qtd} gol(s)").pack(anchor="w")

        frame_carr = ttk.LabelFrame(self.frame_geral, text="Carrascos (Gols contra o Vasco)", padding=10)
        frame_carr.pack(fill="x", padx=10, pady=6)
        for nome, qtd in carrascos.most_common():
            ttk.Label(frame_carr, text=f"{nome}: {qtd} gol(s)").pack(anchor="w")

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

        nb = ttk.Notebook(self.frame_graficos)
        nb.pack(fill="both", expand=True)

        # 1) Pontos acumulados
        f1 = ttk.Frame(nb, padding=8)
        nb.add(f1, text="Pontos")
        self._plot_linhas(f1, series["x"], [series["pontos_acum"]], ["Pontos acumulados"], "Evolução de Pontos", "Jogo", "Pontos")

        # 2) Gols Pró x Contra (acum.)
        f2 = ttk.Frame(nb, padding=8)
        nb.add(f2, text="Gols (Acum.)")
        self._plot_linhas(f2, series["x"], [series["gols_pro_acum"], series["gols_contra_acum"]],
                          ["Gols pró (acum.)", "Gols contra (acum.)"], "Gols Acumulados", "Jogo", "Gols")

        # 3) Saldo de gols acumulado
        f3 = ttk.Frame(nb, padding=8)
        nb.add(f3, text="Saldo")
        self._plot_linhas(f3, series["x"], [series["saldo_acum"]], ["Saldo (acum.)"], "Saldo de Gols (Acum.)", "Jogo", "Saldo")

        # 4) Vitórias/Empates/Derrotas acumulados
        f4 = ttk.Frame(nb, padding=8)
        nb.add(f4, text="VED (Acum.)")
        self._plot_linhas(f4, series["x"],
                          [series["vit_acum"], series["emp_acum"], series["der_acum"]],
                          ["Vitórias (acum.)", "Empates (acum.)", "Derrotas (acum.)"],
                          "Vitórias/Empates/Derrotas (Acum.)", "Jogo", "Quantidade")

        # Botão manual para atualizar
        ttk.Button(self.frame_graficos, text="Recarregar Gráficos", command=self._carregar_graficos).pack(pady=8)

    def _montar_series_evolucao(self):
        """
        Monta séries ordenadas por data:
        - x: 1..N
        - pontos_acum: 3 por vitória, 1 por empate
        - gols_pro_acum, gols_contra_acum, saldo_acum
        - vit_acum, emp_acum, der_acum
        """
        jogos = carregar_dados_jogos()
        if not jogos:
            return {"x": []}

        # Ordena por data (dd/mm/aaaa)
        jogos_ordenados = sorted(jogos, key=lambda j: _parse_data_ptbr(j["data"]))

        x = []
        pontos_acum = []
        gols_pro_acum = []
        gols_contra_acum = []
        saldo_acum = []
        vit_acum = []
        emp_acum = []
        der_acum = []

        p = gp = gc = s = v = e = d = 0

        for i, jogo in enumerate(jogos_ordenados, start=1):
            placar = jogo.get("placar", {"vasco": 0, "adversario": 0})
            vasco = placar.get("vasco", 0)
            adv = placar.get("adversario", 0)

            gp += vasco
            gc += adv
            s = gp - gc

            if vasco > adv:
                p += 3
                v += 1
            elif vasco == adv:
                p += 1
                e += 1
            else:
                d += 1

            x.append(i)
            pontos_acum.append(p)
            gols_pro_acum.append(gp)
            gols_contra_acum.append(gc)
            saldo_acum.append(s)
            vit_acum.append(v)
            emp_acum.append(e)
            der_acum.append(d)

        return {
            "x": x,
            "pontos_acum": pontos_acum,
            "gols_pro_acum": gols_pro_acum,
            "gols_contra_acum": gols_contra_acum,
            "saldo_acum": saldo_acum,
            "vit_acum": vit_acum,
            "emp_acum": emp_acum,
            "der_acum": der_acum,
        }

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
        widget = canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

    # --------------------- Main ---------------------
    # (Nada aqui)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
