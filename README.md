# 📄 Gerador Automatizado de Propostas Comerciais - Armazenagem

Este é um sistema desenvolvido em Python com a biblioteca Streamlit para automatizar o preenchimento de propostas comerciais de logística e armazenagem, eliminando erros manuais de digitação e padronizando os tópicos comerciais.

## 🛠️ Tecnologias Utilizadas
* **Python 3**
* **Streamlit** (Interface Web)
* **Python-docx** (Manipulação de arquivos Word)

## 📁 Estrutura do Projeto
* `app.py`: Interface web e captura de dados.
* `core/`: Inteligência do sistema (lógica de preenchimento do documento).
* `templates/`: Modelos de arquivos oficiais (`.docx`).

## 🚀 Como Executar Localmente
1. Ative o ambiente virtual: `.\venv\Scripts\activate`
2. Instale as dependências: `pip install -r requirements.txt`
3. Rode o app: `streamlit run app.py`