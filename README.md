# 🎸 Guitar Library

Aplicação desktop desenvolvida em Python para organizar uma biblioteca pessoal de músicas, tablaturas e partituras.

O objetivo do projeto é permitir que o usuário pesquise músicas rapidamente e tenha acesso aos arquivos relacionados, como áudio, tablaturas e partituras, tudo em um único lugar.

---

## 🚀 Tecnologias utilizadas

* Python
* SQLite
* Tkinter
* Git

---

## 📂 Estrutura do Projeto

```
guitar-library
│
├── main.py
│
├── database/
│   ├── database.py
│   └── musicas.db
│
├── interface/
│   ├── main_window.py
│   └── add_music_window.py
│
├── services/
│   └── music_service.py
│
├── library/
│   ├── audio/
│   ├── tabs/
│   └── scores/
│
├── docs/
│
├── README.md
└── .gitignore
```

---

## ⚙️ Funcionalidades

* Buscar músicas cadastradas
* Abrir tablaturas
* Reproduzir áudio das músicas
* Abrir partituras em PDF
* Adicionar novas músicas à biblioteca
* Organizar arquivos locais de música

---

## 🧠 Como funciona

O sistema utiliza um banco de dados local SQLite para armazenar informações das músicas, como:

* nome
* artista
* álbum
* caminho da tablatura
* caminho do áudio
* caminho da partitura

Os arquivos reais ficam armazenados nas pastas da biblioteca e o banco guarda apenas o caminho desses arquivos.

---

## ▶️ Como executar o projeto

1. Clone o repositório

```
git clone https://github.com/adrielsoares2309/guitar-library.git
```

2. Entre na pasta do projeto

```
cd guitar-library
```

3. Execute o programa

```
python main.py
```

---

## 📌 Objetivo do projeto

Este projeto foi desenvolvido com fins de estudo, com foco em:

* organização de projetos em Python
* desenvolvimento de interfaces gráficas
* uso de banco de dados local
* versionamento com Git

---

## 📜 Licença

Projeto de uso educacional.
