# Guia de Desenvolvimento com Django Rest Framework (DRF)

## Descrição:

- Esse guia consiste em um mapeamento de com as features mais utilizadas do Django e Django Rest Framework para desenvolvimento de Software.
- Esse guia facilita a utilização de métodos com técnicas para implementações em projetos django.
- Seguindo as instruções desse documento, você conseguirá ter uma base para início de projetos com Django e Django Rest Framework.

---

### Aviso

Antes de qualquer estudo, nada substitui a documentação oficial do Django e Django Rest Framework, e o objetivo desse guia é facilitar o entendimento do framework para futuras implementações.

### Documentação Oficial

**[Django](https://www.djangoproject.com/)**
**[Django Rest Framework](https://www.django-rest-framework.org/)**
---------------------

## Conceitos

**Considerando que criar uma aplicação com Django Rest Framework seja um requisito básico de aprendizado para um junior, pularemos essa parte**

O Django leva em conta em sua estrutura de projeto, um padrão modular, onde cada pequena parte da aplicação pode ser um `app`, e para criar esse app, é necessário usar o comando `py manage.py startapp <nome do app>`, e cada app criado deve ser colocado no `settings.py` que fica na aplicação principal.

Exemplo de instalação no `settings.py`

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    "corsheaders",
    "api", # app chamado "api" configurado no projeto.
]
```

Após essa instalação, você já pode utilizar o app dentro do projeto django.

Por que os apps são a parte do projeto?

- **R:** O Django tenta fazer com que cada app seja plugável, ou seja, ser utilizado em qualquer outro projeto por princípio.
  De início, vamos entender como funcionam algumas partes do django para efetivamente saber como usar cada ferramenta.

## Model

### Descrição:

As `models` são a **fonte única e definitiva da verdade** sobre os seus dados. Elas representam as entidades e suas relações de forma abstrata, permitindo que o Django (através do seu ORM - Object-Relational Mapper) traduza classes Python em estruturas complexas de banco de dados, como tabelas, colunas e chaves estrangeiras.

Uma observação importante sobre a ORM do Django, é que você pode conectar vários bancos de dados de uma vez para uma escalabilidade e também é possível mudar de banco de dados sem alterar o código do projeto.

Em vez de escrever `CREATE TABLE` em SQL, você define uma classe em Python.

### Por que os Models são tão importantes?

1. **Abstração do Banco de Dados:** Você escreve Python, e o Django se encarrega de gerar o SQL apropriado (seja para PostgreSQL, MySQL, SQLite, etc.). Isso permite que você troque de banco de dados com pouquíssimo esforço.
2. **Consistência de Dados:** As regras de negócio (validações, tipos de dados, valores padrão) são definidas diretamente no model, garantindo que nenhum dado "ruim" entre no seu banco, independentemente de onde ele venha (seja do Admin, de uma API ou de um script).
3. **Migrations Automatizadas:** O Django rastreia automaticamente as alterações nos seus arquivos `models.py` e gera os *arquivos de migração* (`migrations`). Esses arquivos são "receitas" que dizem ao banco de dados como aplicar essas mudanças (criar uma tabela, adicionar uma coluna, etc.) de forma segura e versionada.
4. **Facilidade em Consultas (`QuerySets`):** Uma vez que os models estão definidos, o ORM do Django fornece uma API de consulta (QuerySet) poderosa e intuitiva para buscar, filtrar, criar e deletar registros usando métodos Python, sem a necessidade de escrever SQL complexo.

---

### Exemplo Prático: Autores e Livros

Vamos imaginar que estamos criando uma aplicação de livraria. Nossas duas entidades principais serão `Autor` e `Livro`. Um autor pode ter escrito vários livros, e um livro pertence a um autor.

Este é um clássico relacionamento **Um-para-Muitos** (ou `ForeignKey`).

Vamos definir esses models no arquivo `models.py` do nosso app (ex: `api/models.py`):

```python
from django.db import models

# É uma boa prática criar uma classe base para campos comuns,
# como data de criação e atualização.
class BaseTimestampedModel(models.Model):
    """
    Modelo Abstrato com data de criação e atualização.
    'abstract = True' significa que este modelo não criará
    uma tabela no banco de dados; ele apenas servirá de base.
    """
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    class Meta:
        abstract = True


class Autor(BaseTimestampedModel):
    """
    Define o Model para um Autor.
    """
    # CharField é usado para campos de texto curtos.
    # verbose_name é o "nome amigável" usado no Django Admin.
    nome = models.CharField(max_length=255, verbose_name="Nome do Autor")

    # TextField é usado para textos longos, sem limite de tamanho.
    # blank=True e null=True significam que este campo é opcional.
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografia")

    class Meta:
        # Define o nome singular e plural usado no Django Admin.
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        # Garante que os autores sejam ordenados por nome por padrão.
        ordering = ['nome']

    def __str__(self):
        """
        O método __str__ é crucial.
        Ele define como o objeto será representado como texto.
        (Ex: no Django Admin ou ao dar um print).
        """
        return self.nome


class Livro(BaseTimestampedModel):
    """
    Define o Model para um Livro.
    """
    titulo = models.CharField(max_length=255, verbose_name="Título do Livro")

    # DateField armazena apenas a data (sem hora).
    data_publicacao = models.DateField(verbose_name="Data de Publicação")

    # IntegerField armazena números inteiros.
    # null=True e blank=True tornam o campo opcional.
    numero_paginas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Páginas"
    )

    # --- O Relacionamento ---
    # ForeignKey (Chave Estrangeira) cria a relação Muitos-para-Um.
    # Um Livro tem UM Autor, mas um Autor pode ter MUITOS Livros.
    autor = models.ForeignKey(
        Autor,  # O model que estamos relacionando.
        on_delete=models.CASCADE,  # O que fazer se o Autor for deletado?
                                   # CASCADE: Deleta todos os livros deste autor.
                                   # (Outras opções: SET_NULL, PROTECT, etc.)
        related_name="livros",     # Como podemos chamar a lista de livros
                                   # a partir de um objeto Autor?
                                   # Ex: autor_obj.livros.all()
        verbose_name="Autor"
    )

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        # Ordena primeiro pela data de publicação (mais recente primeiro)
        # e depois pelo título.
        ordering = ['-data_publicacao', 'titulo']

    def __str__(self):
        # Retorna o título e o nome do autor para fácil identificação.
        return f"{self.titulo} (por {self.autor.nome})"

```

### O que acontece agora? (O Fluxo de Migração)

Depois de salvar o arquivo `api/models.py` com o código acima, o Django ainda não sabe sobre eles, e o banco de dados não mudou. Precisamos executar dois comandos:

1. **`python manage.py makemigrations`**

   * O Django vai ler todos os arquivos `models.py` dos seus `INSTALLED_APPS`.
   * Ele vai comparar o estado atual dos models com o estado anterior (registrado nos arquivos de migração existentes).
   * Ele detectará que criamos dois novos models (`Autor` e `Livro`) e gerará um novo arquivo de migração (ex: `api/migrations/0001_initial.py`). Esse arquivo contém o "plano de execução" em Python para criar as tabelas.
2. **`python manage.py migrate`**

   * O Django vai executar todos os arquivos de migração que ainda não foram aplicados no banco de dados.
   * Neste caso, ele vai ler o `0001_initial.py` e traduzir aquele plano em comandos SQL (`CREATE TABLE api_autor ...`, `CREATE TABLE api_livro ...`, `ALTER TABLE api_livro ADD CONSTRAINT ... FOREIGN KEY ...`), aplicando as mudanças no banco.

A partir deste ponto, suas tabelas estão criadas e prontas para receber dados através do ORM do Django.

### Referência:

- [Model do Django](https://docs.djangoproject.com/pt-br/5.2/topics/db/models/)

# QuerySet

Se os **Models** são o *plano* da sua tabela no banco de dados, um **QuerySet** é o *resultado* de uma busca nessa tabela.

Pense no QuerySet como uma "pergunta" que você faz ao banco de dados. Por exemplo: "Django, me traga todos os autores" ou "Django, encontre o livro com o título 'Dom Casmurro'".

O resultado dessa "pergunta" é o QuerySet. Ele pode conter zero, um ou vários objetos (registros) do seu banco.

### A "Mágica" do `.objects` (O Manager)

Você não cria um QuerySet diretamente. Em vez disso, você o obtém através do "Manager" (gerente) do seu Model, que por padrão se chama `objects`.

* Para fazer perguntas sobre `Autor`, você usará `Autor.objects`.
* Para fazer perguntas sobre `Livro`, você usará `Livro.objects`.

O Manager é a porta de entrada para o banco de dados, funciona como algo semelhante em outras apis restful como `repository`.

### O Conceito-Chave: Avaliação Preguiçosa (Lazy Evaluation)

Este é o conceito mais importante sobre QuerySets: **eles são preguiçosos (lazy).**

Quando você escreve um QuerySet, o Django **não** vai ao banco de dados imediatamente.

```python
# NENHUMA consulta ao banco de dados é feita ainda.
meus_autores = Autor.objects.filter(nome__startswith="M")
```

O Django só executa a consulta no banco (o `SELECT` em SQL) quando você *realmente* precisa dos dados. Isso acontece ao:

1. Iterar sobre o QuerySet (ex: `for autor in meus_autores: ...`)
2. Tentar acessá-lo como uma lista (ex: `list(meus_autores)`)
3. Imprimi-lo (ex: `print(meus_autores)`)
4. Chamar `len()`, `.count()`, `.exists()`, etc.

Isso é incrivelmente eficiente, pois permite que você construa filtros complexos (encadeados) e o Django otimizará tudo em uma única consulta SQL no final.

---

### Exemplos Práticos: O CRUD com QuerySets

Vamos usar nossos models `Autor` e `Livro` para ver os métodos mais comuns. (CRUD significa Create, Read, Update, Delete).

*(Para os exemplos abaixo, imagine que você os está executando no shell do Django com `python manage.py shell`)*

```python
# Importamos nossos models para poder usá-los
from api.models import Autor, Livro
```

### 1\. Criar (Create)

O método `.create()` constrói, salva e retorna o novo objeto em um único passo.

```python
# Criando um Autor
autor_machado = Autor.objects.create(
    nome="Machado de Assis",
    biografia="Foi um escritor brasileiro, considerado por muitos o maior nome da literatura nacional."
)

# Criando um Livro (repare como usamos o objeto 'autor_machado' que acabamos de criar)
livro_dom_casmurro = Livro.objects.create(
    titulo="Dom Casmurro",
    data_publicacao="1899-03-15",
    autor=autor_machado,
    numero_paginas=256
)

# Criando outro livro para o mesmo autor
livro_memorias = Livro.objects.create(
    titulo="Memórias Póstumas de Brás Cubas",
    data_publicacao="1881-01-01",
    autor=autor_machado
)
```

**Equivalente SQL (conceitual):** `INSERT INTO api_autor (nome, biografia, ...) VALUES (...);`

### 2\. Ler (Read / Buscar)

Esta é a operação mais comum, e existem vários métodos para ela.

#### `all()` - Buscar todos os objetos

Retorna um QuerySet com *todos* os registros da tabela.

```python
# Pega TODOS os autores no banco
todos_os_autores = Autor.objects.all()
# SQL: SELECT * FROM api_autor;

