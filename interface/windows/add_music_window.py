import os
from urllib.parse import urlparse

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from interface.windows.spotify_search_window import SpotifySearchWindow
from services.music_service import add_musica
from services.spotify_service import SpotifyService


class SpotifySearchWorker(QThread):
    resultado = Signal(int, str, str, object)

    def __init__(self, token: int, termo: str, parent=None) -> None:
        super().__init__(parent)
        self.token = token
        self.termo = termo

    def run(self) -> None:
        try:
            resultados = SpotifyService().buscar_musicas(self.termo, limit=5)
            status = "success" if resultados else "not_found"
            self.resultado.emit(self.token, self.termo, status, resultados)
        except Exception:
            self.resultado.emit(self.token, self.termo, "error", [])


class AddMusicWindow(QDialog):
    musica_salva = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.caminho_audio = ""
        self.caminho_partitura = ""
        self._spotify_token = 0
        self._spotify_worker: SpotifySearchWorker | None = None

        self.setWindowTitle("Adicionar Musica")
        self.resize(480, 720)
        self.setMinimumHeight(560)
        self.setModal(True)

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)
        title = QLabel("Adicionar Musica")
        title.setObjectName("titleLabel")
        header_layout.addWidget(title)
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(0)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        card = QFrame()
        card.setObjectName("card")
        self.form_layout = QVBoxLayout(card)
        self.form_layout.setContentsMargins(24, 16, 24, 24)
        self.form_layout.setSpacing(8)
        content_layout.addWidget(card)
        content_layout.addStretch(1)

        self._add_section("BUSCAR MUSICA")
        search_box = QFrame()
        search_box.setObjectName("searchBox")
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(10, 2, 6, 2)
        search_layout.setSpacing(6)
        self.spotify_entry = QLineEdit()
        self.spotify_entry.setObjectName("searchInput")
        self.spotify_entry.setPlaceholderText("Buscar musica no Spotify...")
        self.spotify_entry.returnPressed.connect(self._buscar_spotify)
        self.spotify_button = QPushButton("Buscar")
        self.spotify_button.clicked.connect(self._buscar_spotify)
        search_layout.addWidget(self.spotify_entry, 1)
        search_layout.addWidget(self.spotify_button)
        self.form_layout.addWidget(search_box)

        self.nome_entry = self._add_line_edit("NOME", "Nome da musica")
        self.artista_entry = self._add_line_edit("ARTISTA", "Nome do artista")
        self.album_entry = self._add_line_edit("ALBUM", "Nome do album")
        self.ano_entry = self._add_line_edit("ANO", "Ex: 2024")
        self._add_separator()
        self.cifra_text = self._add_text_edit("CIFRA  (acordes)", 110)
        self.tablatura_text = self._add_text_edit("TABLATURA  (ASCII)", 130)
        self.tablatura_text.setPlainText(
            "E|--0--| (Mi aguda)\n"
            "B|--2--|\n"
            "G|--2--|\n"
            "D|--2--|\n"
            "A|--0--|\n"
            "E|-----| (Mi grave)"
        )
        self._add_separator()

        self.audio_label = self._add_file_picker("AUDIO", "Nenhum arquivo selecionado", "SELECIONAR AUDIO", self._selecionar_audio)
        self.link_entry = self._add_line_edit("LINK EXTERNO", "https://youtube.com/... ou https://open.spotify.com/...")
        self.partitura_label = self._add_file_picker("PARTITURA  (PDF)", "Nenhum arquivo selecionado", "SELECIONAR PARTITURA", self._selecionar_partitura)
        self._add_separator()

        save_button = QPushButton("SALVAR MUSICA")
        save_button.clicked.connect(self._salvar)
        self.form_layout.addWidget(save_button)

    def _add_section(self, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        self.form_layout.addWidget(label)

    def _add_line_edit(self, label: str, placeholder: str) -> QLineEdit:
        self._add_section(label)
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        self.form_layout.addWidget(entry)
        return entry

    def _add_text_edit(self, label: str, height: int) -> QPlainTextEdit:
        self._add_section(label)
        text = QPlainTextEdit()
        text.setObjectName("monoText")
        text.setFixedHeight(height)
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.form_layout.addWidget(text)
        return text

    def _add_separator(self) -> None:
        line = QFrame()
        line.setObjectName("separator")
        self.form_layout.addWidget(line)

    def _add_file_picker(self, label: str, empty: str, button_text: str, slot) -> QLabel:
        self._add_section(label)
        selected = QLabel(empty)
        selected.setObjectName("mutedLabel")
        self.form_layout.addWidget(selected)
        button = QPushButton(button_text)
        button.setObjectName("secondaryButton")
        button.clicked.connect(slot)
        self.form_layout.addWidget(button)
        return selected

    def _selecionar_audio(self) -> None:
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Audio",
            "",
            "Audio files (*.mp3 *.wav);;All files (*.*)",
        )
        if arquivo:
            self.caminho_audio = arquivo
            self.audio_label.setText(os.path.basename(arquivo))

    def _selecionar_partitura(self) -> None:
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Partitura", "", "PDF files (*.pdf)")
        if arquivo:
            self.caminho_partitura = arquivo
            self.partitura_label.setText(os.path.basename(arquivo))

    def _url_valida(self, url: str) -> bool:
        if not url:
            return True
        partes = urlparse(url)
        return partes.scheme in {"http", "https"} and bool(partes.netloc)

    def _buscar_spotify(self) -> None:
        termo = self.spotify_entry.text().strip()
        if not termo or (self._spotify_worker and self._spotify_worker.isRunning()):
            return
        self._spotify_token += 1
        self.spotify_entry.setEnabled(False)
        self.spotify_button.setEnabled(False)
        self.spotify_entry.setPlaceholderText("Buscando...")
        self._spotify_worker = SpotifySearchWorker(self._spotify_token, termo, self)
        self._spotify_worker.resultado.connect(self._receber_spotify)
        self._spotify_worker.finished.connect(lambda: setattr(self, "_spotify_worker", None))
        self._spotify_worker.finished.connect(self._spotify_worker.deleteLater)
        self._spotify_worker.start()

    def _receber_spotify(self, token: int, termo: str, status: str, resultados) -> None:
        if token != self._spotify_token:
            return
        self.spotify_entry.setEnabled(True)
        self.spotify_button.setEnabled(True)
        self.spotify_entry.setPlaceholderText("Buscar musica no Spotify...")
        if self.spotify_entry.text().strip() != termo:
            return
        if status == "success":
            if len(resultados) == 1:
                self._preencher_campos(resultados[0])
            else:
                dialog = SpotifySearchWindow(self, resultados=resultados)
                dialog.selected.connect(self._preencher_campos)
                dialog.exec()
        elif status == "not_found":
            QMessageBox.information(self, "Spotify", "Nenhuma musica encontrada.")
        else:
            QMessageBox.warning(self, "Spotify", "Erro ao buscar musica.")

    def _preencher_campos(self, resultado: dict) -> None:
        self.nome_entry.setText(resultado.get("nome", ""))
        self.artista_entry.setText(resultado.get("artista", ""))
        self.album_entry.setText(resultado.get("album", ""))
        self.ano_entry.setText(resultado.get("ano", ""))
        self.link_entry.setText(resultado.get("link_spotify", ""))

    def _salvar(self) -> None:
        nome = self.nome_entry.text().strip()
        artista = self.artista_entry.text().strip()
        album = self.album_entry.text().strip()
        ano_str = self.ano_entry.text().strip()
        cifra = self.cifra_text.toPlainText().strip()
        tablatura = self.tablatura_text.toPlainText().strip()
        link_externo = self.link_entry.text().strip()

        if not nome or not artista:
            QMessageBox.warning(self, "Atencao", "Nome e Artista sao obrigatorios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                QMessageBox.warning(self, "Atencao", "Ano invalido! Use o formato: 2024")
                return
            ano = int(ano_str)

        if link_externo and not self._url_valida(link_externo):
            QMessageBox.warning(self, "Atencao", "Informe uma URL valida, como um link do YouTube ou Spotify.")
            return

        add_musica(nome, artista, album, ano, cifra, tablatura, self.caminho_audio, link_externo, self.caminho_partitura)
        QMessageBox.information(self, "Sucesso", f'"{nome}" salva com sucesso!')
        self.musica_salva.emit()
        self.accept()

    def closeEvent(self, event) -> None:
        if self._spotify_worker and self._spotify_worker.isRunning():
            self._spotify_worker.wait(3000)
        super().closeEvent(event)


def abrir_janela_adicionar(parent=None):
    dialog = AddMusicWindow(parent)
    dialog.exec()
    return dialog
