import tkinter as tk
from tkinter import filedialog
import os

caminho_tablatura = ""
caminho_audio = ""
caminho_partitura = ""


def abrir_janela_adicionar():

    global caminho_tablatura, caminho_audio, caminho_partitura

    def selecionar_tablatura():

        global caminho_tablatura

        arquivo = filedialog.askopenfilename(
            title="Selecionar Tablatura",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if arquivo:
            caminho_tablatura = arquivo
            label_tab.config(text=os.path.basename(arquivo))


    def selecionar_audio():

        global caminho_audio

        arquivo = filedialog.askopenfilename(
            title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )

        if arquivo:
            caminho_audio = arquivo
            label_audio.config(text=os.path.basename(arquivo))


    def selecionar_partitura():

        global caminho_partitura

        arquivo = filedialog.askopenfilename(
            title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )

        if arquivo:
            caminho_partitura = arquivo
            label_partitura.config(text=os.path.basename(arquivo))


    janela = tk.Toplevel()
    janela.title("Adicionar Música")
    janela.geometry("400x350")

    tk.Label(janela, text="Nome").pack()
    entrada_nome = tk.Entry(janela)
    entrada_nome.pack()

    tk.Label(janela, text="Artista").pack()
    entrada_artista = tk.Entry(janela)
    entrada_artista.pack()

    tk.Label(janela, text="Album").pack()
    entrada_album = tk.Entry(janela)
    entrada_album.pack()

    # BOTÃO TABLATURA

    botao_tab = tk.Button(
        janela,
        text="Selecionar Tablatura",
        command=selecionar_tablatura
    )
    botao_tab.pack(pady=5)

    label_tab = tk.Label(janela, text="Nenhuma tablatura selecionada")
    label_tab.pack()

    # BOTÃO AUDIO

    botao_audio = tk.Button(
        janela,
        text="Selecionar Áudio",
        command=selecionar_audio
    )
    botao_audio.pack(pady=5)

    label_audio = tk.Label(janela, text="Nenhum áudio selecionado")
    label_audio.pack()

    # BOTÃO PARTITURA

    botao_partitura = tk.Button(
        janela,
        text="Selecionar Partitura",
        command=selecionar_partitura
    )
    botao_partitura.pack(pady=5)

    label_partitura = tk.Label(janela, text="Nenhuma partitura selecionada")
    label_partitura.pack()

    botao_salvar = tk.Button(
        janela,
        text="Salvar Música"
    )
    botao_salvar.pack(pady=20)