import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
import json
import os

ARQUIVO_DADOS = "jogos_vasco.json"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(jogos):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(jogos, f, ensure_ascii=False, indent=2)

def calcular_estatisticas(jogos):
    stats = {
        "gols_pro": 0, "gols_contra": 0,
        "vitorias": 0, "empates": 0, "derrotas": 0,
        "vitorias_casa": 0, "empates_casa": 0, "derrotas_casa": 0,
        "vitorias_fora": 0, "empates_fora": 0, "derrotas_fora": 0,
        "artilheiros": defaultdict(int),
        "goleadores_contra": defaultdict(int),
    }
    for jogo in jogos:
        casa = jogo["casa"]
        gols_vasco = int(jogo["gols_vasco"])
        gols_adv = int(jogo["gols_adv"])
        stats["gols_pro"] += gols_vasco
        stats["gols_contra"] += gols_adv
        if gols_vasco > gols_adv:
            stats["vitorias"] += 1
            stats["vitorias_casa" if casa else "vitorias_fora"] += 1
        elif gols_vasco == gols_adv:
            stats["empates"] += 1
            stats["empates_casa" if casa else "empates_fora"] += 1
        else:
            stats["derrotas"] += 1
            stats["derrotas_casa" if casa else "derrotas_fora"] += 1
        for nome in jogo["gols_vasco_jogadores"]:
            stats["artilheiros"][nome] += 1
        for nome in jogo["gols_adv_jogadores"]:
            stats["goleadores_contra"][nome] += 1
    total_jogos = len(jogos)
    stats["aproveitamento"] = round((stats["vitorias"] * 3 + stats["empates"]) / (total_jogos * 3) * 100, 2) if total_jogos else 0
    return stats

class AppEstatisticasVasco:
    def __init__(self, root):
        self.root = root
        self.root.title("Estatísticas do Vasco da Gama")
        self.jogos = carregar_dados()

        self.notebook = ttk.Notebook(root)
        self.frame_registro = ttk.Frame(self.notebook)
        self.frame_estatisticas = ttk.Frame(self.notebook)

        self.notebook.add(self.frame_registro, text="Registrar Jogo")
        self.notebook.add(self.frame_estatisticas, text="Estatísticas")
        self.notebook.pack(fill="both", expand=True)

        self.criar_aba_registro()
        self.criar_aba_estatisticas()

    def criar_aba_registro(self):
        ttk.Label(self.frame_registro, text="Data:").grid(row=0, column=0)
        self.entry_data = ttk.Entry(self.frame_registro)
        self.entry_data.grid(row=0, column=1)

        ttk.Label(self.frame_registro, text="Adversário:").grid(row=1, column=0)
        self.entry_adversario = ttk.Entry(self.frame_registro)
        self.entry_adversario.grid(row=1, column=1)

        ttk.Label(self.frame_registro, text="Gols Vasco:").grid(row=2, column=0)
        self.entry_gols_vasco = ttk.Entry(self.frame_registro)
        self.entry_gols_vasco.grid(row=2, column=1)

        ttk.Label(self.frame_registro, text="Gols Adversário:").grid(row=3, column=0)
        self.entry_gols_adv = ttk.Entry(self.frame_registro)
        self.entry_gols_adv.grid(row=3, column=1)

        ttk.Label(self.frame_registro, text="Jogadores que fizeram gols pelo Vasco (separados por vírgula):").grid(row=4, column=0, columnspan=2)
        self.entry_gols_vasco_jogadores = ttk.Entry(self.frame_registro, width=50)
        self.entry_gols_vasco_jogadores.grid(row=5, column=0, columnspan=2)

        ttk.Label(self.frame_registro, text="Jogadores que fizeram gols contra o Vasco (separados por vírgula):").grid(row=6, column=0, columnspan=2)
        self.entry_gols_adv_jogadores = ttk.Entry(self.frame_registro, width=50)
        self.entry_gols_adv_jogadores.grid(row=7, column=0, columnspan=2)

        self.var_casa = tk.BooleanVar()
        ttk.Checkbutton(self.frame_registro, text="Jogo em casa", variable=self.var_casa).grid(row=8, column=0, columnspan=2)

        ttk.Button(self.frame_registro, text="Salvar Jogo", command=self.salvar_jogo).grid(row=9, column=0, columnspan=2, pady=10)

    def salvar_jogo(self):
        jogo = {
            "data": self.entry_data.get(),
            "adversario": self.entry_adversario.get(),
            "gols_vasco": self.entry_gols_vasco.get(),
            "gols_adv": self.entry_gols_adv.get(),
            "gols_vasco_jogadores": [j.strip() for j in self.entry_gols_vasco_jogadores.get().split(",") if j.strip()],
            "gols_adv_jogadores": [j.strip() for j in self.entry_gols_adv_jogadores.get().split(",") if j.strip()],
            "casa": self.var_casa.get()
        }
        self.jogos.append(jogo)
        salvar_dados(self.jogos)
        messagebox.showinfo("Sucesso", "Jogo salvo com sucesso!")
        self.atualizar_estatisticas()

    def criar_aba_estatisticas(self):
        self.text_estatisticas = tk.Text(self.frame_estatisticas, wrap="word")
        self.text_estatisticas.pack(fill="both", expand=True)
        self.atualizar_estatisticas()

    def atualizar_estatisticas(self):
        stats = calcular_estatisticas(self.jogos)
        self.text_estatisticas.delete("1.0", tk.END)
        self.text_estatisticas.insert(tk.END, f"Gols Pró: {stats['gols_pro']}\n")
        self.text_estatisticas.insert(tk.END, f"Gols Contra: {stats['gols_contra']}\n")
        self.text_estatisticas.insert(tk.END, f"Vitórias: {stats['vitorias']} (Casa: {stats['vitorias_casa']} / Fora: {stats['vitorias_fora']})\n")
        self.text_estatisticas.insert(tk.END, f"Empates: {stats['empates']} (Casa: {stats['empates_casa']} / Fora: {stats['empates_fora']})\n")
        self.text_estatisticas.insert(tk.END, f"Derrotas: {stats['derrotas']} (Casa: {stats['derrotas_casa']} / Fora: {stats['derrotas_fora']})\n")
        self.text_estatisticas.insert(tk.END, f"Aproveitamento: {stats['aproveitamento']}%\n\n")
        self.text_estatisticas.insert(tk.END, "Artilheiros do Vasco:\n")
        for nome, gols in sorted(stats["artilheiros"].items(), key=lambda x: -x[1]):
            self.text_estatisticas.insert(tk.END, f"  {nome}: {gols} gol(s)\n")
        self.text_estatisticas.insert(tk.END, "\nJogadores que fizeram gol contra o Vasco:\n")
        for nome, gols in sorted(stats["goleadores_contra"].items(), key=lambda x: -x[1]):
            self.text_estatisticas.insert(tk.END, f"  {nome}: {gols} gol(s)\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppEstatisticasVasco(root)
    root.mainloop()
