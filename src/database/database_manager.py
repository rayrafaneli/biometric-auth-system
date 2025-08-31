import sqlite3
import json

class DatabaseManager:
    """
    Classe responsável por toda a comunicação com o banco de dados SQLite.
    """
    def __init__(self, db_path):
        """
        Inicializa a conexão com o banco e cria a tabela se não existir.
        """
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        Cria a tabela 'users' para armazenar os dados biométricos.
        (Privado: usado apenas na inicialização)
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    access_level INTEGER NOT NULL,
                    biometric_features TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar a tabela: {e}")

    def register_user(self, name, access_level, features):
        """
        Insere um novo usuário no banco de dados.
        As características (features) são serializadas para JSON antes de salvar.
        """
        # Serializa a lista/array de features para uma string JSON
        features_json = json.dumps(features.tolist() if hasattr(features, 'tolist') else features)

        try:
            self.cursor.execute('''
                INSERT INTO users (name, access_level, biometric_features)
                VALUES (?, ?, ?)
            ''', (name, access_level, features_json))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro ao registrar usuário: {e}")
            return None

    def get_all_users_with_features(self):
        """
        Busca todos os usuários e suas características biométricas no banco.
        As características são desserializadas de JSON para o formato original.
        """
        try:
            self.cursor.execute('SELECT id, name, access_level, biometric_features FROM users')
            rows = self.cursor.fetchall()
            
            users_data = []
            for row in rows:
                user_dict = {
                    'id': row[0],
                    'name': row[1],
                    'access_level': row[2],
                    # Desserializa a string JSON de volta para uma lista/array
                    'features': json.loads(row[3])
                }
                users_data.append(user_dict)
            return users_data
        except sqlite3.Error as e:
            print(f"Erro ao buscar usuários: {e}")
            return []

    def close_connection(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.conn:
            self.conn.close() 

