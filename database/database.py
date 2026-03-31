import sqlite3  # biblioteca nativa do Python para SQLite
import os       # manipulação de arquivos e diretórios


def get_caminho_banco():
    # Define a pasta AppData/Gralha
    pasta = os.path.join(
        os.environ.get("APPDATA", os.path.expanduser("~")),
        "Gralha"
    )

    # Cria a pasta se não existir
    os.makedirs(pasta, exist_ok=True)

    # Retorna o caminho completo do banco
    return os.path.join(pasta, "musicas.db")


def conectar_banco():
    # Abre conexão com o banco
    return sqlite3.connect(get_caminho_banco())


def _garantir_colunas_musicas(cursor):
    """Adiciona colunas novas sem perder dados existentes."""
    cursor.execute("PRAGMA table_info(musicas)")
    colunas_existentes = {coluna[1] for coluna in cursor.fetchall()}

    novas_colunas = {
        "link_externo": "TEXT",
        "youtube_id": "TEXT",
        "favorita": "BOOLEAN DEFAULT 0",
    }

    for nome_coluna, definicao in novas_colunas.items():
        if nome_coluna not in colunas_existentes:
            cursor.execute(
                f"ALTER TABLE musicas ADD COLUMN {nome_coluna} {definicao}"
            )


# ─────────────────────────────────────────────
# CRIAÇÃO DE TABELAS
# ─────────────────────────────────────────────

def criar_tabela():
    with conectar_banco() as conn:
        cursor = conn.cursor()

        # ── Tabela de músicas ─────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS musicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                artista TEXT NOT NULL,
                album TEXT,
                ano INTEGER,
                cifra TEXT,
                tablatura TEXT,
                caminho_audio TEXT,
                link_externo TEXT,
                caminho_partitura TEXT,
                youtube_id TEXT,
                favorita BOOLEAN DEFAULT 0
            )
        """)

        _garantir_colunas_musicas(cursor)

        # ── Tabela de playlists ───────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                criado_em TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # ── Relacionamento playlist ↔ músicas ─
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_musicas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                musica_id INTEGER NOT NULL,
                ordem INTEGER NOT NULL DEFAULT 0,
                adicionado_em TEXT DEFAULT (datetime('now', 'localtime')),

                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (musica_id) REFERENCES musicas(id) ON DELETE CASCADE,

                UNIQUE (playlist_id, musica_id)
            )
        """)