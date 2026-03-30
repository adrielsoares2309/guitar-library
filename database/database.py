import sqlite3
import os


def get_caminho_banco():
    """Retorna o caminho absoluto do banco SQLite na pasta AppData do usuário."""
    pasta = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Gralha")
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, "musicas.db")


def conectar_banco():
    """Abre e retorna uma conexão com o banco. Ativa suporte a FK."""
    conn = sqlite3.connect(get_caminho_banco())
    conn.execute("PRAGMA foreign_keys = ON")   # garante integridade relacional
    return conn


def _garantir_colunas_musicas(cursor):
    """Adiciona novas colunas da tabela sem perder dados existentes."""
    cursor.execute("PRAGMA table_info(musicas)")
    colunas_existentes = {coluna[1] for coluna in cursor.fetchall()}

    novas_colunas = {
        "link_externo": "TEXT",
        "youtube_id": "TEXT",
        "favorita": "BOOLEAN DEFAULT 0",
    }

    for nome_coluna, definicao in novas_colunas.items():
        if nome_coluna not in colunas_existentes:
            cursor.execute(f"ALTER TABLE musicas ADD COLUMN {nome_coluna} {definicao}")


# ─────────────────────────────────────────────────────────────
# CRIAÇÃO DE TABELAS
# ─────────────────────────────────────────────────────────────

def criar_tabela():
    """
    Cria (se não existirem) todas as tabelas do banco:
      • musicas             – biblioteca de músicas
      • playlists           – coleções criadas pelo usuário
      • playlist_musicas    – relacionamento N:N entre playlists e músicas
    """
    conn = conectar_banco()
    cursor = conn.cursor()

    # ── 1. Músicas ────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS musicas (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT    NOT NULL,
            artista          TEXT    NOT NULL,
            album            TEXT,
            ano              INTEGER,
            cifra            TEXT,
            tablatura        TEXT,
            caminho_audio    TEXT,
            link_externo     TEXT,
            caminho_partitura TEXT,
            youtube_id       TEXT,
            favorita         BOOLEAN DEFAULT 0
        )
    """)

    _garantir_colunas_musicas(cursor)

    # ── 2. Playlists ──────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            descricao   TEXT,
            criado_em   TEXT    DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # ── 3. Relacionamento playlist ↔ músicas ──────────────────
    # • ordem     → posição da música dentro da playlist (para reordenar)
    # • adicionado_em → timestamp de quando foi inserida na playlist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlist_musicas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id     INTEGER NOT NULL,
            musica_id       INTEGER NOT NULL,
            ordem           INTEGER NOT NULL DEFAULT 0,
            adicionado_em   TEXT    DEFAULT (datetime('now', 'localtime')),

            FOREIGN KEY (playlist_id) REFERENCES playlists(id)  ON DELETE CASCADE,
            FOREIGN KEY (musica_id)   REFERENCES musicas(id)     ON DELETE CASCADE,

            UNIQUE (playlist_id, musica_id)   -- evita duplicatas na mesma playlist
        )
    """)

    conn.commit()
    conn.close()
