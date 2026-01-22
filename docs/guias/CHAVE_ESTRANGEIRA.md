## Índice

1. Introdução rápida
2. Por que deletar objetos é mais complicado do que parece
3. `on_delete` — as opções padrões e quando usar cada uma

   * `CASCADE`
   * `SET_NULL`
   * `SET_DEFAULT`
   * `DO_NOTHING`
   * `PROTECT`
   * `RESTRICT`
   * `SET(value)`
4. Como testar o comportamento de exclusão
5. Erros importantes: `ProtectedError` e `RestrictedError`
6. `Collector` — o que é e como o Django usa internamente

   * principais métodos e uso prático
7. `get_candidate_relations_to_delete` — para que serve
8. Boas práticas e recomendações
9. Resumo rápido
10. Extras: dicas de depuração e admin

---

## 1. Introdução rápida

No Django, quando você tem um relacionamento entre modelos (por exemplo, `Post` que tem um `ForeignKey` para `Author`), você precisa decidir o que acontece com os objetos filhos quando o objeto pai for apagado. Essas regras são definidas com o parâmetro `on_delete` do campo (`ForeignKey`, `OneToOneField`, etc.).

O Django fornece funções/constantes que definem esse comportamento — elas podem deletar em cascata, proteger, setar `NULL`, etc. Além disso, o Django possui uma classe interna chamada `Collector` que realiza a "coleta" dos objetos que serão afetados por uma exclusão.

Este documento explica cada item com exemplos práticos e fáceis de entender.

---

## 2. Por que deletar objetos é mais complicado do que parece

* Um banco de dados pode ter várias relações encadeadas. Ao remover A, B e C podem ser afetados.
* Você pode querer evitar perda acidental de dados (por isso `PROTECT` e `RESTRICT` existem).
* Em alguns casos precisamos apenas desassociar (ex.: `SET_NULL`) em vez de deletar.

Por isso Django pede para você escolher explicitamente o comportamento — isso evita decisões implícitas perigosas.

---

## 3. `on_delete` — opções e exemplos

> Exemplo mínimo de uso:

```py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
```

A seguir explicamos cada valor possível de `on_delete`.

### `CASCADE`

* **O que faz:** Deleta os objetos relacionados também. Se você deletar o `Author`, todos os `Post`s ligados a esse `Author` serão deletados.
* **Quando usar:** Quando os objetos filhos só fazem sentido atrelados ao pai (ex.: comentários de um post).
* **Exemplo:** `on_delete=models.CASCADE`
* **Atenção:** pode causar grandes deleções encadeadas se o seu esquema tiver muitos relacionamentos.

### `SET_NULL`

* **O que faz:** Define o campo `NULL` nos objetos relacionados.
* **Requisito:** o campo deve ter `null=True`.
* **Quando usar:** quando você deseja manter os registros filhos, mas indicar que a referência foi removida.
* **Exemplo:** `author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)`

### `SET_DEFAULT`

* **O que faz:** Define o campo para o valor default do campo (ou um valor definido pelo `default=` do campo).
* **Requisito:** o campo deve ter `default=` configurado.
* **Quando usar:** se houver um valor padrão lógico que represente "sem pai".
* **Exemplo:** `on_delete=models.SET_DEFAULT` e `default=some_default_author`

### `DO_NOTHING`

* **O que faz:** Não faz nada automaticamente — a operação de delete é tentada, mas se o banco exigir integridade referencial (constraint de FK) o banco pode lançar um erro.
* **Quando usar:** raramente; somente quando você gerencia integridade manualmente ou possui triggers/constraints no banco que tratarão o caso.
* **Atenção:** pode causar `IntegrityError` no nível do banco. Use com cuidado.

### `PROTECT`

* **O que faz:** Impede a exclusão do objeto pai enquanto existirem filhos relacionados. Levanta `ProtectedError` se você tentar deletar.
* **Quando usar:** quando é crítico que existam filhos para um pai (ex.: não permitir apagar um `Category` que ainda tem `Product`s).
* **Exemplo:** `on_delete=models.PROTECT`

