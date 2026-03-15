import sqlite3


def buscar_musica(nome):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT artista, album, tablatura, caminho_audio
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()

    conn.close()

    return resultado


def add_musica(nome, artista, album, tablatura, audio, partitura):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO musicas
        (nome, artista, album, tablatura, caminho_audio, caminho_partitura)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, artista, album, tablatura, audio, partitura))

    conn.commit()
    conn.close()