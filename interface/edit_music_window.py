import tkinter as tk
from tkinter import filedialog, messagebox
from services.music_service import editar_musica, excluir_musica
import os


def abrir_janela_editar(musica, ao_salvar=None):

    # musica = (id, nome, artista, album, tablatura, caminho_audio, caminho_partitura)
    id_musica     = musica[0]
    novo_audio    = musica[5] or ""
    nova_partitura = musica[6] or ""

    def selecionar_audio():

        nonlocal novo_audio

        arquivo = filedialog.askopenfilename(
            parent=janela,
            title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )

        if arquivo:
            novo_audio = arquivo
            label_audio.config(text=os.path.basename(arquivo))

        janela.grab_set()
        janela.focus_force()


    def selecionar_partitura():

        nonlocal nova_partitura

        arquivo = filedialog.askopenfilename(
            parent=janela,
            title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )

        if arquivo:
            nova_partitura = arquivo
            label_partitura.config(text=os.path.basename(arquivo))

        janela.grab_set()
        janela.focus_force()


    def salvar():

        nome      = entrada_nome.get().strip()
        artista   = entrada_artista.get().strip()
        album     = entrada_album.get().strip()
        tablatura = texto_tablatura.get("1.0", "end").strip()

        if not nome or not artista:
            messagebox.showwarning("Atenção", "Nome e Artista são obrigatórios!")
            return

        editar_musica(id_musica, nome, artista, album, tablatura, novo_audio, nova_partitura)

        messagebox.showinfo("Sucesso", f'"{nome}" atualizada com sucesso!')

        if ao_salvar:
            ao_salvar()

        janela.destroy()


    def excluir():

        nome = entrada_nome.get().strip() or "esta música"

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            f'Tem certeza que deseja excluir "{nome}"?'
        )

        if confirmar:
            excluir_musica(id_musica)
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')

            if ao_salvar:
                ao_salvar()

            janela.destroy()


    janela = tk.Toplevel()
    janela.title("Editar Música")
    janela.geometry("400x620")
    janela.grab_set()
    janela.focus_force()

    tk.Label(janela, text="Nome").pack()
    entrada_nome = tk.Entry(janela)
    entrada_nome.insert(0, musica[1] or "")
    entrada_nome.pack()

    tk.Label(janela, text="Artista").pack()
    entrada_artista = tk.Entry(janela)
    entrada_artista.insert(0, musica[2] or "")
    entrada_artista.pack()

    tk.Label(janela, text="Album").pack()
    entrada_album = tk.Entry(janela)
    entrada_album.insert(0, musica[3] or "")
    entrada_album.pack()

    # CAMPO TABLATURA ASCII

    tk.Label(janela, text="Tablatura (formato ASCII)").pack(pady=(10, 0))

    texto_tablatura = tk.Text(janela, height=10, width=40, font=("Courier", 10))
    texto_tablatura.insert("1.0", musica[4] or "")
    texto_tablatura.pack(pady=5)

    # BOTÃO AUDIO

    botao_audio = tk.Button(
        janela,
        text="Trocar Áudio",
        command=selecionar_audio
    )
    botao_audio.pack(pady=5)

    label_audio = tk.Label(
        janela,
        text=os.path.basename(musica[5]) if musica[5] else "Nenhum áudio selecionado"
    )
    label_audio.pack()

    # BOTÃO PARTITURA

    botao_partitura = tk.Button(
        janela,
        text="Trocar Partitura",
        command=selecionar_partitura
    )
    botao_partitura.pack(pady=5)

    label_partitura = tk.Label(
        janela,
        text=os.path.basename(musica[6]) if musica[6] else "Nenhuma partitura selecionada"
    )
    label_partitura.pack()

    # BOTÕES SALVAR E EXCLUIR

    botao_salvar = tk.Button(
        janela,
        text="Salvar Alterações",
        command=salvar
    )
    botao_salvar.pack(pady=(20, 5))

    botao_excluir = tk.Button(
        janela,
        text="Excluir Música",
        fg="red",
        command=excluir
    )
    botao_excluir.pack()