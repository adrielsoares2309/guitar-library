import customtkinter as ctk
from tkinter import filedialog, messagebox
from services.music_service import editar_musica, excluir_musica
import os

# ── Paleta de cores usada em toda a janela ───────────────
AZUL       = "#2B5BA8"   # Cor principal dos botões de ação
AZUL_HOV   = "#1E4280"   # Cor do botão ao passar o mouse (hover)
BRANCO     = "#ffffff"
FUNDO      = "#f0f0eb"   # Cor de fundo geral da janela
CARD_BG    = "#ffffff"   # Cor de fundo do card de formulário
TEXTO      = "#1a1a1a"   # Cor do texto principal
SUBTEXTO   = "#666666"   # Cor dos rótulos e placeholders
CINZA_BD   = "#e0e0e0"   # Cor das bordas e separadores


def abrir_janela_editar(musica, ao_salvar=None):
    """
    Abre uma janela modal para editar ou excluir uma música existente.

    Parâmetros:
        musica (tuple): Dados da música no formato:
                        (id, nome, artista, album, ano, cifra,
                         tablatura, caminho_audio, caminho_partitura)
        ao_salvar (callable | None): Callback opcional chamado após salvar
                                     ou excluir, para atualizar a tela principal.
    """

    # Extrai o ID e os caminhos de arquivo da tupla recebida.
    # Esses valores podem ser substituídos pelo usuário durante a edição.
    id_musica      = musica[0]
    novo_audio     = musica[7] or ""   # Caminho do áudio atual (pode ser trocado)
    nova_partitura = musica[8] or ""   # Caminho da partitura atual (pode ser trocada)

    # ════════════════════════════════════════════════════
    # JANELA
    # Cria uma janela secundária (Toplevel) modal, bloqueando a janela pai
    # enquanto estiver aberta. grab_set() impede interação com outras janelas.
    # ════════════════════════════════════════════════════
    janela = ctk.CTkToplevel()
    janela.title("Editar Música")
    janela.geometry("480x720")
    janela.configure(fg_color=FUNDO)
    janela.resizable(False, True)   # Permite redimensionar apenas verticalmente
    janela.grab_set()               # Torna a janela modal
    janela.focus_force()            # Garante que o foco vá para esta janela

    # ── Header ───────────────────────────────────────────
    # Barra superior branca com o título da janela
    header = ctk.CTkFrame(janela, fg_color=BRANCO, corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(
        header, text="Editar Música",
        font=ctk.CTkFont("Segoe UI", 16, "bold"),
        text_color=TEXTO
    ).pack(side="left", padx=24, pady=18)

    # ── Scroll ───────────────────────────────────────────
    # Frame rolável que contém todo o formulário,
    # necessário pois o conteúdo pode ultrapassar a altura da janela
    scroll = ctk.CTkScrollableFrame(
        janela, fg_color=FUNDO, corner_radius=0,
        scrollbar_button_color=CINZA_BD,
        scrollbar_button_hover_color=SUBTEXTO
    )
    scroll.pack(fill="both", expand=True)

    # ── Helpers (funções utilitárias de UI) ──────────────

    def secao(pai, titulo):
        """
        Cria um rótulo de seção em maiúsculas acima de cada campo do formulário.
        Ex: "NOME *", "ARTISTA *", "CIFRA (acordes)"
        """
        ctk.CTkLabel(
            pai, text=titulo,
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=SUBTEXTO, anchor="w"
        ).pack(anchor="w", padx=24, pady=(16, 4))

    def campo_entrada(pai, valor="", placeholder=""):
        """
        Cria e retorna um campo de entrada (Entry) de linha única.
        Se um valor inicial for fornecido, ele é inserido automaticamente.
        Usado para: nome, artista, álbum e ano.
        """
        e = ctk.CTkEntry(
            pai, placeholder_text=placeholder,
            fg_color=BRANCO, border_color=CINZA_BD, border_width=1,
            text_color=TEXTO, placeholder_text_color=SUBTEXTO,
            font=ctk.CTkFont("Segoe UI", 12), corner_radius=8, height=40
        )
        if valor:
            e.insert(0, valor)   # Preenche com o valor existente da música
        e.pack(fill="x", padx=24, pady=(0, 2))
        return e

    def campo_texto(pai, conteudo="", altura=6):
        """
        Cria e retorna um campo de texto multilinha (Textbox) com fonte monospace.
        Usado para: cifra e tablatura, onde a formatação visual importa.
        A altura é proporcional: altura * 20 pixels.
        """
        frame = ctk.CTkFrame(pai, fg_color=BRANCO, corner_radius=8,
                              border_width=1, border_color=CINZA_BD)
        frame.pack(fill="x", padx=24, pady=(0, 2))
        txt = ctk.CTkTextbox(
            frame, height=altura * 20,
            font=ctk.CTkFont("Courier New", 11),  # Fonte monospace para alinhar acordes/tabs
            fg_color=BRANCO, text_color=TEXTO,
            corner_radius=8, wrap="none"           # Sem quebra de linha automática
        )
        if conteudo:
            txt.insert("1.0", conteudo)   # Insere o conteúdo existente da música
        txt.pack(fill="both", expand=True, padx=2, pady=2)
        return txt

    def btn_arquivo(pai, icone, texto, cmd):
        """
        Cria um botão cinza para seleção de arquivo (áudio ou partitura).
        O ícone é exibido antes do texto para identificação visual rápida.
        """
        ctk.CTkButton(
            pai, text=f"  {icone}   {texto}", command=cmd,
            fg_color=CINZA_BD, hover_color="#d0d0d0",
            text_color=TEXTO, font=ctk.CTkFont("Segoe UI", 11, "bold"),
            corner_radius=8, height=38, anchor="w"
        ).pack(fill="x", padx=24, pady=(0, 4))

    # ── Card ─────────────────────────────────────────────
    # Container principal que agrupa todos os campos do formulário
    card = ctk.CTkFrame(scroll, fg_color=CARD_BG, corner_radius=16,
                         border_width=1, border_color=CINZA_BD)
    card.pack(fill="x", padx=16, pady=16)

    # ── Campos do formulário preenchidos com os dados atuais da música ──
    secao(card, "NOME  *")
    entrada_nome = campo_entrada(card, musica[1] or "", "Nome da música")

    secao(card, "ARTISTA  *")
    entrada_artista = campo_entrada(card, musica[2] or "", "Nome do artista")

    secao(card, "ÁLBUM")
    entrada_album = campo_entrada(card, musica[3] or "", "Nome do álbum")

    secao(card, "ANO")
    # Converte o inteiro do banco para string; se for None, deixa vazio
    entrada_ano = campo_entrada(card, str(musica[4]) if musica[4] else "", "Ex: 2024")

    # Linha separadora visual entre metadados e conteúdo musical
    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(16, 0))

    secao(card, "CIFRA  (acordes)")
    entrada_cifra = campo_texto(card, musica[5] or "", altura=5)

    secao(card, "TABLATURA  (ASCII)")
    entrada_tablatura = campo_texto(card, musica[6] or "", altura=6)

    # Linha separadora entre conteúdo musical e arquivos anexos
    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(16, 0))

    # ── Áudio ─────────────────────────────────────────────
    secao(card, "ÁUDIO")

    # Label que mostra o nome do arquivo atual ou mensagem padrão se não houver
    label_audio = ctk.CTkLabel(
        card,
        text=f"▶  {os.path.basename(musica[7])}" if musica[7] else "Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=TEXTO if musica[7] else SUBTEXTO, anchor="w"
    )
    label_audio.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_audio():
        """
        Abre o explorador de arquivos para o usuário escolher um novo arquivo de áudio.
        Aceita .mp3 e .wav. Ao selecionar, atualiza a variável novo_audio e o label exibido.
        nonlocal é necessário pois novo_audio foi definida no escopo pai (abrir_janela_editar).
        """
        nonlocal novo_audio
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if arquivo:
            novo_audio = arquivo
            label_audio.configure(
                text=f"▶  {os.path.basename(arquivo)}",
                text_color=TEXTO
            )
        # Reposiciona o grab e foco na janela após fechar o filedialog
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, "▶", "TROCAR ÁUDIO", selecionar_audio)

    # ── Partitura ─────────────────────────────────────────
    secao(card, "PARTITURA  (PDF)")

    # Label que mostra o nome do PDF atual ou mensagem padrão se não houver
    label_partitura = ctk.CTkLabel(
        card,
        text=f"◉  {os.path.basename(musica[8])}" if musica[8] else "Nenhum arquivo selecionado",
        font=ctk.CTkFont("Segoe UI", 10),
        text_color=TEXTO if musica[8] else SUBTEXTO, anchor="w"
    )
    label_partitura.pack(anchor="w", padx=24, pady=(0, 6))

    def selecionar_partitura():
        """
        Abre o explorador de arquivos para o usuário escolher um novo PDF de partitura.
        Ao selecionar, atualiza nova_partitura e o label exibido.
        """
        nonlocal nova_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )
        if arquivo:
            nova_partitura = arquivo
            label_partitura.configure(
                text=f"◉  {os.path.basename(arquivo)}",
                text_color=TEXTO
            )
        janela.grab_set()
        janela.focus_force()

    btn_arquivo(card, "◉", "TROCAR PARTITURA", selecionar_partitura)

    ctk.CTkFrame(card, fg_color=CINZA_BD, height=1,
                 corner_radius=0).pack(fill="x", padx=24, pady=(12, 0))

    # ── Salvar ────────────────────────────────────────────
    def salvar():
        """
        Valida os campos e persiste as alterações da música no banco de dados.

        Validações realizadas:
            - Nome e Artista são obrigatórios (campos com *)
            - Ano, se preenchido, deve ser um número com exatamente 4 dígitos

        Após salvar com sucesso:
            - Exibe mensagem de confirmação
            - Chama o callback ao_salvar (se fornecido) para atualizar a lista principal
            - Fecha a janela
        """
        nome      = entrada_nome.get().strip()
        artista   = entrada_artista.get().strip()
        album     = entrada_album.get().strip()
        ano_str   = entrada_ano.get().strip()
        cifra     = entrada_cifra.get("1.0", "end").strip()      # Lê do início ao fim do Textbox
        tablatura = entrada_tablatura.get("1.0", "end").strip()

        if not nome or not artista:
            messagebox.showwarning("Atenção", "Nome e Artista são obrigatórios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showwarning("Atenção", "Ano inválido! Use o formato: 2024")
                return
            ano = int(ano_str)

        # Chama o serviço que executa o UPDATE no banco SQLite
        editar_musica(id_musica, nome, artista, album, ano, cifra, tablatura,
                      novo_audio, nova_partitura)
        messagebox.showinfo("Sucesso", f'"{nome}" atualizada com sucesso!')
        if ao_salvar:
            ao_salvar()      # Atualiza a lista na janela principal
        janela.destroy()     # Fecha esta janela

    ctk.CTkButton(
        card, text="✔   SALVAR ALTERAÇÕES", command=salvar,
        fg_color=AZUL, hover_color=AZUL_HOV,
        text_color=BRANCO, font=ctk.CTkFont("Segoe UI", 12, "bold"),
        corner_radius=10, height=44
    ).pack(fill="x", padx=24, pady=(16, 8))

    # ── Excluir ───────────────────────────────────────────
    def excluir():
        """
        Solicita confirmação e remove permanentemente a música do banco de dados.

        Exibe um diálogo de confirmação (sim/não) antes de executar a exclusão.
        Após excluir:
            - Exibe mensagem de confirmação
            - Chama o callback ao_salvar para atualizar a lista principal
            - Fecha a janela
        """
        nome = entrada_nome.get().strip() or "esta música"
        if messagebox.askyesno("Confirmar exclusão",
                               f'Tem certeza que deseja excluir "{nome}"?'):
            excluir_musica(id_musica)       # Chama o serviço que executa o DELETE no banco
            messagebox.showinfo("Excluído", f'"{nome}" foi excluída.')
            if ao_salvar:
                ao_salvar()
            janela.destroy()

    # Botão de exclusão com cor neutra (cinza) para não chamar atenção desnecessária
    ctk.CTkButton(
        card, text="🗑   EXCLUIR MÚSICA", command=excluir,
        fg_color="#cccccc", hover_color="#bbbbbb",
        text_color=TEXTO, font=ctk.CTkFont("Segoe UI", 12, "bold"),
        corner_radius=10, height=44
    ).pack(fill="x", padx=24, pady=(0, 24))