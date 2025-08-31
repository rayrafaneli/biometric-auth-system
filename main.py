import os
from src.database.database_manager import DatabaseManager
import json


# Inicializa o gerenciador do banco de dados (arquivo criado na raiz do projeto)
DB_PATH = 'biometric_database.db'
db_manager = DatabaseManager(DB_PATH)


def register_new_user_simple():
    """Registra um usuário apenas com nome e nível de acesso.

    Como a extração de features não está disponível neste momento,
    armazenamos uma lista vazia ([]) como placeholder para
    `biometric_features`.
    """
    print("\n--- Cadastro Simples de Usuário ---")
    try:
        name = input("Nome: ").strip()
        if not name:
            print("Nome não pode ser vazio.")
            return

        access_input = input("Nível de acesso (1, 2 ou 3): ").strip()
        if not access_input.isdigit() or int(access_input) not in [1, 2, 3]:
            print("Nível de acesso inválido. Use 1, 2 ou 3.")
            return
        access_level = int(access_input)

        # Placeholder: nenhuma feature biométrica disponível ainda
        features = []

        user_id = db_manager.register_user(name, access_level, features)
        if user_id:
            print(f"Usuário cadastrado com sucesso. ID = {user_id}")
        else:
            print("Falha ao cadastrar usuário.")

    except Exception as e:
        print(f"Erro durante cadastro: {e}")


def list_all_users():
    """Busca e imprime todos os usuários cadastrados."""
    users = db_manager.get_all_users_with_features()
    if not users:
        print("Nenhum usuário cadastrado.")
        return

    print("\n--- Usuários Cadastrados ---")
    for u in users:
        # Mostra apenas informações de identificação e nível de acesso
        print(f"ID: {u['id']} | Nome: {u['name']} | Nível: {u['access_level']} | Features: {len(u.get('features', []))} items")


def show_user_details():
    """Mostra detalhes (incluindo as features desserializadas) de um usuário por ID."""
    id_input = input("Digite o ID do usuário: ").strip()
    if not id_input.isdigit():
        print("ID inválido.")
        return
    user_id = int(id_input)

    users = db_manager.get_all_users_with_features()
    for u in users:
        if u['id'] == user_id:
            print(json.dumps(u, indent=2, ensure_ascii=False))
            return
    print("Usuário não encontrado.")


def delete_user():
    """Apaga um usuário por ID (opcional, operação simples)."""
    try:
        id_input = input("Digite o ID do usuário a remover: ").strip()
        if not id_input.isdigit():
            print("ID inválido.")
            return
        user_id = int(id_input)

        # operação direta com SQL já que o DatabaseManager não expõe remoção
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        if affected:
            print(f"Usuário {user_id} removido com sucesso.")
        else:
            print("Nenhum usuário removido (ID pode não existir).")
    except Exception as e:
        print(f"Erro ao remover usuário: {e}")


if __name__ == '__main__':
    # Cria as pastas de dados se elas não existirem (úteis para futuras funcionalidades)
    os.makedirs('data/images_to_register', exist_ok=True)
    os.makedirs('data/images_to_authenticate', exist_ok=True)

    try:
        while True:
            print("\n===== Banco de Dados - Cadastro Simples =====")
            print("1. Cadastrar novo usuário")
            print("2. Listar todos os usuários")
            print("3. Mostrar detalhes de um usuário (por ID)")
            print("4. Remover usuário (por ID)")
            print("5. Sair")
            choice = input("Escolha uma opção: ").strip()

            if choice == '1':
                register_new_user_simple()
            elif choice == '2':
                list_all_users()
            elif choice == '3':
                show_user_details()
            elif choice == '4':
                delete_user()
            elif choice == '5':
                print("Saindo.")
                break
            else:
                print("Opção inválida. Tente novamente.")

    finally:
        db_manager.close_connection()

