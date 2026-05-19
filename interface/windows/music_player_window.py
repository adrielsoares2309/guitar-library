import os
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.player.playback_controller import PlaybackController
from interface.components.player_widget import PlayerWidget


def _refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class TextViewerDialog(QDialog):
    def __init__(self, titulo: str, conteudo: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(620, 520)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel(titulo.upper())
        title.setObjectName("titleLabel")
        root.addWidget(title)

        text = QPlainTextEdit()
        text.setObjectName("viewerText")
        text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        text.setPlainText(conteudo or "")
        text.setReadOnly(True)
        root.addWidget(text, 1)


class MusicPlayerWindow(QDialog):
    def __init__(self, controller: PlaybackController, parent=None) -> None:
        super().__init__(parent)
        self.musica = None
        self.fila = []
        self.controller = controller

        self.setWindowTitle("Musica")
        self.resize(860, 620)
        self.setMinimumSize(620, 460)
        self.setModal(False)
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, True)

        self.player_widget = PlayerWidget(self)
        self.controller.conectar_widget(self.player_widget)
        self.controller.error.connect(self._show_error)
        self.controller.music_changed.connect(self._on_music_changed)

        self._build_ui()

    def reproduzir(self, musica, fila: list[object] | None = None) -> None:
        self.musica = musica
        self.fila = fila or [musica]
        self.controller.carregar_fila(self.fila, self.musica)
        self.controller.tocar_musica()
        self.show()
        self.raise_()
        self.activateWindow()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(0)

        card = QFrame()
        card.setObjectName("musicPlayerCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        root.addWidget(card, 1)

        info = QVBoxLayout()
        info.setSpacing(4)
        self.title_label = QLabel("")
        self.title_label.setObjectName("musicTitleLabel")
        self.artist_label = QLabel("")
        self.artist_label.setObjectName("musicMetaLabel")
        self.album_label = QLabel("")
        self.album_label.setObjectName("musicMetaLabel")
        self.year_label = QLabel("")
        self.year_label.setObjectName("musicMetaLabel")
        info.addWidget(self.title_label)
        info.addWidget(self.artist_label)
        info.addWidget(self.album_label)
        info.addWidget(self.year_label)
        card_layout.addLayout(info)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.cifra_button = self._content_button("Cifra", self.abrir_cifra)
        self.tablatura_button = self._content_button("Tablatura", self.abrir_tablatura)
        self.partitura_button = self._content_button("Partitura", self.visualizar_partitura)
        self.audio_button = self._content_button("Audio", self.controller.toggle_play_pause)
        self.link_button = self._content_button("Link", self.abrir_link_externo)
        for button in [
            self.cifra_button,
            self.tablatura_button,
            self.partitura_button,
            self.audio_button,
            self.link_button,
        ]:
            buttons.addWidget(button)
        buttons.addStretch(1)
        card_layout.addLayout(buttons)

        card_layout.addStretch(1)
        card_layout.addWidget(self.player_widget)
        self._sync_music_info()

    def _content_button(self, text: str, slot) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName("contentButton")
        button.clicked.connect(slot)
        return button

    def _on_music_changed(self, musica) -> None:
        if musica is not None:
            self.musica = musica
            self._sync_music_info()

    def _sync_music_info(self) -> None:
        self.title_label.setText(self._value("nome") or "-")
        self.artist_label.setText(self._value("artista") or "-")
        self.album_label.setText(self._value("album") or "-")
        year = self._value("ano")
        self.year_label.setText(str(year) if year else "-")

        self._set_content_active(self.cifra_button, bool(self._value("cifra")))
        self._set_content_active(self.tablatura_button, bool(self._value("tablatura")))
        self._set_content_active(self.partitura_button, bool(self._value("caminho_partitura")))
        self._set_content_active(self.audio_button, bool(self._value("caminho_audio")))
        self._set_content_active(self.link_button, bool(self._value("link_externo")))

    def _set_content_active(self, button: QPushButton, active: bool) -> None:
        button.setProperty("active", active)
        button.setEnabled(active)
        _refresh_style(button)

    def abrir_cifra(self) -> None:
        TextViewerDialog("Cifra", self._value("cifra") or "", self).exec()

    def abrir_tablatura(self) -> None:
        TextViewerDialog("Tablatura", self._value("tablatura") or "", self).exec()

    def visualizar_partitura(self) -> None:
        partitura = self._value("caminho_partitura") or ""
        if os.path.exists(partitura):
            os.startfile(partitura)
        else:
            QMessageBox.warning(self, "Aviso", f"Arquivo de partitura nao encontrado:\n{partitura}")

    def abrir_link_externo(self) -> None:
        link_externo = self._value("link_externo") or ""
        if link_externo:
            webbrowser.open(link_externo)

    def _show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Player", message)

    def closeEvent(self, event) -> None:
        self.controller.parar()
        super().closeEvent(event)

    def _value(self, name: str):
        if hasattr(self.musica, name):
            return getattr(self.musica, name)

        indexes = {
            "id": 0,
            "nome": 1,
            "artista": 2,
            "album": 3,
            "ano": 4,
            "cifra": 5,
            "tablatura": 6,
            "caminho_audio": 7,
            "link_externo": 8,
            "caminho_partitura": 9,
            "duracao": 10,
        }
        index = indexes.get(name)
        if isinstance(self.musica, (tuple, list)) and index is not None and len(self.musica) > index:
            return self.musica[index]
        return None
