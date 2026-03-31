import customtkinter as ctk
from tkinter import messagebox # Para exibir mensagens (alertas, confirmações, etc.)
from PIL import Image # Para manipular imagens (ícones)
import os # Manipulação de arquivos e caminhos
import webbrowser # Para abrir links no navegador

from services.music_service import excluir_musica, listar_musicas, filtrar_musicas
from interface.windows.add_music_window import abrir_janela_adicionar
from interface.windows.edit_music_window import abrir_janela_editar

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL = "#2B5BA8"
AZUL_HOV = "#1E4280"
BRANCO = "#ffffff"
FUNDO = "#f0f0eb"
CARD_BG = "#ffffff"
SIDEBAR_BG = "#ffffff"
TEXTO = "#1a1a1a"
SUBTEXTO = "#666666"
CINZA_BD = "#e0e0e0"
LINHA_ALT = "#fafafa"

# VARIÁVEIS GLOBAIS (ESTADO DA UI)
cifra = ""
tablatura = ""
audio = ""
link_externo = ""
partitura = ""
musica_atual = None

# Caminho da pasta de ícones
ICONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "icons")

# CARREGAMENTO DE ÍCONES
def carregar_icone(nome_arquivo, tamanho=(20, 20)):
    caminho = os.path.join(ICONS_DIR, nome_arquivo)
    # Se não existir, retorna None
    if not os.path.exists(caminho):
        return None
    try:
        # Abre, converte e redimensiona a imagem
        img = Image.open(caminho).convert("RGBA").resize(tamanho, Image.LANCZOS)
        # Converte para formato compatível com CustomTkinter
        return ctk.CTkImage(light_image=img, dark_image=img, size=tamanho)
    except Exception:
        return None

