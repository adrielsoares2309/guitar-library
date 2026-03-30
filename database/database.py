import sqlite3 #iblioteca nativa do Python pra trabalhar com banco de dados SQLite (arquivo .db)
import os #usada pra mexer com arquivos, pastas e caminhos do sistema


def get_caminho_banco():
   #encontra o caminho da pasta appdata, e cria a pasta "gralha"
    pasta = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Gralha") 
    #Cria a pasta "Gralha" se ela não existir
    os.makedirs(pasta, exist_ok=True)
    #Retorna o caminho completo do banco 
    return os.path.join(pasta, "musicas.db")


def conectar_banco():

    #Cria (ou abre) o banco SQLite no caminho definido antes
    conn = sqlite3.connect(get_caminho_banco())
    #Retorna a conexão pra ser usada em outras partes do código

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
<<<<<<< HEAD
    """
    Cria (se não existirem) todas as tabelas do banco:
      • musicas             – biblioteca de músicas
      • playlists           – coleções criadas pelo usuário
      • playlist_musicas    – relacionamento N:N entre playlists e músicas
    """
=======
    #abre a conexão com o banco de dados
>>>>>>> 964bfb2e8aa5ed86e8eb00f7981ab2e8ab0c49cb
    conn = conectar_banco()
    #Cria um cursor (Cursor é o objeto que executa comandos SQL)
    cursor = conn.cursor()
<<<<<<< HEAD

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
=======
    #O cursor executa a query
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas ( #Cria a tabela musicas se ela não existir
        id INTEGER PRIMARY KEY AUTOINCREMENT, #responsável por atribuir um id único a linha
        nome TEXT, #cria coluna nome com o tipo de variável text
        artista TEXT, #cria coluna artista com o tipo de variável text
        album TEXT, #cria coluna album com o tipo de variável text
        ano INTEGER, #cria coluna album com o tipo de variável integer
        cifra TEXT, #cria coluna cifra com o tipo de variável text
        tablatura TEXT, #cria coluna tablatura com o tipo de variável text
        caminho_audio TEXT, #cria coluna caminho_audio com o tipo de variável text
        caminho_partitura TEXT #cria coluna caminho_partitura com o tipo de variável text
    )
    """)
    conn.commit() #salva as alterações no banco de dados
    conn.close() #fecha a conexão com o banco
>>>>>>> 964bfb2e8aa5ed86e8eb00f7981ab2e8ab0c49cb
