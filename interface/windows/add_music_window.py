import customtkinter as ctk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
import os

from services.music_service import add_musica

AZUL = "#2B5BA8"
AZUL_HOV = "#1E4280"
BRANCO = "#ffffff"
FUNDO = "#f0f0eb"
CARD_BG = "#ffffff"
TEXTO = "#1a1a1a"
SUBTEXTO = "#666666"
CINZA_BD = "#e0e0e0"

caminho_audio = ""
caminho_partitura = ""


def abrir_janela_adicionar():
    global caminho_audio, caminho_partitura
    caminho_audio = ""
    caminho_partitura = ""

    janela = ctk.CTkToplevel()
    janela.title("Adicionar Musica")
    janela.geometry("480x720")
    janela.configure(fg_color=FUNDO)
    janela.resizable(False, True)
    janela.grab_set()
    janela.focus_force()

    header = ctk.CTkFrame(janela, fg_color=BRANCO, corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(
        header,
        text="Adicionar Musica",
        font=ctk.CTkFont("Segoe UI", 16, "bold"),
        text_color=TEXTO,
    ).pack(side="left", padx=24, pady=18)

    scroll = ctk.CTkScrollableFrame(
        janela,
        fg_color=FUNDO,
        corner_radius=0,
        scrollbar_button_color=CINZA_BD,
        scrollbar_button_hover_color=SUBTEXTO,
    )
    scroll.pack(fill="both", expand=True)

    def secao(pai, titulo):
        ctk.CTkLabel(
            pai,
            text=titulo,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=SUBTEXTO,
            anchor="w",
        ).pack(anchor="w", padx=24, pady=(16, 4))

    def campo_entrada(pai, placeholder=""):
        entrada = ctk.CTkEntry(
            pai,
            placeholder_text=placeholder,
            fg_color=BRANCO,
            border_color=CINZA_BD,
            border_width=1,
            text_color=TEXTO,
            placeholder_text_color=SUBTEXTO,
            font=ctk.CTkFont("Segoe UI", 12),
            corner_radius=8,
            height=40,
        )
        entrada.pack(fill="x", padx=24, pady=(0, 2))
        return entrada

    def campo_texto(pai, altura=6):
        frame = ctk.CTkFrame(
            pai,
            fg_color=BRANCO,
            corner_radius=8,
            border_width=1,
            border_color=CINZA_BD,
        )
        frame.pack(fill="x", padx=24, pady=(0, 2))
        txt = ctk.CTkTextbox(
            frame,
            height=altura * 20,
            font=ctk.CTkFont("Courier New", 11),
            fg_color=BRANCO,
            text_color=TEXTO,
            corner_radius=8,
            wrap="none",
        )
        txt.pack(fill="both", expand=True, padx=2, pady=2)
        return txt

    def btn_arquivo(pai, icone, texto, cmd):
        ctk.CTkButton(
            pai,
            text=f"  {icone}   {texto}",
            command=cmd,
            fg_color=CINZA_BD,
            hover_color="#d0d0d0",
            text_color=TEXTO,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            corner_radius=8,
            height=38,
            anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 4))

    def url_valida(url):
        if not url:
            return True
        partes = urlparse(url)
        return partes.scheme in {"http", "https"} and bool(partes.netloc)

    card = ctk.CTkFrame(
        scroll,
        fg_color=CARD_BG,
        corner_radius=16,
        border_width=1,
        border_color=CINZA_BD,
    )
    card.pack(fill="x", padx=16, pady=16)

    secao(card, "NOME  *")
    entrada_nome = campo_entrada(card, "Nome da musica")

    secao(card, "ARTISTA  *")
    entrada_artista = campo_entrada(card, "Nome do artista")

    secao(card, "ALBUM")
    entrada_album = campo_entrada(card, "Nome do album")

    secao(card, "ANO")
    entrada_ano = campo_entrada(card, "Ex: 2024")

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1, corner_radius=0).pack(
        fill="x", padx=24, pady=(16, 0)
    )

    secao(card, "CIFRA  (acordes)")
    entrada_cifra = campo_texto(card, altura=5)

    secao(card, "TABLATURA  (ASCII)")
    entrada_tablatura = campo_texto(card, altura=6)
    entrada_tablatura.insert(
        "1.0",
        "E|--0--| (Mi aguda)\n"
        "B|--2--|\n"
        "G|--2--|\n"
        "D|--2--|\n"
        "A|--0--|\n"
        "E|-----| (Mi grave)",
    )

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1, corner_radius=0).pack(
        fill="x", padx=24, pady=(16, 0)
    )

    secao(card, "AUDIO")
    label_audio = ctk.CTkLabel(
        card,
        text="Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=SUBTEXTO,
        anchor="w",
    )
    label_audio.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_audio():
        global caminho_audio
        arquivo = filedialog.askopenfilename(
            parent=janela,
            title="Selecionar Audio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")],
        )
        if arquivo:
            caminho_audio = arquivo
            label_audio.configure(text=f"> {os.path.basename(arquivo)}", text_color=TEXTO)
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, ">", "SELECIONAR AUDIO", selecionar_audio)

    secao(card, "LINK EXTERNO")
    entrada_link = campo_entrada(
        card, "https://youtube.com/... ou https://open.spotify.com/..."
    )

    secao(card, "PARTITURA  (PDF)")
    label_partitura = ctk.CTkLabel(
        card,
        text="Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=SUBTEXTO,
        anchor="w",
    )
    label_partitura.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_partitura():
        global caminho_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela,
            title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")],
        )
        if arquivo:
            caminho_partitura = arquivo
            label_partitura.configure(text=f"PDF  {os.path.basename(arquivo)}", text_color=TEXTO)
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, "PDF", "SELECIONAR PARTITURA", selecionar_partitura)

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1, corner_radius=0).pack(
        fill="x", padx=24, pady=(12, 0)
    )

    def salvar():
        nome = entrada_nome.get().strip()
        artista = entrada_artista.get().strip()
        album = entrada_album.get().strip()
        ano_str = entrada_ano.get().strip()
        cifra = entrada_cifra.get("1.0", "end").strip()
        tablatura = entrada_tablatura.get("1.0", "end").strip()
        link_externo = entrada_link.get().strip()

        if not nome or not artista:
            messagebox.showwarning("Atencao", "Nome e Artista sao obrigatorios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showwarning("Atencao", "Ano invalido! Use o formato: 2024")
                return
            ano = int(ano_str)

        if link_externo and not url_valida(link_externo):
            messagebox.showwarning(
                "Atencao",
                "Informe uma URL valida, como um link do YouTube ou Spotify.",
            )
            return

        add_musica(
            nome,
            artista,
            album,
            ano,
            cifra,
            tablatura,
            caminho_audio,
            link_externo,
            caminho_partitura,
        )
        messagebox.showinfo("Sucesso", f'"{nome}" salva com sucesso!')
        janela.destroy()

    ctk.CTkButton(
        card,
        text="SALVAR MUSICA",
        command=salvar,
        fg_color=AZUL,
        hover_color=AZUL_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 12, "bold"),
        corner_radius=10,
        height=44,
    ).pack(fill="x", padx=24, pady=(16, 24))
