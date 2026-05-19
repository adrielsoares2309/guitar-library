import os
import sys
import webbrowser

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.player.playback_controller import PlaybackController
from interface.components.playlist_widget import PlaylistWidget
from interface.windows.add_music_window import AddMusicWindow
from interface.windows.edit_music_window import EditMusicWindow
from interface.windows.music_player_window import MusicPlayerWindow
from interface.windows.playlist_window import PlaylistWindow
from services.music_service import excluir_musica, filtrar_musicas, listar_musicas
from services.playlist_service import create_playlist, get_all_playlists


def _refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class _TableRow(QFrame):
    clicked = Signal(object)
    double_clicked = Signal(object)

    def __init__(self, musica, alternate: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.musica = musica
        self.setProperty("row", True)
        self.setProperty("alternate", alternate)
        self.setCursor(Qt.PointingHandCursor)

        layout = QGridLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setHorizontalSpacing(8)

        values = [
            musica[1] or "-",
            musica[2] or "-",
            musica[3] or "-",
            str(musica[4]) if musica[4] else "-",
        ]
        for column, value in enumerate(values):
            label = QLabel(value)
            if column == 0:
                font = label.font()
                font.setBold(True)
                label.setFont(font)
            else:
                label.setObjectName("mutedLabel")
            layout.addWidget(label, 0, column)
            layout.setColumnStretch(column, 1 if column < 3 else 0)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.musica)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.musica)
        super().mouseDoubleClickEvent(event)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        _refresh_style(self)

    def enterEvent(self, event) -> None:
        self.setProperty("hovered", True)
        _refresh_style(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hovered", False)
        _refresh_style(self)
        super().leaveEvent(event)


class TextViewerDialog(QDialog):
    def __init__(self, titulo: str, conteudo: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(500, 440)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(10)

        title = QLabel(titulo.upper())
        title.setObjectName("titleLabel")
        text = QPlainTextEdit()
        text.setObjectName("viewerText")
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        text.setPlainText(conteudo)
        text.setReadOnly(True)

        root.addWidget(title)
        root.addWidget(text, 1)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.musica_atual = None
        self.sidebar_visible = False
        self._open_dialogs = []
        self.playback_controller = PlaybackController(parent=self)
        self.player_window: MusicPlayerWindow | None = None
        self.music_rows: list[_TableRow] = []
        self.musicas_visiveis = []

        self.setWindowTitle("Gralha")
        self.resize(680, 560)
        self.setMinimumSize(620, 500)

        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(180)
        self.search_timer.timeout.connect(self.on_busca)

        self._build_ui()
        self.atualizar_playlists()
        self.mostrar_lista()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("contentArea")
        self.setCentralWidget(central)
        shell = QHBoxLayout(central)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        self.sidebar = self._create_sidebar()
        self.sidebar.hide()
        shell.addWidget(self.sidebar)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        shell.addWidget(content, 1)

        content_layout.addWidget(self._create_topbar())

        body = QWidget()
        body.setObjectName("contentArea")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        content_layout.addWidget(body, 1)

        self.playlist_widget = PlaylistWidget(
            body,
            on_open_playlist=self.abrir_playlist,
            on_create_playlist=self.criar_playlist_nova,
        )
        body_layout.addWidget(self.playlist_widget)

        self.content_area = QWidget()
        self.content_area.setObjectName("contentArea")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        body_layout.addWidget(self.content_area, 1)

    def _create_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(170)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 28, 12, 12)
        layout.setSpacing(8)

        title = QLabel("MENU")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        for text, slot in [
            ("ADICIONAR", self.adicionar),
            ("EDITAR", self.editar),
            ("EXCLUIR", self.excluir),
        ]:
            button = QPushButton(text)
            button.clicked.connect(slot)
            layout.addWidget(button)
        layout.addStretch(1)
        return sidebar

    def _create_topbar(self) -> QFrame:
        topbar = QFrame()
        topbar.setObjectName("topbar")
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        menu_button = QPushButton("☰")
        menu_button.setObjectName("iconButton")
        menu_button.clicked.connect(self.toggle_sidebar)

        search_box = QFrame()
        search_box.setObjectName("searchBox")
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(12, 2, 6, 2)
        search_layout.setSpacing(6)
        self.entrada = QLineEdit()
        self.entrada.setObjectName("searchInput")
        self.entrada.setPlaceholderText("Buscar musica...")
        self.entrada.textChanged.connect(self.schedule_search)
        self.entrada.returnPressed.connect(self.on_busca)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.on_busca)
        search_layout.addWidget(self.entrada, 1)
        search_layout.addWidget(search_button)

        layout.addWidget(menu_button)
        layout.addWidget(search_box, 1)
        return topbar

    def toggle_sidebar(self) -> None:
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)

    def _clear_content(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _create_scroll(self) -> tuple[QScrollArea, QWidget, QVBoxLayout]:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 8, 16, 16)
        layout.setSpacing(6)
        scroll.setWidget(content)
        return scroll, content, layout

    def atualizar_playlists(self) -> None:
        self.playlist_widget.set_playlists(get_all_playlists())

    def abrir_playlist(self, playlist) -> None:
        dialog = PlaylistWindow(self, playlist_id=playlist.id)
        dialog.musicaSelecionada.connect(self.abrir_janela_musica)
        self.playback_controller.music_changed.connect(dialog.sincronizar_musica_atual)
        dialog.playlist_updated.connect(self.atualizar_playlists)
        dialog.playlist_deleted.connect(self._playlist_deleted)
        dialog.destroyed.connect(lambda _=None, opened=dialog: self._forget_dialog(opened))
        self._open_dialogs.append(dialog)
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def _playlist_deleted(self) -> None:
        self.atualizar_playlists()
        self.entrada.clear()
        self.mostrar_lista()

    def criar_playlist_nova(self) -> None:
        nome, ok = QInputDialog.getText(self, "Criar playlist", "Nome da playlist:")
        if not ok:
            return
        try:
            create_playlist(nome)
        except ValueError as exc:
            QMessageBox.warning(self, "Atencao", str(exc))
            return
        self.atualizar_playlists()

    def mostrar_lista(self, musicas=None) -> None:
        self.musica_atual = None
        self._clear_content()
        if musicas is None:
            musicas = listar_musicas()
        self.musicas_visiveis = list(musicas)
        self.music_rows = []

        scroll, _, layout = self._create_scroll()
        self.content_layout.addWidget(scroll)

        header = QFrame()
        header.setObjectName("card")
        header_layout = QGridLayout(header)
        header_layout.setContentsMargins(10, 8, 10, 8)
        for column, title in enumerate(["NOME", "ARTISTA", "ALBUM", "ANO"]):
            label = QLabel(title)
            label.setObjectName("sectionLabel")
            header_layout.addWidget(label, 0, column)
            header_layout.setColumnStretch(column, 1 if column < 3 else 0)
        layout.addWidget(header)

        if not musicas:
            empty = QLabel("Nenhuma musica cadastrada ainda.\nUse o menu para adicionar.")
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty)
            layout.addStretch(1)
            return

        for index, musica in enumerate(musicas):
            row = _TableRow(musica, alternate=bool(index % 2))
            row.clicked.connect(self.selecionar_musica)
            row.double_clicked.connect(self.abrir_janela_musica)
            self.music_rows.append(row)
            layout.addWidget(row)
        layout.addStretch(1)

    def selecionar_musica(self, musica) -> None:
        self.musica_atual = musica
        music_id = self._music_id(musica)
        for row in self.music_rows:
            row.set_selected(self._music_id(row.musica) == music_id)

    def abrir_janela_musica(self, musica, fila=None) -> None:
        self.selecionar_musica(musica)
        if self.player_window is None:
            self.player_window = MusicPlayerWindow(self.playback_controller, self)
        self.player_window.reproduzir(musica, list(fila or self.musicas_visiveis))

    def _forget_dialog(self, dialog) -> None:
        if dialog in self._open_dialogs:
            self._open_dialogs.remove(dialog)

    @staticmethod
    def _music_id(musica) -> object:
        if hasattr(musica, "id"):
            return musica.id
        if isinstance(musica, (tuple, list)) and musica:
            return musica[0]
        return None

    def mostrar_card(self, musica) -> None:
        self.musica_atual = musica
        _, nome, artista, album, ano, cifra, tablatura, audio, link_externo, partitura, *_ = musica
        self._clear_content()

        scroll, _, layout = self._create_scroll()
        self.content_layout.addWidget(scroll)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(8)

        title = QLabel((nome or "").upper())
        title.setObjectName("titleLabel")
        artist = QLabel(artista or "-")
        artist.setObjectName("mutedLabel")
        card_layout.addWidget(title)
        card_layout.addWidget(artist)

        partes = []
        if album:
            partes.append(album)
        if ano:
            partes.append(str(ano))
        if partes:
            meta = QLabel("  .  ".join(partes))
            meta.setObjectName("mutedLabel")
            card_layout.addWidget(meta)

        line = QFrame()
        line.setObjectName("separator")
        card_layout.addWidget(line)

        for text, slot, active in [
            ("CIFRA", lambda: self.abrir_viewer("Cifra", cifra), bool(cifra)),
            ("TABLATURA", lambda: self.abrir_viewer("Tablatura", tablatura), bool(tablatura)),
            ("PARTITURA", self.visualizar_partitura, bool(partitura)),
            ("AUDIO", self.tocar_audio, bool(audio)),
            ("LINK EXTERNO", self.abrir_link_externo, bool(link_externo)),
        ]:
            button = QPushButton(text)
            button.setEnabled(active)
            button.clicked.connect(slot)
            card_layout.addWidget(button)

        layout.addWidget(card)
        layout.addStretch(1)

    def mostrar_nao_encontrado(self) -> None:
        self.musica_atual = None
        self._clear_content()
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        empty = QLabel("Musica nao encontrada.")
        empty.setObjectName("emptyLabel")
        empty.setAlignment(Qt.AlignCenter)
        layout.addWidget(empty)
        self.content_layout.addWidget(card)
        self.content_layout.addStretch(1)

    def schedule_search(self) -> None:
        self.search_timer.start()

    def on_busca(self) -> None:
        self.search_timer.stop()
        texto = self.entrada.text().strip()
        if not texto:
            self.mostrar_lista()
            return
        resultados = filtrar_musicas(texto)
        if not resultados:
            self.mostrar_nao_encontrado()
        else:
            self.mostrar_lista(resultados)

    def adicionar(self) -> None:
        dialog = AddMusicWindow(self)
        dialog.musica_salva.connect(self._after_music_change)
        dialog.exec()

    def editar(self) -> None:
        if not self.musica_atual:
            QMessageBox.warning(self, "Atencao", "Selecione ou busque uma musica primeiro!")
            return
        dialog = EditMusicWindow(self.musica_atual, self)
        dialog.musica_salva.connect(self._after_music_change)
        dialog.musica_excluida.connect(self._after_music_change)
        dialog.exec()

    def _after_music_change(self) -> None:
        self.entrada.clear()
        self.mostrar_lista()
        self.atualizar_playlists()

    def excluir(self) -> None:
        if not self.musica_atual:
            QMessageBox.warning(self, "Atencao", "Selecione ou busque uma musica primeiro!")
            return
        nome = self.musica_atual[1]
        resposta = QMessageBox.question(self, "Confirmar exclusao", f'Tem certeza que deseja excluir "{nome}"?')
        if resposta != QMessageBox.Yes:
            return
        excluir_musica(self.musica_atual[0])
        QMessageBox.information(self, "Excluido", f'"{nome}" foi excluida.')
        self._after_music_change()

    def abrir_viewer(self, titulo: str, conteudo: str) -> None:
        TextViewerDialog(titulo, conteudo or "", self).exec()

    def tocar_audio(self) -> None:
        audio = self.musica_atual[7] if self.musica_atual else ""
        if not audio:
            return
        if os.path.exists(audio):
            os.startfile(audio)
        else:
            QMessageBox.warning(self, "Aviso", f"Arquivo de audio nao encontrado:\n{audio}")

    def abrir_link_externo(self) -> None:
        link_externo = self.musica_atual[8] if self.musica_atual else ""
        if link_externo:
            webbrowser.open(link_externo)

    def visualizar_partitura(self) -> None:
        partitura = self.musica_atual[9] if self.musica_atual else ""
        if not partitura:
            return
        if os.path.exists(partitura):
            os.startfile(partitura)
        else:
            QMessageBox.warning(self, "Aviso", f"Arquivo de partitura nao encontrado:\n{partitura}")


def iniciar_interface() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    qss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "styles", "theme.qss"))
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as theme_file:
            app.setStyleSheet(theme_file.read())
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
