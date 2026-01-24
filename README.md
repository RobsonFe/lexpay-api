# API LexPay

## Descrição

O projeto LexPay é uma API REST para gestão e negociação de precatórios (títulos judiciais) que conecta cedentes (titulares), brokers, advogados e administradores, permitindo cadastro do ativo, anexação de documentos, execução de due diligence e geração de propostas de antecipação com cálculo financeiro e trilha de histórico.

## Objetivo

- Fornecer uma interface RESTful relacionada a precatórios de documentos. Funcionará como backend para um sistema de gerenciamento de precatórios de documentos.

## Inspiração

- Esse sistema foi desenvolvido como um protótipo básico para treinamento de desenvolvedores juniores se inteirarem em um sistema real de gerenciamento de precatórios da Ativos, que é o Celer.
- Origem do nome: LexPay (A união da LEI com o PAGAMENTO)

## Tecnologias

- Python 3.12
- Django 6.0
- Django Rest Framework 3.16.1
- Django Cors Headers 4.9.0
- Django Filter 25.2
- Django Rest Framework Simple JWT 5.5.1
- Python Decouple 3.8
- Postgres 17
- drf spectacular 0.29.0
- django filter 25.2
- python decouple 3.8

## Como Instalar as dependências do Projeto

- Inicie o ambiente virtual `venv`

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

## Documentação da API

A documentação da API está disponível em `http://localhost:8000/api/docs/` e `http://localhost:8000/api/schema/redoc/`.

### Como configurar os Endpoints na Documentação

- No arquivo `core/settings.py` na variável `SPECTACULAR_SETTINGS`
- Adicione a tag do endpoint no campo `tags`
- Adicione a descrição do endpoint no campo `description`
- Adicione a requisição do endpoint no campo `request`
- Adicione a resposta do endpoint no campo `responses`
- Adicione o exemplo de requisição no campo `examples`
- Adicione o exemplo de resposta no campo `examples`
- Use o `Hook` para filtrar os endpoints que possuem uma das tags permitidas.

**Exemplo:**

```python
'TAGS': [
    {'name': 'Autenticação', 'description': 'Configurações referentes à autenticação do sistema'},
    {'name': 'Usuário', 'description': 'Configurações referentes aos usuários do sistema'},
    {'name': 'Endereço', 'description': 'Configurações referentes aos endereços do sistema'},
],
```

Após isso, no `settings.py` adicione a tag no campo `TAGS` da configuração do `SPECTACULAR_SETTINGS`.

