from core.playlist.playlist_controller import PlaylistController


_controller = PlaylistController()


def create_playlist(nome):
    return _controller.create_playlist(nome)


def get_all_playlists():
    return _controller.get_all_playlists()


def get_playlist(playlist_id):
    return _controller.get_playlist(playlist_id)


def delete_playlist(playlist_id):
    return _controller.delete_playlist(playlist_id)


def add_music_to_playlist(playlist_id, music_id):
    return _controller.add_music_to_playlist(playlist_id, music_id)


def remove_music_from_playlist(playlist_id, music_id):
    return _controller.remove_music_from_playlist(playlist_id, music_id)


def get_musics_from_playlist(playlist_id):
    return _controller.get_musics_from_playlist(playlist_id)
