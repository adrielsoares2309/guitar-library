import os

from mutagen import File


class MetadataExtractor:
    @staticmethod
    def obter_duracao(caminho):
        if not caminho or not os.path.exists(caminho):
            return None

        try:
            audio = File(caminho)
        except Exception:
            return None

        if not audio or not getattr(audio, "info", None):
            return None

        duracao = getattr(audio.info, "length", None)
        if duracao is None:
            return None

        return int(round(duracao))
