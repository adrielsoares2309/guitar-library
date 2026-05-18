# Gralha — Base técnica para o Codex

> Documento de referência consolidado para agentes de engenharia.
> Cobre: nova arquitetura, servidor local via FastAPI, migração CustomTkinter → PySide6.

---

## 1. Contexto do projeto

**Gralha** é um gerenciador de biblioteca musical para guitarristas. Permite cadastrar músicas com cifra, tablatura, partitura e áudio, buscar e organizar em playlists, e integrar com Spotify para busca de metadados.

**Stack atual:**
- Python 3.12
- CustomTkinter (sendo migrado para PySide6)
- SQLite3
- Pillow
- spotipy (integração Spotify)

**Novo objetivo:** além do app desktop, o Gralha deve funcionar como servidor local opcional — permitindo que celulares e outros computadores na mesma rede Wi-Fi acessem o acervo via navegador, sem instalação.

---

## 2. Arquitetura atual (antes das mudanças)

```
gralha/
├── assets/
│   ├── icons/
│   └── logo.png
├── database/
│   ├── database.py
│   ├── models/
│   │   ├── musica.py
│   │   └── playlist.py
│   └── musicas.db
├── interface/
│   ├── windows/
│   │   ├── main_window.py
│   │   ├── add_music_window.py
│   │   ├── edit_music_window.py
│   │   ├── playlist_window.py
│   │   └── spotify_search_window.py
│   ├── components/
│   │   ├── player_widget.py
│   │   ├── playlist_widget.py
│   │   └── youtube_player_widget.py
│   └── styles/
│       └── theme.qss
├── core/
│   ├── player/
│   │   ├── player_controller.py
│   │   ├── audio_engine.py
│   │   └── timer.py
│   └── playlist/
│       ├── playlist_controller.py
│       └── playlist_search_manager.py
├── services/
│   ├── music_service.py
│   ├── playlist_service.py
│   └── spotify_service.py
├── integrations/
│   ├── spotify/
│   │   └── spotify_client.py
│   └── youtube/
│       └── youtube_service.py
├── utils/
│   └── helpers.py
├── config/
│   └── settings.py
└── main.py
```

---

## 3. Nova arquitetura alvo

```
gralha/
├── assets/
│   ├── icons/
│   └── logo.png
│
├── database/
│   ├── database.py
│   ├── models/
│   │   ├── musica.py
│   │   ├── playlist.py
│   │   └── user.py                      # NOVO — modelo de usuário
│   └── musicas.db
│
├── interface/                            # MIGRADO para PySide6
│   ├── windows/
│   │   ├── main_window.py
│   │   ├── add_music_window.py
│   │   ├── edit_music_window.py
│   │   ├── playlist_window.py
│   │   ├── spotify_search_window.py
│   │   ├── server_window.py             # NOVO — painel ligar/desligar servidor
│   │   └── login_window.py              # NOVO — tela de login desktop
│   ├── components/
│   │   ├── player_widget.py
│   │   ├── playlist_widget.py
│   │   ├── youtube_player_widget.py
│   │   └── qr_display_widget.py         # NOVO — exibe QR code com IP:porta
│   └── styles/
│       └── theme.qss                    # QSS nativo do Qt
│
├── server/                              # NOVO — módulo completo do servidor
│   ├── __init__.py
│   ├── app.py                           # cria o app FastAPI, registra routers
│   ├── server_manager.py                # QThread que roda o Uvicorn
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── music_routes.py              # GET /api/musicas, GET /api/musicas/{id}
│   │   ├── playlist_routes.py           # CRUD playlists via API
│   │   ├── stream_routes.py             # GET /stream/{id} com Range headers
│   │   └── auth_routes.py              # POST /login, POST /logout
│   ├── schemas/
│   │   ├── music_schema.py              # Pydantic — serialização de Musica
│   │   └── playlist_schema.py
│   ├── middleware/
│   │   ├── auth_middleware.py           # verifica JWT em cada request
│   │   └── cors_middleware.py           # libera origem da rede local
│   ├── discovery/
│   │   └── mdns_service.py              # anuncia gralha.local via zeroconf
│   └── web/                             # cliente web servido pelo servidor
│       ├── index.html
│       ├── static/
│       │   ├── app.js
│       │   └── style.css
│
├── core/
│   ├── player/
│   │   ├── player_controller.py
│   │   ├── audio_engine.py
│   │   └── timer.py
│   ├── playlist/
│   │   ├── playlist_controller.py
│   │   └── playlist_search_manager.py
│   └── auth/                            # NOVO
│       └── auth_controller.py           # cria usuário, valida senha, gera JWT
│
├── services/
│   ├── music_service.py
│   ├── playlist_service.py
│   ├── spotify_service.py
│   └── user_service.py                  # NOVO — CRUD de usuários
│
├── integrations/
│   ├── spotify/
│   │   └── spotify_client.py
│   └── youtube/
│       └── youtube_service.py
│
├── utils/
│   ├── helpers.py
│   ├── network.py                       # NOVO — get_local_ip()
│   └── qrcode_gen.py                    # NOVO — gera QR code como QPixmap
│
├── config/
│   └── settings.py                      # SERVER_PORT, ADMIN_HASH, ENABLE_AUTH
│
└── main.py
```