# Pega TODOS os livros
todos_os_livros = Livro.objects.all()
# SQL: SELECT * FROM api_livro;
```

#### `get()` - Buscar um ÚNICO objeto

Usado quando você sabe que quer exatamente **um** resultado.

```python
# Busca um autor específico pelo seu ID (chave primária)
autor_id_1 = Autor.objects.get(id=1)
# SQL: SELECT * FROM api_autor WHERE id = 1;

# Busca um livro específico pelo título
livro = Livro.objects.get(titulo="Dom Casmurro")
# SQL: SELECT * FROM api_livro WHERE titulo = 'Dom Casmurro';
```

> **Atenção!** Use `get()` com cuidado.
>
> * Se ele não encontrar **nenhum** objeto, ele gera um erro: `Autor.DoesNotExist`.
> * Se ele encontrar **mais de um** objeto, ele gera outro erro: `Autor.MultipleObjectsReturned`.
>
> Por isso, `get()` é ideal para buscar por chaves primárias (`id`) ou campos únicos.

#### `filter()` - Filtrar múltiplos objetos

Usado para encontrar todos os objetos que correspondem a certos critérios (filtros). Retorna um QuerySet (que pode estar vazio).

```python
# Encontra todos os livros publicados antes do ano 1900
# O "duplo underscore" (__) é usado para navegar nos campos
livros_seculo_19 = Livro.objects.filter(data_publicacao__year__lt=1900)
# SQL: SELECT * FROM api_livro WHERE EXTRACT(YEAR FROM data_publicacao) < 1900;

# Encontra todos os autores cujo nome começa com "Machado"
autores_machado = Autor.objects.filter(nome__startswith="Machado")
# SQL: SELECT * FROM api_autor WHERE nome LIKE 'Machado%';
```

#### `exclude()` - Excluir objetos

O oposto de `filter()`. Retorna todos os objetos, *exceto* os que correspondem aos critérios.

```python
# Todos os autores, MENOS o "Machado de Assis"
outros_autores = Autor.objects.exclude(nome="Machado de Assis")
# SQL: SELECT * FROM api_autor WHERE nome != 'Machado de Assis';
```

### 3\. Atualizar (Update)

Existem duas formas principais de atualizar.

**Forma 1: Para um único objeto (Padrão)**
Você busca (`get`), altera os atributos em Python, e depois chama `.save()`.

```python
# 1. Buscar o objeto
autor = Autor.objects.get(nome="Machado de Assis")

# 2. Alterar o atributo em Python
autor.biografia = "Biografia atualizada."

# 3. Salvar de volta no banco
autor.save()
# SQL: UPDATE api_autor SET biografia = 'Biografia atualizada.' WHERE id = ...;
```

**Forma 2: Para múltiplos objetos (em Massa)**
Você usa `filter()` e depois chama `.update()` no QuerySet. Isso é muito mais rápido para atualizações em massa.

```python
# Atualiza TODOS os livros do Machado de Assis para terem 100 páginas
Livro.objects.filter(autor__nome="Machado de Assis").update(numero_paginas=100)
# SQL: UPDATE api_livro SET numero_paginas = 100 WHERE autor_id IN (SELECT id FROM api_autor WHERE nome = 'Machado de Assis');
```

**Nota:** O método `.update()` em massa **não** chama o método `.save()` do seu model.

### 4\. Deletar (Delete)

Similar à atualização, você pode deletar um objeto ou vários.

**Forma 1: Para um único objeto**
Busque (`get`) e chame `.delete()`.

```python
livro_para_deletar = Livro.objects.get(titulo="Memórias Póstumas de Brás Cubas")
livro_para_deletar.delete()
# SQL: DELETE FROM api_livro WHERE id = ...;
```

**Forma 2: Para múltiplos objetos (em Massa)**
Use `filter()` e chame `.delete()`.

```python
# Deleta todos os livros publicados antes de 1850
Livro.objects.filter(data_publicacao__year__lt=1850).delete()
# SQL: DELETE FROM api_livro WHERE EXTRACT(YEAR FROM data_publicacao) < 1850;
```

---

### O Poder dos Relacionamentos

QuerySets brilham ao usar as `ForeignKeys` que definimos.

#### Acesso Direto (Do "Muitos" para o "Um")

Quando você tem um objeto `Livro`, pode acessar seu `Autor` diretamente.

```python
livro = Livro.objects.get(titulo="Dom Casmurro")

# Acessa o objeto 'Autor' relacionado
print(livro.autor)
# Saída: Machado de Assis

# Você pode até "navegar" pelos campos do autor
print(livro.autor.biografia)
# Saída: Foi um escritor brasileiro...
```

#### Acesso Reverso (Do "Um" para os "Muitos")

Quando você tem um objeto `Autor`, como pegar todos os seus `Livros`?
Usando o `related_name="livros"` que definimos no model `Livro`!

```python
autor = Autor.objects.get(nome="Machado de Assis")

# Graças ao related_name="livros", podemos fazer isso:
# Isso retorna um "RelatedManager", que age como um QuerySet
livros_do_autor = autor.livros.all()

# Você pode filtrar isso como qualquer outro QuerySet!
livros_antigos_do_autor = autor.livros.filter(data_publicacao__year__lt=1890)

print(f"O autor {autor.nome} tem {livros_do_autor.count()} livros no total.")
```

# Performance nas Queries

## Otimizando Consultas: O Próximo Nível do QuerySet

Uma vez que você sabe como criar, ler, atualizar e deletar dados, o próximo desafio é fazer isso de forma **eficiente**.

Quando sua aplicação cresce, com milhares de Autores e dezenas de milhares de Livros, a forma como você busca os dados pode ser a diferença entre uma página que carrega em 50 milissegundos e uma que demora 10 segundos (ou quebra o servidor).

O objetivo é simples: **reduzir o número de consultas ao banco de dados.** O ideal é que cada "página" ou "endpoint de API" faça o mínimo de consultas possível (idealmente, uma ou duas).

### O Problema: A "Bomba" do N+1

Este é o erro de performance mais comum que desenvolvedores Django (e de qualquer ORM) cometem. Ele acontece quando você busca uma lista de objetos (1 consulta) e depois, dentro de um loop, acessa um campo relacionado de cada objeto (N consultas).

**O Jeito Lento (Ruim):**

Imagine que queremos listar todos os livros e o nome do autor de cada um.

```python
# Em nossa view ou serializer, faríamos algo assim:
# 1. Busca todos os livros
livros = Livro.objects.all() # <-- CONSULTA 1 (SELECT * FROM api_livro)

# 2. Agora, vamos iterar sobre eles
for livro in livros:
    # PROBLEMA! Para cada livro, fazemos uma nova consulta
    # para buscar o nome do autor.
    print(f"Livro: {livro.titulo}, Autor: {livro.autor.nome}")
    # <-- CONSULTA 2 (SELECT * FROM api_autor WHERE id = 1)
    # <-- CONSULTA 3 (SELECT * FROM api_autor WHERE id = 2)
    # <-- CONSULTA 4 (SELECT * FROM api_autor WHERE id = 1)
    # <-- CONSULTA 5 (SELECT * FROM api_autor WHERE id = 3)
    # ... e assim por diante
```

Se tivermos 100 livros, este código fará **101 consultas** ao banco de dados! (1 para pegar os livros + 100 para pegar o autor de cada livro). Isso é o problema do N+1.

Para resolver isso, temos duas ferramentas principais: `select_related` e `prefetch_related`.

### 1\. `select_related` (O Otimizador de `ForeignKey`)

* **O que faz?** Ele "avisa" ao Django para, na mesma consulta, já trazer os dados do objeto relacionado usando um `JOIN` do SQL.
* **Quando usar? (A Regra de Ouro):** Use `select_related` para relacionamentos **Um-para-Um** (`OneToOneField`) ou **Muitos-para-Um** (`ForeignKey`). Ou seja, quando você está buscando o lado "Um" de uma relação.
* **Por quê?** Porque ele pega o objeto "pai" (o `Autor`) e o "filho" (`Livro`) em uma única e eficiente consulta SQL.

**O Jeito Rápido (Bom) - Resolvendo o N+1:**

```python
# A única mudança é adicionar .select_related('autor')
livros = Livro.objects.select_related('autor').all() # <-- UMA ÚNICA CONSULTA!

# 2. Agora, o loop é "de graça"
for livro in livros:
    # NENHUMA consulta nova é feita aqui!
    # O 'livro.autor' já veio do banco na primeira chamada.
    print(f"Livro: {livro.titulo}, Autor: {livro.autor.nome}")
```

**O que aconteceu?** O Django fez UMA consulta SQL parecida com esta:
`SELECT * FROM api_livro INNER JOIN api_autor ON api_livro.autor_id = api_autor.id;`

**Resultado:** 1 consulta total, em vez de 101.

### 2\. `prefetch_related` (O Otimizador de "Muitos")

E se o problema for o inverso? Se quisermos listar todos os Autores e, para cada um, listar *todos* os seus livros?

```python
# O Jeito Lento (Ruim) - O N+1 Reverso:
# 1. Busca todos os autores
autores = Autor.objects.all() # <-- CONSULTA 1 (SELECT * FROM api_autor)

# 2. Itera sobre os autores
for autor in autores:
    print(f"Autor: {autor.nome}")
    # PROBLEMA! Acessamos o related_name "livros"
    # Isso faz uma nova consulta PARA CADA autor.
    livros_do_autor = autor.livros.all() # <-- CONSULTA 2 (SELECT * FROM api_livro WHERE autor_id = 1)
                                         # <-- CONSULTA 3 (SELECT * FROM api_livro WHERE autor_id = 2)
                                         # ... e assim por diante
```

Novamente, temos um problema de N+1.

Não podemos usar `select_related('livros')` aqui, porque "livros" não é um objeto único, é uma *lista* de objetos. Um `JOIN` aqui seria muito ineficiente.

* **O que faz?** O `prefetch_related` é mais inteligente. Ele faz **duas** consultas separadas e "junta" os resultados em Python de forma eficiente.
  1. Consulta 1: Busca todos os Autores (`SELECT * FROM api_autor;`).
  2. Consulta 2: Busca *todos* os Livros que pertencem a *qualquer* um desses autores (`SELECT * FROM api_livro WHERE autor_id IN (1, 2, 3...);`).
* **Quando usar? (A Regra de Ouro):** Use `prefetch_related` para relacionamentos **Muitos-para-Muitos** (`ManyToManyField`) ou o reverso de `ForeignKey` (como o nosso `autor.livros`).

**O Jeito Rápido (Bom) - Resolvendo o N+1 Reverso:**

```python
# A única mudança é adicionar .prefetch_related('livros')
autores = Autor.objects.prefetch_related('livros').all() # <-- DUAS CONSULTAS TOTAIS

for autor in autores:
    print(f"Autor: {autor.nome}")

    # NENHUMA consulta nova é feita aqui!
    # Os livros já estão "cacheados" no objeto 'autor'
    for livro in autor.livros.all(): # 'autor.livros.all()' aqui é instantâneo
        print(f"  - {livro.titulo}")
