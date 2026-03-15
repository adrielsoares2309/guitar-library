import tkinter as tk
import os
from services.music_service import buscar_musica

tablatura = ""
audio = ""

def iniciar_interface():

    global tablatura, audio

    def buscar():

        global tablatura, audio

        nome = entrada.get()

        resultado = buscar_musica(nome)

        if resultado:

            artista, album, tablatura, audio = resultado

            label_info.config(
                text=f"Artista: {artista}\nAlbum: {album}"
            )

        else:

            label_info.config(text="Música não encontrada")

    def abrir_tablatura():

        if tablatura:

            caminho = os.path.join(os.path.dirname(__file__), "..", tablatura)

            if os.path.exists(caminho):
                os.startfile(caminho)

    def tocar_audio():

        if audio:

            caminho = os.path.join(os.path.dirname(__file__), "..", audio)

            if os.path.exists(caminho):
                os.startfile(caminho)

    janela = tk.Tk()
    janela.title("Biblioteca de Músicas")
    janela.geometry("400x300")

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

    janela.mainloop()