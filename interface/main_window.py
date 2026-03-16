import tkinter as tk
import os
from services.music_service import buscar_musica, buscar_musica_completa
from interface.add_music_window import abrir_janela_adicionar
from interface.edit_music_window import abrir_janela_editar

tablatura = ""
audio = ""
partitura = ""
musica_atual = None


def iniciar_interface():

    global tablatura, audio, partitura, musica_atual

    def buscar():

        global tablatura, audio, partitura, musica_atual

        nome = entrada.get()
        resultado = buscar_musica_completa(nome)

        if resultado:

            musica_atual = resultado
            _, _, artista, album, tablatura, audio, partitura = resultado

            label_info.config(
                text=f"Artista: {artista}\nAlbum: {album}"
            )

        else:

            musica_atual = None
            label_info.config(text="Música não encontrada")

    def abrir_tablatura():

        if not tablatura:
            return

        janela_tab = tk.Toplevel()
        janela_tab.title("Tablatura")
        janela_tab.geometry("400x300")

        texto = tk.Text(janela_tab, font=("Courier", 12), state="normal")
        texto.insert("1.0", tablatura)
        texto.config(state="disabled")
        texto.pack(expand=True, fill="both", padx=10, pady=10)

    def tocar_audio():

        if audio:

            caminho = os.path.join(os.path.dirname(__file__), "..", audio)

            if os.path.exists(caminho):
                os.startfile(caminho)

    def visualizar_partitura():

        if partitura:

            caminho = os.path.join(os.path.dirname(__file__), "..", partitura)

            if os.path.exists(caminho):
                os.startfile(caminho)

    def editar():

        if not musica_atual:
            return

        def ao_salvar():
            buscar()

        abrir_janela_editar(musica_atual, ao_salvar=ao_salvar)

    janela = tk.Tk()
    janela.title("Biblioteca de Músicas")
    janela.geometry("400x430")

    entrada = tk.Entry(janela, width=30)
    entrada.pack(pady=10)

    botao_buscar = tk.Button(janela, text="Buscar", command=buscar)
    botao_buscar.pack()

    label_info = tk.Label(janela, text="")
    label_info.pack(pady=10)

    botao_tab = tk.Button(janela, text="Abrir Tablatura", command=abrir_tablatura)
    botao_tab.pack(pady=5)

    botao_audio = tk.Button(janela, text="Tocar Áudio", command=tocar_audio)
    botao_audio.pack(pady=5)

    botao_partitura = tk.Button(janela, text="Visualizar Partitura", command=visualizar_partitura)
    botao_partitura.pack(pady=5)

    botao_editar = tk.Button(janela, text="Editar Música", command=editar)
    botao_editar.pack(pady=5)

    botao_adicionar = tk.Button(janela, text="Adicionar Música", command=abrir_janela_adicionar)
    botao_adicionar.pack(pady=10)

    janela.mainloop()