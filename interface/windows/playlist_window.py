from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.playlist.playlist_search_manager import PlaylistSearchManager
from services.music_service import listar_musicas
from services.playlist_service import (
    add_music_to_playlist,
    delete_playlist,
    get_playlist,
    remove_music_from_playlist,
)


def _refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class _MusicRow(QFrame):
    clicked = Signal(object)
    double_clicked = Signal(object)

    def __init__(self, musica, alternate: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.musica = musica
        self.setProperty("row", True)
        self.setProperty("alternate", alternate)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        name = QLabel(getattr(musica, "nome", "") or "-")
        font = name.font()
        font.setBold(True)
        name.setFont(font)

        subtitulo = getattr(musica, "artista", "") or "-"
        album = getattr(musica, "album", "") or ""
        if album:
            subtitulo = f"{subtitulo}  -  {album}"
        details = QLabel(subtitulo)
        details.setObjectName("mutedLabel")

        layout.addWidget(name)
        layout.addWidget(details)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        _refresh_style(self)

    def set_alternate(self, alternate: bool) -> None:
        self.setProperty("alternate", alternate)
        _refresh_style(self)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.musica)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.musica)
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event) -> None:
        if not self.property("selected"):
            self.setProperty("hovered", True)
            _refresh_style(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hovered", False)
        _refresh_style(self)
        super().leaveEvent(event)


class _TupleMusicRow(QFrame):
    add_requested = Signal(int)

    def __init__(self, musica, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.musica = musica
        self.setObjectName("card")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        texts = QVBoxLayout()
        name = QLabel(musica[1] or "-")
        font = name.font()
        font.setBold(True)
        name.setFont(font)
        artist = QLabel(musica[2] or "-")
        artist.setObjectName("mutedLabel")
        texts.addWidget(name)
        texts.addWidget(artist)

        button = QPushButton("Adicionar")
        button.clicked.connect(lambda: self.add_requested.emit(musica[0]))
        layout.addLayout(texts, 1)
        layout.addWidget(button)


class AddToPlaylistDialog(QDialog):
    music_added = Signal(int)

    def __init__(self, playlist, parent=None) -> None:
        super().__init__(parent)
        self.playlist = playlist
        self.setWindowTitle("Adicionar musica")
        self.resize(420, 480)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(10)

        title = QLabel("Adicionar musica a playlist")
        title.setObjectName("titleLabel")
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        musicas = listar_musicas()
        ids_existentes = {musica.id for musica in playlist.musicas}
        disponiveis = [musica for musica in musicas if musica[0] not in ids_existentes]

        if not disponiveis:
            empty = QLabel("Todas as musicas ja estao nesta playlist.")
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(empty)
            content_layout.addStretch(1)
            return

        for musica in disponiveis:
            row = _TupleMusicRow(musica)
            row.add_requested.connect(self._add)
            content_layout.addWidget(row)
        content_layout.addStretch(1)

    def _add(self, music_id: int) -> None:
        self.music_added.emit(music_id)
        self.accept()


class PlaylistWindow(QDialog):
    playlist_updated = Signal()
    playlist_deleted = Signal()
    musicaSelecionada = Signal(object, object)

    def __init__(self, parent=None, playlist_id=None, on_playlist_updated=None, on_playlist_deleted=None, master=None):
        super().__init__(parent or master)
        self.playlist_id = playlist_id
        self.playlist = None
        self.musica_atual = None
        self.search_manager = PlaylistSearchManager()
        self.music_rows: list[_MusicRow] = []
        self.search_text = ""
        self.side_panel_visible = False

        if on_playlist_updated:
            self.playlist_updated.connect(on_playlist_updated)
        if on_playlist_deleted:
            self.playlist_deleted.connect(on_playlist_deleted)

        self.setWindowTitle("Playlist")
        self.resize(860, 560)
        self.setMinimumSize(760, 520)
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(90)
        self.search_timer.timeout.connect(self.apply_search)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(10)

        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        self.title_label = QLabel("PLAYLIST")
        self.title_label.setObjectName("titleLabel")
        self.info_label = QLabel("")
        self.info_label.setObjectName("mutedLabel")
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(self.toggle_side_panel)
        add_button = QPushButton("+")
        add_button.setObjectName("iconButton")
        add_button.clicked.connect(self.abrir_seletor_musicas)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.info_label)
        header_layout.addStretch(1)
        header_layout.addWidget(edit_button)
        header_layout.addWidget(add_button)
        root.addWidget(header)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(12)
        root.addLayout(main_layout, 1)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        main_layout.addWidget(content, 1)

        search_box = QFrame()
        search_box.setObjectName("searchBox")
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(12, 2, 8, 2)
        self.search_entry = QLineEdit()
        self.search_entry.setObjectName("searchInput")
        self.search_entry.setPlaceholderText("Buscar nesta playlist...")
        self.search_entry.textChanged.connect(self.schedule_search)
        self.search_entry.returnPressed.connect(self.apply_search)
        self.clear_search_button = QPushButton("X")
        self.clear_search_button.setObjectName("secondaryButton")
        self.clear_search_button.clicked.connect(self.clear_search)
        search_layout.addWidget(self.search_entry, 1)
        search_layout.addWidget(self.clear_search_button)
        content_layout.addWidget(search_box)

        self.music_scroll = QScrollArea()
        self.music_scroll.setWidgetResizable(True)
        self.music_content = QWidget()
        self.music_content.setObjectName("scrollContent")
        self.music_layout = QVBoxLayout(self.music_content)
        self.music_layout.setContentsMargins(0, 0, 0, 0)
        self.music_layout.setSpacing(8)
        self.music_scroll.setWidget(self.music_content)
        content_layout.addWidget(self.music_scroll, 1)

        self.side_panel = QFrame()
        self.side_panel.setObjectName("panel")
        self.side_panel.setFixedWidth(250)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(14, 14, 14, 14)
        self.side_layout.setSpacing(8)
        self.side_panel.hide()
        main_layout.addWidget(self.side_panel)

    def refresh(self) -> None:
        self.playlist = get_playlist(self.playlist_id)
        if not self.playlist:
            QMessageBox.warning(self, "Atencao", "A playlist selecionada nao existe mais.")
            self.reject()
            return

        self.title_label.setText((self.playlist.nome or "PLAYLIST").upper())
        self.info_label.setText(f"{len(self.playlist.musicas)} musica(s)")
        self.search_manager.set_musicas(self.playlist.musicas)

        if self.musica_atual:
            current_id = self.musica_atual.id
            self.musica_atual = next((m for m in self.playlist.musicas if m.id == current_id), None)

        self.render_music_list()
        self.render_side_panel()
        self.playlist_updated.emit()

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def render_music_list(self) -> None:
        self._clear_layout(self.music_layout)
        self.music_rows = []

        if not self.playlist.musicas:
            self.search_entry.setEnabled(False)
            self.clear_search_button.setEnabled(False)
            empty = QLabel("Nenhuma musica na playlist ainda.\nUse o botao + para adicionar.")
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            self.music_layout.addWidget(empty)
            self.music_layout.addStretch(1)
            return

        self.search_entry.setEnabled(True)
        for index, musica in enumerate(self.playlist.musicas):
            row = _MusicRow(musica, alternate=bool(index % 2))
            row.clicked.connect(self._select_music)
            row.double_clicked.connect(self._play_music)
            self.music_rows.append(row)
            self.music_layout.addWidget(row)
        self.no_results_label = QLabel("No songs found")
        self.no_results_label.setObjectName("emptyLabel")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.music_layout.addWidget(self.no_results_label)
        self.music_layout.addStretch(1)
        self.apply_search()

    def schedule_search(self) -> None:
        self.search_timer.start()

    def clear_search(self) -> None:
        self.search_entry.clear()
        self.apply_search()

    def apply_search(self) -> None:
        self.search_timer.stop()
        self.search_text = self.search_entry.text().strip()
        resultados = self.search_manager.filter(self.search_text)
        ids_visiveis = {musica.id for musica in resultados}
        visible_count = 0

        for row in self.music_rows:
            visible = row.musica.id in ids_visiveis
            row.setVisible(visible)
            if visible:
                row.set_alternate(bool(visible_count % 2))
                visible_count += 1
            row.set_selected(bool(self.musica_atual and self.musica_atual.id == row.musica.id))

        self.clear_search_button.setEnabled(bool(self.search_text))
        if hasattr(self, "no_results_label"):
            self.no_results_label.setVisible(bool(self.playlist.musicas and not visible_count))

    def _select_music(self, musica) -> None:
        self.musica_atual = musica
        self._sync_selected_row()

    def _play_music(self, musica) -> None:
        self.musica_atual = musica
        self._sync_selected_row()
        self.musicaSelecionada.emit(musica, list(self.playlist.musicas if self.playlist else [musica]))

    def sincronizar_musica_atual(self, musica) -> None:
        if not musica:
            return
        current_id = getattr(musica, "id", None)
        if current_id is None and isinstance(musica, (tuple, list)) and musica:
            current_id = musica[0]
        self.musica_atual = next(
            (item for item in (self.playlist.musicas if self.playlist else []) if item.id == current_id),
            self.musica_atual,
        )
        self._sync_selected_row()

    def _sync_selected_row(self) -> None:
        for row in self.music_rows:
            row.set_selected(bool(self.musica_atual and row.musica.id == self.musica_atual.id))

    def toggle_side_panel(self) -> None:
        self.side_panel_visible = not self.side_panel_visible
        self.side_panel.setVisible(self.side_panel_visible)

    def render_side_panel(self) -> None:
        self._clear_layout(self.side_layout)
        title = QLabel("EDITAR PLAYLIST")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Remover musicas desta playlist")
        subtitle.setObjectName("mutedLabel")
        self.side_layout.addWidget(title)
        self.side_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")
        list_layout = QVBoxLayout(content)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(8)
        scroll.setWidget(content)
        self.side_layout.addWidget(scroll, 1)

        if not self.playlist.musicas:
            empty = QLabel("Sem musicas para remover.")
            empty.setObjectName("emptyLabel")
            list_layout.addWidget(empty)
        else:
            for musica in self.playlist.musicas:
                item = QFrame()
                item.setObjectName("sideItem")
                row = QHBoxLayout(item)
                row.setContentsMargins(10, 8, 10, 8)
                texts = QVBoxLayout()
                name = QLabel(musica.nome)
                font = name.font()
                font.setBold(True)
                name.setFont(font)
                artist = QLabel(musica.artista or "-")
                artist.setObjectName("mutedLabel")
                texts.addWidget(name)
                texts.addWidget(artist)
                remove = QPushButton("X")
                remove.setObjectName("iconButton")
                remove.clicked.connect(lambda checked=False, music_id=musica.id: self.remover_musica(music_id))
                row.addLayout(texts, 1)
                row.addWidget(remove)
                list_layout.addWidget(item)
        list_layout.addStretch(1)

        delete_button = QPushButton("EXCLUIR PLAYLIST")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self.excluir_playlist)
        self.side_layout.addWidget(delete_button)

    def abrir_seletor_musicas(self) -> None:
        dialog = AddToPlaylistDialog(self.playlist, self)
        dialog.music_added.connect(lambda music_id: self.adicionar_musica(music_id))
        dialog.exec()

    def adicionar_musica(self, music_id: int) -> None:
        try:
            add_music_to_playlist(self.playlist_id, music_id)
        except ValueError as exc:
            QMessageBox.warning(self, "Atencao", str(exc))
            return
        self.refresh()

    def remover_musica(self, music_id: int) -> None:
        remove_music_from_playlist(self.playlist_id, music_id)
        if self.musica_atual and self.musica_atual.id == music_id:
            self.musica_atual = None
        self.refresh()

    def excluir_playlist(self) -> None:
        nome = self.playlist.nome if self.playlist else "esta playlist"
        resposta = QMessageBox.question(self, "Confirmar exclusao", f'Tem certeza que deseja excluir "{nome}"?')
        if resposta != QMessageBox.Yes:
            return
        delete_playlist(self.playlist_id)
        self.playlist_deleted.emit()
        self.accept()


def abrir_janela_playlist(master, playlist_id, on_playlist_updated=None, on_playlist_deleted=None):
    dialog = PlaylistWindow(
        parent=master,
        playlist_id=playlist_id,
        on_playlist_updated=on_playlist_updated,
        on_playlist_deleted=on_playlist_deleted,
    )
    if hasattr(master, "_open_dialogs"):
        master._open_dialogs.append(dialog)
        dialog.destroyed.connect(lambda _=None, opened=dialog: master._forget_dialog(opened))
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    return dialog
