# 🔐 Sistema de Reconhecimento Facial

Este projeto implementa um sistema completo de **identificação e autenticação biométrica via reconhecimento facial**.  
Ele foi desenvolvido como uma solução prática para **cadastrar usuários, armazenar seus dados biométricos e realizar autenticação**.

---

## 🚀 Funcionalidades

- 📸 **Cadastro de Usuários**: Registra imagens faciais e extrai características únicas.  
- 🔎 **Autenticação**: Compara a biometria de um usuário com a base cadastrada.  
- 🗄️ **Banco de Dados SQLite**: Armazena usuários e suas informações biométricas.   

---

## ⚙️ Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/rayrafaneli/biometric-auth-system.git
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
## ⚠️ Solução de Problemas
Ocasionalmente, o OpenCV pode não ler corretamente o caminho para os recursos de Haar Cascade. Se o sistema apresentar erros relacionados a não encontrar esses arquivos:

**Solução** - Mova a pasta haarcascades (localizada em src/biometrics/haarcascades) inteira para a raiz do seu disco principal, como C:/. O sistema deve então conseguir localizar os arquivos necessários.

---

## 🧰 Tecnologias Utilizadas

- **Python 3.10+**
- **OpenCV** – Processamento e captura de imagens   
- **PyQt6 ** – Interface Gráfica (UI)
- **SQLite3** – Banco de dados leve e integrado    


