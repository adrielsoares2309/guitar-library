class Playlist:
    """Representa uma playlist criada pelo usuário."""

    def __init__(self, id, nome, descricao=None, criado_em=None):
        self.id         = id
        self.nome       = nome
        self.descricao  = descricao
        self.criado_em  = criado_em
        self.musicas    = []   # lista de objetos Musica (populada sob demanda)

    # ── Fábrica a partir de linha do banco ────────────────────
    @classmethod
    def from_row(cls, row):
        """Cria uma instância a partir de uma tupla retornada pelo SQLite.
        
        Espera colunas: (id, nome, descricao, criado_em)
        """
        return cls(*row)

    def __repr__(self):
        return f"<Playlist id={self.id} nome={self.nome!r}>"