### `RESTRICT`

* **O que faz:** Semelhante ao `PROTECT`, impede a exclusão do pai se existirem objetos referenciando ele, mas com regras mais finas (pode levar em conta chaves compostas e outras situações).
* **Quando usar:** quando você quer bloquear a exclusão do pai enquanto houver referências — é uma versão mais "recente"/"estrita" que lida melhor com certas relações.
* **Atenção:** verifique a versão do Django do seu projeto — `RESTRICT` foi introduzido em versões recentes do Django. (Se seu projeto usa Django antigo, esse comportamento pode não estar disponível.)

### `SET(value)`

* **O que faz:** Permite passar uma **função** ou **valor** que será definido no campo quando o pai for deletado.
* **Útil para:** setar um valor customizado (ex.: `SET(get_default_user)` ou `SET(0)`)
* **Exemplo:**

```py
from django.db import models
from django.db.models import SET

def get_system_user_id():
    # exemplo: retornar id do usuário "sistema"
    return 1

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=SET(get_system_user_id))
```

`SET()` retorna uma callable que o Django chamará para obter o valor.

---

## 4. Como testar o comportamento de exclusão

Crie pequenos testes unitários com `pytest` ou `unittest`:

```py
from django.test import TestCase
from myapp.models import Author, Post

class DeleteBehaviorTests(TestCase):
    def test_cascade_deletes_posts(self):
        a = Author.objects.create(name='A')
        p = Post.objects.create(author=a, title='X')
        a.delete()
        self.assertEqual(Post.objects.count(), 0)
```

Teste para cada estratégia: `CASCADE`, `SET_NULL`, `PROTECT` etc. Isso te dá confiança ao mudar modelos.

---

## 5. Erros importantes: `ProtectedError` e `RestrictedError`

* **`ProtectedError`**

  * Quando ocorre: ao tentar deletar um objeto pai que está protegido por `on_delete=PROTECT`.
  * O que contém: `protected_objects` — um `set` com os objetos que causaram a proteção.
  * Como tratar: capturar a exceção e informar o usuário (ou deletar filhos antes, se fizer sentido).
* **`RestrictedError`**

  * Quando ocorre: quando `on_delete=RESTRICT` bloqueia a exclusão.
  * O que contém: `restricted_objects` — um `set` com os objetos que impedem a exclusão.
  * Como tratar: igual ao `ProtectedError` — capturar e decidir próxima ação.

**Exemplo de captura**:

```py
from django.db.models.deletion import ProtectedError

try:
    parent.delete()
except ProtectedError as e:
    # e.protected_objects tem os objetos relacionados
    print('Não foi possível deletar, existem objetos protegidos:', e.protected_objects)
```

---

## 6. `Collector` — o que é e como o Django usa internamente

O `Collector` é uma classe interna do Django usada para **coletar** todos os objetos que serão afetados por uma operação de exclusão. Ele percorre o grafo de relações entre modelos e monta uma lista/estrutura de objetos a serem deletados ou processados segundo o `on_delete`.

### Principais responsabilidades

* Descobrir *quais* objetos seriam afetados por uma exclusão (incluindo objetos relacionados várias camadas abaixo).
* Aplicar as ações definidas em `on_delete` (por exemplo: chamar funções como `CASCADE`, `SET_NULL`, `PROTECT`).
* Determinar se um delete pode ser feito "rápido" (fast delete) ou requer processamento (`can_fast_delete`).

### Uso básico (interno do Django)

Você normalmente **não precisa instanciar** `Collector` no seu código aplicado. O Django usa-o dentro de `Model.delete()` e do ORM. Ainda assim, entender sua API ajuda ao depurar exclusões complexas.

Assinatura simplificada (para entendimento):

```py
class Collector:
    def __init__(self, using: str) -> None: ...
    def collect(self, objs, source=None, source_attr=None, **kwargs): ...
    def can_fast_delete(self, objs, from_field=None) -> bool: ...
```