```

**Resultado:** 2 consultas totais (sempre!), em vez de N+1.

| Método                        | Quando Usar                                                          | Como Funciona (SQL)             |
| :----------------------------- | :------------------------------------------------------------------- | :------------------------------ |
| **`select_related`**   | `ForeignKey`, `OneToOneField` (Relações "Um")                  | 1 Consulta com `JOIN`         |
| **`prefetch_related`** | `ManyToManyField`, Reverso de `ForeignKey` (Relações "Muitos") | 2 Consultas (sem `JOIN` feio) |

---

### 3\. `annotate` (Agregações no Banco)

E se quisermos apenas *contar* quantos livros cada autor tem?

* **O que faz?** Permite que você "anote" (adicione) um novo campo em cada objeto do seu QuerySet, com um valor calculado *pelo banco de dados*. As funções mais comuns são `Count`, `Sum`, `Avg`, `Min`, `Max`.
* **Quando usar?** Sempre que você precisar de um valor agregado (como uma contagem ou soma) junto com os dados do objeto. É a forma correta de fazer "contagens em massa".
* **Por quê?** É *infinitamente* mais rápido do que fazer `len(autor.livros.all())` dentro de um loop em Python, pois o banco de dados é otimizado para contar.

```python
from django.db.models import Count

# Queremos todos os autores, e um novo campo 'total_livros' em cada um.
autores_com_contagem = Autor.objects.annotate(
    total_livros=Count('livros') # 'livros' é o related_name
)

# SQL: SELECT ..., COUNT(api_livro.id) AS total_livros
#      FROM api_autor
#      LEFT OUTER JOIN api_livro ON (api_autor.id = api_livro.autor_id)
#      GROUP BY api_autor.id;

for autor in autores_com_contagem:
    # 'total_livros' não existe no model, mas foi criado pelo 'annotate'!
    print(f"{autor.nome} - Total de livros: {autor.total_livros}")
```

**Resultado:** Uma única consulta super otimizada que já traz os autores e a contagem de livros de cada um.

---

### 4\. Objetos `Q` (Filtros Complexos com `OU`)

Por padrão, quando você passa múltiplos argumentos para `filter()`, eles são unidos por `AND` (E).

`Livro.objects.filter(numero_paginas=100, data_publicacao__year=1900)`
*SQL: ... WHERE numero\_paginas = 100 **AND** data\_publicacao ... = 1900*

Mas e se quisermos usar `OR` (OU)?

* **O que faz?** O objeto `Q` encapsula uma condição de filtro e permite que você os combine com operadores lógicos `|` (OU) e `&` (E).
* **Quando usar?** Quando você precisar de uma lógica de filtro complexa que vá além do simples `AND`.

```python
from django.db.models import Q

# Queremos livros que comecem com "Dom" OU tenham mais de 300 páginas
livros_complexos = Livro.objects.filter(
    Q(titulo__startswith="Dom") | Q(numero_paginas__gt=300)
)
# SQL: ... WHERE titulo LIKE 'Dom%' OR numero_paginas > 300;

# Você pode criar lógicas complexas:
# (Título começa com "Dom" E autor é Machado) OU (publicado antes de 1850)
Livro.objects.filter(
    (Q(titulo__startswith="Dom") & Q(autor__nome="Machado de Assis")) |
    Q(data_publicacao__year__lt=1850)
)
```

---

### 5\. Objetos `F` (Operações no Nível do Banco)

* **O que faz?** Um objeto `F` representa o valor de um campo *no próprio banco de dados*. Ele permite que você faça operações no banco sem precisar trazer o valor para o Python primeiro.
* **Quando usar?**
  1. **Atualizações Atômicas:** Para atualizar um valor com base nele mesmo (ex: incrementar um contador). Isso evita uma *race condition* (condição de corrida).
  2. **Comparações de Campos:** Para comparar dois campos do *mesmo* modelo.

**Exemplo 1: Atualização Atômica (O mais comum)**

Queremos adicionar 10 páginas a todos os livros do Machado de Assis.

```python
from django.db.models import F

# Pega todos os livros dele
livros_machado = Livro.objects.filter(autor__nome="Machado de Assis")

# O 'F('numero_paginas')' diz ao banco:
# "Pegue o valor QUE JÁ ESTÁ LÁ no banco e some 10"
livros_machado.update(numero_paginas=F('numero_paginas') + 10)
```

**Por que isso é bom?** Isso é feito em UMA instrução SQL (`UPDATE ... SET numero_paginas = numero_paginas + 10`). O "jeito lento" seria um loop em Python: buscar o livro, `livro.numero_paginas += 10`, `livro.save()`. O método com `F` é atômico (seguro para concorrência) e muito mais rápido.

**Exemplo 2: Comparação de Campos**

Queremos encontrar livros onde a data de publicação foi (hipoteticamente) no mesmo ano do ID do autor (exemplo bobo para ilustrar).

```python
# Não funciona:
# Livro.objects.filter(data_publicacao__year = 'autor_id') # Errado

# Jeito certo:
Livro.objects.filter(data_publicacao__year=F('autor_id'))
# SQL: ... WHERE EXTRACT(YEAR FROM data_publicacao) = "autor_id";
```

## Outras Técnicas de Performance Essenciais

Além de reduzir o número de consultas com `select_related` e `prefetch_related`, podemos otimizar a performance de duas outras formas:

1. **Reduzindo a Carga:** Trazendo menos dados do banco de dados (menos colunas ou dados brutos em vez de objetos).
2. **Reduzindo a Memória:** Processando grandes volumes de dados sem sobrecarregar a memória da aplicação.
3. **Otimizando a Criação:** Inserindo múltiplos dados de forma eficiente.
4. **Otimizando a Estrutura:** Garantindo que o próprio banco de dados seja rápido nas buscas.

### 6\. `values()` e `values_list()` (Buscando Dados Brutos)

* **O que faz?** Em vez de retornar objetos completos do Model (que têm métodos, `__str__`, etc.), eles retornam dados brutos:
  * `values()`: Retorna um QuerySet de **dicionários** Python.
  * `values_list()`: Retorna um QuerySet de **tuplas** Python.
* **Quando usar?** Quando você **não** precisa do objeto Model. Por exemplo, para popular um gráfico, gerar um CSV, ou quando a sua API precisa retornar apenas alguns campos e você não vai modificar o objeto.
* **Por quê?** A "hidratação" do modelo (o processo de pegar dados brutos do banco e transformá-los em um objeto Python) tem um custo de processamento e memória. Para milhares de registros, usar `values` ou `values_list` pode ser *drasticamente* mais rápido.

```python
# O Jeito Normal (Lento se forem 10.000 livros)
# Retorna uma lista de objetos <Livro>
livros = Livro.objects.all()
# Custo de criar 10.000 objetos Livro na memória.

# O Jeito Rápido (para dados brutos)
# Se você SÓ precisa do título e do ID:
titulos_livros = Livro.objects.values('id', 'titulo')
# Saída (conceitual):
# [{'id': 1, 'titulo': 'Dom Casmurro'}, {'id': 2, 'titulo': 'Memórias Póstumas...'}]
# SQL: SELECT "id", "titulo" FROM api_livro;

# Ainda mais rápido (e com menos memória) se você só quer os valores:
titulos_flat = Livro.objects.values_list('titulo', flat=True)
# O 'flat=True' é um truque para quando você pede SÓ UM CAMPO.
# Saída (conceitual): ['Dom Casmurro', 'Memórias Póstumas...']
```

### 7\. `only()` e `defer()` (Buscando Colunas Específicas)

* **O que faz?** Estes são o "meio-termo". Eles ainda retornam objetos do Model, mas controlam quais colunas são trazidas do banco.
  * `only('campo1', 'campo2')`: Traz **APENAS** os campos especificados (e a `pk`).
  * `defer('campo_pesado')`: Traz **TODOS** os campos, **EXCETO** os especificados.
* **Quando usar?** Quando você *precisa* do objeto Model (seus métodos, etc.), mas sabe que não vai usar certas colunas que são "pesadas" (como um `TextField` de biografia ou um JSONField grande).
* **Por quê?** Evita trafegar dados desnecessários pela rede (entre o banco e sua app). Se você tem uma coluna `biografia` de 5MB e não vai usá-la numa lista, use `defer('biografia')`.

```python
# Queremos listar autores, mas sem suas biografias (que são textos longos)
autores = Autor.objects.defer('biografia')
# SQL: SELECT "id", "nome", "criado_em", "atualizado_em" FROM api_autor;
# (Repare que "biografia" ficou de fora)

for autor in autores:
    print(autor.nome) # Rápido! O dado veio do banco.
    # print(autor.biografia) # LENTO! Se você acessar, o Django fará
                           # UMA NOVA CONSULTA só para buscar a biografia.
```

### 8\. `count()` e `exists()` (Contagens e Verificações Eficientes)

Você já viu `count()` no `annotate`, mas ele também é vital para evitar um erro comum de performance.

* **O que faz?**
  * `count()`: Executa um `SELECT COUNT(*)` no banco. É a forma mais rápida de saber *quantos* objetos existem.
  * `exists()`: Executa um `SELECT ... LIMIT 1`. É a forma mais rápida de saber se *pelo menos um* objeto existe.
* **Quando usar?** Sempre que você precisar saber o número de itens ou se algum item existe.
* **Por quê?** Para evitar carregar todos os objetos na memória só para contá-los.

**O Anti-Padrão (RUIM):**

```python
# NÃO FAÇA ISSO:
livros = Livro.objects.filter(autor__nome="Machado de Assis")
total = len(livros) # RUIM! Traz todos os livros para o Python só para contar.

# NEM ISSO:
if len(livros) > 0: # PÉSSIMO! Mesma coisa.
    print("Ele tem livros!")
```

**O Jeito Correto (BOM):**

```python
# BOM:
total = Livro.objects.filter(autor__nome="Machado de Assis").count()
# SQL: SELECT COUNT(*) FROM api_livro WHERE ...; (Super rápido)

# ÓTIMO (se você só quer saber "tem ou não tem?"):
tem_livros = Livro.objects.filter(autor__nome="Machado de Assis").exists()
# SQL: SELECT 1 FROM api_livro WHERE ... LIMIT 1; (Mais rápido ainda)

if tem_livros:
    print("Ele tem livros!")
```

### 9\. `bulk_create()` (Criação em Massa)

* **O que faz?** Insere uma lista de objetos no banco de dados em uma **única consulta SQL** (`INSERT ... VALUES (...), (...), (...)`).
* **Quando usar?** Sempre que você precisar criar mais de um objeto ao mesmo tempo (ex: importando dados de um CSV, criando muitos objetos em um loop).
* **Por quê?** Fazer 100 consultas `INSERT` separadas é ordens de magnitude mais lento do que fazer 1 única consulta `INSERT` com 100 registros.

```python
# Jeito Lento (RUIM):
for i in range(100):
    Autor.objects.create(nome=f"Autor de Teste {i}")
# (Faz 100 consultas ao banco!)

