from PySide6.QtCore import QObject, Signal


class QueueManager(QObject):
    current_changed = Signal(object)
    queue_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._queue: list[object] = []
        self._current_index = -1

    def set_queue(self, musicas: list[object], current_music: object | None = None) -> None:
        self._queue = list(musicas)
        self._current_index = 0 if self._queue else -1

        if current_music is not None:
            current_id = self._music_id(current_music)
            for index, musica in enumerate(self._queue):
                if self._music_id(musica) == current_id:
                    self._current_index = index
                    break

        self.queue_changed.emit()
        self.current_changed.emit(self.atual())

    def adicionar(self, musica: object) -> None:
        self._queue.append(musica)
        if self._current_index < 0:
            self._current_index = 0
            self.current_changed.emit(self.atual())
        self.queue_changed.emit()

    def remover(self, musica: object) -> None:
        music_id = self._music_id(musica)
        for index, item in enumerate(self._queue):
            if self._music_id(item) == music_id:
                del self._queue[index]
                if index <= self._current_index:
                    self._current_index -= 1
                if self._queue and self._current_index < 0:
                    self._current_index = 0
                if self._current_index >= len(self._queue):
                    self._current_index = len(self._queue) - 1
                self.queue_changed.emit()
                self.current_changed.emit(self.atual())
                return

    def proxima(self) -> object | None:
        if not self._queue:
            return None
        if self._current_index + 1 >= len(self._queue):
            return None
        self._current_index += 1
        musica = self.atual()
        self.current_changed.emit(musica)
        return musica

    def anterior(self) -> object | None:
        if not self._queue:
            return None
        if self._current_index <= 0:
            return None
        self._current_index -= 1
        musica = self.atual()
        self.current_changed.emit(musica)
        return musica

    def atual(self) -> object | None:
        if self._current_index < 0 or self._current_index >= len(self._queue):
            return None
        return self._queue[self._current_index]

    def limpar_fila(self) -> None:
        self._queue.clear()
        self._current_index = -1
        self.queue_changed.emit()
        self.current_changed.emit(None)

    @staticmethod
    def _music_id(musica: object) -> object:
        if hasattr(musica, "id"):
            return getattr(musica, "id")
        if isinstance(musica, (tuple, list)) and musica:
            return musica[0]
        return id(musica)
