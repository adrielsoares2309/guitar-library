import customtkinter as ctk


AZUL = "#2B5BA8"
AZUL_HOV = "#1E4280"
BRANCO = "#ffffff"
FUNDO = "#f0f0eb"
TEXTO = "#1a1a1a"
SUBTEXTO = "#666666"
CINZA_BD = "#e0e0e0"


class PlaylistWidget(ctk.CTkFrame):
    def __init__(self, master, on_open_playlist, on_create_playlist):
        super().__init__(master, fg_color=FUNDO, corner_radius=0)
        self.on_open_playlist = on_open_playlist
        self.on_create_playlist = on_create_playlist
        self.playlists = []

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(8, 4))

        ctk.CTkLabel(
            header,
            text="PLAYLISTS",
            font=ctk.CTkFont("Segoe UI", 10, "bold"),
            text_color=SUBTEXTO,
        ).pack(side="left")

        self.list_frame = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            fg_color=FUNDO,
            corner_radius=0,
            height=128,
            scrollbar_button_color=CINZA_BD,
            scrollbar_button_hover_color=SUBTEXTO,
        )
        self.list_frame.pack(fill="x", padx=8, pady=(0, 10))

        self.render()

    def set_playlists(self, playlists):
        self.playlists = playlists or []
        self.render()

    def render(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        ctk.CTkButton(
            self.list_frame,
            text="+",
            command=self.on_create_playlist,
            width=58,
            height=86,
            corner_radius=14,
            fg_color=AZUL,
            hover_color=AZUL_HOV,
            text_color=BRANCO,
            font=ctk.CTkFont("Segoe UI", 28, "bold"),
        ).pack(side="left", padx=(8, 10), pady=10)

        if not self.playlists:
            ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma playlist criada ainda.",
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=SUBTEXTO,
            ).pack(side="left", padx=8, pady=36)
            return

        for playlist in self.playlists:
            total_musicas = getattr(playlist, "total_musicas", 0)
            card = ctk.CTkFrame(
                self.list_frame,
                width=132,
                height=86,
                fg_color=BRANCO,
                corner_radius=14,
                border_width=1,
                border_color=CINZA_BD,
                cursor="hand2",
            )
            card.pack(side="left", padx=6, pady=10)
            card.pack_propagate(False)

            ctk.CTkLabel(
                card,
                text=playlist.nome,
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=TEXTO,
                anchor="w",
            ).pack(fill="x", padx=12, pady=(16, 4))

            ctk.CTkLabel(
                card,
                text=f"{total_musicas} musica(s)",
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=SUBTEXTO,
                anchor="w",
            ).pack(fill="x", padx=12)

            def abrir_playlist(event=None, item=playlist):
                self.on_open_playlist(item)

            def on_enter(event, frame=card):
                frame.configure(border_color=AZUL)

            def on_leave(event, frame=card):
                frame.configure(border_color=CINZA_BD)

            card.bind("<Button-1>", abrir_playlist)
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            for child in card.winfo_children():
                child.bind("<Button-1>", abrir_playlist)
                child.bind("<Enter>", on_enter)
                child.bind("<Leave>", on_leave)