# Jeito Rápido (BOM):
autores_para_criar = [
    Autor(nome=f"Autor de Teste {i}") for i in range(100)
]
Autor.objects.bulk_create(autores_para_criar)
# (Faz 1 ÚNICA consulta ao banco!)
```

### 10\. `iterator()` (Processando Milhares de Registros)

* **O que faz?** Por padrão, um `QuerySet` guarda os resultados em cache na memória (`queryset._result_cache`). Se você busca 1 milhão de livros, sua aplicação vai usar *muita* memória. O `.iterator()` desliga esse cache e busca os resultados um por um, usando muito menos memória.
* **Quando usar?** Quando você precisa processar um volume *gigantesco* de dados (ex: um script de background que varre todos os livros) e está sofrendo com picos de uso de memória.
* **Por quê?** Troca performance (cache) por eficiência de memória.

```python
# Se 'Livro' tiver 500.000 registros, isso pode quebrar sua app por falta de memória:
# for livro in Livro.objects.all():
#    ...

# Isso usa uma quantidade constante e pequena de memória, não importa o tamanho:
for livro in Livro.objects.iterator():
    # Processa um livro de cada vez
    print(livro.titulo)
```

---

### Bônus: A Otimização Mais Importante (que não é um QuerySet)

Nenhuma otimização de QuerySet vai salvar uma consulta que não usa **índices de banco de dados**.

* **O que é?** Um índice (`index`) é como o índice de um livro. Em vez de ler o livro (tabela) inteiro para achar um tópico (um autor), o banco de dados consulta o índice e vai direto para a página certa.
* **Quando usar?** Em *todos* os campos que você usa frequentemente para filtrar (`filter()`), buscar (`get()`), ou ordenar (`order_by()`).
* **Como?** Adicionando `db_index=True` ao seu campo no `models.py`.

```python
class Autor(BaseTimestampedModel):
    # Se você vai filtrar muito por nome (ex: /api/autores?nome=...)
    # adicionar um índice é CRUCIAL.
    nome = models.CharField(
        max_length=255,
        verbose_name="Nome do Autor",
        db_index=True  # <-- A MÁGICA ACONTECE AQUI
    )
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografia")

# ... não se esqueça de rodar makemigrations e migrate depois!
```

Sem `db_index=True`, uma busca por `nome` em uma tabela com 1 milhão de autores fará um "Full Table Scan" (lerá os 1 milhão de registros) e será *extremamente* lenta. Com o índice, a busca será quase instantânea.

### Referência:

- [QuerySets](https://docs.djangoproject.com/en/5.2/ref/models/querysets/)

## Filtros e Agregações

Até agora, usamos filtros simples como `filter(nome="Machado de Assis")` ou `filter(data_publicacao__year__lt=1900)`.

Vamos revelar um "segredo": `filter(nome="Machado")` é, na verdade, um atalho para `filter(nome__exact="Machado")`.

O **duplo underscore (`__`)** é a sintaxe especial que o Django usa para "consultas de campo" (field lookups). É como você diz ao `filter()`, `exclude()` e `get()` *exatamente como* eles devem comparar os valores no banco de dados.

Dominar esses *lookups* permite que você crie consultas de qualquer complexidade sem escrever uma linha de SQL. Vamos ver os mais importantes.

#### Comparações de Texto

Estes são os mais usados para campos como `CharField` e `TextField`.

| Lookup                      | O que faz                                                                       | Quando usar                                                                                                     | Exemplo (com `Autor.objects.filter(...)`)                                                     |
| :-------------------------- | :------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| **`__exact`**       | Correspondência exata (padrão). É*case-sensitive* (diferencia 'A' de 'a'). | Quando você precisa da correspondência exata. Raramente usado para texto, pois `__iexact` é melhor.        | `(nome__exact="Machado de Assis")` `<br>` *(Não acharia "machado de assis")*             |
| **`__iexact`**      | Correspondência exata,*case-insensitive*.                                    | **Sempre** que você for comparar um texto vindo de um usuário. É o que o usuário espera de uma busca. | `(nome__iexact="machado de assis")` `<br>` *(Acha "Machado de Assis", "machado...", etc)* |
| **`__contains`**    | Verifica se o campo*contém* um pedaço de texto. É *case-sensitive*.      | Para buscas parciais onde a capitalização importa (raro).                                                     | `(biografia__contains="escritor")` `<br>` *(Não acharia "Escritor")*                     |
| **`__icontains`**   | Verifica se o campo*contém* um pedaço de texto, *case-insensitive*.       | **Seu principal "cavalo de batalha" para barras de busca.** Qualquer busca de texto livre deve usar isso. | `(nome__icontains="assis")` `<br>` *(Acha "Machado de Assis", "ASSIS", etc)*              |
| **`__startswith`**  | Verifica se o campo*começa com* o texto. *Case-sensitive*.                 | Útil para filtros de auto-complete ou buscas em "índices" (ex: autores com a letra 'M').                      | `(nome__startswith="Ma")`                                                                     |
| **`__istartswith`** | Versão*case-insensitive* do `startswith`.                                  | A versão mais segura e amigável para o usuário de `startswith`.                                            | `(nome__istartswith="ma")`                                                                    |
| **`__endswith`**    | Verifica se o campo*termina com* o texto. *Case-sensitive*.                 | Menos comum, mas útil para filtrar por coisas como extensões de arquivo ou sufixos.                           | `(nome__endswith="Assis")`                                                                    |
| **`__iendswith`**   | Versão*case-insensitive* do `endswith`.                                    | Versão mais segura do `endswith`.                                                                            | `(nome__iendswith="assis")`                                                                   |

---

#### Comparações de Valores (Números, Datas e Booleanos)

| Lookup                 | O que faz                                                   | Quando usar                                                                              | Exemplo (com `Livro.objects.filter(...)`)                                                                                                                                             |
| :--------------------- | :---------------------------------------------------------- | :--------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`__gt`**     | *Greater Than* (Maior que `>`)                          | Para encontrar valores acima de um limite (não incluindo o limite).                     | `(numero_paginas__gt=300)` `<br>` *(Livros com 301 páginas ou mais)*                                                                                                             |
| **`__gte`**    | *Greater Than or Equal* (Maior ou igual a `>=`)         | Para encontrar valores acima de um limite (incluindo o limite).                          | `(numero_paginas__gte=300)` `<br>` *(Livros com 300 páginas ou mais)*                                                                                                            |
| **`__lt`**     | *Less Than* (Menor que `<`)                             | Para encontrar valores abaixo de um limite.                                              | `(data_publicacao__year__lt=1900)` `<br>` *(Livros publicados até 1899)*                                                                                                         |
| **`__lte`**    | *Less Than or Equal* (Menor ou igual a `<=`)            | Para encontrar valores abaixo de um limite (incluindo).                                  | `(data_publicacao__year__lte=1900)` `<br>` *(Livros publicados até 1900)*                                                                                                        |
| **`__range`**  | Verifica se o valor está*entre* dois outros (inclusive). | Perfeito para filtros de "De-Até" (como um seletor de datas ou faixa de preço).        | `(numero_paginas__range=(200, 300))` `<br>` *(Livros com 200 a 300 páginas)*                                                                                                     |
| **`__isnull`** | Verifica se o valor no banco é `NULL`.                   | **Essencial** para encontrar registros com campos opcionais preenchidos (ou não). | `(numero_paginas__isnull=True)` `<br>` *(Livros sem número de páginas cadastrado)* `<br><br>` `(biografia__isnull=False)` `<br>` *(Autores que *têm* uma biografia)* |

---

#### Comparações de Conjunto (Listas)

| Lookup             | O que faz                                                                                  | Quando usar                                                                                                                                                                                        | Exemplo (com `Autor.objects.filter(...)`)                                                                                                |
| :----------------- | :----------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| **`__in`** | Verifica se o valor está*dentro de uma lista* (ou `list`, `tuple` ou `QuerySet`). | **Uma das ferramentas de otimização mais importantes.** Use-a sempre que precisar buscar múltiplos itens de uma vez. É *muito* mais rápido do que fazer um loop e vários `.get()`. | `ids_desejados = [1, 3, 5]` `<br>` `(id__in=ids_desejados)` `<br><br>` *(Também funciona com QuerySets, como veremos a seguir)* |

---

#### O Superpoder: Navegando por Relacionamentos (`ForeignKey`, `ManyToManyField`)

O duplo underscore (`__`) não serve apenas para *comparações*. Ele é a sua principal ferramenta para "atravessar" models e filtrar baseado em dados de uma tabela relacionada.

**Pergunta 1: "Quero todos os *Livros* de autores cujo nome começa com 'M'."**

* **Models envolvidos:** Começamos em `Livro` e pulamos para `Autor`.
* **Como?** `Livro.objects.filter( ... )`
* **Filtro:** `autor` (pula para o `Autor`) `__` `nome` (acessa o campo `nome` do `Autor`) `__` `startswith` (aplica o *lookup*).

```python
# O filtro "atravessa" a ForeignKey 'autor' para ler o campo 'nome' do Autor
livros = Livro.objects.filter(autor__nome__istartswith="m")
```

**SQL (Conceitual):** `SELECT * FROM api_livro INNER JOIN api_autor ON ... WHERE api_autor.nome ILIKE 'm%'`

---

**Pergunta 2: "Quero todos os *Autores* que publicaram livros antes de 1890."**

* **Models envolvidos:** Começamos em `Autor` e pulamos para `Livro`.
* **Como?** `Autor.objects.filter( ... )`
* **Filtro:** `livros` (usa o `related_name` que definimos!) `__` `data_publicacao` (acessa o campo do `Livro`) `__` `year__lt` (aplica o *lookup*).

```python
# O filtro "atravessa" a relação reversa 'livros' para ler os dados
autores = Autor.objects.filter(livros__data_publicacao__year__lt=1890)
```

**SQL (Conceitual):** `SELECT * FROM api_autor WHERE EXISTS (SELECT 1 FROM api_livro WHERE ... AND data_publicacao ... < 1890)`

**Atenção: Duplicatas!**
Se um autor escreveu *dois* livros antes de 1890, ele aparecerá *duas vezes* no resultado acima. Para consertar isso, você pode usar `.distinct()`:

```python
autores_unicos = Autor.objects.filter(
    livros__data_publicacao__year__lt=1890
).distinct()
```

Dominar esses *lookups* é o que transforma suas consultas de simples para poderosas, permitindo que você peça ao banco de dados *exatamente* o que você precisa em uma única consulta.

### Agregações (Aggregation)

Chegamos ao tópico final de consultas com ORM: **Agregações**

Enquanto `annotate` é usado para calcular um valor *para cada item* em um QuerySet (ex: a contagem de livros de *cada* autor), a **Agregação** é usada para calcular um valor-resumo para o **QuerySet inteiro**.

Pense no `aggregate` como o "Relatório Final". Ele não adiciona uma coluna a cada linha; ele te dá um único resultado no final de tudo.

### A Diferença Crucial: `aggregate()` vs. `annotate()`

Este é o ponto que mais confunde novos desenvolvedores, mas é simples de entender:

* **`annotate()` (Anota para cada item):**

  * **Pergunta:** "Quero uma *lista de Autores* e, ao lado de cada um, o seu *total de livros*."
  * **Resultado:** Um QuerySet (vários Autores), cada um com um novo campo.
  * **Exemplo:** `Autor.objects.annotate(total_livros=Count('livros'))`
* **`aggregate()` (Resume o total):**

  * **Pergunta:** "Qual o *número total de páginas* em minha biblioteca inteira?"
  * **Resultado:** Um dicionário com um único valor.
  * **Exemplo:** `Livro.objects.aggregate(soma_total=Sum('numero_paginas'))`

### Como Usar `aggregate()`

O `aggregate()` é um método terminal de um QuerySet (ou seja, ele retorna um resultado final, não outro QuerySet). O resultado é sempre um **dicionário**.

Vamos importar as funções que precisamos:

```python
from django.db.models import Sum, Avg, Count, Max, Min
```

#### Exemplo 1: `Sum` (Soma)

**Pergunta:** "Quantas páginas existem na biblioteca inteira, somando todos os livros?"

```python
# Pedimos ao Django para 'sumarizar' o campo 'numero_paginas'
resultado = Livro.objects.aggregate(total_de_paginas=Sum('numero_paginas'))

