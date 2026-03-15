import sqlite3

def conectar_banco():
    conn = sqlite3.connect("database/musicas.db")
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