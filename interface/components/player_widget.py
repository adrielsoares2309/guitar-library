from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget


class PlayerWidget(QWidget):
    play_pause_requested = Signal()
    restart_requested = Signal()
    loop_toggled = Signal(bool)
    seek_requested = Signal(int)
    volume_changed = Signal(int)
    next_requested = Signal()
    previous_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("playerWidget")
        self._duration = 0
        self._seeking = False
        self._loop_enabled = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setObjectName("timeLabel")
        self.remaining_time_label = QLabel("-0:00")
        self.remaining_time_label.setObjectName("timeLabel")

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderPressed.connect(self._start_seek)
        self.progress_slider.sliderMoved.connect(self._seek_moved)
        self.progress_slider.sliderReleased.connect(self._finish_seek)

        progress_row.addWidget(self.current_time_label)
        progress_row.addWidget(self.progress_slider, 1)
        progress_row.addWidget(self.remaining_time_label)
        root.addLayout(progress_row)

        controls = QHBoxLayout()
        controls.setSpacing(16)
        controls.addStretch(1)

        self.restart_button = QPushButton("\u27f3")
        self.restart_button.setObjectName("playerIconButton")
        self.restart_button.clicked.connect(self.restart_requested.emit)

        self.play_button = QPushButton("\u25b6")
        self.play_button.setObjectName("playerMainButton")
        self.play_button.clicked.connect(self.play_pause_requested.emit)

        self.loop_button = QPushButton("\u29c9")
        self.loop_button.setObjectName("playerIconButton")
        self.loop_button.setCheckable(True)
        self.loop_button.clicked.connect(self._toggle_loop)

        volume_row = QHBoxLayout()
        volume_row.setSpacing(8)
        volume_label = QLabel("\U0001f50a")
        volume_label.setObjectName("timeLabel")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        volume_row.addWidget(volume_label)
        volume_row.addWidget(self.volume_slider)

        controls.addWidget(self.restart_button)
        controls.addWidget(self.play_button)
        controls.addWidget(self.loop_button)
        controls.addLayout(volume_row)
        controls.addStretch(1)
        root.addLayout(controls)

    def set_music(self, musica: object | None) -> None:
        has_audio = bool(self._audio_path(musica))
        self.play_button.setEnabled(has_audio)
        self.restart_button.setEnabled(has_audio)
        self.progress_slider.setEnabled(has_audio)

    def set_position(self, position: int) -> None:
        if not self._seeking:
            self.progress_slider.setValue(position)
        self.current_time_label.setText(self._format_time(position))
        remaining = max(0, self._duration - position)
        self.remaining_time_label.setText(f"-{self._format_time(remaining)}")

    def set_duration(self, duration: int) -> None:
        self._duration = max(0, duration)
        self.progress_slider.setRange(0, self._duration)
        self.remaining_time_label.setText(f"-{self._format_time(self._duration)}")

    def set_playing(self, playing: bool) -> None:
        self.play_button.setText("\u23f8" if playing else "\u25b6")

    def set_loop_enabled(self, enabled: bool) -> None:
        self._loop_enabled = enabled
        self.loop_button.setChecked(enabled)
        self.loop_button.setProperty("active", enabled)
        self.loop_button.style().unpolish(self.loop_button)
        self.loop_button.style().polish(self.loop_button)

    def _start_seek(self) -> None:
        self._seeking = True

    def _seek_moved(self, position: int) -> None:
        self.set_position(position)
        self.seek_requested.emit(position)

    def _finish_seek(self) -> None:
        self._seeking = False
        self.seek_requested.emit(self.progress_slider.value())

    def _toggle_loop(self) -> None:
        self.loop_toggled.emit(self.loop_button.isChecked())

    @staticmethod
    def _format_time(milliseconds: int) -> str:
        total_seconds = max(0, milliseconds // 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    @staticmethod
    def _audio_path(musica: object | None) -> str:
        if musica is None:
            return ""
        if hasattr(musica, "caminho_audio"):
            return getattr(musica, "caminho_audio") or ""
        if isinstance(musica, (tuple, list)) and len(musica) > 7:
            return musica[7] or ""
        return ""