print(resultado)
# Saída: {'total_de_paginas': 5420}
# (ou qualquer que seja a soma total de páginas no seu banco)
```

**Por que usar?** Para obter um grande total de qualquer campo numérico (preço, quantidade, etc.).

---

#### Exemplo 2: `Avg` (Média)

**Pergunta:** "Qual é a média de páginas de um livro na nossa biblioteca?"

```python
resultado = Livro.objects.aggregate(media_de_paginas=Avg('numero_paginas'))

print(resultado)
# Saída: {'media_de_paginas': 285.25}
```

**Por que usar?** Para calcular médias de forma rápida e precisa (o banco de dados é ótimo nisso).

---

#### Exemplo 3: `Count` (Contagem)

**Pergunta:** "Quantos autores temos cadastrados no total?"

```python
# Usamos 'id' para garantir que estamos contando autores únicos.
resultado = Autor.objects.aggregate(numero_de_autores=Count('id'))

print(resultado)
# Saída: {'numero_de_autores': 52}
```

**Por que usar?** É a forma correta e performática de contar o total de registros. É mais rápido que `Autor.objects.all().count()` pois é mais explícito.

---

#### Exemplo 4: `Max` (Máximo) e `Min` (Mínimo)

**Pergunta:** "Qual é a data de publicação do livro mais novo (Max) e do mais antigo (Min)?"

```python
resultado = Livro.objects.aggregate(
    livro_mais_recente=Max('data_publicacao'),
    livro_mais_antigo=Min('data_publicacao')
)

print(resultado)
# Saída: {
#   'livro_mais_recente': datetime.date(2023, 10, 20),
#   'livro_mais_antigo': datetime.date(1881, 1, 1)
# }
```

**Por que usar?** Perfeito para encontrar "recordes" nos dados: o produto mais caro, o usuário mais recente, o pedido mais antigo.

### Agregando um QuerySet Filtrado

O `aggregate()` opera sobre o QuerySet que você construiu. Isso significa que você pode (e deve) filtrar *antes* de agregar.

**Pergunta:** "Qual o número total de páginas escritas *apenas* por Machado de Assis?"

```python
# 1. Primeiro, filtramos os livros para pegar apenas os do Machado
livros_do_machado = Livro.objects.filter(autor__nome__iexact="machado de assis")

# 2. Agora, agregamos o resultado DESSE FILTRO
resultado = livros_do_machado.aggregate(paginas_do_machado=Sum('numero_paginas'))

print(resultado)
# Saída: {'paginas_do_machado': 1250}
```

Com isso, você tem uma visão completa de como sumarizar dados, seja por linha (`annotate`) ou no total (`aggregate`), finalizando os conceitos mais importantes do ORM do Django.

### Referências:

- [Aggregation](https://docs.djangoproject.com/pt-br/5.2/topics/db/aggregation/)

---

## Serializers: O Tradutor e o Contrato da API

Se os `Models` são a fonte da verdade dos seus *dados em Python*, os `Serializers` são a fonte da verdade da sua *API em JSON*.

Eles têm duas funções críticas:

1. **Tradução (Serialização):** Pegam um objeto complexo do Python (um `QuerySet` ou uma instância do model `Autor`) e o transformam em um formato simples de texto, como JSON.

   * `Objeto Autor` (Python) -\> `Serializer` -\> `JSON` (Texto)
2. **Validação (Desserialização):** Pegam um JSON enviado pelo usuário (`request.data`), verificam se todos os dados estão corretos (regras de negócio) e, se estiverem, transformam de volta em dados Python válidos para salvar no banco.

   * `JSON` (Texto) -\> `Serializer` -\> `validação` -\> `Dicionário Python` (Limpo)

Pense no `Serializer` como um **Contrato de API**. Ele define *exatamente* quais campos o frontend pode esperar receber e quais campos ele *deve* enviar.

### Tipos de Serializer: `Serializer` vs. `ModelSerializer`

Existem duas formas principais de herança para criar um serializer:

#### 1\. `serializers.Serializer` (O Manual)

Você define *cada campo* manualmente. Ele não sabe nada sobre seus models.

* **Quando usar?** Para dados que **não** vêm de um model. Ex: um formulário de "contato" que apenas envia um e-mail, ou um endpoint que recebe dados para um cálculo complexo.

**Exemplo:**

```python
# api/serializers.py
from rest_framework import serializers

class FormularioContatoSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    mensagem = serializers.CharField(max_length=1000, required=True)
    # Este serializer não vai salvar nada no banco,
    # apenas validar a entrada.
```

#### 2\. `serializers.ModelSerializer` (O Mágico)

Este é o que você usará em 95% do tempo. Você "aponta" o serializer para um `Model` e ele *automaticamente* cria os campos e as regras de validação para você, com base na definição do seu model.

* `CharField` no model? Vira `CharField` no serializer.
* `blank=True, null=True` no model? Vira `required=False` no serializer.

```python
# api/serializers.py
from .models import Autor, Livro

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        # fields = ['id', 'nome', 'biografia'] # Define campos específicos
        fields = '__all__' # Pega todos os campos do model
```

Com essas 4 linhas, o `AutorSerializer` já sabe como serializar, desserializar, validar, criar e atualizar um `Autor`.

---

### O Processo de Validação: `is_valid()` e `partial`

Esta é a parte de "Contrato" e "Segurança". Você NUNCA deve confiar nos dados vindos do usuário.

Quando um `POST` (criação) ou `PUT` (atualização) chega, seu `request.data` contém o JSON. Veja como usá-lo:

```python
# Em uma View (vamos ver em breve):
def post(self, request, *args, **kwargs):

    # 1. Instanciamos o serializer com os dados da requisição
    serializer = AutorSerializer(data=request.data)

    # 2. A MÁGICA: Chamamos .is_valid()
    # O DRF vai checar:
    # - O 'nome' veio? (required=True)
    # - A 'biografia' (opcional) é um texto?
    if serializer.is_valid():
        # 3. Se tudo estiver OK, podemos salvar.
        # .save() é inteligente: ele chama .create() internamente
        serializer.save()

        # serializer.data agora contém o objeto recém-criado
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 4. Se a validação FALHAR:
    # serializer.errors conterá um dicionário com os problemas
    # Ex: {'nome': ['Este campo é obrigatório.']}
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

#### `partial=True` (Para `PATCH`)

* `PUT`: Exige que o usuário envie **todos** os campos do serializer (o objeto completo). Se um campo obrigatório (`nome`) faltar, `is_valid()` falha.
* `PATCH`: Permite que o usuário envie *apenas* os campos que deseja alterar.

Para fazer um `PATCH` funcionar, você deve passar `partial=True` ao instanciar o serializer. Isso diz ao `is_valid()`: "Relaxe, não tem problema se campos obrigatórios estiverem faltando, só valide os que você recebeu."

```python
# Em um método PATCH de uma view...
autor_existente = ... # Buscamos o autor
dados_parciais = request.data # Ex: {'biografia': 'Nova bio'} (sem 'nome')

# Passamos a instância que queremos atualizar E partial=True
serializer = AutorSerializer(
    instance=autor_existente,
    data=dados_parciais,
    partial=True # <-- A MÁGICA DO PATCH
)

if serializer.is_valid():
    serializer.save() # .save() chama .update() internamente
    return Response(serializer.data)
```

---

### O `context` do Serializer

E se o serializer precisar de uma informação que *não* veio no JSON, mas que a *View* conhece? Exemplo clássico: o `request.user` (o usuário logado).

O `context` é um dicionário que você pode "injetar" no serializer no momento da criação.

**Exemplo:** Queremos que o `AutorSerializer` salve quem foi o `usuario_criador`.

```python
# Na View:
serializer = AutorSerializer(
    data=request.data,
    context={'request': request} # Passamos o request inteiro
)

if serializer.is_valid():
    # Passamos o usuário logado para o método save()
    # (que por sua vez passa para o .create())
    serializer.save(usuario_criador=request.user)
    ...

# E/OU no Serializer:
class AutorSerializer(serializers.ModelSerializer):
    ...
    def validate_nome(self, value):
        # Podemos acessar o context para validações complexas
        request = self.context.get('request')
        if request and request.user.is_superuser:
            # Superusuários não podem ter nomes curtos (exemplo bobo)
            if len(value) < 10:
                raise serializers.ValidationError("Superusuários precisam de nomes longos!")
        return value
```

---

### Lidando com Relacionamentos (Nested Serializers)

Este é um ponto crucial. Por padrão, um `ModelSerializer` lida com `ForeignKey` assim:

```python
class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = '__all__'

# O JSON de saída será:
{
    "id": 1,
    "titulo": "Dom Casmurro",
    "autor": 1  # <-- Ele mostra apenas o ID (PrimaryKey) do autor.
}
```

Isso é ruim para o frontend! Ele teria que fazer outra requisição (`/api/autores/1/`) para descobrir o nome.

Temos 3 formas de melhorar isso:

**1. `StringRelatedField` (Leitura, `__str__`)**
Mostra o que o método `__str__` do model `Autor` retorna (no nosso caso, o nome).

```python
class LivroSerializer(serializers.ModelSerializer):
    # Diga ao DRF para usar o __str__ do Autor
    autor = serializers.StringRelatedField()

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'numero_paginas']

# JSON de saída (GET):
# { "id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis" }
```

* **Pró:** Leve e legível.
* **Contra:** É somente leitura. Você não pode usar esse serializer para *criar* um livro (ele não saberia como transformar "Machado de Assis" de volta no ID 1).

**2. Serializer Aninhado (Nested Serializer)**
Incorpora o JSON completo do `Autor` dentro do JSON do `Livro`.

```python
# Precisamos do AutorSerializer definido ANTES
class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id', 'nome'] # Só queremos o ID e o nome

class LivroSerializer(serializers.ModelSerializer):
    # Diga ao DRF para usar o AutorSerializer para "traduzir" o campo 'autor'
    autor = AutorSerializer(read_only=True) # read_only=True é recomendado
                                            # para evitar complexidade na escrita

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'numero_paginas']

# JSON de saída (GET):
# {
#   "id": 1,
#   "titulo": "Dom Casmurro",
#   "autor": {
#       "id": 1,
#       "nome": "Machado de Assis"
#   }
# }
```