# FUNÇÃO PRINCIPAL DA INTERFACE
def iniciar_interface():
    global cifra, tablatura, audio, link_externo, partitura, musica_atual

    # Cria a janela principal
    janela = ctk.CTk()
    janela.title("Gralha")
    janela.geometry("680x560")
    janela.configure(fg_color=FUNDO)
    janela.resizable(True, True)

    # Define ícone da janela (se existir)
    icone_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "logo.ico")
    if os.path.exists(icone_path):
        janela.iconbitmap(icone_path)

    # Controle de exibição da sidebar
    sidebar_visivel = False

    # Carrega ícones
    ic_add = carregar_icone("add.png", (25, 25))
    ic_edit = carregar_icone("edit.png", (25, 25))
    ic_delete = carregar_icone("delete.png", (25, 25))
    ic_cifra = carregar_icone("cifra.png", (25, 25))
    ic_tablatura = carregar_icone("tablatura.png", (25, 25))
    ic_partitura = carregar_icone("partitura.png", (25, 25))
    ic_audio = carregar_icone("audio.png", (25, 25))

    # SIDEBAR (MENU LATERAL)
    def criar_sidebar():
        sidebar = ctk.CTkFrame(
            janela,
            width=170,
            corner_radius=0,
            fg_color=SIDEBAR_BG,
            border_width=1,
            border_color=CINZA_BD,
        )
        # Título do menu
        ctk.CTkLabel(
            sidebar,
            text="MENU",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO,
        ).pack(pady=(28, 16), padx=20, anchor="w")

        # Função para criar botões do menu
        def btn_sidebar(texto, comando, icone_ctk=None):
            ctk.CTkButton(
                sidebar,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",
                command=comando,
                fg_color=AZUL,
                hover_color=AZUL_HOV,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                corner_radius=10,
                height=42,
                anchor="w",
            ).pack(fill="x", padx=12, pady=5)

        # Botões do menu
        btn_sidebar("ADICIONAR", lambda: adicionar(), ic_add)
        btn_sidebar("EDITAR", lambda: editar(), ic_edit)
        btn_sidebar("EXCLUIR", lambda: excluir(), ic_delete)
        return sidebar

    sidebar_frame = criar_sidebar()

    # ÁREA PRINCIPAL
    frame_conteudo = ctk.CTkFrame(janela, fg_color=FUNDO, corner_radius=0)
    frame_conteudo.pack(side="left", fill="both", expand=True)

    # Mostra/oculta sidebar
    def toggle_sidebar():
        nonlocal sidebar_visivel
        if sidebar_visivel:
            sidebar_frame.pack_forget()
            sidebar_visivel = False
        else:
            sidebar_frame.pack(side="left", fill="y", before=frame_conteudo)
            sidebar_visivel = True

    # BOTÃO DE ABRIR A SIDEBAR
    topbar = ctk.CTkFrame(frame_conteudo, fg_color=FUNDO, corner_radius=0, height=64)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    ctk.CTkButton(
        topbar,
        text="☰",
        command=toggle_sidebar,
        width=44,
        height=44,
        corner_radius=10,
        fg_color=AZUL,
        hover_color=AZUL_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 18, "bold"),
    ).pack(side="left", padx=(14, 0), pady=10)

    # BARRA DE BUSCA
    frame_busca = ctk.CTkFrame(
        topbar,
        fg_color=BRANCO,
        corner_radius=25,
        border_width=1,
        border_color=CINZA_BD,
    )
    frame_busca.pack(side="left", padx=14, pady=10, fill="x", expand=True)

    entrada = ctk.CTkEntry(
        frame_busca,
        placeholder_text="Buscar musica...",
        border_width=0,
        fg_color=BRANCO,
        text_color=TEXTO,
        placeholder_text_color=SUBTEXTO,
        font=ctk.CTkFont("Segoe UI", 12),
        corner_radius=25,
        height=38,
    )
    #Barra de pesquisa dinâmica
    entrada.pack(side="left", fill="x", expand=True, padx=(14, 4), pady=2)
    entrada.bind("<Return>", lambda e: on_busca())
    entrada.bind("<KeyRelease>", lambda e: on_busca())

    ctk.CTkButton(
        frame_busca,
        text="Buscar",
        command=on_busca if 'on_busca' in locals() else None,
        width=72,
        height=38,
        corner_radius=20,
        fg_color=AZUL,
        hover_color=AZUL_HOV,
        text_color=BRANCO,
        font=ctk.CTkFont("Segoe UI", 12, "bold"),
    ).pack(side="right", padx=4, pady=2)
    
    # CORPO PRINCIPAL
    corpo = ctk.CTkFrame(frame_conteudo, fg_color=FUNDO, corner_radius=0)
    corpo.pack(fill="both", expand=True)
    
    # Limpa o conteúdo da tela
    def limpar_corpo():
        for widget in corpo.winfo_children():
            widget.destroy()

    # LISTA DE MÚSICAS
    def mostrar_lista(musicas=None):
        global musica_atual, cifra, tablatura, audio, link_externo, partitura
        musica_atual = None
        cifra = tablatura = audio = link_externo = partitura = ""

        limpar_corpo()
        # Se não receber lista, busca todas do banco
        if musicas is None:
            musicas = listar_musicas()

        # Scroll para lista
        scroll = ctk.CTkScrollableFrame(
            corpo,
            fg_color=FUNDO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        scroll.pack(fill="both", expand=True)

        cab = ctk.CTkFrame(scroll, fg_color=BRANCO, corner_radius=0, border_width=0)
        cab.pack(fill="x", padx=16, pady=(8, 0))

        for titulo, expandir in [("NOME", True), ("ARTISTA", True), ("ALBUM", True), ("ANO", False)]:
            ctk.CTkLabel(
                cab,
                text=titulo,
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(side="left", fill="x", expand=expandir, padx=(10, 4))

        ctk.CTkFrame(scroll, fg_color=CINZA_BD, height=1, corner_radius=0).pack(fill="x", padx=16, pady=(4, 2))
        
        # Caso não tenha músicas
        if not musicas:
            ctk.CTkLabel(
                scroll,
                text="Nenhuma musica cadastrada ainda.\nUse o menu para adicionar.",
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=SUBTEXTO,
                justify="center",
            ).pack(pady=40)
            return
        
        # Pega cada música do banco e transforma em uma linha clicável na tela
        for i, musica in enumerate(musicas):
            _, nome_r, artista_r, album_r, ano_r, *_ = musica
            cor_linha = CARD_BG if i % 2 == 0 else LINHA_ALT

            linha = ctk.CTkFrame(scroll, fg_color=cor_linha, corner_radius=6, border_width=0, cursor="hand2")
            linha.pack(fill="x", padx=16, pady=1)

            def celula(pai, texto, expandir=True, bold=False):
                ctk.CTkLabel(
                    pai,
                    text=texto or "-",
                    font=ctk.CTkFont("Segoe UI", 12, "bold" if bold else "normal"),
                    text_color=TEXTO if bold else SUBTEXTO,
                    anchor="w",
                ).pack(side="left", fill="x", expand=expandir, padx=(10, 4), pady=8)

            celula(linha, nome_r, bold=True)
            celula(linha, artista_r)
            celula(linha, album_r)
            celula(linha, str(ano_r) if ano_r else "-", expandir=False)

            def on_enter(e, frame=linha):
                frame.configure(fg_color="#e8eef8")

            def on_leave(e, frame=linha, cor=cor_linha):
                frame.configure(fg_color=cor)

            linha.bind("<Enter>", on_enter)
            linha.bind("<Leave>", on_leave)
            for filho in linha.winfo_children():
                filho.bind("<Enter>", on_enter)
                filho.bind("<Leave>", on_leave)

            def abrir_musica(e=None, item=musica):
                mostrar_card(item)

            linha.bind("<Button-1>", abrir_musica)
            for filho in linha.winfo_children():
                filho.bind("<Button-1>", abrir_musica)
    # Responsável por mostrar os detalhes de uma música selecionada
    def mostrar_card(resultado):
        global musica_atual, cifra, tablatura, audio, link_externo, partitura

        musica_atual = resultado
        _, nome_r, artista_r, album_r, ano_r, cifra, tablatura, audio, link_externo, partitura = resultado

        limpar_corpo()

        #Cria scroll
        scroll_area = ctk.CTkScrollableFrame(
            corpo,
            fg_color=FUNDO,
            corner_radius=0,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        scroll_area.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll_area, fg_color=CARD_BG, corner_radius=16, border_width=1, border_color=CINZA_BD)
        card.pack(padx=24, pady=20, fill="x")

        cab = ctk.CTkFrame(card, fg_color="transparent")
        cab.pack(fill="x", padx=24, pady=(20, 6))

        ctk.CTkLabel(
            cab,
            text=(nome_r or "").upper(),
            font=ctk.CTkFont("Segoe UI", 16, "bold"),
            text_color=TEXTO,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            cab,
            text=artista_r or "-",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=SUBTEXTO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        partes = []
        if album_r:
            partes.append(album_r)
        if ano_r:
            partes.append(str(ano_r))
        if partes:
            ctk.CTkLabel(
                cab,
                text="  .  ".join(partes),
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(card, fg_color=CINZA_BD, height=1, corner_radius=0).pack(fill="x", padx=24, pady=(12, 8))

        frame_btns = ctk.CTkFrame(card, fg_color="transparent")
        frame_btns.pack(fill="x", padx=24, pady=(0, 20))

        def btn_acao(texto, cmd, icone_ctk=None, ativo=True):
            cor = AZUL if ativo else "#cccccc"
            hover = AZUL_HOV if ativo else "#bbbbbb"
            ctk.CTkButton(
                frame_btns,
                text=f"  {texto}",
                image=icone_ctk,
                compound="left",
                command=cmd if ativo else (lambda: None),
                fg_color=cor,
                hover_color=hover,
                text_color=BRANCO,
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                corner_radius=10,
                height=42,
                anchor="w",
            ).pack(fill="x", pady=4)
        
        #Botões de ação após abrir a música
        btn_acao("CIFRA", lambda: abrir_viewer("Cifra", cifra), ic_cifra, ativo=bool(cifra)) 
        btn_acao("TABLATURA", lambda: abrir_viewer("Tablatura", tablatura), ic_tablatura, ativo=bool(tablatura))
        btn_acao("PARTITURA", visualizar_partitura, ic_partitura, ativo=bool(partitura))
        btn_acao("AUDIO", tocar_audio, ic_audio, ativo=bool(audio))
        btn_acao("LINK EXTERNO", abrir_link_externo, ativo=bool(link_externo))

    def mostrar_nao_encontrado():
        global musica_atual, cifra, tablatura, audio, link_externo, partitura
        musica_atual = None
        cifra = tablatura = audio = link_externo = partitura = ""

        limpar_corpo()
        card = ctk.CTkFrame(corpo, fg_color=CARD_BG, corner_radius=16, border_width=1, border_color=CINZA_BD)
        card.pack(padx=24, pady=20, fill="x")
        ctk.CTkLabel(
            card,
            text="Musica nao encontrada.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=SUBTEXTO,
        ).pack(pady=30)

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

    for widget in frame_busca.winfo_children():
        if isinstance(widget, ctk.CTkButton):
            widget.configure(command=on_busca)
            break

    def adicionar():
        abrir_janela_adicionar()
        janela.after(300, mostrar_lista)

    #Função de abrir a janela de editar a música
    def editar():
        if not musica_atual:
            messagebox.showwarning("Atencao", "Selecione ou busque uma musica primeiro!")
            return
        abrir_janela_editar(
            musica_atual,
            ao_salvar=lambda: (
                entrada.delete(0, "end"),
                mostrar_lista(),
            ),
        )

    #Função de abrir a janela de excluir a música
    def excluir():
        if not musica_atual:
            messagebox.showwarning("Atencao", "Selecione ou busque uma musica primeiro!")
            return
        nome = musica_atual[1]
        if messagebox.askyesno("Confirmar exclusao", f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(musica_atual[0])
            messagebox.showinfo("Excluido", f'"{nome}" foi excluida.')
            entrada.delete(0, "end")
            mostrar_lista()

    #Função para abrir janela pop up de 
    def abrir_viewer(titulo, conteudo):
        viewer = ctk.CTkToplevel(janela)
        viewer.title(titulo)
        viewer.geometry("500x440")
        viewer.configure(fg_color=FUNDO)
        viewer.grab_set()
        viewer.focus_force()

        ctk.CTkLabel(
            viewer,
            text=titulo.upper(),
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            text_color=TEXTO,
        ).pack(pady=(20, 10))

        frame_txt = ctk.CTkFrame(viewer, fg_color=BRANCO, corner_radius=12, border_width=1, border_color=CINZA_BD)
        frame_txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        txt = ctk.CTkTextbox(
            frame_txt,
            font=ctk.CTkFont("Courier New", 12),
            fg_color=BRANCO,
            text_color=TEXTO,
            wrap="none",
            corner_radius=12,
        )
        txt.pack(fill="both", expand=True, padx=4, pady=4)
        txt.insert("1.0", conteudo)
        txt.configure(state="disabled")

    #Função para tocar o audio 
    def tocar_audio():
        if not audio:
            return
        if os.path.exists(audio):
            os.startfile(audio)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de audio nao encontrado:\n{audio}")

    # Função para abrir link cadastrados
    def abrir_link_externo():
        if not link_externo:
            return
        try:
            webbrowser.open(link_externo)
        except Exception:
            messagebox.showwarning("Aviso", f"Nao foi possivel abrir o link:\n{link_externo}")

    # Função para abrir o pdf da partitura 
    def visualizar_partitura():
        if not partitura:
            return
        if os.path.exists(partitura):
            os.startfile(partitura)
        else:
            messagebox.showwarning("Aviso", f"Arquivo de partitura nao encontrado:\n{partitura}")

    mostrar_lista() #busca as músicas no banco e cria a lista na tela
    janela.mainloop() #mantém a janela aberta
