import sqlite3
from database.database import get_caminho_banco


def buscar_musica(nome):

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT artista, album, ano, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()
    conn.close()
    return resultado


def buscar_musica_completa(nome):

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome LIKE ?
    """, (f"%{nome}%",))

    resultado = cursor.fetchone()
    conn.close()
    return resultado


def listar_musicas():
    """Retorna todas as músicas cadastradas ordenadas por nome."""

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        ORDER BY nome ASC
    """)

    resultado = cursor.fetchall()
    conn.close()
    return resultado


def filtrar_musicas(texto):
    """
    Filtra musicas pelo texto digitado (nome, artista ou album).
    Prioridade: musicas que COMECAM com o texto vem primeiro,
    depois as que CONTEM o texto, ambos em ordem alfabetica.
    """

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    like = f"%{texto}%"
    cursor.execute("""
        SELECT id, nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura
        FROM musicas
        WHERE nome    LIKE ?
           OR artista LIKE ?
           OR album   LIKE ?
        ORDER BY
            CASE
                WHEN LOWER(nome) LIKE LOWER(?) THEN 0
                ELSE 1
            END,
            LOWER(nome) ASC
    """, (like, like, like, f"{texto}%"))

    resultado = cursor.fetchall()
    conn.close()
    return resultado


def add_musica(nome, artista, album, ano, cifra, tablatura, audio, partitura):

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO musicas
        (nome, artista, album, ano, cifra, tablatura, caminho_audio, caminho_partitura)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, artista, album, ano, cifra, tablatura, audio, partitura))

    conn.commit()
    conn.close()


def editar_musica(id, nome, artista, album, ano, cifra, tablatura, audio, partitura):

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE musicas
        SET nome = ?, artista = ?, album = ?, ano = ?, cifra = ?, tablatura = ?,
            caminho_audio = ?, caminho_partitura = ?
        WHERE id = ?
    """, (nome, artista, album, ano, cifra, tablatura, audio, partitura, id))

    conn.commit()
    conn.close()


def excluir_musica(id):

    conn = sqlite3.connect(get_caminho_banco())
    cursor = conn.cursor()

    cursor.execute("DELETE FROM musicas WHERE id = ?", (id,))

    conn.commit()
    conn.close()