* **Pró:** Envia todos os dados de uma vez. O frontend adora.
* **Contra:** Pode causar o **problema N+1**. Se você listar 100 livros, fará 101 consultas (1 para os livros, 100 para os autores). **Solução:** Use `select_related('autor')` na *View*!

---

## 9\. As Views (Controllers)

Agora sim, a `View`. Se o `Model` é o dado e o `Serializer` é o tradutor, a `View` é o **cérebro**. É a classe que:

1. Recebe a requisição HTTP (GET, POST, PUT, DELETE).
2. Usa os `kwargs` da URL (ex: `/api/autores/1/`) para saber *sobre qual* objeto falamos.
3. Usa o `request.query_params` (ex: `?nome=...`) para filtrar buscas.
4. Usa o `request.data` (o JSON) para obter dados.
5. Chama o `Serializer` para validar e traduzir.
6. Chama o `Model` (ORM) para buscar ou salvar.
7. Envia uma `Response` HTTP.

### A `APIView`: O Bloco de Construção Manual

A `APIView` é a classe base. Ela nos permite definir métodos que correspondem aos verbos HTTP.

Vamos criar nossas views no arquivo `api/views.py`:

```python
# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404 # Atalho útil!

from .models import Autor
from .serializers import AutorSerializer

# Vamos criar DUAS views:
# 1. Uma para a LISTA de autores (/api/autores/)
# 2. Uma para o DETALHE de um autor (/api/autores/<pk>/)

# 1. View de LISTA (GET para listar, POST para criar)
class AutorListaView(APIView):
    """
    View para listar todos os autores e criar um novo.
    """

    def get(self, request, *args, **kwargs):
        """
        Lida com requisições GET para /api/autores/
        Usa 'request.query_params' para filtros.
        """
        # Exemplo de 'request.query_params':
        # /api/autores/?nome=machado
        nome_filtrar = request.query_params.get('nome', None)

        queryset = Autor.objects.all()

        if nome_filtrar:
            # Usamos o que aprendemos de ORM!
            queryset = queryset.filter(nome__icontains=nome_filtrar)

        serializer = AutorSerializer(queryset, many=True) # many=True -> é uma lista!
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Lida com requisições POST para /api/autores/
        Usa 'request.data' para criar.
        """
        # request.data contém o dicionário Python do JSON enviado
        serializer = AutorSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. View de DETALHE (GET, PUT, DELETE para um item específico)
class AutorDetalheView(APIView):
    """
    View para buscar (GET), atualizar (PUT) ou deletar (DELETE)
    um autor específico pelo seu ID (pk).
    """

    def get(self, request, pk, *args, **kwargs):
        """
        Lida com GET para /api/autores/<pk>/
        O 'pk' vem dos 'kwargs' da URL.
        """
        # get_object_or_404: Tenta buscar. Se não achar,
        # retorna um erro 404 (Not Found) automaticamente.
        autor = get_object_or_404(Autor, pk=pk)

        serializer = AutorSerializer(autor)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        """
        Lida com PUT para /api/autores/<pk>/
        Atualiza um objeto completo.
        """
        autor = get_object_or_404(Autor, pk=pk)

        # A diferença do POST: passamos a 'instance' que queremos ATUALIZAR
        serializer = AutorSerializer(instance=autor, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """
        Lida com DELETE para /api/autores/<pk>/
        """
        autor = get_object_or_404(Autor, pk=pk)
        autor.delete()

        # A resposta para um DELETE bem-sucedido é 204 (No Content)
        return Response(status=status.HTTP_204_NO_CONTENT)

```

---

## 10\. Sessão Especial: Generic Views (O Jeito Rápido)

Você deve ter notado que o código da `APIView` é MUITO repetitivo.

* "Busque um objeto, serialize, retorne".
* "Receba dados, valide, salve, retorne".

Isso é o que chamamos de CRUD (Create, Read, Update, Delete). O DRF sabe que isso é 90% do trabalho de uma API e, por isso, ele nos dá as **Generic Views**.

Elas são classes que já vêm com o `get`, `post`, `put`, `delete` prontos. Você só precisa dizer a elas duas coisas:

1. `queryset`: Quais dados usar (ex: `Autor.objects.all()`).
2. `serializer_class`: Qual "tradutor" usar (ex: `AutorSerializer`).

**O Jeito Simples (Estático):**

```python
# api/views.py (O Jeito Simples)
from rest_framework import generics
from .models import Autor
from .serializers import AutorSerializer

class AutorListaView(generics.ListCreateAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer

class AutorDetalheView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
```

Isso funciona, mas tem um problema: o `queryset` é estático. Ele é definido *uma vez* quando o servidor sobe. E se quisermos filtrar dinamicamente com base no usuário logado ou em parâmetros da URL?

### O Próximo Nível: Customizando com `get_queryset()`

Esta é a forma **correta** e mais poderosa de usar Generic Views. Em vez de definir o atributo `queryset`, você sobrescreve o **método** `get_queryset()`.

Este método é chamado *a cada requisição*, o que lhe dá acesso ao `self.request` (com `query_params`, `user`, etc.) e aos `self.kwargs` (com o `pk` da URL).

Vamos ver dois exemplos de por que isso é fundamental.

#### Exemplo 1: Movendo a Lógica de Filtro (O Jeito Certo)

Lembra da nossa `AutorListaView(APIView)` manual, onde colocamos a lógica de filtro dentro do método `get`?

```python
# No nosso 'get' manual da APIView, fizemos isso:
nome_filtrar = request.query_params.get('nome', None)
if nome_filtrar:
    queryset = queryset.filter(nome__icontains=nome_filtrar)
```

Ao usar `generics.ListCreateAPIView`, o lugar certo para essa lógica é dentro de `get_queryset()`:

```python
# api/views.py (O Jeito Correto e Dinâmico)
class AutorListaView(generics.ListCreateAPIView):
    # Não definimos mais 'queryset' aqui!
    serializer_class = AutorSerializer # Só o serializer

    def get_queryset(self):
        """
        Este método é chamado a cada requisição GET.
        É o lugar perfeito para adicionar filtros dinâmicos.
        """
        # 1. Começamos com o queryset base
        queryset = Autor.objects.all()

        # 2. Acessamos a requisição via 'self.request'
        # (Ex: /api/autores/?nome=machado)
        nome_filtrar = self.request.query_params.get('nome', None)

        # 3. Aplicamos o filtro se ele existir
        if nome_filtrar:
            queryset = queryset.filter(nome__icontains=nome_filtrar)

        # 4. Retornamos o queryset final
        return queryset
```

Agora, sua `ListCreateAPIView` tem a mesma capacidade de filtragem que a `APIView` manual, mas com muito menos código.

#### Exemplo 2: Otimizando Performance (Resolvendo o N+1)

Este é o exemplo mais importante.

Lembra na **Seção 8 (Serializers)** que criamos um `LivroSerializer` com um `AutorSerializer` aninhado?

```python
class LivroSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    ...
```

E lembra na **Seção de Performance do ORM** que isso causa o **problema N+1** (1 consulta para os livros + N consultas para os autores)?

A solução que aprendemos foi usar `select_related('autor')`.

Onde colocamos esse `select_related` em uma Generic View? **No `get_queryset()`!**

```python
# api/views.py
from .models import Livro
from .serializers import LivroSerializer # O serializer aninhado

class LivroListaView(generics.ListCreateAPIView):
    """
    Uma view de lista para Livros que resolve o N+1.
    """
    serializer_class = LivroSerializer
    # NUNCA FAÇA ISSO:
    # queryset = Livro.objects.all() # <-- ISSO CAUSA N+1 (RUIM!)

    def get_queryset(self):
        """
        Otimiza a consulta para resolver o N+1
        causado pelo Serializer Aninhado 'autor'.
        """
        # Otimizamos a consulta base ANTES de retorná-la
        return Livro.objects.select_related('autor').all()
```

Agora, quando o DRF for listar os livros, ele usará este `queryset` otimizado, e fará apenas **uma** consulta ao banco de dados, resolvendo o N+1.

Com `get_queryset()`, você conecta tudo o que aprendeu sobre otimização de ORM diretamente nas suas Views.

### Regra de Ouro

* Sempre comece com **`Generic Views`** (como `ListCreateAPIView`). Elas são a norma.
* **Sempre** prefira sobrescrever `get_queryset()` em vez de usar o atributo estático `queryset`. Isso torna seu código dinâmico, testável e otimizado desde o início.
* Use `APIView` (manual) apenas para endpoints que não são CRUD (ex: `/api/mudar-senha/` ou `/api/relatorio-vendas/`).

## 11\. Rotas (URLs)

Temos nossos `Models` (Dados), `Serializers` (Tradutores) e `Views` (Cérebros). Agora, a última peça: como conectar uma URL (ex: `/api/autores/`) a uma `View` (ex: `AutorListaView`)?

Este é o trabalho do `urls.py`. O Django usa um sistema de "dois níveis" de rotas:

1. **Rotas do Projeto (Principais):** O arquivo `seu_projeto/urls.py`.
2. **Rotas do App (Internas):** O arquivo `api/urls.py` (que nós vamos criar).

### 1\. Rotas Internas (do App)

Primeiro, criamos um arquivo `urls.py` dentro do nosso app `api`:

**`api/urls.py`**

```python
from django.urls import path
from . import views # Importa as views que acabamos de criar

app_name = 'api' # Boa prática para organizar

urlpatterns = [
    # Conecta a URL 'autores/' à View 'AutorListaView'
    path(
        'autores/',
        views.AutorListaView.as_view(),
        name='autor-lista'
    ),

    # Conecta a URL 'autores/<int:pk>/' à View 'AutorDetalheView'
    # <int:pk> captura o número da URL e o passa como 'pk' para a View
    path(
        'autores/<int:pk>/',
        views.AutorDetalheView.as_view(),
        name='autor-detalhe'
    ),
]
```

**Nota:** Como estamos usando *Classes* de View (ex: `AutorListaView`), somos obrigados a chamar `.as_view()` para que o Django saiba como usá-la.

### 2\. Rotas Normais (do Projeto)

Agora, só precisamos "avisar" ao projeto principal que as rotas do nosso app `api` existem. Fazemos isso usando `include()` no `urls.py` principal:

**`seu_projeto/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include # IMPORTANTE: Adicionar 'include'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Esta é a linha que você adiciona:
    # Ela diz ao Django: "Qualquer URL que comece com 'api/',
    # vá procurar as regras dentro do arquivo 'api.urls'".
    path('api/', include('api.urls')),
]
```

### Resumo das Rotas:

* O usuário acessa: `http://localhost:8000/api/autores/1/`
* O Django lê `seu_projeto/urls.py`.
* Ele encontra `path('api/', ...)` e "corta" o `api/` da URL.
* Ele entrega o resto da URL (`autores/1/`) para o arquivo `api/urls.py`.
* O `api/urls.py` lê `autores/1/`.
* Ele encontra `path('autores/<int:pk>/', ...)`.
* Ele "casa" a URL, captura `pk = 1`.
* Ele chama a view `AutorDetalheView` e passa o `request` e o `pk=1` para ela.

---

## Bônus

## 12\. ViewSets e Routers: O Jeito Mais Rápido do DRF

