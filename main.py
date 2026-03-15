import sqlite3
from interface.main_window import iniciar_interface
from database.database import criar_tabela

def main():
    print("Iniciando Guitar Library...")

    # garantir que o banco e tabela existam
    criar_tabela()

    # iniciar interface gráfica
    iniciar_interface()

if __name__ == "__main__":
    main()