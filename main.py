from interface.windows.main_window import iniciar_interface
from database.database import criar_tabela

def main():
    print("Iniciando Guitar Library...")
    criar_tabela()
    iniciar_interface()

if __name__ == "__main__":
    main()