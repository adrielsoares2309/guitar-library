import sqlite3


def buscar_musica(nome):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT artista, album, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()

    conn.close()

    return resultado


def buscar_musica_completa(nome):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, artista, album, tablatura, caminho_audio, caminho_partitura
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


def editar_musica(id, nome, artista, album, tablatura, audio, partitura):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE musicas
        SET nome = ?, artista = ?, album = ?, tablatura = ?,
            caminho_audio = ?, caminho_partitura = ?
        WHERE id = ?
    """, (nome, artista, album, tablatura, audio, partitura, id))

    conn.commit()
    conn.close()


def excluir_musica(id):

    conn = sqlite3.connect("database/musicas.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM musicas WHERE id = ?", (id,))

    conn.commit()
    conn.close()