---

## 4. Dependências

### Existentes (manter)
```
customtkinter       # sendo removido após migração
pillow
spotipy
python-dotenv
```

### Novas — interface
```
PySide6
```

### Novas — servidor
```
fastapi
uvicorn
pydantic
python-jose[cryptography]    # JWT
passlib[bcrypt]              # hash de senha
zeroconf                     # mDNS para descoberta automática
qrcode[pil]                  # geração de QR code
python-multipart             # uploads via API (opcional)
```

Instalação completa:
```bash
pip install PySide6 fastapi uvicorn pydantic "python-jose[cryptography]" "passlib[bcrypt]" zeroconf "qrcode[pil]"
```

---

## 5. Servidor local — como funciona

### Modelo mental

O servidor faz duas coisas ao mesmo tempo:

1. **Serve o HTML/CSS/JS** — o celular abre o IP e recebe `index.html`. Acontece uma vez.
2. **Responde às chamadas da API** — o JavaScript no celular faz `fetch('/api/musicas')` e recebe JSON com os dados do banco.

### Por que FastAPI + Uvicorn

- Mais moderno e performático que Flask
- Suporte nativo a streaming de áudio com `StreamingResponse`
- Validação automática de dados via Pydantic
- Documentação interativa automática em `/docs`
- Assíncrono nativo

### Problema: desktop + servidor no mesmo processo

O Qt tem seu próprio loop de eventos (`app.exec()`). O Uvicorn também tem o seu. Rodar os dois no mesmo thread trava um dos dois.

**Solução:** o servidor roda em `QThread` separado. Comunicação com a UI acontece exclusivamente via signals — nunca tocar em widgets de outro thread diretamente.

---

## 6. Implementação do servidor

### `server/app.py`

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from server.routes import music_routes, playlist_routes, stream_routes