* `collect(objs, source, source_attr)` — percorre e adiciona objetos que seriam afetados.
* `can_fast_delete(...)` — verifica se o Django pode emitir um `DELETE FROM table WHERE pk IN (...)` diretamente no banco, ou se precisa carregar objetos Python (por causa de `on_delete` customizado, sinais, ou restrições).

### Exemplo de por que isso importa

Se `can_fast_delete()` for `True`, Django pode executar uma query direta e rápida no banco. Caso contrário, ele carrega os objetos e executa a lógica Python (mais lenta, segura para `SET()` e `PROTECT`).

---

## 7. `get_candidate_relations_to_delete` — para que serve

* Essa função recebe os `Options` (metadados do modelo) e retorna *os campos relacionados* que devem ser considerados quando um modelo for deletado.
* Em termos simples: dado um modelo, ela ajuda a listar *quais* relacionamentos (FKs) apontam para ele e que precisam ser avaliados pelo processo de exclusão.

Você raramente precisa chamá-la diretamente; é mais útil para quem escreve ferramentas/metadados ou prende-se ao internals do Django.

---

## 8. Boas práticas e recomendações

1. **Escolha o comportamento mais conservador por padrão** — `PROTECT` ou `RESTRICT` são boas opções quando existe risco de perda de dados importante.
2. **Use `CASCADE` quando os filhos não fizerem sentido isolados** (comentários de post, por exemplo).
3. **Evite `DO_NOTHING` a menos que saiba exatamente o que está fazendo** — pode quebrar integridade referencial.
4. **Documente decisões de `on_delete` no model docstring ou no README do projeto** — outros devs precisam entender o porquê da escolha.
5. **Teste com unit tests** — sempre crie testes que verifiquem o comportamento de delete.
6. **Tenha cuidado com deleções em massa** — um `delete()` em queryset pode disparar cascading inesperado.
7. **Considere usar `signals` (ex.: `pre_delete`, `post_delete`) com cuidado** — útil para auditoria, limpeza de arquivos, etc., mas podem interagir com o Collector e `on_delete`.

---

## 9. Resumo rápido

* `on_delete` controla o que acontece com objetos relacionados quando o pai é deletado.
* Principais opções: `CASCADE`, `SET_NULL`, `SET_DEFAULT`, `DO_NOTHING`, `PROTECT`, `RESTRICT`, `SET()`.
* `ProtectedError` e `RestrictedError` são lançados quando `PROTECT`/`RESTRICT` impedem a exclusão.
* `Collector` é a classe interna que calcula e executa o que deve acontecer numa exclusão.
* Testes e documentação salvam tempo e evitam bugs.

---

## 10. Extras: dicas de depuração

* Para ver o que o Django está fazendo internamente, habilite o logging do ORM e observe queries: `LOGGING` no `settings.py`.
* Em casos complexos, crie pequenos scripts (ou `manage.py shell`) e use o `Collector` para inspecionar (apenas para depuração). Exemplo: (apenas leitura, não execute em produção sem entender):

```py
from django.db.models.deletion import Collector
from django.db import router
from myapp.models import Author

using = router.db_for_write(Author)
collector = Collector(using)
collector.collect([Author.objects.get(pk=1)])
# inspecione collector.data ou estruturas internas (dependendo da versão do Django)
```

* Se o delete dá `IntegrityError` com `DO_NOTHING`, provavelmente o banco impõe FK `ON DELETE RESTRICT` ou similar.

---

### Perguntas frequentes (caso tenha dúvidas)

* **Posso mudar `on_delete` depois que já tenho dados?** Sim, mas tome cuidado: os dados existentes podem ficar em estado ambíguo (ex.: filhos apontando para pais inexistentes) — geralmente você precisa migrar os dados antes e garantir integridade.
* **`CASCADE` pode deletar tudo?** Sim, dependendo do grafo de relações, pode causar deleções em cascata profundas. Use com cuidado.
