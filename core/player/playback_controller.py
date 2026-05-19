import os

from PySide6.QtCore import QObject, Signal

from core.player.audio_player import AudioPlayer
from core.player.audio_state import AudioState
from core.player.queue_manager import QueueManager


class PlaybackController(QObject):
    music_changed = Signal(object)
    error = Signal(str)

    def __init__(self, player_widget=None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.audio_player = AudioPlayer.instance()
        self.queue_manager = QueueManager(self)
        self.widget = None
        self.estado = AudioState.STOPPED
        self.loop_enabled = False

        self.audio_player.position_changed.connect(self._on_position_changed)
        self.audio_player.duration_changed.connect(self._on_duration_changed)
        self.audio_player.state_changed.connect(self._on_state_changed)
        self.audio_player.finished.connect(self._on_finished)
        self.audio_player.error_changed.connect(self.error.emit)
        self.queue_manager.current_changed.connect(self.music_changed.emit)

        if player_widget is not None:
            self.conectar_widget(player_widget)

    def conectar_widget(self, widget) -> None:
        self.widget = widget
        widget.play_pause_requested.connect(self.toggle_play_pause)
        widget.restart_requested.connect(self.reiniciar)
        widget.loop_toggled.connect(self.definir_loop)
        widget.seek_requested.connect(self.audio_player.alterar_posicao)
        widget.volume_changed.connect(self.audio_player.alterar_volume)
        widget.next_requested.connect(self.proxima)
        widget.previous_requested.connect(self.anterior)
        widget.set_loop_enabled(self.loop_enabled)

    def carregar_fila(self, musicas: list[object], musica_atual: object | None = None) -> None:
        self.queue_manager.set_queue(musicas, musica_atual)
        self._sync_current_metadata()

    def tocar_musica(self, musica: object | None = None) -> None:
        if musica is not None:
            self.queue_manager.set_queue([musica], musica)
        atual = self.queue_manager.atual()
        caminho = self._audio_path(atual)
        if not caminho:
            self.error.emit("Esta musica nao possui arquivo de audio.")
            return
        if not os.path.exists(caminho):
            self.error.emit(f"Arquivo de audio nao encontrado:\n{caminho}")
            return
        self._sync_current_metadata()
        self.audio_player.tocar(caminho)

    def toggle_play_pause(self) -> None:
        if self.estado == AudioState.PLAYING:
            self.audio_player.pausar()
            return
        if self.estado == AudioState.PAUSED:
            self.audio_player.tocar()
            return
        self.tocar_musica()

    def reiniciar(self) -> None:
        self.audio_player.reiniciar()

    def definir_loop(self, enabled: bool) -> None:
        self.loop_enabled = enabled
        if self.widget:
            self.widget.set_loop_enabled(enabled)

    def proxima(self) -> None:
        if self.queue_manager.proxima():
            self.tocar_musica()

    def anterior(self) -> None:
        if self.queue_manager.anterior():
            self.tocar_musica()

    def parar(self) -> None:
        self.audio_player.parar()

    def _on_position_changed(self, position: int) -> None:
        if self.widget:
            self.widget.set_position(position)

    def _on_duration_changed(self, duration: int) -> None:
        if self.widget:
            self.widget.set_duration(duration)

    def _on_state_changed(self, estado: AudioState) -> None:
        self.estado = estado
        if self.widget:
            self.widget.set_playing(estado == AudioState.PLAYING)

    def _on_finished(self) -> None:
        if self.loop_enabled:
            self.audio_player.reiniciar()
            return
        if self.queue_manager.proxima():
            self.tocar_musica()

    def _sync_current_metadata(self) -> None:
        if self.widget:
            self.widget.set_music(self.queue_manager.atual())

    @staticmethod
    def _audio_path(musica: object | None) -> str:
        if musica is None:
            return ""
        if hasattr(musica, "caminho_audio"):
            return getattr(musica, "caminho_audio") or ""
        if isinstance(musica, (tuple, list)) and len(musica) > 7:
            return musica[7] or ""
        return ""
