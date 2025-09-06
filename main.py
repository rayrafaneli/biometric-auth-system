import os
from src.database.database_manager import DatabaseManager
from src.cli import TerminalController


# Inicializa o gerenciador do banco de dados (arquivo criado na raiz do projeto)
DB_PATH = 'biometric_database.db'
db_manager = DatabaseManager(DB_PATH)


if __name__ == '__main__':
    controller = TerminalController(db_manager)
    try:
        controller.run()
    finally:
        db_manager.close_connection()