app = FastAPI(title="Gralha API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # rede local — sem restrição de origem
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(music_routes.router,    prefix="/api")
app.include_router(playlist_routes.router, prefix="/api")
app.include_router(stream_routes.router)

app.mount("/static", StaticFiles(directory="server/web/static"), name="static")

@app.get("/")
def index():
    return FileResponse("server/web/index.html")
```

### `server/routes/music_routes.py`

```python
from fastapi import APIRouter
from services.music_service import listar_musicas, filtrar_musicas

router = APIRouter()

@router.get("/musicas")
def get_musicas(q: str = ""):
    if q:
        musicas = filtrar_musicas(q)
    else:
        musicas = listar_musicas()
    return [
        {
            "id": m[0], "nome": m[1], "artista": m[2],
            "album": m[3], "ano": m[4],
            "tem_cifra": bool(m[5]), "tem_tablatura": bool(m[6]),
            "tem_audio": bool(m[7]), "tem_partitura": bool(m[9]),
        }
        for m in musicas
    ]

@router.get("/musicas/{musica_id}")
def get_musica(musica_id: int):
    from services.music_service import buscar_musica_completa_por_id
    musica = buscar_musica_completa_por_id(musica_id)
    if not musica:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Música não encontrada")
    return {
        "id": musica[0], "nome": musica[1], "artista": musica[2],
        "album": musica[3], "ano": musica[4],
        "cifra": musica[5], "tablatura": musica[6],
        "tem_audio": bool(musica[7]), "link_externo": musica[8],
    }
```

### `server/routes/stream_routes.py`

```python
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/stream/{musica_id}")
def stream_audio(musica_id: int, request: Request):
    from services.music_service import buscar_musica_completa_por_id
    musica = buscar_musica_completa_por_id(musica_id)

    if not musica or not musica[7]:
        raise HTTPException(status_code=404, detail="Áudio não encontrado")

    caminho = musica[7]

    if not os.path.exists(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    tamanho = os.path.getsize(caminho)
    range_header = request.headers.get("range")
    inicio, fim = 0, tamanho - 1

    if range_header:
        partes = range_header.replace("bytes=", "").split("-")
        inicio = int(partes[0])
        fim = int(partes[1]) if partes[1] else tamanho - 1

    comprimento = fim - inicio + 1

    def gerar():
        with open(caminho, "rb") as f:
            f.seek(inicio)
            restante = comprimento
            while restante > 0:
                chunk = f.read(min(8192, restante))
                if not chunk:
                    break
                restante -= len(chunk)
                yield chunk

    headers = {
        "Content-Range": f"bytes {inicio}-{fim}/{tamanho}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(comprimento),
        "Content-Type": "audio/mpeg",
    }

    return StreamingResponse(gerar(), status_code=206 if range_header else 200, headers=headers)
```

### `server/server_manager.py`

```python
import uvicorn
from PySide6.QtCore import QThread, Signal


class ServidorThread(QThread):
    iniciado = Signal()
    parado = Signal()
    erro = Signal(str)

    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__()
        self.host = host
        self.port = port
        self._server = None

    def run(self):
        try:
            from server.app import app
            config = uvicorn.Config(app, host=self.host, port=self.port, log_level="warning")
            self._server = uvicorn.Server(config)
            self.iniciado.emit()
            self._server.run()
        except Exception as e:
            self.erro.emit(str(e))
        finally:
            self.parado.emit()

    def parar(self):
        if self._server:
            self._server.should_exit = True
```

### `utils/network.py`

```python
import socket


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
```

---

## 7. Migração CustomTkinter → PySide6

### Filosofia do Qt

| Conceito | CustomTkinter | PySide6 |
|---|---|---|
| Layout | `.pack()`, `.grid()` | `QVBoxLayout`, `QHBoxLayout`, `QGridLayout` |
| Eventos | `command=funcao` | `signal.connect(funcao)` |
| Atualizar texto | `.configure(text=x)` | `.setText(x)` |
| Ler texto | `.get()` | `.text()` |
| Timer | `janela.after(ms, fn)` | `QTimer.singleShot(ms, fn)` |
| Thread segura | `threading.Thread` | `QThread` + `Signal` |
| Diálogo input | `CTkInputDialog` | `QInputDialog.getText()` |
| Aviso | `messagebox.showwarning` | `QMessageBox.warning()` |
| Estilo | parâmetros no construtor | QSS via `setStyleSheet()` |

### Mapeamento de classes

| CustomTkinter | PySide6 |
|---|---|
| `CTk()` | `QMainWindow` |
| `CTkToplevel` | `QDialog` |
| `CTkFrame` | `QWidget` / `QFrame` |
| `CTkLabel` | `QLabel` |
| `CTkButton` | `QPushButton` |
| `CTkEntry` | `QLineEdit` |
| `CTkTextbox` | `QPlainTextEdit` |
| `CTkScrollableFrame` | `QScrollArea` |

### Estrutura base da janela principal

```python
# main_window.py — PySide6
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QScrollArea
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gralha")
        self.resize(680, 560)
        self._montar_ui()

    def _montar_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._criar_topbar())
        layout.addWidget(self._criar_corpo(), stretch=1)

    def _criar_topbar(self):
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setObjectName("topbar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(14, 10, 14, 10)

        btn_menu = QPushButton("☰")
        btn_menu.setFixedSize(44, 44)
        btn_menu.setObjectName("btnMenu")
        btn_menu.clicked.connect(self._toggle_sidebar)

        self.entrada_busca = QLineEdit()
        self.entrada_busca.setPlaceholderText("Buscar música...")
        self.entrada_busca.textChanged.connect(self._on_busca)

        h.addWidget(btn_menu)
        h.addWidget(self.entrada_busca, stretch=1)
        return bar

    def _criar_corpo(self):
        # implementar área de conteúdo
        return QWidget()

    def _toggle_sidebar(self):
        pass  # implementar

    def _on_busca(self, texto):
        pass  # implementar


def iniciar_interface():
    app = QApplication(sys.argv)

    with open("interface/styles/theme.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

### Janela de diálogo (substitui CTkToplevel)

```python
# Antes — CustomTkinter
janela = ctk.CTkToplevel()
janela.grab_set()
janela.focus_force()

# Depois — PySide6
class AddMusicWindow(QDialog):
    musica_salva = Signal()     # notifica a janela principal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Música")
        self.resize(480, 720)
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        # ... campos e botões
        btn_salvar = QPushButton("Salvar Música")
        btn_salvar.clicked.connect(self._salvar)
        layout.addWidget(btn_salvar)

    def _salvar(self):
        # ... lógica de salvar
        self.musica_salva.emit()
        self.accept()           # fecha o diálogo com código de sucesso
```

### Comunicação entre threads — regra fundamental

**Nunca tocar em widgets de outro thread.** Sempre usar signals.

```python
# ERRADO — vai crashar ou ter comportamento imprevisível
def worker():
    dados = buscar_dados()
    label.setText(dados)    # tocando em widget de outro thread

threading.Thread(target=worker).start()

# CORRETO — via QThread + Signal
class BuscaThread(QThread):
    resultado = Signal(list)

    def run(self):
        dados = buscar_dados()
        self.resultado.emit(dados)  # envia para o thread principal via signal

class MinhaJanela(QWidget):
    def iniciar_busca(self):
        self.thread = BuscaThread()
        self.thread.resultado.connect(self._ao_receber)  # conecta no thread principal
        self.thread.start()

    def _ao_receber(self, dados):
        self.label.setText(str(dados))   # seguro — roda no thread principal
```

### QSS — estilo para o tema do Gralha

```css
/* interface/styles/theme.qss */

QMainWindow, QDialog, QWidget {
    background-color: #f0f0eb;
    font-family: "Segoe UI", sans-serif;
}

QPushButton {
    background-color: #2B5BA8;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1E4280;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
}

QPushButton#btnSecundario {
    background-color: #cccccc;
    color: #1a1a1a;
}

QLineEdit, QPlainTextEdit {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    color: #1a1a1a;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border-color: #2B5BA8;
}

QLabel {
    color: #1a1a1a;
    font-size: 12px;
}

QLabel#labelSubtexto {
    color: #666666;
    font-size: 11px;
}

QFrame#card {
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 16px;
}

QScrollBar:vertical {
    border: none;
    background: #f0f0eb;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #e0e0e0;
    border-radius: 4px;
    min-height: 20px;
}
```

---

## 8. Janela de controle do servidor

```python
# interface/windows/server_window.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from server.server_manager import ServidorThread
from utils.network import get_local_ip


class ServerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Servidor local")
        self.setFixedSize(360, 220)
        self._thread = None
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.label_status = QLabel("Servidor desligado")
        self.label_status.setObjectName("labelSubtexto")

        self.label_ip = QLabel("")
        self.label_ip.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_ip.setAlignment(Qt.AlignCenter)

        self.btn_toggle = QPushButton("Ligar servidor")
        self.btn_toggle.clicked.connect(self._toggle)

        layout.addWidget(QLabel("Servidor local Wi-Fi"))
        layout.addWidget(self.label_status)
        layout.addWidget(self.label_ip)
        layout.addStretch()
        layout.addWidget(self.btn_toggle)

    def _toggle(self):
        if self._thread is None or not self._thread.isRunning():
            self._iniciar()
        else:
            self._parar()

    def _iniciar(self):
        self._thread = ServidorThread()
        self._thread.iniciado.connect(self._ao_iniciar)
        self._thread.parado.connect(self._ao_parar)
        self._thread.erro.connect(self._ao_erro)
        self._thread.start()
        self.btn_toggle.setEnabled(False)
        self.label_status.setText("Iniciando...")

    def _parar(self):
        if self._thread:
            self._thread.parar()
        self.btn_toggle.setEnabled(False)

    def _ao_iniciar(self):
        ip = get_local_ip()
        self.label_status.setText("Servidor ligado")
        self.label_ip.setText(f"http://{ip}:8000")
        self.btn_toggle.setText("Desligar servidor")
        self.btn_toggle.setEnabled(True)

    def _ao_parar(self):
        self.label_status.setText("Servidor desligado")
        self.label_ip.setText("")
        self.btn_toggle.setText("Ligar servidor")
        self.btn_toggle.setEnabled(True)

    def _ao_erro(self, msg):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Erro", f"Falha ao iniciar servidor:\n{msg}")
        self._ao_parar()

    def closeEvent(self, event):
        if self._thread and self._thread.isRunning():
            self._thread.parar()
            self._thread.wait(2000)
        super().closeEvent(event)
```

---

## 9. Cliente web (celular)

```html
<!-- server/web/index.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gralha</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <header>
    <h1>Gralha</h1>
    <input type="search" id="busca" placeholder="Buscar música...">
  </header>

  <main>
    <ul id="lista-musicas"></ul>
  </main>

  <footer id="player-bar" hidden>
    <div id="player-info">
      <span id="player-nome"></span>
      <span id="player-artista"></span>
    </div>
    <audio id="player" controls></audio>
  </footer>

  <script src="/static/app.js"></script>
</body>
</html>
```

```javascript
// server/web/static/app.js
let musicas = [];

async function carregarMusicas() {
  const res = await fetch('/api/musicas');
  musicas = await res.json();
  renderizar(musicas);
}

function renderizar(lista) {
  const ul = document.getElementById('lista-musicas');
  ul.innerHTML = lista.map(m => `
    <li class="musica-item" data-id="${m.id}" ${!m.tem_audio ? 'data-sem-audio' : ''}>
      <div class="musica-nome">${m.nome}</div>
      <div class="musica-artista">${m.artista || '—'}</div>
    </li>
  `).join('');

  ul.querySelectorAll('.musica-item[data-id]').forEach(li => {
    li.addEventListener('click', () => {
      const id = li.dataset.id;
      if (!li.dataset.semAudio) tocar(id, li);
    });
  });
}

function tocar(id, li) {
  const musica = musicas.find(m => m.id == id);
  const player = document.getElementById('player');
  const bar = document.getElementById('player-bar');

  player.src = `/stream/${id}`;
  player.play();

  document.getElementById('player-nome').textContent = musica.nome;
  document.getElementById('player-artista').textContent = musica.artista || '';
  bar.hidden = false;

  document.querySelectorAll('.musica-item.tocando').forEach(el => el.classList.remove('tocando'));
  li.classList.add('tocando');
}

document.getElementById('busca').addEventListener('input', e => {
  const termo = e.target.value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const filtrado = musicas.filter(m => {
    const campo = `${m.nome} ${m.artista} ${m.album || ''}`.toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return campo.includes(termo);
  });
  renderizar(filtrado);
});

carregarMusicas();
```

---

## 10. `config/settings.py`

```python
import os

# Servidor
SERVER_HOST = os.getenv("GRALHA_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("GRALHA_PORT", "8000"))

# Auth (opcional para uso em estúdio — desabilitar se não precisar)
ENABLE_AUTH = os.getenv("GRALHA_ENABLE_AUTH", "false").lower() == "true"
SECRET_KEY = os.getenv("GRALHA_SECRET_KEY", "gralha-estudio-chave-local")
TOKEN_EXPIRE_HOURS = 8

# Banco
DATABASE_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "Gralha",
)
```

---

## 11. `main.py` atualizado

```python
import sys
from database.database import criar_tabela
from interface.windows.main_window import iniciar_interface


def main():
    criar_tabela()
    iniciar_interface()


if __name__ == "__main__":
    main()
```

---

## 12. Restrições e contratos que o Codex deve respeitar

### Não alterar
- Estrutura do banco de dados (`database/database.py`, `database/models/`)
- Lógica de negócio em `services/` e `core/` — apenas a interface muda
- Integração com Spotify em `services/spotify_service.py`

### Padrões obrigatórios

**PySide6:**
- Toda comunicação entre threads via `Signal` — nunca tocar em widgets diretamente de outro thread
- Janelas secundárias herdam de `QDialog`, não de `QWidget`
- Layouts sempre explícitos — sem geometria absoluta
- `setObjectName()` nos widgets que precisam de estilo específico no QSS

**FastAPI:**
- Rotas da API sempre prefixadas com `/api/`
- Arquivos de áudio sempre via endpoint `/stream/{id}` com suporte a Range headers
- Arquivos estáticos (HTML/CSS/JS) servidos pela pasta `server/web/`
- CORS liberado para todas as origens (rede local — sem exposição à internet)

**Geral:**
- Python 3.12+
- Type hints em funções novas
- Sem dependências externas além das listadas na seção 4

---

## 13. Ordem sugerida de implementação

```
Fase 1 — Servidor mínimo funcional
  [ ] server/app.py — FastAPI com /api/musicas e servir index.html
  [ ] server/routes/music_routes.py
  [ ] server/routes/stream_routes.py — com Range headers
  [ ] server/server_manager.py — QThread com Uvicorn
  [ ] utils/network.py — get_local_ip()
  [ ] server/web/index.html + app.js — cliente web básico

Fase 2 — Controle pela interface
  [ ] interface/windows/server_window.py — painel ligar/desligar
  [ ] Integrar ServerWindow no menu da MainWindow

Fase 3 — Migração PySide6
  [ ] main_window.py
  [ ] add_music_window.py
  [ ] edit_music_window.py
  [ ] playlist_window.py
  [ ] spotify_search_window.py
  [ ] Componentes: player_widget, playlist_widget

Fase 4 — Polimento
  [ ] server/routes/playlist_routes.py — playlists via API
  [ ] utils/qrcode_gen.py + qr_display_widget.py
  [ ] server/discovery/mdns_service.py — gralha.local via zeroconf
  [ ] Autenticação JWT (apenas se necessário)
```

---

*Documento gerado com base na arquitetura atual do Gralha e nas decisões técnicas discutidas.*
*Versão: 1.0 — Mai 2026*
