from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from core.player.audio_state import AudioState


class AudioPlayer(QObject):
    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(AudioState)
    finished = Signal()
    error_changed = Signal(str)
    _instance = None

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.75)

        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_error)

    @classmethod
    def instance(cls) -> "AudioPlayer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def tocar(self, caminho: str | None = None) -> None:
        if caminho:
            self.player.setSource(QUrl.fromLocalFile(caminho))
        self.player.play()

    def pausar(self) -> None:
        self.player.pause()

    def parar(self) -> None:
        self.player.stop()

    def reiniciar(self) -> None:
        self.player.setPosition(0)
        self.player.play()

    def alterar_volume(self, valor: int) -> None:
        volume = max(0, min(100, valor)) / 100
        self.audio_output.setVolume(volume)

    def alterar_posicao(self, posicao: int) -> None:
        self.player.setPosition(max(0, posicao))

    def _on_playback_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.state_changed.emit(AudioState.PLAYING)
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.state_changed.emit(AudioState.PAUSED)
        else:
            self.state_changed.emit(AudioState.STOPPED)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()

    def _on_error(self, error, error_string: str) -> None:
        if error_string:
            self.error_changed.emit(error_string)
