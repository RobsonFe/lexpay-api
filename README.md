# API do Projeto LexPay

## Descrição

API de gerenciamento de precatórios construída com Django Rest Framework.

## Objetivo

- Fornecer uma interface RESTful relacionado a precatórios de documentos. Funcionará como backend para um sistema de gerenciamento de precatórios de documentos.

## Inspiração

- Esse sistema foi desenvolvido como um prototipo básico para treinamento de desenvlvedores juniors se inteirando em um sistema real de gerenciamento de precatórios da Ativos, que é o Celer.

- Origem do nome: LexPay (A união da lei com o pagamento)

## Tecnologias

- Python 3.12
- Django 6.0
- Django Rest Framework 3.16.1
- PostgreSQL/ psycopg2 2.9.10
- Django Cors Headers 4.9.0
- Django Filter 25.2
- Django Rest Framework Simple JWT 5.5.1
- Python Decouple 3.8
- SQLParse 0.5.4
- TZData 2025.3

## Como Instalar as dependencias do Projeto

- inicie Ambiente Virtual `venv`

```bash
python -m venv venv
```

**Ative o ambiente virtual**:

- No Windows (cmd.exe):

  ```sh
  venv\Scripts\activate.bat
  ```

- No Windows (PowerShell):

  ```sh
  venv\Scripts\Activate.ps1
  ```

- No Git Bash ou Linux/Mac:

  ```sh
  source venv/Scripts/activate
  ```

Para instalar todas as ferramentas necessárias, basta utilizar o `requirements.txt`.

```python
pip install -r requirements.txt
```
