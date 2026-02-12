import tkinter as tk
from tkinter import messagebox

from main import App


class DemoApp(App):
    MSG_LICENCA = (
        "Versão de demonstração.\n\n"
        "Compre a licença para desbloquear todos os recursos do app."
    )

    def __init__(self, root):
        super().__init__(root)
        self.root.title("Estatísticas do Vasco (Demonstração)")

    def _bloquear_criacao(self):
        messagebox.showinfo("Recurso bloqueado", self.MSG_LICENCA)

    # Bloqueia criação/edição de jogo registrado
    def salvar_partida(self):
        self._bloquear_criacao()

    # Bloqueia inclusão de novos jogos futuros via JSON
    def _importar_jogos_futuros(self):
        self._bloquear_criacao()

    # Bloqueia inclusão manual de jogo futuro
    def _adicionar_jogo_futuro_manual(self):
        self._bloquear_criacao()


if __name__ == "__main__":
    root = tk.Tk()
    app = DemoApp(root)
    root.mainloop()
