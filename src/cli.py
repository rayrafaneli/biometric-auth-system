import os
import json
from src.biometrics import matcher

#CLI Temporário para desenvolver e testar funcionalidades antes da interface gráfica.

# TerminalController é responsável apenas por interação com o usuário via terminal:
# - mostrar o menu
# - capturar entradas
# - delegar as ações pesadas (captura, extração, matching, DB) a outros módulos
#
# Mantemos imports pesados (OpenCV, sessão de captura, extrator) dentro dos métodos
# para evitar que o módulo todo exija dependências (útil em testes/unitários sem câmera).



class TerminalController:
    def __init__(self, db_manager):
        self.db = db_manager

    def run(self):
        # Cria pastas necessárias
        os.makedirs('data/images_to_register', exist_ok=True)
        os.makedirs('data/images_to_authenticate', exist_ok=True)

        try:
            while True:
                print("\n===== Banco de Dados - Cadastro Simples =====")
                print("0. Login (biométrico)")
                print("1. Cadastrar novo usuário")
                print("2. Listar todos os usuários")
                print("3. Mostrar detalhes de um usuário (por ID)")
                print("4. Remover usuário (por ID)")
                print("5. Sair")
                choice = input("Escolha uma opção: ").strip()

                if choice == '0':
                    self.login_flow()
                    continue
                if choice == '1':
                    self.register_new_user_simple()
                elif choice == '2':
                    self.list_all_users()
                elif choice == '3':
                    self.show_user_details()
                elif choice == '4':
                    self.delete_user()
                elif choice == '5':
                    print("Saindo.")
                    break
                else:
                    print("Opção inválida. Tente novamente.")

        finally:
            # garantia: fechar conexão está a cargo de quem instanciou db
            pass

    def register_new_user_simple(self):
        # fluxo simples de cadastro: coleta nome, nível e (opcional) captura via webcam
        # a função apenas orquestra; a captura efetiva e a extração de features são feitas
        # por objetos especializados (SessaoCaptura, feature_extractor)
        print("\n--- Cadastro Simples de Usuário ---")
        try:
            name = input("Nome: ").strip()
            # Garante que o nome é string Unicode (Python 3 já faz isso)
            if not name:
                print("Nome não pode ser vazio.")
                return
            # Se quiser garantir, pode forçar:
            # name = str(name)

            access_input = input("Nível de acesso (1, 2 ou 3): ").strip()
            if not access_input.isdigit() or int(access_input) not in [1, 2, 3]:
                print("Nível de acesso inválido. Use 1, 2 ou 3.")
                return
            access_level = int(access_input)

            # Fonte das imagens: câmera ou diretório (arquivo). CLI só pergunta; extração é delegada.
            src_choice = input("Fonte para cadastro - (c)âmera, (d)iretório, (n)enhum: ").strip().lower()
            features = []

            if src_choice == 'c':
                # Se o usuário quer capturar agora, fazemos imports locais (lazy-load)
                # Isso evita exigir OpenCV no momento em que o módulo é importado.
                # Aqui só estamos orquestrando: config -> sessão -> extração -> salvar no DB.
                from src.biometrics.ConfigCaptura import CaptureConfig
                from src.biometrics.SessaoCaptura import CaptureSession
                from src.biometrics.feature_extractor import extract_features_from_folder

                base_dir = os.path.join('data', 'images_to_register')
                user_dir = os.path.join(base_dir, name.replace(' ', '_'))
                os.makedirs(user_dir, exist_ok=True)

                # Usar os defaults do CaptureConfig; só passamos o user_id
                config = CaptureConfig(user_id=name.replace(' ', '_'))

                session = CaptureSession(config)
                if not session.inicializar_camera(0):
                    print("Não foi possível acessar a câmera. Cadastro continuará sem imagens.")
                else:
                    success = session.iniciar_captura_fluida()
                    session.liberar_recursos()
                    if success:
                        print("Captura concluída. Extraindo features...")
                        features = extract_features_from_folder(os.path.join(base_dir, name.replace(' ', '_')))
                    else:
                        print("Captura interrompida. Cadastro continuará sem imagens.")
            elif src_choice == 'd':
                # Usuário escolheu fornecer um diretório com imagens
                folder_path = input("Caminho para a pasta com imagens do usuário: ").strip()
                if not folder_path:
                    print("Caminho vazio. Cadastro sem imagens.")
                elif not os.path.exists(folder_path):
                    print("Caminho não encontrado. Cadastro sem imagens.")
                else:
                    # import local do extrator
                    from src.biometrics.feature_extractor import extract_features_from_folder
                    features = extract_features_from_folder(folder_path)
                    if not features:
                        print("Nenhuma feature extraída do diretório informado.")

            user_id = self.db.register_user(name, access_level, features)
            if user_id:
                print(f"Usuário cadastrado com sucesso. ID = {user_id}")
            else:
                print("Falha ao cadastrar usuário.")

        except Exception as e:
            print(f"Erro durante cadastro: {e}")

    def list_all_users(self):
        users = self.db.get_all_users_with_features()
        if not users:
            print("Nenhum usuário cadastrado.")
            return

        print("\n--- Usuários Cadastrados ---")
        for u in users:
            print(f"ID: {u['id']} | Nome: {u['name']} | Nível: {u['access_level']} | Features: {len(u.get('features', []))} items")

    def show_user_details(self):
        id_input = input("Digite o ID do usuário: ").strip()
        if not id_input.isdigit():
            print("ID inválido.")
            return
        user_id = int(id_input)

        # pedir ao DatabaseManager o registro já desserializado
        user = self.db.get_user_by_id(user_id)
        if user:
            print(json.dumps(user, indent=2, ensure_ascii=False))
        else:
            print("Usuário não encontrado.")

    def delete_user(self):
        try:
            id_input = input("Digite o ID do usuário a remover: ").strip()
            if not id_input.isdigit():
                print("ID inválido.")
                return
            user_id = int(id_input)

            # DatabaseManager encapsula a lógica do DELETE
            ok = self.db.delete_user(user_id)
            if ok:
                print(f"Usuário {user_id} removido com sucesso.")
            else:
                print("Nenhum usuário removido (ID pode não existir).")
        except Exception as e:
            print(f"Erro ao remover usuário: {e}")

    def login_flow(self):
        # Orquestra fluxo de login biométrico:
        # - abre a câmera
        # - captura uma imagem (com timeout)
        # - pede ao extractor para transformar a imagem em vetor
        # - consulta DB e pede ao matcher para decidir
        print("\n--- Login Biométrico ---")
        # escolher fonte: câmera ou diretório/arquivo
        source = input("Fonte para autenticação - (c)âmera, (d)iretório/arquivo: ").strip().lower()

        query_feat = None

        if source == 'c':
            # import local do OpenCV e do extrator (evita importar cv2 ao importar o módulo inteiro)
            import cv2
            from src.biometrics.feature_extractor import extract_feature_from_image

            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cam.isOpened():
                print("Não foi possível abrir a câmera.")
                return

            try:
                print("Pressione 's' para capturar, ESC para cancelar (ou aguarde captura automática em 10s)")
                start_time = __import__('time').time()
                auto_capture_seconds = 2
                captured = False
                while True:
                    ret, frame = cam.read()
                    if not ret:
                        continue
                    cv2.imshow('Login - Pressione s para capturar', frame)
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        print('Cancelado pelo usuário')
                        break
                    if k == ord('s') or k == ord('S'):
                        captured = True
                    if __import__('time').time() - start_time >= auto_capture_seconds:
                        captured = True

                    if captured:
                        tmp_path = os.path.join('data', 'images_to_authenticate', 'tmp_capture.jpg')
                        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                        cv2.imwrite(tmp_path, frame)
                        cv2.destroyAllWindows()
                        cam.release()

                        query_feat = extract_feature_from_image(tmp_path)
                        if not query_feat:
                            print('Falha ao extrair features da captura. Tente novamente.')
                        break
            finally:
                try:
                    cam.release()
                    cv2.destroyAllWindows()
                except Exception:
                    pass

        elif source == 'd':
            path = input("Caminho para imagem ou diretório: ").strip()
            if not path:
                print('Nenhum caminho fornecido.')
                return
            if not os.path.exists(path):
                print('Caminho não encontrado.')
                return
            # import local do extrator
            from src.biometrics.feature_extractor import extract_feature_from_image, extract_features_from_folder
            if os.path.isfile(path):
                query_feat = extract_feature_from_image(path)
            else:
                vecs = extract_features_from_folder(path)
                query_feat = vecs[0] if vecs else None
            if not query_feat:
                print('Falha ao extrair features do caminho informado.')
                return

        else:
            print('Fonte inválida. Abortando login.')
            return

        # se chegamos até aqui, temos query_feat extraído com sucesso
        users = self.db.get_all_users_with_features()
        if not users:
            print('Nenhum usuário cadastrado no sistema.')
            return

        # Também mostramos os top matches para debug/explicabilidade.
        scored = matcher.score_users(query_feat, users)

        print('\nTop matches:')
        for i, (u, best_s, mean_k) in enumerate(scored[:3]):
            print(f"{i+1}. {u['name']} (ID {u['id']}): best={best_s:.4f} mean_top={mean_k:.4f}")

        # Delegar a política de decisão para matcher.decide_match.
        granted, best_user, best_score_val, mean_top_val, reason, scored_full = matcher.decide_match(
            query_feat,
            users,
        )

        if granted:
            print(f"Acesso concedido: {best_user['name']} (ID {best_user['id']}) - best={best_score_val:.3f} mean_top={mean_top_val:.3f}")
        else:
            print('Acesso negado:', reason)