Até agora, para criar um CRUD completo para `Autor`, nós precisamos de:

1. Uma classe `AutorListaView(generics.ListCreateAPIView)` para a lista (`GET`, `POST`).
2. Uma classe `AutorDetalheView(generics.RetrieveUpdateDestroyAPIView)` para o detalhe (`GET`, `PUT`, `DELETE`).
3. Duas chamadas `path()` no `api/urls.py` para ligar essas views.

Isso funciona, mas ainda é um pouco repetitivo. O DRF oferece uma abstração ainda maior que combina tudo isso: `ViewSet` e `Router`.

### O que é um `ViewSet`?

Um `ViewSet` não é exatamente uma `View`. É uma classe que **agrupa a lógica de múltiplas views relacionadas** em um único lugar.

Em vez de ter uma classe para "Lista" e outra para "Detalhe", você terá apenas **uma classe**: `AutorViewSet`.

Ele não usa métodos `get()`, `post()`, etc. Em vez disso, ele implementa *ações* que o `Router` saberá como mapear:

* `.list()` (para o `GET` da lista)
* `.create()` (para o `POST` da lista)
* `.retrieve()` (para o `GET` do detalhe)
* `.update()` (para o `PUT` do detalhe)
* `.partial_update()` (para o `PATCH` do detalhe)
* `.destroy()` (para o `DELETE` do detalhe)

### `ModelViewSet`: O "Generic ViewSet"

Assim como temos `Generic Views` (ex: `ListCreateAPIView`), nós temos "Generic ViewSets". O mais poderoso de todos é o **`ModelViewSet`**.

Ele já vem com a implementação de **todas as 6 ações** (list, create, retrieve, update, partial\_update, destroy) prontas. Você só precisa dizer o `queryset` e o `serializer_class`.

Vamos reescrever nossas views de `Autor` usando um `ModelViewSet`:

```python
# api/views.py (O Jeito ViewSet)
from rest_framework import viewsets
from .models import Autor
from .serializers import AutorSerializer

# A UMA CLASSE PARA GOVERNAR TODAS
class AutorViewSet(viewsets.ModelViewSet):
    """
    Este ÚNICO ViewSet substitui AMBAS as classes
    'AutorListaView' e 'AutorDetalheView'.

    Ele já fornece as ações:
    - .list()
    - .create()
    - .retrieve()
    - .update()
    - .partial_update()
    - .destroy()
    """
    serializer_class = AutorSerializer

    # E, claro, o mais importante:
    # Podemos usar get_queryset() para otimizações e filtros!
    def get_queryset(self):
        """
        Este método continua sendo a melhor prática!
        """
        queryset = Autor.objects.all()

        # Filtro dinâmico
        nome_filtrar = self.request.query_params.get('nome', None)
        if nome_filtrar:
            queryset = queryset.filter(nome__icontains=nome_filtrar)

        # Otimização de N+1 (se tivéssemos um 'prefetch_related' para livros)
        # queryset = queryset.prefetch_related('livros') # Exemplo

        return queryset
```

Pronto. É só isso. Agora temos toda a lógica de CRUD do `Autor` em uma única classe.

### O que é um `Router`?

Agora vem a mágica. Se o `ViewSet` não tem métodos `.get()` ou `.post()`, como o `urls.py` sabe o que chamar?

A resposta é que você **não usa `path()` para um ViewSet**. Você usa um `Router`.

O **`Router`** é um objeto que *inspeciona* seu `ViewSet` e **gera automaticamente as rotas (`path`) para você**, conectando os verbos HTTP (GET, POST, etc.) às ações corretas (.list(), .create(), etc.).

Vamos reescrever nosso `api/urls.py` para usar o `Router`.

```python
# api/urls.py (O Jeito Router)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 1. Cria uma instância do DefaultRouter
# O DefaultRouter também cria uma "página raiz" da API para você!
router = DefaultRouter()

# 2. REGISTRA o ViewSet no router
# router.register(prefixo_url, viewset, nome_base)
# O 'r' antes da string é para 'raw string', uma boa prática para URLs
router.register(r'autores', views.AutorViewSet, basename='autor')
router.register(r'livros', views.LivroViewSet, basename='livro') # Se tivéssemos um

app_name = 'api'

# 3. As urlpatterns do Django agora só precisam incluir as URLs do router
urlpatterns = [
    path('', include(router.urls)),
    # Você ainda pode adicionar paths manuais aqui se precisar
    # path('meu-path-manual/', views.MinhaViewManual.as_view()),
]
```

### O que o `Router` Acabou de Fazer?

Ao registrar `r'autores'` com o `AutorViewSet`, o `DefaultRouter` gerou automaticamente as seguintes rotas para nós:

* **URL:** `api/autores/`
  * `GET`: Mapeado para `AutorViewSet.list()`
  * `POST`: Mapeado para `AutorViewSet.create()`
* **URL:** `api/autores/<int:pk>/`
  * `GET`: Mapeado para `AutorViewSet.retrieve()`
  * `PUT`: Mapeado para `AutorViewSet.update()`
  * `PATCH`: Mapeado para `AutorViewSet.partial_update()`
  * `DELETE`: Mapeado para `AutorViewSet.destroy()`

Tudo isso, com 2 linhas de código no `urls.py` e \~10 linhas no `views.py`.

---

### Qual Abordagem Usar? (Resumo)

Agora você conhece as 3 formas de criar Views no DRF:

1. **`APIView` (Manual)**

   * **Pró:** Controle total e absoluto.
   * **Contra:** Muito código repetitivo (boilerplate).
   * **Quando:** Para endpoints que não são CRUD (ex: `/api/mudar-senha/`, `/api/relatorio-vendas/`).
2. **`Generic Views` (Semi-Automática)**

   * **Pró:** Remove todo o boilerplate do CRUD. `get_queryset()` e `get_serializer_class()` dão ótimo controle.
   * **Contra:** Requer que você configure as rotas manualmente no `urls.py` com `path()`.
   * **Quando:** Excelente para CRUDs onde você quer ter controle fino sobre as URLs ou quando você só quer expor *parte* do CRUD (ex: apenas `List` e `Retrieve`, sem `Create` ou `Delete`).
3. **`ViewSets` + `Routers` (Automática)**

   * **Pró:** O mais rápido de implementar. Gera todo o CRUD e as URLs com pouquíssimo código.
   * **Contra:** Você "perde" o controle explícito das URLs (elas são geradas por convenção).
   * **Quando:** O padrão para a vasta maioria dos CRUDs em APIs RESTful. Se você tem um model e quer expô-lo via API, comece aqui.

### Referências:

