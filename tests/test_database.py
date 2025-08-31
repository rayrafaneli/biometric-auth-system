import os
from src.database.database_manager import DatabaseManager
import json


# Inicializa o gerenciador do banco de dados (arquivo criado na raiz do projeto)
DB_PATH = 'biometric_database.db'
db_manager = DatabaseManager(DB_PATH)