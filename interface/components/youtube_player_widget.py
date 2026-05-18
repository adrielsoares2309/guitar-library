import webbrowser

from PySide6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget


class YoutubePlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._url = ""

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.url_label = QLabel("Nenhum link externo")
        self.url_label.setObjectName("mutedLabel")
        self.open_button = QPushButton("ABRIR LINK")
        self.open_button.clicked.connect(self.open_link)

        layout.addWidget(self.url_label, 1)
        layout.addWidget(self.open_button)

    def set_url(self, url: str) -> None:
        self._url = url or ""
        self.url_label.setText(self._url or "Nenhum link externo")
        self.open_button.setEnabled(bool(self._url))

    def open_link(self) -> None:
        if self._url:
            webbrowser.open(self._url)
