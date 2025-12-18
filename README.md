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

## Configuração do Banco de Dados com Docker

O projeto utiliza Docker Compose para gerenciar os serviços de banco de dados PostgreSQL e PgAdmin.

### Pré-requisitos

- Docker Desktop instalado e em execução
- Docker Compose (geralmente incluído no Docker Desktop)

### Configuração do Arquivo .env

Antes de iniciar os containers, é necessário configurar o arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do Banco de Dados PostgreSQL
DB_NAME=lexpay
DB_USER=lexpay
DB_PASSWORD=sua_senha_aqui
DB_PORT=5433
DB_HOST=localhost

# Configurações do PgAdmin (opcional)
PGADMIN_EMAIL=admin@lexpay.com
PGADMIN_PASSWORD=senha_pgadmin
PGADMIN_PORT=5050
```

**Observações importantes:**
- `DB_HOST`: Use `localhost` quando o Django estiver rodando fora do Docker. Use `postgres` (nome do serviço) quando o Django estiver rodando dentro do Docker.
- `DB_PORT`: Porta externa mapeada (5433 por padrão). A porta interna do container é sempre 5432.
- Se as variáveis não forem definidas, os valores padrão do `docker-compose.yml` serão utilizados.

### Iniciando os Containers

Para iniciar os serviços do banco de dados e PgAdmin:

```bash
docker-compose up -d
```

O comando `-d` executa os containers em modo detached (em segundo plano).

**Serviços iniciados:**
- **PostgreSQL**: Container `lexpay-db` na porta `5433` (ou a porta definida em `DB_PORT`)
- **PgAdmin**: Container `lexpay-pgadmin` na porta `5050` (ou a porta definida em `PGADMIN_PORT`)

### Verificando o Status dos Containers

Para verificar se os containers estão rodando:

```bash
docker-compose ps
```

Para ver os logs dos containers:

```bash
docker-compose logs -f
```

### Parando os Containers

Para parar os containers sem remover os volumes (dados serão preservados):

```bash
docker-compose stop
```

Para parar e remover os containers (os volumes ainda serão preservados):

```bash
docker-compose down
```

Para parar e remover os containers **incluindo os volumes** (⚠️ **ATENÇÃO**: Isso apagará todos os dados do banco):

```bash
docker-compose down -v
```

### Acessando o Banco de Dados

#### Via PgAdmin (Interface Web)

1. Acesse: `http://localhost:5050` (ou a porta definida em `PGADMIN_PORT`)
2. Faça login com:
   - **Email**: `admin@lexpay.com` (ou o valor de `PGADMIN_EMAIL`)
   - **Senha**: `lexpay` (ou o valor de `PGADMIN_PASSWORD`)

3. Para adicionar o servidor PostgreSQL no PgAdmin:
   - Clique com botão direito em "Servers" → "Register" → "Server"
   - **Name**: LexPay DB
   - **Host**: `postgres` (nome do serviço no Docker)
   - **Port**: `5432` (porta interna do container)
   - **Database**: `lexpay` (ou o valor de `DB_NAME`)
   - **Username**: `lexpay` (ou o valor de `DB_USER`)
   - **Password**: A senha definida em `DB_PASSWORD`

#### Via Linha de Comando

Para acessar o PostgreSQL via terminal:

```bash
docker-compose exec postgres psql -U lexpay -d lexpay
```

Substitua `lexpay` pelos valores de `DB_USER` e `DB_NAME` se diferentes.

### Configuração do Django

O Django está configurado para se conectar ao banco de dados usando as variáveis do arquivo `.env`. A configuração está em `core/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5433"),
        "NAME": config("DB_NAME", default="lexpay"),
        "USER": config("DB_USER", default="lexpay"),
        "PASSWORD": config("DB_PASSWORD", default="lexpay"),
    },
}
```

**Importante**: Certifique-se de que o valor de `DB_HOST` no `.env` está correto:
- `DB_HOST=localhost` → Quando o Django roda na sua máquina
- `DB_HOST=postgres` → Quando o Django roda dentro do Docker

### Executando Migrações

Após iniciar os containers, execute as migrações do Django:

```bash
python manage.py migrate
```

### Troubleshooting

**Problema**: Erro de conexão com o banco de dados
- Verifique se os containers estão rodando: `docker-compose ps`
- Verifique se as variáveis no `.env` estão corretas
- Verifique se a porta não está em uso: `netstat -an | findstr 5433` (Windows)

**Problema**: Container não inicia
- Verifique os logs: `docker-compose logs postgres`
- Verifique se o Docker está em execução
- Verifique se a porta está disponível

**Problema**: Dados foram perdidos
- Os dados são persistidos em volumes Docker. Use `docker-compose down` (sem `-v`) para preservar os dados
- Os volumes são: `postgres_data` e `pgadmin_data`
