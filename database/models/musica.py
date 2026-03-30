class Musica:
    """Representa uma música cadastrada na biblioteca."""

    def __init__(self, id, nome, artista, album=None, ano=None,
                 cifra=None, tablatura=None,
                 caminho_audio=None, link_externo=None, caminho_partitura=None,
                 youtube_id=None, favorita=None):
        self.id                = id
        self.nome              = nome
        self.artista           = artista
        self.album             = album
        self.ano               = ano
        self.cifra             = cifra
        self.tablatura         = tablatura
        self.caminho_audio     = caminho_audio
        self.link_externo      = link_externo
        self.caminho_partitura = caminho_partitura
        self.youtube_id        = youtube_id
        self.favorita          = favorita

    # ── Fábrica a partir de linha do banco ────────────────────
    @classmethod
    def from_row(cls, row):
        """Cria uma instância a partir de uma tupla retornada pelo SQLite."""
        return cls(*row)

    def __repr__(self):
        return f"<Musica id={self.id} nome={self.nome!r} artista={self.artista!r}>"
