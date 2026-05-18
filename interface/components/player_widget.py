from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget


class PlayerWidget(QWidget):
    play_requested = Signal(str)
    stop_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._audio_path = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.info_label = QLabel("Nenhum audio selecionado")
        self.info_label.setObjectName("mutedLabel")

        self.play_button = QPushButton("TOCAR")
        self.play_button.clicked.connect(self._emit_play)
        self.stop_button = QPushButton("PARAR")
        self.stop_button.setObjectName("secondaryButton")
        self.stop_button.clicked.connect(self.stop_requested.emit)

        layout.addWidget(self.info_label, 1)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)

    def set_audio(self, path: str) -> None:
        self._audio_path = path or ""
        self.info_label.setText(self._audio_path or "Nenhum audio selecionado")
        self.play_button.setEnabled(bool(self._audio_path))

    def _emit_play(self) -> None:
        if self._audio_path:
            self.play_requested.emit(self._audio_path)
