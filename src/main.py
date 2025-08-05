import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from collections import defaultdict, Counter
import json
import os
from tkcalendar import DateEntry
import tkinter.font as tkFont  # certifique-se de importar isso no topo do arquivo


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
        "jogadores_contra": []
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

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Estatísticas do Vasco")

        self.listas = carregar_listas()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.frame_registro = ttk.Frame(self.notebook)
        self.frame_temporadas = ttk.Frame(self.notebook)
        self.frame_geral = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_temporadas, text="Temporadas")
        self.notebook.add(self.frame_geral, text="Geral")

        self._criar_formulario(self.frame_registro)
        self._carregar_temporadas()
        self._carregar_geral()


    def _criar_formulario(self, frame):
        ttk.Label(frame, text="Data da Partida:").grid(row=0, column=0, sticky="w")
        self.data_entry = DateEntry(frame, width=12, date_pattern='dd/mm/yyyy')

        self.data_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Adversário:").grid(row=1, column=0, sticky="w")
        self.adversario_var = tk.StringVar()
        self.adversario_entry = ttk.Combobox(frame, textvariable=self.adversario_var)
        self.adversario_entry['values'] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=1, column=1)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))

        ttk.Label(frame, text="Placar (Vasco x Adversário):").grid(row=2, column=0, sticky="w")
        self.placar_vasco = ttk.Entry(frame, width=5)
        self.placar_adversario = ttk.Entry(frame, width=5)
        self.placar_vasco.grid(row=2, column=1, sticky="w")
        ttk.Label(frame, text="x").grid(row=2, column=1)
        self.placar_adversario.grid(row=2, column=1, sticky="e")

        ttk.Label(frame, text="Local:").grid(row=3, column=0, sticky="w")
        self.local_var = tk.StringVar(value="casa")
        ttk.Radiobutton(frame, text="Casa", variable=self.local_var, value="casa").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(frame, text="Fora", variable=self.local_var, value="fora").grid(row=3, column=1, sticky="e")

        # Gols Vasco
        ttk.Label(frame, text="Gols do Vasco:").grid(row=4, column=0, sticky="nw")
        self.entry_gol_vasco = ttk.Combobox(frame)
        self.entry_gol_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_gol_vasco.bind("<Return>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.grid(row=4, column=1, sticky="ew")
        self.entry_gol_vasco.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vasco"))
        self.lista_gols_vasco = tk.Listbox(frame, height=4)
        self.lista_gols_vasco.grid(row=5, column=1, sticky="ew")
        self.lista_gols_vasco.bind("<Delete>", self.remover_gol_vasco)

        # Gols adversário
        ttk.Label(frame, text="Gols do Adversário:").grid(row=6, column=0, sticky="nw")
        self.entry_gol_contra = ttk.Combobox(frame)
        self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self.entry_gol_contra.bind("<Return>", self.adicionar_gol_contra)
        self.entry_gol_contra.grid(row=6, column=1, sticky="ew")
        self.entry_gol_contra.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "contra"))
        self.lista_gols_contra = tk.Listbox(frame, height=4)
        self.lista_gols_contra.grid(row=7, column=1, sticky="ew")
        self.lista_gols_contra.bind("<Delete>", self.remover_gol_contra)

        # Gols ANULADOS do Vasco
        ttk.Label(frame, text="Gols do Vasco Anulados (VAR):").grid(row=8, column=0, sticky="nw")
        self.entry_anulado_vasco = ttk.Combobox(frame)
        self.entry_anulado_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_anulado_vasco.bind("<Return>", self.adicionar_anulado_vasco)
        self.entry_anulado_vasco.grid(row=8, column=1, sticky="ew")
        self.lista_anulados_vasco = tk.Listbox(frame, height=2)
        self.lista_anulados_vasco.grid(row=9, column=1, sticky="ew")

        # Gols ANULADOS do Adversário
        ttk.Label(frame, text="Gols do Adversário Anulados (VAR):").grid(row=10, column=0, sticky="nw")
        self.entry_anulado_contra = ttk.Combobox(frame)
        self.entry_anulado_contra['values'] = self.listas["jogadores_contra"]
        self.entry_anulado_contra.bind("<Return>", self.adicionar_anulado_contra)
        self.entry_anulado_contra.grid(row=10, column=1, sticky="ew")
        self.lista_anulados_contra = tk.Listbox(frame, height=2)
        self.lista_anulados_contra.grid(row=11, column=1, sticky="ew")

        # Bind para Delete (remover item selecionado)
        self.lista_anulados_vasco.bind("<Delete>", lambda e: self.lista_anulados_vasco.delete(self.lista_anulados_vasco.curselection()))
        self.lista_anulados_contra.bind("<Delete>", lambda e: self.lista_anulados_contra.delete(self.lista_anulados_contra.curselection()))


        self.btn_salvar = ttk.Button(frame, text="Salvar Partida", command=self.salvar_partida)
        self.btn_salvar.grid(row=12, column=0, columnspan=2, pady=10)


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
    
    def remover_gol_vasco(self, event):
        sel = self.lista_gols_vasco.curselection()
        if sel:
            self.lista_gols_vasco.delete(sel[0])

    def remover_gol_contra(self, event):
        sel = self.lista_gols_contra.curselection()
        if sel:
            self.lista_gols_contra.delete(sel[0])




    def salvar_partida(self):
        data = self.data_entry.get()
        adversario = self.adversario_var.get().strip()
        placar_vasco = self.placar_vasco.get().strip()
        placar_adv = self.placar_adversario.get().strip()
        local = self.local_var.get()
        # Gols Vasco com contagem
        nomes_vasco = list(self.lista_gols_vasco.get(0, tk.END))
        contagem_vasco = Counter(nomes_vasco)
        gols_vasco = [{"nome": nome, "gols": qtd} for nome, qtd in contagem_vasco.items()]
        # Gols Adversário com contagem
        nomes_contra = list(self.lista_gols_contra.get(0, tk.END))
        contagem_contra = Counter(nomes_contra)
        gols_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_contra.items()]


        if not (data and adversario and placar_vasco and placar_adv):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
            return

        if adversario not in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].append(adversario)
            self.adversario_entry['values'] = self.listas["clubes_adversarios"]

        salvar_listas(self.listas)

        contagem_anulados_vasco = Counter(self.lista_anulados_vasco.get(0, tk.END))
        gols_anulados_vasco = [{"nome": nome, "gols": qtd} for nome, qtd in contagem_anulados_vasco.items()]

        contagem_anulados_contra = Counter(self.lista_anulados_contra.get(0, tk.END))
        gols_anulados_contra = [{"nome": nome, "clube": adversario, "gols": qtd} for nome, qtd in contagem_anulados_contra.items()]

        jogo = {
            "data": data,
            "adversario": adversario,
            "local": local,
            "placar": {
                "vasco": int(placar_vasco),
                "adversario": int(placar_adv)
            },
            "gols_vasco": gols_vasco,
            "gols_adversario": gols_contra
        }

        salvar_jogo(jogo)
        messagebox.showinfo("Sucesso", "Partida registrada com sucesso!")
        self._limpar_formulario()

    def _limpar_formulario(self):
        self.adversario_var.set("")
        self.placar_vasco.delete(0, tk.END)
        self.placar_adversario.delete(0, tk.END)
        self.lista_gols_vasco.delete(0, tk.END)
        self.lista_gols_contra.delete(0, tk.END)
        self.entry_gol_vasco.delete(0, tk.END)
        self.entry_gol_contra.delete(0, tk.END)
        self.local_var.set("casa")
    
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
        if tipo == "vasco" and nome in self.listas["jogadores_vasco"]:
            self.listas["jogadores_vasco"].remove(nome)
            widget['values'] = self.listas["jogadores_vasco"]
        elif tipo == "contra" and nome in self.listas["jogadores_contra"]:
            self.listas["jogadores_contra"].remove(nome)
            widget['values'] = self.listas["jogadores_contra"]
        elif tipo == "clubes" and nome in self.listas["clubes_adversarios"]:
            self.listas["clubes_adversarios"].remove(nome)
            widget['values'] = self.listas["clubes_adversarios"]
        else:
            messagebox.showwarning("Não encontrado", f"'{nome}' não está na lista.")

        salvar_listas(self.listas)
        widget.set("")
    
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
    
    def _carregar_temporadas(self):
        # Criar canvas com scrollbar para frame_temporadas
        canvas = tk.Canvas(self.frame_temporadas)
        scrollbar = ttk.Scrollbar(self.frame_temporadas, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Habilita scroll com a roda do mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)


        # A partir daqui usa scroll_frame no lugar de self.frame_temporadas
        jogos = carregar_dados_jogos()
        temporadas = defaultdict(list)

        for jogo in jogos:
            ano = jogo["data"][-4:]  # Assume formato dd/mm/aaaa
            temporadas[ano].append(jogo)

        for ano in sorted(temporadas.keys(), reverse=True):
            cor_fundo = "#DFDFDF" if int(ano) % 2 != 0 else "#C0C0C0"  # cor clara para ímpar
            fonte_titulo = tkFont.Font(weight="bold")  # cria uma fonte com peso negrito
            frame_ano = tk.LabelFrame(
                scroll_frame,
                text=f"Temporada {ano}",
                bg=cor_fundo,
                font=fonte_titulo,
                padx=10,
                pady=10
            )

            frame_ano.pack(fill="x", padx=10, pady=5)

            jogos_ano = temporadas[ano]
            vitorias = empates = derrotas = 0
            gols_pro = gols_contra = 0
            anulados_vasco = anulados_contra = 0
            artilheiros = Counter()
            carrascos = Counter()

            for jogo in jogos_ano:
                local = jogo.get("local", "desconhecido").capitalize()
                placar = jogo.get("placar", {"vasco": "?", "adversario": "?"})
                linha = f"{jogo['data']} - {local} : {jogo['adversario']}: Vasco {placar['vasco']} x {placar['adversario']} {jogo['adversario']}"
                ttk.Label(frame_ano, text=linha, background=cor_fundo).pack(anchor="w")

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

            resumo = f"""
    Total de jogos: {len(jogos_ano)}
    Vitórias: {vitorias}
    Empates: {empates}
    Derrotas: {derrotas}
    Gols Pró: {gols_pro}
    Gols Contra: {gols_contra}
    Gols Anulados do Vasco: {anulados_vasco}
    Gols Anulados Contra: {anulados_contra}
            """.strip()

            for linha in resumo.splitlines():
                ttk.Label(frame_ano, text=linha,background=cor_fundo).pack(anchor="w")

            if artilheiros:
                ttk.Label(frame_ano, text="Artilheiros do Vasco:",background=cor_fundo).pack(anchor="w", pady=(5, 0))
                for nome, qtd in artilheiros.most_common():
                    ttk.Label(frame_ano, text=f" - {nome}: {qtd} gol(s)",background=cor_fundo).pack(anchor="w")

            if carrascos:
                ttk.Label(frame_ano, text="Carrascos (Gols contra o Vasco):",background=cor_fundo).pack(anchor="w", pady=(5, 0))
                for nome, qtd in carrascos.most_common():
                    ttk.Label(frame_ano, text=f" - {nome}: {qtd} gol(s)",background=cor_fundo).pack(anchor="w")


    
    def _carregar_geral(self):
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
                continue  # ignora jogos sem placar

            gols_pro += placar.get("vasco", 0)
            gols_contra += placar.get("adversario", 0)


            if placar["vasco"] > placar["adversario"]:
                vitorias += 1
            elif placar["vasco"] < placar["adversario"]:
                derrotas += 1
            else:
                empates += 1

            # Gols válidos do Vasco
            for g in jogo.get("gols_vasco", []):
                if isinstance(g, dict):
                    artilheiros[g["nome"]] += g["gols"]


            # Gols válidos contra o Vasco
            for g in jogo.get("gols_adversario", []):
                if isinstance(g, dict):
                    carrascos[g["nome"]] += g["gols"]


            # Gols anulados
            for g in jogo.get("gols_anulados", {}).get("vasco", []):
                anulados_vasco += g["gols"]
            for g in jogo.get("gols_anulados", {}).get("adversario", []):
                anulados_contra += g["gols"]

        texto = f"""
Total de jogos: {total}
Vitórias: {vitorias}
Empates: {empates}
Derrotas: {derrotas}
Gols Pró: {gols_pro}
Gols Contra: {gols_contra}
Gols Anulados do Vasco: {anulados_vasco}
Gols Anulados Contra: {anulados_contra}
        """.strip()

        frame_resumo = ttk.LabelFrame(self.frame_geral, text="Resumo Geral", padding=10)
        frame_resumo.pack(fill="x", padx=10, pady=5)
        for linha in texto.splitlines():
            ttk.Label(frame_resumo, text=linha).pack(anchor="w")

        frame_art = ttk.LabelFrame(self.frame_geral, text="Artilheiros do Vasco", padding=10)
        frame_art.pack(fill="x", padx=10, pady=5)
        for nome, qtd in artilheiros.most_common():
            ttk.Label(frame_art, text=f"{nome}: {qtd} gol(s)").pack(anchor="w")

        frame_carr = ttk.LabelFrame(self.frame_geral, text="Carrascos (Gols contra o Vasco)", padding=10)
        frame_carr.pack(fill="x", padx=10, pady=5)
        for nome, qtd in carrascos.most_common():
            ttk.Label(frame_carr, text=f"{nome}: {qtd} gol(s)").pack(anchor="w")





if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