- [Views](https://www.django-rest-framework.org/api-guide/views/)
- [Generics](https://www.django-rest-framework.org/api-guide/generic-views/)
- [Routers](https://www.django-rest-framework.org/api-guide/routers/)
- [Serializers](https://www.django-rest-framework.org/api-guide/serializers/)
- [Relacionamentos com Serializers](https://www.django-rest-framework.org/api-guide/relations/)

---

## Autenticação e Permissões

1. **Autenticação (AuthN):** "Quem é você?"

   * É o processo de identificar o usuário que está fazendo a requisição. Ele é o segurança na porta "checando sua identidade".
   * O DRF não "se importa" *como* você prova quem é (se é por sessão, token, etc.), desde que você prove.
   * Se a autenticação for bem-sucedida, ela preenche o objeto `request.user`. Se falhar, ela preenche `request.user` com um `AnonymousUser`.
2. **Permissões (AuthZ):** "O que você *pode* fazer?"

   * É o processo que ocorre *depois* que o usuário é identificado (ou não).
   * Ele olha para o `request.user`, o método da requisição (`GET`, `POST`) e o objeto (se for o caso) e decide: "Esse usuário tem autorização para fazer *esta* ação?"
   * Ele é o segurança "checando a lista VIP" para ver se você pode entrar na área restrita.

O fluxo em toda `View` do DRF é sempre este:

1. A requisição chega.
2. As classes de **Autenticação** rodam primeiro para popular o `request.user`.
3. As classes de **Permissão** rodam em seguida, usando o `request.user` para decidir se a requisição continua.
4. Se for permitida, o seu código da view (ex: `get`, `post`, ou `get_queryset`) finalmente executa.

---

## 12\. Autenticação e Permissões

Com nossos endpoints de CRUD funcionando, eles ainda estão totalmente públicos. Esta seção explica como controlar *quem* pode acessar sua API e *o que* eles podem fazer.

### Autenticação (Quem é você?)

O primeiro passo é a autenticação. O trabalho dela é popular o `request.user` com um usuário válido. O DRF vem com várias estratégias prontas. As mais comuns para APIs são:

1. **`SessionAuthentication`**: Usa o sistema de sessão padrão do Django. Perfeito se o seu frontend é um template do Django (no mesmo projeto) e o usuário "faz login" no site.
2. **`TokenAuthentication`**: Uma estratégia simples baseada em token. Você gera um token de API (uma longa string) para cada usuário, e o cliente deve enviar esse token em cada requisição no cabeçalho `Authorization`.
   * Ex: `Authorization: Token 9944b09199c62bcf94180da8f80041251e608a11`
   * É ideal para apps mobile ou frontends externos (React, Vue) que não compartilham sessões.

#### Configurando a Autenticação

Você pode definir quais métodos de autenticação sua API aceita globalmente no `settings.py`:

```python
# seu_projeto/settings.py

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Permite que o usuário seja identificado por Sessão (ex: no Admin)
        'rest_framework.authentication.SessionAuthentication',

        # Permite que o usuário seja identificado por Token
        'rest_framework.authentication.TokenAuthentication',
    ],
    # Por enquanto, vamos deixar as permissões abertas por padrão
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# Para TokenAuthentication funcionar, não se esqueça de adicionar
# 'rest_framework.authtoken' ao seu INSTALLED_APPS e rodar migrate.
```

Agora, sua API tentará identificar o usuário usando Sessão *ou* Token. Se nenhum for fornecido, `request.user` será `AnonymousUser`.

### Permissões (O que você pode fazer?)

Depois que o `request.user` é definido, as permissões entram em ação. O DRF também fornece várias classes prontas que são extremamente úteis.

Aqui estão as mais importantes:

* **`AllowAny`**: (Padrão) Permite acesso a qualquer um, incluindo usuários anônimos (`AnonymousUser`).
* **`IsAuthenticated`**: Permite acesso *apenas* a usuários autenticados (ou seja, `request.user` não pode ser `AnonymousUser`).
* **`IsAdminUser`**: Permite acesso *apenas* a usuários administradores (`user.is_staff == True`).
* **`IsAuthenticatedOrReadOnly`**: **A mais útil!** Ela permite que qualquer um faça requisições "seguras" (`GET`, `HEAD`, `OPTIONS`), mas exige autenticação para qualquer requisição de "escrita" (`POST`, `PUT`, `PATCH`, `DELETE`).

#### Aplicando Permissões nas nossas Views

Vamos aplicar `IsAuthenticatedOrReadOnly` em nossas `Generic Views` de `Autor`. Isso fará com que nossa API seja uma "API de leitura pública":

* **Qualquer um** (anônimo) pode *ver* a lista de autores (`GET /api/autores/`).
* **Qualquer um** (anônimo) pode *ver* o detalhe de um autor (`GET /api/autores/1/`).
* **Apenas usuários logados** podem *criar* um novo autor (`POST /api/autores/`).
* **Apenas usuários logados** podem *atualizar* um autor (`PUT /api/autores/1/`).
* **Apenas usuários logados** podem *deletar* um autor (`DELETE /api/autores/1/`).

```python
# api/views.py
from rest_framework import generics
from rest_framework import permissions # 1. Importamos as permissões

from .models import Autor
from .serializers import AutorSerializer

class AutorListaView(generics.ListCreateAPIView):
    # 2. Adicionamos a classe de permissão
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = AutorSerializer

    def get_queryset(self):
        queryset = Autor.objects.all()
        nome_filtrar = self.request.query_params.get('nome', None)
        if nome_filtrar:
            queryset = queryset.filter(nome__icontains=nome_filtrar)
        return queryset

class AutorDetalheView(generics.RetrieveUpdateDestroyAPIView):
    # 2. Adicionamos a classe de permissão aqui também
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
```

Com apenas **duas linhas de código**, nossa API agora está protegida contra escrita não autorizada.

---

### Criando Permissões Customizadas (O Próximo Nível)

E se quisermos uma regra mais complexa?
**Regra:** "O usuário só pode editar ou deletar um `Autor` se ele mesmo o criou."

Isso é uma **permissão em nível de objeto**. Para isso, precisamos de duas coisas:

1. Um jeito de saber quem "criou" o autor.
2. Uma classe de permissão customizada que checa isso.

#### 1\. Salvando o "Dono" (com `perform_create`)

Primeiro, vamos assumir que nosso model `Autor` tem um campo `ForeignKey` para o usuário:

```python
# api/models.py
from django.conf import settings

class Autor(BaseTimestampedModel):
    # ... outros campos ...
    usuario_criador = models.ForeignKey(
        settings.AUTH_USER_MODEL, # O jeito correto de apontar para o User
        on_delete=models.SET_NULL, # Se o usuário for deletado, não delete o autor
        null=True,
        blank=True,
        related_name="autores_criados"
    )
```

*(Lembre-se de rodar `makemigrations` e `migrate` depois de adicionar este campo)*

Agora, como preenchemos esse campo? Não podemos pedir para o usuário enviá-lo no JSON (seria uma falha de segurança). Nós devemos preenchê-lo automaticamente na View, usando o `request.user` logado.

Nas `Generic Views`, o método correto para isso é o `perform_create()`:

```python
# api/views.py
class AutorListaView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = AutorSerializer
    # ... get_queryset ...

    def perform_create(self, serializer):
        """
        Este método é chamado pelo DRF logo antes de salvar
        um novo objeto (após .is_valid() ser True).
        """
        # Salvamos o objeto, mas injetamos o 'usuario_criador'
        # com o usuário que está logado no request.
        serializer.save(usuario_criador=self.request.user)
```

Agora, todo novo `Autor` criado via `POST` terá o `usuario_criador` corretamente associado.

#### 2\. A Classe de Permissão Customizada

Agora, criamos nossa regra. Crie um novo arquivo `api/permissions.py`:

```python
# api/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada que só permite que o "dono" (criador)
    de um objeto possa editá-lo.
    Todos os outros podem ver (somente leitura).
    """

    def has_object_permission(self, request, view, obj):
        # 'has_object_permission' é chamado para o detalhe (GET, PUT, DELETE)
        # 'obj' aqui é a instância do Autor que está sendo acessada.

        # 1. Permite requisições de leitura (GET, HEAD, OPTIONS) para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Nega a permissão se o objeto não tiver um criador
        if obj.usuario_criador is None:
            return False

        # 3. Permite a escrita (PUT, DELETE) apenas se
        # o usuário do request for o mesmo que o 'usuario_criador' do objeto.
        return obj.usuario_criador == request.user
```

#### 3\. Aplicando a Nova Permissão

Por fim, usamos nossa nova permissão na View de *Detalhe*, pois ela é a única que lida com objetos individuais.

```python
# api/views.py
from .permissions import IsOwnerOrReadOnly # Importamos nossa permissão

class AutorDetalheView(generics.RetrieveUpdateDestroyAPIView):
    # Aplicamos nossa nova permissão!
    # O DRF é inteligente: ele usa a primeira permissão que se aplica.
    # IsAuthenticatedOrReadOnly garante que o usuário esteja logado para editar
    # IsOwnerOrReadOnly garante que ele seja o dono.
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
```

E pronto! Agora nossa API tem uma lógica de permissão em nível de objeto, que é segura e robusta.

## 13\. Autenticação Moderna com JWT (Simple JWT)

Enquanto a `TokenAuthentication` (que vimos na seção anterior) é simples, ela não é ideal para a maioria das aplicações modernas por questões de segurança (tokens permanentes) e performance (consultas ao banco).

A solução padrão da indústria hoje é o **JWT (JSON Web Token)**.

### O que é um JWT?

Pense no `TokenAuthentication` como uma "chave de hotel" que abre uma porta e é salva no banco de dados.

Pense no `JWT` como um "crachá de evento" (um *token*) que contém informações verificadas:

* **Payload:** "Este crachá pertence ao usuário 'João' (user\_id: 5)."
* **Payload:** "Este crachá expira às 17:00h."
* **Assinatura:** "Este crachá foi emitido pela 'Organização do Evento' (seu servidor) e é autêntico."

**A grande vantagem:** Quando o segurança (seu servidor) vê o crachá, ele não precisa consultar uma lista no banco de dados. Ele apenas verifica a **assinatura** para garantir que é um crachá válido e verifica a **data de expiração**.

Isso é chamado de autenticação **"stateless" (sem estado)**. É muito mais rápido e seguro.

### O Conceito-Chave do `simplejwt`: Access e Refresh

Para evitar que um token de longa duração vaze, o `simplejwt` usa um sistema de dois tokens:

1. **Token de Acesso (Access Token):**

   * É o token que você envia em *cada* requisição para se autenticar.
   * Tem uma **duração muito curta** (ex: 5 a 15 minutos).
   * Se ele vazar, o invasor só tem acesso por 5 minutos.
   * É enviado no cabeçalho: `Authorization: Bearer <access_token>`
2. **Token de Atualização (Refresh Token):**

   * É um token de **longa duração** (ex: 1 dia ou 1 semana).
   * Ele é usado **apenas uma vez**: quando o seu *Access Token* expirar.
   * Sua única função é ser enviado para um endpoint especial (`/api/token/refresh/`) para "provar" que você ainda é um usuário válido e "pegar" um *novo* Access Token.
   * Ele deve ser guardado de forma segura pelo cliente.

---

### Como Implementar o `simplejwt` (Passo a Passo)

#### Passo 1: Instalação

```bash
pip install djangorestframework-simplejwt
```

#### Passo 2: Configuração (`settings.py`)

Primeiro, adicione a biblioteca ao seu `INSTALLED_APPS`:

```python
# seu_projeto/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt', # Adicione esta linha
    'corsheaders',
    'api',
]
```

Segundo, diga ao DRF para usar o `simplejwt` como o método de autenticação padrão. Isso substitui o `TokenAuthentication` que vimos antes.

```python
# seu_projeto/settings.py

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Diga ao DRF para usar JWT
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        # Mantenha as permissões que já definimos
        'rest_framework.permissions.IsAuthenticated',
        # 'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # 'rest_framework.permissions.AllowAny',
    ],
}
```

**Pronto!** A partir de agora, as permissões como `IsAuthenticated` vão *automaticamente* funcionar com JWT. Elas não se importam *como* o `request.user` foi preenchido, apenas *se* ele foi preenchido.

#### (Opcional) Configurando o Tempo de Vida dos Tokens

Por padrão, o Access Token dura 5 minutos. Você pode mudar isso adicionando um bloco `SIMPLE_JWT` ao seu `settings.py`:

```python
# seu_projeto/settings.py
from datetime import timedelta

# ...

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}
```

#### Passo 3: Configurando as Rotas (`urls.py`)

O `simplejwt` já vem com views prontas para "obter" e "atualizar" os tokens. Você só precisa adicioná-las às suas URLs.

É comum adicioná-las no `urls.py` **principal do projeto**.

```python
# seu_projeto/urls.py
from django.contrib import admin
from django.urls import path, include

# 1. Importe as views do simplejwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # 2. Adicione as rotas de JWT

    # Esta rota espera um POST com 'username' e 'password'
    # e retorna os tokens 'access' e 'refresh'
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Esta rota espera um POST com o 'refresh' token
    # e retorna um 'access' token novo
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

### O Fluxo de Autenticação na Prática

Agora que está tudo configurado, veja como o cliente (frontend/mobile) irá usar sua API:

**1. Fazer Login (Obter Tokens)**
O usuário digita o login e senha. O cliente faz um `POST` para a rota que você criou:

`POST /api/token/`

```json
{
    "username": "junior_developer",
    "password": "senha_super_segura_123"
}
```

Se o login e senha estiverem corretos, o `simplejwt` (através da `TokenObtainPairView`) responderá com:

```json
{
    "refresh": "eyJ...longo_refresh_token...Dk0",
    "access": "eyJ...longo_access_token...fX0"
}
```

O cliente deve salvar esses dois tokens de forma segura.

**2. Fazer Requisições (Acessar dados protegidos)**
Agora, para acessar sua view de Autores (que tem `permission_classes = [IsAuthenticated]`), o cliente deve enviar o **Access Token** no cabeçalho `Authorization`:

`GET /api/autores/`

```http
Header:
Authorization: Bearer eyJ...longo_access_token...fX0
```

O `JWTAuthentication` do DRF irá:

1. Ver o cabeçalho.
2. Validar a assinatura e a expiração do token.
3. Descobrir o `user_id` de dentro do token.
4. Preencher o `request.user` com o usuário correspondente.
5. A permissão `IsAuthenticated` vê um usuário válido e permite o acesso.

**3. Quando o Token Expirar (Atualizar)**
Após 15 minutos (ou o tempo que você definiu), a requisição do passo 2 vai falhar com um erro `401 Unauthorized`.

O cliente, ao ver esse erro, deve **automaticamente e em silêncio**:

1. Fazer um `POST` para a rota de refresh com o **Refresh Token** que ele guardou:

   `POST /api/token/refresh/`

   ```json
   {
       "refresh": "eyJ...longo_refresh_token...Dk0"
   }
   ```
2. O servidor responderá com um *novo* Access Token:

   ```json
   {
       "access": "eyJ...NOVO_access_token...Kx8"
   }
   ```
3. O cliente salva esse *novo* Access Token (substituindo o antigo) e **tenta novamente** a requisição original (`GET /api/autores/`).

Para o usuário, todo esse processo de atualização é invisível. A aplicação apenas "continua funcionando" sem pedir que ele faça login novamente.
--------------------------------------------------------------------------------------------------------------------------------------------------------

### Referências:

- [ViewSets](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Autenticação](https://www.django-rest-framework.org/api-guide/authentication/)
- [Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)

---

# **Qualquer dúvida, sempre consulte a `Documentação` do projeto que foram deixados no início do documento.**
