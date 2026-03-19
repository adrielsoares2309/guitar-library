import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from services.music_service import buscar_musica_completa, excluir_musica, listar_musicas, filtrar_musicas
from interface.add_music_window import abrir_janela_adicionar
from interface.edit_music_window import abrir_janela_editar

# ── Tema global ──────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL       = "#2B5BA8"
AZUL_HOV   = "#1E4280"
BRANCO     = "#ffffff"
FUNDO      = "#f0f0eb"
CARD_BG    = "#ffffff"
SIDEBAR_BG = "#ffffff"
TEXTO      = "#1a1a1a"
SUBTEXTO   = "#666666"
CINZA_BD   = "#e0e0e0"
LINHA_ALT  = "#fafafa"

cifra        = ""
tablatura    = ""
audio        = ""
partitura    = ""
musica_atual = None

ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "assets", "icons")


def carregar_icone(nome_arquivo, tamanho=(20, 20)):
    caminho = os.path.join(ICONS_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        return None
    try:
        img = Image.open(caminho).convert("RGBA").resize(tamanho, Image.LANCZOS)
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
    except Exception:
        return None


def iniciar_interface():

    global cifra, tablatura, audio, partitura, musica_atual

    # ════════════════════════════════════════════════════
    # JANELA PRINCIPAL
    # ════════════════════════════════════════════════════
    janela = ctk.CTk()
    janela.title("Guitar Library")
    janela.geometry("680x560")
    janela.configure(fg_color=FUNDO)
    janela.resizable(True, True)

    # ── Ícone da janela (barra de título e taskbar) ──────
    _ICO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "assets", "logo.ico")
    if os.path.exists(_ICO_PATH):
        janela.iconbitmap(_ICO_PATH)

    sidebar_visivel = False

    # ── Ícones ───────────────────────────────────────────
    ic_add       = carregar_icone("add.png",       (25, 25))
    ic_edit      = carregar_icone("edit.png",      (25, 25))
    ic_delete    = carregar_icone("delete.png",    (25, 25))
    ic_cifra     = carregar_icone("cifra.png",     (25, 25))
    ic_tablatura = carregar_icone("tablatura.png", (25, 25))
    ic_partitura = carregar_icone("partitura.png", (25, 25))
    ic_audio     = carregar_icone("audio.png",     (25, 25))

    # ════════════════════════════════════════════════════
    # SIDEBAR
    # ════════════════════════════════════════════════════
    def criar_sidebar():
        sidebar = ctk.CTkFrame(
            janela, width=170, corner_radius=0,
            fg_color=SIDEBAR_BG,
            border_width=1, border_color=CINZA_BD
        )

        ctk.CTkLabel(
            sidebar, text="MENU",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO
        ).pack(pady=(28, 16), padx=20, anchor="w")

        def btn_sidebar(texto, comando, icone_ctk=None):
            ctk.CTkButton(
                sidebar,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",
                command=comando,
                fg_color=AZUL, hover_color=AZUL_HOV,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                corner_radius=10,
                height=42,
                anchor="w"
            ).pack(fill="x", padx=12, pady=5)

        btn_sidebar("ADICIONAR", lambda: _adicionar(), ic_add)
        btn_sidebar("EDITAR",    lambda: editar(),     ic_edit)
        btn_sidebar("EXCLUIR",   lambda: excluir(),    ic_delete)
        return sidebar

    sidebar_frame = criar_sidebar()

    # ════════════════════════════════════════════════════
    # CONTEÚDO PRINCIPAL
    # ════════════════════════════════════════════════════
    frame_conteudo = ctk.CTkFrame(janela, fg_color=FUNDO, corner_radius=0)
    frame_conteudo.pack(side="left", fill="both", expand=True)

    def toggle_sidebar():
        nonlocal sidebar_visivel
        if sidebar_visivel:
            sidebar_frame.pack_forget()
            sidebar_visivel = False
        else:
            sidebar_frame.pack(side="left", fill="y", before=frame_conteudo)
            sidebar_visivel = True

    # ── Topbar ───────────────────────────────────────────
    topbar = ctk.CTkFrame(frame_conteudo, fg_color=FUNDO,
                           corner_radius=0, height=64)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    ctk.CTkButton(
        topbar, text="☰",
        command=toggle_sidebar,
        width=44, height=44,
        corner_radius=10,
        fg_color=AZUL, hover_color=AZUL_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 18, "bold")
    ).pack(side="left", padx=(14, 0), pady=10)

    frame_busca = ctk.CTkFrame(
        topbar, fg_color=BRANCO,
        corner_radius=25,
        border_width=1, border_color=CINZA_BD
    )
    frame_busca.pack(side="left", padx=14, pady=10, fill="x", expand=True)

    entrada = ctk.CTkEntry(
        frame_busca,
        placeholder_text="Buscar música...",
        border_width=0,
        fg_color=BRANCO,
        text_color=TEXTO,
        placeholder_text_color=SUBTEXTO,
        font=ctk.CTkFont("Segoe UI", 12),
        corner_radius=25,
        height=38
    )
    entrada.pack(side="left", fill="x", expand=True, padx=(14, 4), pady=2)
    entrada.bind("<Return>",     lambda e: on_busca())
    entrada.bind("<KeyRelease>", lambda e: on_busca())

    ctk.CTkButton(
        frame_busca, text="🔍",
        command=lambda: on_busca(),
        width=42, height=38,
        corner_radius=20,
        fg_color=AZUL, hover_color=AZUL_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 14)
    ).pack(side="right", padx=4, pady=2)

    # ════════════════════════════════════════════════════
    # ÁREA DO CORPO  (lista  OU  card de detalhes)
    # ════════════════════════════════════════════════════
    corpo = ctk.CTkFrame(frame_conteudo, fg_color=FUNDO, corner_radius=0)
    corpo.pack(fill="both", expand=True)

    def limpar_corpo():
        for w in corpo.winfo_children():
            w.destroy()

    # ════════════════════════════════════════════════════
    # ESTADO 1 — LISTA DE MÚSICAS
    # ════════════════════════════════════════════════════
    def mostrar_lista(musicas=None):
        global musica_atual, cifra, tablatura, audio, partitura
        musica_atual = None
        cifra = tablatura = audio = partitura = ""

        limpar_corpo()
        if musicas is None:
            musicas = listar_musicas()

        # área scrollável com cabeçalho dentro
        scroll = ctk.CTkScrollableFrame(
            corpo, fg_color=FUNDO, corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO
        )
        scroll.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(scroll, fg_color=BRANCO,
                            corner_radius=0, border_width=0)
        cab.pack(fill="x", padx=16, pady=(8, 0))

        for titulo, peso in [("NOME", True), ("ARTISTA", True),
                              ("ÁLBUM", True), ("ANO", False)]:
            ctk.CTkLabel(
                cab, text=titulo,
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                text_color=SUBTEXTO, anchor="w"
            ).pack(side="left", fill="x", expand=peso, padx=(10, 4))

        ctk.CTkFrame(scroll, fg_color=CINZA_BD,
                     height=1, corner_radius=0).pack(fill="x", padx=16, pady=(4, 2))

        if not musicas:
            ctk.CTkLabel(
                scroll,
                text="Nenhuma música cadastrada ainda.\nUse ☰ → Adicionar para começar!",
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=SUBTEXTO, justify="center"
            ).pack(pady=40)
            return

        for i, m in enumerate(musicas):
            _, nome_r, artista, album, ano, *_ = m
            cor_linha = CARD_BG if i % 2 == 0 else LINHA_ALT

            linha = ctk.CTkFrame(scroll, fg_color=cor_linha,
                                  corner_radius=6, border_width=0,
                                  cursor="hand2")
            linha.pack(fill="x", padx=16, pady=1)

            def celula(pai, texto, expand=True, bold=False):
                ctk.CTkLabel(
                    pai, text=texto or "—",
                    font=ctk.CTkFont("Segoe UI", 12, "bold" if bold else "normal"),
                    text_color=TEXTO if bold else SUBTEXTO,
                    anchor="w"
                ).pack(side="left", fill="x", expand=expand,
                       padx=(10, 4), pady=8)

            celula(linha, nome_r,                    bold=True)
            celula(linha, artista or "—")
            celula(linha, album   or "—")
            celula(linha, str(ano) if ano else "—",  expand=False)

            def _on_enter(e, f=linha):          f.configure(fg_color="#e8eef8")
            def _on_leave(e, f=linha, c=cor_linha): f.configure(fg_color=c)
            linha.bind("<Enter>", _on_enter)
            linha.bind("<Leave>", _on_leave)
            for filho in linha.winfo_children():
                filho.bind("<Enter>", _on_enter)
                filho.bind("<Leave>", _on_leave)

            # clique abre o card de detalhes
            def _abrir(e=None, musica=m):
                mostrar_card(musica)
            linha.bind("<Button-1>", _abrir)
            for filho in linha.winfo_children():
                filho.bind("<Button-1>", _abrir)

    # ════════════════════════════════════════════════════
    # ESTADO 2 — CARD DE DETALHES
    # ════════════════════════════════════════════════════
    def mostrar_card(resultado):
        global musica_atual, cifra, tablatura, audio, partitura

        musica_atual = resultado
        _, nome_r, artista, album, ano, cifra, tablatura, audio, partitura = resultado

        limpar_corpo()

        scroll_area = ctk.CTkScrollableFrame(
            corpo, fg_color=FUNDO, corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO
        )
        scroll_area.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll_area, fg_color=CARD_BG,
                             corner_radius=16,
                             border_width=1, border_color=CINZA_BD)
        card.pack(padx=24, pady=20, fill="x")

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            cab, text=nome_r.upper(),
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            text_color=TEXTO, anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            cab, text=artista or "—",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO, anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        partes = []
        if album: partes.append(album)
        if ano:   partes.append(str(ano))
        if partes:
            ctk.CTkLabel(
                cab, text="  ·  ".join(partes),
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO, anchor="w"
            ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                     corner_radius=0).pack(fill="x", padx=24, pady=(12, 8))

        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.pack(fill="x", padx=24, pady=(0, 20))

        def btn_acao(texto, cmd, icone_ctk=None, ativo=True):
            cor   = AZUL if ativo else "#cccccc"
            hover = AZUL_HOV if ativo else "#bbbbbb"
            ctk.CTkButton(
                frame_btns,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",
                command=cmd if ativo else lambda: None,
                fg_color=cor, hover_color=hover,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                corner_radius=10,
                height=42,
                anchor="w"
            ).pack(fill="x", pady=4)

        btn_acao("CIFRA",
                 lambda: abrir_viewer("Cifra", cifra),
                 ic_cifra, ativo=bool(cifra))
        btn_acao("TABLATURA",
                 lambda: abrir_viewer("Tablatura", tablatura),
                 ic_tablatura, ativo=bool(tablatura))
        btn_acao("PARTITURA",
                 visualizar_partitura,
                 ic_partitura, ativo=bool(partitura))
        btn_acao("ÁUDIO",
                 tocar_audio,
                 ic_audio, ativo=bool(audio))

    def mostrar_nao_encontrado():
        global musica_atual, cifra, tablatura, audio, partitura
        musica_atual = None
        cifra = tablatura = audio = partitura = ""

        limpar_corpo()
        card = ctk.CTkFrame(corpo, fg_color=CARD_BG,
                             corner_radius=16,
                             border_width=1, border_color=CINZA_BD)
        card.pack(padx=24, pady=20, fill="x")
        ctk.CTkLabel(
            card,
            text="Música não encontrada.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=SUBTEXTO
        ).pack(pady=30)

    # ════════════════════════════════════════════════════
    # LÓGICA DE BUSCA
    # ════════════════════════════════════════════════════
    def on_busca():
        texto = entrada.get().strip()
        if not texto:
            mostrar_lista()
            return
        resultados = filtrar_musicas(texto)
        if not resultados:
            mostrar_nao_encontrado()
        elif len(resultados) == 1:
            mostrar_card(resultados[0])
        else:
            mostrar_lista(musicas=resultados)

    # ════════════════════════════════════════════════════
    # AÇÕES DA SIDEBAR
    # ════════════════════════════════════════════════════
    def _adicionar():
        abrir_janela_adicionar()
        janela.after(300, mostrar_lista)

    def editar():
        if not musica_atual:
            messagebox.showwarning("Atenção", "Selecione ou busque uma música primeiro!")
            return
        abrir_janela_editar(musica_atual, ao_salvar=lambda: (
            entrada.delete(0, "end"),
            mostrar_lista()
        ))

    def excluir():
        if not musica_atual:
            messagebox.showwarning("Atenção", "Selecione ou busque uma música primeiro!")
            return
        nome = musica_atual[1]
        if messagebox.askyesno("Confirmar exclusão",
                               f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(musica_atual[0])
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')
            entrada.delete(0, "end")
            mostrar_lista()

    # ════════════════════════════════════════════════════
    # VIEWERS
    # ════════════════════════════════════════════════════
    def abrir_viewer(titulo, conteudo):
        jan = ctk.CTkToplevel(janela)
        jan.title(titulo)
        jan.geometry("500x440")
        jan.configure(fg_color=FUNDO)
        jan.grab_set()
        jan.focus_force()

        ctk.CTkLabel(
            jan, text=f"── {titulo.upper()} ──",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=TEXTO
        ).pack(pady=(20, 10))

        frame_txt = ctk.CTkFrame(jan, fg_color=BRANCO, corner_radius=12,
                                  border_width=1, border_color=CINZA_BD)
        frame_txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        txt = ctk.CTkTextbox(
            frame_txt,
            font=ctk.CTkFont("Courier New", 12),
            fg_color=BRANCO,
            text_color=TEXTO,
            wrap="none",
            corner_radius=12
        )
        txt.pack(fill="both", expand=True, padx=4, pady=4)
        txt.insert("1.0", conteudo)
        txt.configure(state="disabled")

    def tocar_audio():
        if not audio:
            return
        if os.path.exists(audio):
            os.startfile(audio)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de áudio não encontrado:\n{audio}")

    def visualizar_partitura():
        if not partitura:
            return
        if os.path.exists(partitura):
            os.startfile(partitura)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de partitura não encontrado:\n{partitura}")

    # ── Inicia com a lista ────────────────────────────────
    mostrar_lista()

    janela.mainloop()