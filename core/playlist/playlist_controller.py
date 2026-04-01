from database.database import conectar_banco
from database.models.musica import Musica
from database.models.playlist import Playlist


class PlaylistController:
    """Centraliza as regras de negócio de playlists."""

    def create_playlist(self, nome):
        nome_limpo = (nome or "").strip()
        if not nome_limpo:
            raise ValueError("O nome da playlist é obrigatório.")

        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO playlists (nome) VALUES (?)",
                (nome_limpo,),
            )
            playlist_id = cursor.lastrowid
            cursor.execute(
                "SELECT id, nome, descricao, criado_em FROM playlists WHERE id = ?",
                (playlist_id,),
            )
            row = cursor.fetchone()

        return Playlist.from_row(row) if row else None

    def get_all_playlists(self):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.id, p.nome, p.descricao, p.criado_em, COUNT(pm.musica_id) AS total_musicas
                FROM playlists p
                LEFT JOIN playlist_musicas pm ON pm.playlist_id = p.id
                GROUP BY p.id, p.nome, p.descricao, p.criado_em
                ORDER BY LOWER(p.nome) ASC
                """
            )
            playlists = []
            for row in cursor.fetchall():
                playlist = Playlist.from_row(row[:4])
                playlist.total_musicas = row[4]
                playlists.append(playlist)

        return playlists

    def get_playlist(self, playlist_id):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nome, descricao, criado_em FROM playlists WHERE id = ?",
                (playlist_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        playlist = Playlist.from_row(row)
        playlist.musicas = self.get_musics_from_playlist(playlist_id)
        playlist.total_musicas = len(playlist.musicas)
        return playlist

    def delete_playlist(self, playlist_id):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
            return cursor.rowcount > 0

    def add_music_to_playlist(self, playlist_id, music_id):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            self._ensure_playlist_exists(cursor, playlist_id)
            self._ensure_music_exists(cursor, music_id)

            cursor.execute(
                "SELECT 1 FROM playlist_musicas WHERE playlist_id = ? AND musica_id = ?",
                (playlist_id, music_id),
            )
            if cursor.fetchone():
                raise ValueError("Essa música já está na playlist.")

            cursor.execute(
                """
                SELECT COALESCE(MAX(ordem), 0) + 1
                FROM playlist_musicas
                WHERE playlist_id = ?
                """,
                (playlist_id,),
            )
            ordem = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO playlist_musicas (playlist_id, musica_id, ordem)
                VALUES (?, ?, ?)
                """,
                (playlist_id, music_id, ordem),
            )

        return True

    def remove_music_from_playlist(self, playlist_id, music_id):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM playlist_musicas
                WHERE playlist_id = ? AND musica_id = ?
                """,
                (playlist_id, music_id),
            )
            return cursor.rowcount > 0

    def get_musics_from_playlist(self, playlist_id):
        with conectar_banco() as conn:
            cursor = conn.cursor()
            self._ensure_playlist_exists(cursor, playlist_id)
            cursor.execute(
                """
                SELECT
                    m.id,
                    m.nome,
                    m.artista,
                    m.album,
                    m.ano,
                    m.cifra,
                    m.tablatura,
                    m.caminho_audio,
                    m.link_externo,
                    m.caminho_partitura
                FROM playlist_musicas pm
                INNER JOIN musicas m ON m.id = pm.musica_id
                WHERE pm.playlist_id = ?
                ORDER BY pm.ordem ASC, LOWER(m.nome) ASC
                """,
                (playlist_id,),
            )
            return [Musica.from_row(row) for row in cursor.fetchall()]

    def _ensure_playlist_exists(self, cursor, playlist_id):
        cursor.execute("SELECT 1 FROM playlists WHERE id = ?", (playlist_id,))
        if not cursor.fetchone():
            raise ValueError("Playlist não encontrada.")

    def _ensure_music_exists(self, cursor, music_id):
        cursor.execute("SELECT 1 FROM musicas WHERE id = ?", (music_id,))
        if not cursor.fetchone():
            raise ValueError("Música não encontrada.")
