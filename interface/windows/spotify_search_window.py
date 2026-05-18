from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def _refresh_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)


class _ResultCard(QFrame):
    clicked = Signal(object)

    def __init__(self, resultado: dict, alternate: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.resultado = resultado
        self.setProperty("row", True)
        self.setProperty("alternate", alternate)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)

        title = QLabel(resultado.get("nome", "") or "-")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)

        detalhes = [
            resultado.get("artista", "") or "-",
            resultado.get("album", "") or "-",
            resultado.get("ano", "") or "-",
        ]
        subtitle = QLabel("  -  ".join(detalhes))
        subtitle.setObjectName("mutedLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.resultado)
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        self.setProperty("selected", True)
        _refresh_style(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("selected", False)
        _refresh_style(self)
        super().leaveEvent(event)


class SpotifySearchWindow(QDialog):
    selected = Signal(dict)

    def __init__(self, parent=None, resultados=None, on_select=None, master=None) -> None:
        super().__init__(parent or master)
        self.resultados = resultados or []
        if on_select:
            self.selected.connect(on_select)

        self.setWindowTitle("Resultados Spotify")
        self.resize(560, 420)
        self.setMinimumSize(480, 360)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(10)

        title = QLabel("RESULTADOS SPOTIFY")
        title.setObjectName("titleLabel")
        count = QLabel(f"{len(self.resultados)} resultado(s)")
        count.setObjectName("mutedLabel")
        root.addWidget(title)
        root.addWidget(count)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        if not self.resultados:
            empty = QLabel("Nenhuma musica encontrada.")
            empty.setObjectName("emptyLabel")
            empty.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(empty)
            content_layout.addStretch(1)
            return

        for index, item in enumerate(self.resultados):
            card = _ResultCard(item, alternate=bool(index % 2))
            card.clicked.connect(self._select)
            content_layout.addWidget(card)
        content_layout.addStretch(1)

    def _select(self, resultado: dict) -> None:
        self.selected.emit(resultado)
        self.accept()
