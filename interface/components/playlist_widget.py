from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def _refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class _ClickableFrame(QFrame):
    clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        self.setProperty("hovered", True)
        _refresh_style(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hovered", False)
        _refresh_style(self)
        super().leaveEvent(event)


class PlaylistWidget(QWidget):
    open_playlist_requested = Signal(object)
    create_playlist_requested = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        on_open_playlist=None,
        on_create_playlist=None,
    ) -> None:
        super().__init__(parent)
        self.playlists = []
        if on_open_playlist:
            self.open_playlist_requested.connect(on_open_playlist)
        if on_create_playlist:
            self.create_playlist_requested.connect(on_create_playlist)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 8, 16, 10)
        root.setSpacing(4)

        title = QLabel("PLAYLISTS")
        title.setObjectName("sectionLabel")
        root.addWidget(title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFixedHeight(118)

        self.content = QWidget()
        self.content.setObjectName("scrollContent")
        self.list_layout = QHBoxLayout(self.content)
        self.list_layout.setContentsMargins(0, 4, 0, 4)
        self.list_layout.setSpacing(10)
        self.scroll.setWidget(self.content)
        root.addWidget(self.scroll)

        self.render()

    def set_playlists(self, playlists) -> None:
        self.playlists = playlists or []
        self.render()

    def render(self) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        add_button = QPushButton("+")
        add_button.setObjectName("iconButton")
        add_button.setFixedSize(58, 86)
        add_button.clicked.connect(self.create_playlist_requested.emit)
        self.list_layout.addWidget(add_button)

        if not self.playlists:
            empty = QLabel("Nenhuma playlist criada ainda.")
            empty.setObjectName("emptyLabel")
            self.list_layout.addWidget(empty)
            self.list_layout.addStretch(1)
            return

        for playlist in self.playlists:
            self.list_layout.addWidget(self._create_playlist_card(playlist))
        self.list_layout.addStretch(1)

    def _create_playlist_card(self, playlist) -> QFrame:
        card = _ClickableFrame()
        card.setProperty("playlistCard", True)
        card.setFixedSize(132, 86)
        card.clicked.connect(lambda item=playlist: self.open_playlist_requested.emit(item))

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(4)

        name = QLabel(getattr(playlist, "nome", "") or "-")
        name.setWordWrap(True)
        font = name.font()
        font.setBold(True)
        name.setFont(font)

        total = getattr(playlist, "total_musicas", 0)
        count = QLabel(f"{total} musica(s)")
        count.setObjectName("mutedLabel")

        layout.addWidget(name)
        layout.addStretch(1)
        layout.addWidget(count)
        return card
