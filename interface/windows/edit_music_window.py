import os

from PySide6.QtCore import Signal
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

from services.music_service import editar_musica, excluir_musica


class EditMusicWindow(QDialog):
    musica_salva = Signal()
    musica_excluida = Signal()

    def __init__(self, musica, parent=None) -> None:
        super().__init__(parent)
        self.musica = musica
        self.id_musica = musica[0]
        self.novo_audio = musica[7] or ""
        self.link_externo = musica[8] or ""
        self.nova_partitura = musica[9] or ""

        self.setWindowTitle("Editar Musica")
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
        title = QLabel("Editar Musica")
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

        self.nome_entry = self._add_line_edit("NOME  *", "Nome da musica", self.musica[1] or "")
        self.artista_entry = self._add_line_edit("ARTISTA  *", "Nome do artista", self.musica[2] or "")
        self.album_entry = self._add_line_edit("ALBUM", "Nome do album", self.musica[3] or "")
        self.ano_entry = self._add_line_edit("ANO", "Ex: 2024", str(self.musica[4]) if self.musica[4] else "")
        self._add_separator()
        self.cifra_text = self._add_text_edit("CIFRA  (acordes)", 110, self.musica[5] or "")
        self.tablatura_text = self._add_text_edit("TABLATURA  (ASCII)", 130, self.musica[6] or "")
        self._add_separator()
        self.audio_label = self._add_file_picker(
            "AUDIO",
            os.path.basename(self.novo_audio) if self.novo_audio else "Nenhum arquivo selecionado",
            "TROCAR AUDIO",
            self._selecionar_audio,
        )
        self.partitura_label = self._add_file_picker(
            "PARTITURA  (PDF)",
            os.path.basename(self.nova_partitura) if self.nova_partitura else "Nenhum arquivo selecionado",
            "TROCAR PARTITURA",
            self._selecionar_partitura,
        )
        self._add_separator()

        save_button = QPushButton("SALVAR ALTERACOES")
        save_button.clicked.connect(self._salvar)
        self.form_layout.addWidget(save_button)

        delete_button = QPushButton("EXCLUIR MUSICA")
        delete_button.setObjectName("dangerButton")
        delete_button.clicked.connect(self._excluir)
        self.form_layout.addWidget(delete_button)

    def _add_section(self, text: str) -> None:
        label = QLabel(text)
        label.setObjectName("sectionLabel")
        self.form_layout.addWidget(label)

    def _add_line_edit(self, label: str, placeholder: str, value: str) -> QLineEdit:
        self._add_section(label)
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.setText(value)
        self.form_layout.addWidget(entry)
        return entry

    def _add_text_edit(self, label: str, height: int, value: str) -> QPlainTextEdit:
        self._add_section(label)
        text = QPlainTextEdit()
        text.setObjectName("monoText")
        text.setFixedHeight(height)
        text.setLineWrapMode(QPlainTextEdit.NoWrap)
        text.setPlainText(value)
        self.form_layout.addWidget(text)
        return text

    def _add_separator(self) -> None:
        line = QFrame()
        line.setObjectName("separator")
        self.form_layout.addWidget(line)

    def _add_file_picker(self, label: str, current_text: str, button_text: str, slot) -> QLabel:
        self._add_section(label)
        selected = QLabel(current_text)
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
            self.novo_audio = arquivo
            self.audio_label.setText(os.path.basename(arquivo))

    def _selecionar_partitura(self) -> None:
        arquivo, _ = QFileDialog.getOpenFileName(self, "Selecionar Partitura", "", "PDF files (*.pdf)")
        if arquivo:
            self.nova_partitura = arquivo
            self.partitura_label.setText(os.path.basename(arquivo))

    def _salvar(self) -> None:
        nome = self.nome_entry.text().strip()
        artista = self.artista_entry.text().strip()
        album = self.album_entry.text().strip()
        ano_str = self.ano_entry.text().strip()
        cifra = self.cifra_text.toPlainText().strip()
        tablatura = self.tablatura_text.toPlainText().strip()

        if not nome or not artista:
            QMessageBox.warning(self, "Atencao", "Nome e Artista sao obrigatorios!")
            return

        ano = None
        if ano_str:
            if not ano_str.isdigit() or len(ano_str) != 4:
                QMessageBox.warning(self, "Atencao", "Ano invalido! Use o formato: 2024")
                return
            ano = int(ano_str)

        editar_musica(
            self.id_musica,
            nome,
            artista,
            album,
            ano,
            cifra,
            tablatura,
            self.novo_audio,
            self.link_externo,
            self.nova_partitura,
        )
        QMessageBox.information(self, "Sucesso", f'"{nome}" atualizada com sucesso!')
        self.musica_salva.emit()
        self.accept()

    def _excluir(self) -> None:
        nome = self.nome_entry.text().strip() or "esta musica"
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f'Tem certeza que deseja excluir "{nome}"?',
        )
        if resposta != QMessageBox.Yes:
            return
        excluir_musica(self.id_musica)
        QMessageBox.information(self, "Excluido", f'"{nome}" foi excluida.')
        self.musica_excluida.emit()
        self.accept()


def abrir_janela_editar(musica, ao_salvar=None, parent=None):
    dialog = EditMusicWindow(musica, parent)
    if ao_salvar:
        dialog.musica_salva.connect(ao_salvar)
        dialog.musica_excluida.connect(ao_salvar)
    dialog.exec()
    return dialog
