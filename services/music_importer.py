from services.metadata_extractor import MetadataExtractor
from services.music_service import add_musica


class MusicImporter:
    @staticmethod
    def importar_musica(nome, artista, album, ano, cifra, tablatura, audio, link_externo, partitura):
        duracao = MetadataExtractor.obter_duracao(audio)
        add_musica(
            nome,
            artista,
            album,
            ano,
            cifra,
            tablatura,
            audio,
            link_externo,
            partitura,
            duracao,
        )
        return duracao
