import tkinter as tk
from tkinter import filedialog, messagebox
from services.music_service import add_musica
import os

BG        = "#0a0a0a"
BG2       = "#141414"
BG3       = "#1e1e1e"
BRANCO    = "#f0f0f0"
BRANCO2   = "#cccccc"
CINZA     = "#666666"
CINZA2    = "#333333"
FONTE     = ("Courier New", 10)
FONTE_T   = ("Courier New", 11, "bold")
FONTE_TIT = ("Courier New", 16, "bold")

caminho_audio     = ""
caminho_partitura = ""


def estilo_botao(btn):
    btn.config(bg=BRANCO, fg=BG, relief="flat",
               activebackground=BRANCO2, activeforeground=BG,
               cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=BRANCO2))
    btn.bind("<Leave>", lambda e: btn.config(bg=BRANCO))


def estilo_botao_secundario(btn):
    btn.config(bg=CINZA2, fg=BRANCO, relief="flat",
               activebackground=CINZA, activeforeground=BRANCO,
               cursor="hand2", font=FONTE_T, bd=0, padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.config(bg=CINZA))
    btn.bind("<Leave>", lambda e: btn.config(bg=CINZA2))


def estilo_entrada(entry):
    entry.config(bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                 relief="flat", font=FONTE_T, bd=0)


def abrir_janela_adicionar():

    global caminho_audio, caminho_partitura
    caminho_audio = ""
    caminho_partitura = ""

    def selecionar_audio():
        global caminho_audio
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Áudio",
            filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
        )
        if arquivo:
            caminho_audio = arquivo
            label_audio.config(text=f"▶  {os.path.basename(arquivo)}", fg=BRANCO)
        janela.grab_set()
        janela.focus_force()

    def selecionar_partitura():
        global caminho_partitura
        arquivo = filedialog.askopenfilename(
            parent=janela, title="Selecionar Partitura",
            filetypes=[("PDF files", "*.pdf")]
        )
        if arquivo:
            caminho_partitura = arquivo
            label_partitura.config(text=f"◉  {os.path.basename(arquivo)}", fg=BRANCO)
        janela.grab_set()
        janela.focus_force()

    def salvar():
        nome      = entrada_nome.get().strip()
        artista   = entrada_artista.get().strip()
        album     = entrada_album.get().strip()
        ano_str   = entrada_ano.get().strip()
        tablatura = texto_tablatura.get("1.0", "end").strip()

        if not nome or not artista:
            messagebox.showwarning("Atenção", "Nome e Artista são obrigatórios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                messagebox.showwarning("Atenção", "Ano inválido! Use o formato: 2024")
                return
            ano = int(ano_str)

        add_musica(nome, artista, album, ano, tablatura, caminho_audio, caminho_partitura)
        messagebox.showinfo("Sucesso", f'"{nome}" salva com sucesso!')
        janela.destroy()

    # ── Janela com scroll ────────────────────────────────
    janela = tk.Toplevel()
    janela.title("Adicionar Música")
    janela.geometry("440x600")
    janela.configure(bg=BG)
    janela.resizable(False, True)
    janela.grab_set()
    janela.focus_force()

    canvas = tk.Canvas(janela, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(janela, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas, bg=BG)
    frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    def atualizar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(frame_id, width=canvas.winfo_width())

    frame.bind("<Configure>", atualizar_scroll)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def lbl(texto):
        tk.Label(frame, text=texto, bg=BG, fg=CINZA,
                 font=("Courier New", 8, "bold")).pack(anchor="w", padx=40, pady=(10, 2))

    def entrada_campo(valor=""):
        e = tk.Entry(frame, width=36)
        estilo_entrada(e)
        e.insert(0, valor)
        e.pack(padx=40, ipady=6, fill="x")
        return e

    # ── Conteúdo ─────────────────────────────────────────
    tk.Label(frame, text="ADICIONAR MÚSICA", bg=BG, fg=BRANCO,
             font=FONTE_TIT).pack(pady=(24, 2))
    tk.Label(frame, text="─" * 36, bg=BG, fg=CINZA2).pack(pady=(0, 8))

    lbl("NOME")
    entrada_nome = entrada_campo()

    lbl("ARTISTA")
    entrada_artista = entrada_campo()

    lbl("ÁLBUM")
    entrada_album = entrada_campo()

    lbl("ANO")
    entrada_ano = entrada_campo()

    lbl("TABLATURA (ASCII)")
    exemplo = (
        "E|--0--| (Mi aguda)\n"
        "B|--2--|\n"
        "G|--2--|\n"
        "D|--2--|\n"
        "A|--0--|\n"
        "E|-----| (Mi grave)"
    )
    texto_tablatura = tk.Text(frame, height=7, width=36,
                               font=("Courier New", 10),
                               bg=BG2, fg=BRANCO, insertbackground=BRANCO,
                               relief="flat", bd=0, padx=8, pady=8)
    texto_tablatura.insert("1.0", exemplo)
    texto_tablatura.pack(padx=40, fill="x")

    tk.Label(frame, text="─" * 36, bg=BG, fg=CINZA2).pack(pady=(12, 6))

    btn_audio = tk.Button(frame, text="♪  SELECIONAR ÁUDIO", command=selecionar_audio)
    estilo_botao_secundario(btn_audio)
    btn_audio.pack(padx=40, pady=(0, 4), fill="x")

    label_audio = tk.Label(frame, text="Nenhum áudio selecionado",
                            bg=BG, fg=CINZA, font=FONTE)
    label_audio.pack(padx=40, anchor="w")

    btn_partitura = tk.Button(frame, text="◉  SELECIONAR PARTITURA", command=selecionar_partitura)
    estilo_botao_secundario(btn_partitura)
    btn_partitura.pack(padx=40, pady=(8, 4), fill="x")

    label_partitura = tk.Label(frame, text="Nenhuma partitura selecionada",
                                bg=BG, fg=CINZA, font=FONTE)
    label_partitura.pack(padx=40, anchor="w")

    tk.Label(frame, text="─" * 36, bg=BG, fg=CINZA2).pack(pady=(12, 6))

    btn_salvar = tk.Button(frame, text="✔  SALVAR MÚSICA", command=salvar)
    estilo_botao(btn_salvar)
    btn_salvar.pack(padx=40, pady=(0, 30), fill="x")