Projeto de Identificação e Autenticação Biométrica (APS 5º/6º Sem)

📂 Estrutura de Pastas
A estrutura foi pensada para ser ortogonal, separando as responsabilidades:

biometric-auth-system/
│
├── data/
│   ├── images_to_register/     # imagens para cadastrar novos usuários
│   └── images_to_authenticate/ # imagens para testar a autenticação
│
├── notebooks/                  # Jupyter notebooks para testes e prototipagem (opcional)
│   └── 1-testando-extracao.ipynb
│
├── src/                        # Todo o código fonte da aplicação
│   ├── biometrics/             # Módulos relacionados à lógica biométrica
│   │   ├── __init__.py
│   │   ├── feature_extractor.py  # Função para extrair características da imagem
│   │   └── matcher.py            # Função para comparar duas biometrias
│   │
│   ├── database/               # Módulo para gerenciar o banco de dados
│   │   ├── __init__.py
│   │   └── database_manager.py   # Classe que lida com todas as operações do BD
│   │
│   └── models/                 # Classes que representam os dados (opcional, mas boa prática)
│       ├── __init__.py
│       └── user.py               # Classe/modelo para representar um usuário
│
├── tests/                      # Testes unitários para garantir que tudo funciona
│   ├── __init__.py
│   └── test_database.py
│
├── .gitignore                  # Arquivo para ignorar arquivos desnecessários no Git
├── main.py                     # Ponto de entrada da aplicação, onde tudo é orquestrado
├── requirements.txt            # Lista de bibliotecas Python necessárias
└── biometric_database.db       # O arquivo do banco de dados SQLite (será criado na 1ª execução)

Como Executar o Projeto
Clone o repositório:

git clone <url-do-seu-repositorio>
cd biometric-auth-system

Crie um ambiente virtual (recomendado):

python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

Instale as dependências:

pip install -r requirements.txt

Execute a aplicação principal:

python main.py