## Executando o Servidor Django
Para executar o servidor Django, utilize o comando:

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000/`.

## Estrutura do Projeto
A estrutura do projeto é organizada da seguinte forma:

```
LEXPAY-API
│   docker-compose.yml
│   manage.py
│   README.md
│   requirements.txt
├── auth/
├── core/
├── docs/
├── due/
├── hook/
├── media/
├── oficio/
└── proposal/
```
Segue a descrição dos principais diretórios:
- `auth/`: Módulo responsável pela autenticação e gerenciamento de usuários.
- `core/`: Configurações principais do projeto Django.
- `docs/`: Documentação do projeto.
- `due/`: Módulo responsável pela due diligence dos precatórios.
- `hook/`: Módulo responsável pelos hooks do sistema.
- `media/`: Diretório para armazenamento de arquivos de mídia.
- `oficio/`: Módulo responsável pelo gerenciamento dos ofícios relacionados aos precatórios.
- `proposal/`: Módulo responsável pela geração e gerenciamento de propostas de antecipação.
- `docker-compose.yml`: Arquivo de configuração do Docker Compose para orquestração dos containers.
- `manage.py`: Script de gerenciamento do Django.
- `README.md`: Documentação do projeto.
- `requirements.txt`: Lista de dependências do projeto.


## Exemplos de Fluxo da API
Os exemplos mostram um fluxo completo: cadastro do ativo, análise/aprovação e negociação.

### 1. Cadastro do precatório (Ofício › Criar Precatório)
**Endpoint:** `POST /api/v1/oficio/precatorios/`

**Request**
```json
{
  "numero_processo": "PROC-EXEMPLO-0001",
  "natureza": "Alimentar",
  "valor_principal": "190000.00",
  "valor_venda": "100000.00",
  "percentual_honorarios": "10.00",
  "data_expedicao": "2024-11-30",
  "ano_orcamentario": 2025,
  "status": "Em Análise",
  "descricao": "Precatório alimentar de exemplo",
  "tribunal_id": "UUID-TRIBUNAL-EXEMPLO",
  "ente_devedor_id": "UUID-ENTE-DEVEDOR-EXEMPLO"
}
```

**Response**
```json
{
  "message": "Precatório criado com sucesso",
  "result": {
    "id": "PRECATORIO_ID_EXEMPLO",
    "numero_processo": "PROC-EXEMPLO-0001",
    "natureza": "Alimentar",
    "valor_principal": "190000.00",
    "valor_venda": "100000.00",
    "percentual_honorarios": "10.00",
    "status": "Em Análise",
    "tribunal": { "nome": "Tribunal Exemplo", "sigla": "TRB", "uf": "SP" },
    "ente_devedor": { "nome": "Ente Devedor Exemplo", "esfera": "Estadual" },
    "cedente": { "name": "Cedente Exemplo", "email": "cedente@example.com" },
    "documentos": []
  }
}
```

### 2. Distribuição da Due Diligence (Due › Criar Due Diligence)
**Endpoint:** `POST /api/v1/due/`

```json
{
  "precatorio": "PRECATORIO_ID_EXEMPLO",
  "prioridade": "ALTA",
  "observacoes": "Pendências de comprovação de vínculo serão analisadas."
}
```

**Resposta resumida**
```json
{
  "id": "DUE_ID_EXEMPLO",
  "precatorio": "PRECATORIO_ID_EXEMPLO",
  "analista": "USUARIO_ID_ANALISTA",
  "prioridade": "ALTA",
  "status_analise": "PENDENTE",
  "observacoes": "Pendências de comprovação de vínculo serão analisadas.",
  "created_at": "2026-01-19T11:55:00Z"
}
```

### 3. Aprovação da Due (Due › PATCH /due/aprovadas/{id}/)
Após revisar documentos no Swagger da tag **Due Diligence**, atualize o status:

```json
{
  "status_analise": "APROVADO",
  "observacoes": "Documentação validada. Seguir para marketplace."
}
```

**Resposta**
```json
{
  "id": "DUE_ID_EXEMPLO",
  "status_analise": "APROVADO",
  "documento_aprovado": true,
  "observacoes": "Documentação validada. Seguir para marketplace.",
  "updated_at": "2026-01-22T14:30:00Z"
}
```

### 4. Criação da proposta (Propostas › Calculadora)
**Endpoint:** `POST /api/v1/proposals/`

```json
{
  "precatorio": "PRECATORIO_ID_EXEMPLO",
  "valor_proposto": "150000.00",
  "taxa_desconto": "18.50",
  "taxa_juros_anual": "12.50",
  "prazo_pagamento_meses": 18,
  "data_vencimento": "2026-12-31",
  "observacoes": "Oferta condicionada à aprovação interna."
}
```

**Resposta**
```json
{
  "id": "PROPOSTA_ID_EXEMPLO",
  "precatorio": "PRECATORIO_ID_EXEMPLO",
  "valor_proposto": "150000.00",
  "valor_liquido_cedente": "135000.00",
  "valor_liquido_proponente": "41250.00",
  "taxa_desconto": "18.50",
  "status": "ENVIADA",
  "created_at": "2026-01-22T15:05:00Z"
}
```

### 5. Visualização pelo cedente (Propostas › Listar)
**Endpoint:** `GET /api/v1/proposals/`

```json
{
  "results": [
    {
      "id": "PROPOSTA_ID_EXEMPLO",
      "precatorio_detalhes": {
        "numero_processo": "PROC-EXEMPLO-0001",
        "tribunal": { "sigla": "TRB" },
        "valor_principal": "190000.00"
      },
      "proponente_nome": "Broker Exemplo",
      "valor_proposto": "150000.00",
      "valor_liquido_cedente": "135000.00",
      "status": "ENVIADA",
      "data_vencimento": "31-12-2026",
      "created_at": "22-01-2026 15:05"
    }
  ]
}
```

## Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
