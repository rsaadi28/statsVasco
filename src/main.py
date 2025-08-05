import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from collections import Counter

ARQUIVO_JOGOS = "jogos_vasco.json"
ARQUIVO_LISTAS = "listas_auxiliares.json"

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
        self.root.title("Estatísticas do Vasco - Registro de Partidas")

        self.listas = carregar_listas()

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack()

        self._criar_formulario()

    def _criar_formulario(self):
        ttk.Label(self.frame, text="Data da Partida:").grid(row=0, column=0, sticky="w")
        self.data_entry = DateEntry(self.frame, width=12, date_pattern='dd/mm/yyyy')
        self.data_entry.grid(row=0, column=1)

        ttk.Label(self.frame, text="Adversário:").grid(row=1, column=0, sticky="w")
        self.adversario_var = tk.StringVar()
        self.adversario_entry = ttk.Combobox(self.frame, textvariable=self.adversario_var)
        self.adversario_entry['values'] = self.listas["clubes_adversarios"]
        self.adversario_entry.grid(row=1, column=1)
        self.adversario_entry.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "clubes"))

        ttk.Label(self.frame, text="Placar (Vasco x Adversário):").grid(row=2, column=0, sticky="w")
        self.placar_vasco = ttk.Entry(self.frame, width=5)
        self.placar_adversario = ttk.Entry(self.frame, width=5)
        self.placar_vasco.grid(row=2, column=1, sticky="w")
        ttk.Label(self.frame, text="x").grid(row=2, column=1)
        self.placar_adversario.grid(row=2, column=1, sticky="e")

        ttk.Label(self.frame, text="Local:").grid(row=3, column=0, sticky="w")
        self.local_var = tk.StringVar(value="casa")
        ttk.Radiobutton(self.frame, text="Casa", variable=self.local_var, value="casa").grid(row=3, column=1, sticky="w")
        ttk.Radiobutton(self.frame, text="Fora", variable=self.local_var, value="fora").grid(row=3, column=1, sticky="e")

        # Gols Vasco
        ttk.Label(self.frame, text="Gols do Vasco:").grid(row=4, column=0, sticky="nw")
        self.entry_gol_vasco = ttk.Combobox(self.frame)
        self.entry_gol_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_gol_vasco.bind("<Return>", self.adicionar_gol_vasco)
        self.entry_gol_vasco.grid(row=4, column=1, sticky="ew")
        self.entry_gol_vasco.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "vasco"))
        self.lista_gols_vasco = tk.Listbox(self.frame, height=4)
        self.lista_gols_vasco.grid(row=5, column=1, sticky="ew")
        self.lista_gols_vasco.bind("<Delete>", self.remover_gol_vasco)

        # Gols adversário
        ttk.Label(self.frame, text="Gols do Adversário:").grid(row=6, column=0, sticky="nw")
        self.entry_gol_contra = ttk.Combobox(self.frame)
        self.entry_gol_contra['values'] = self.listas["jogadores_contra"]
        self.entry_gol_contra.bind("<Return>", self.adicionar_gol_contra)
        self.entry_gol_contra.grid(row=6, column=1, sticky="ew")
        self.entry_gol_contra.bind("<Button-3>", lambda e: self.mostrar_menu_contexto(e, "contra"))
        self.lista_gols_contra = tk.Listbox(self.frame, height=4)
        self.lista_gols_contra.grid(row=7, column=1, sticky="ew")
        self.lista_gols_contra.bind("<Delete>", self.remover_gol_contra)

        # Gols ANULADOS do Vasco
        ttk.Label(self.frame, text="Gols do Vasco Anulados (VAR):").grid(row=8, column=0, sticky="nw")
        self.entry_anulado_vasco = ttk.Combobox(self.frame)
        self.entry_anulado_vasco['values'] = self.listas["jogadores_vasco"]
        self.entry_anulado_vasco.bind("<Return>", self.adicionar_anulado_vasco)
        self.entry_anulado_vasco.grid(row=8, column=1, sticky="ew")
        self.lista_anulados_vasco = tk.Listbox(self.frame, height=2)
        self.lista_anulados_vasco.grid(row=9, column=1, sticky="ew")

        # Gols ANULADOS do Adversário
        ttk.Label(self.frame, text="Gols do Adversário Anulados (VAR):").grid(row=10, column=0, sticky="nw")
        self.entry_anulado_contra = ttk.Combobox(self.frame)
        self.entry_anulado_contra['values'] = self.listas["jogadores_contra"]
        self.entry_anulado_contra.bind("<Return>", self.adicionar_anulado_contra)
        self.entry_anulado_contra.grid(row=10, column=1, sticky="ew")
        self.lista_anulados_contra = tk.Listbox(self.frame, height=2)
        self.lista_anulados_contra.grid(row=11, column=1, sticky="ew")

        # Bind para Delete (remover item selecionado)
        self.lista_anulados_vasco.bind("<Delete>", lambda e: self.lista_anulados_vasco.delete(self.lista_anulados_vasco.curselection()))
        self.lista_anulados_contra.bind("<Delete>", lambda e: self.lista_anulados_contra.delete(self.lista_anulados_contra.curselection()))


        self.btn_salvar = ttk.Button(self.frame, text="Salvar Partida", command=self.salvar_partida)
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



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
