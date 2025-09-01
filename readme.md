# 🔐 Sistema de Reconhecimento Facial

Este projeto implementa um sistema completo de **identificação e autenticação biométrica via reconhecimento facial**.  
Ele foi desenvolvido como uma solução prática para **cadastrar usuários, armazenar seus dados biométricos e realizar autenticação**.

---

## 🚀 Funcionalidades

- 📸 **Cadastro de Usuários**: Registra imagens faciais e extrai características únicas.  
- 🔎 **Autenticação**: Compara a biometria de um usuário com a base cadastrada.  
- 🗄️ **Banco de Dados SQLite**: Armazena usuários e suas informações biométricas.   

---

## 📂 Estrutura do Projeto

```bash
biometric-auth-system/
│
├── data/
│   ├── images_to_register/      # imagens para cadastrar novos usuários (criado na 1ª execução)
│   └── images_to_authenticate/  # imagens para testar a autenticação (criado na 1ª execução)
│
├── notebooks/                   # notebooks para prototipagem e testes
│   └── 1-testando-extracao.ipynb
│
├── src/                         # código-fonte da aplicação
│   ├── biometrics/              # lógica biométrica
│   │   ├── __init__.py
│   │   ├── feature_extractor.py # extração de características
│   │   └── matcher.py           # comparação de biometrias
│   │
│   ├── database/                # gerenciamento do banco de dados
│   │   ├── __init__.py
│   │   └── database_manager.py  # operações no banco de dados
│   │
│   └── models/                  # modelos de dados
│       ├── __init__.py
│       └── user.py              # classe de usuário
│
├── tests/                       # testes unitários
│   ├── __init__.py
│   └── test_database.py
│
├── .gitignore                   # arquivos ignorados pelo Git
├── main.py                      # ponto de entrada da aplicação
├── requirements.txt             # dependências do projeto
└── biometric_database.db        # banco de dados SQLite (criado na 1ª execução)
```

---

## ⚙️ Como Executar

1. Clone o repositório:
```bash
git clone <url-do-seu-repositorio>
cd biometric-auth-system
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação principal:
```bash
python main.py
```

---

## 🧰 Tecnologias Utilizadas

- **Python 3.10+**
- **OpenCV** – Processamento e captura de imagens  
- **#** – Extração de características faciais  
- **#** – UI  
- **SQLite3** – Banco de dados leve e integrado    


