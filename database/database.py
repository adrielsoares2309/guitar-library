import sqlite3
import os

def get_caminho_banco():
    # Cria a pasta de dados do app na pasta AppData do usuário
    pasta = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GuitarLibrary")
    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, "musicas.db")

def conectar_banco():
    conn = sqlite3.connect(get_caminho_banco())
    return conn

def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        artista TEXT,
        album TEXT,
        ano INTEGER,
        cifra TEXT,
        tablatura TEXT,
        caminho_audio TEXT,
        caminho_partitura TEXT
    )
    """)
    conn.commit()
    conn.close()