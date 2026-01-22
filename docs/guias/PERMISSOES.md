# Uso de Permissions no Django Rest Framework (DRF)

Esta documentação explica **de forma simples e prática** como funcionam as **Permissions (permissões)** no Django Rest Framework, usando um **exemplo genérico de controle de estoque**, com os papéis:

* **Supervisor**
* **Gerente**
* **Estoquista**

O objetivo é ajudar desenvolvedores a entender **quando e por que usar permissions**, sem entrar em detalhes técnicos desnecessários.

---

## 📌 O que são Permissions no DRF?

Permissions definem **quem pode acessar o quê** dentro da API.

Em outras palavras, elas respondem à pergunta:

> “Esse usuário pode acessar esse endpoint?”

No DRF, as permissions são avaliadas **antes** da execução da lógica da view.

Se a permissão falhar:

* A requisição é bloqueada
* A API retorna **403 – Forbidden**

---

## 🏢 Cenário do exemplo: Sistema de Estoque

Imagine um sistema simples de estoque com três tipos de usuários:

### 👷 Estoquista

* Pode **consultar produtos**
* Pode **dar entrada e saída no estoque**

### 🧑‍💼 Supervisor

* Pode fazer tudo que o Estoquista faz
* Pode **corrigir movimentações**

### 🧑‍💻 Gerente

* Pode fazer tudo
* Pode **gerenciar produtos**
* Pode **acessar relatórios**

---

## 🧩 Como o DRF usa permissions

As permissions ficam dentro da view ou viewset:

```python
from rest_framework.permissions import BasePermission
```

O DRF chama automaticamente o método:

```python
has_permission(self, request, view)
```

Se ele retornar:

* `True` → acesso liberado
* `False` → acesso negado

---

## ✨ Criando uma permission personalizada

Vamos criar uma permission que permita acesso apenas para **Supervisor ou Gerente**.

### Exemplo: `IsSupervisorOrGerente`

```python
from rest_framework import permissions

class IsSupervisorOrGerente(permissions.BasePermission):

    def has_permission(self, request, view):
        # 1️⃣ Verifica se o usuário está autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # 2️⃣ Gerente tem acesso total
        if request.user.is_staff:
            return True

        # 3️⃣ Verifica o tipo de usuário
        return request.user.role in [
            'SUPERVISOR',
            'GERENTE'
        ]
```

---

## 🔍 Entendendo a lógica passo a passo

### 1️⃣ Usuário autenticado

```python
if not request.user or not request.user.is_authenticated:
    return False
```

➡️ Garante que **usuários anônimos** não tenham acesso.

---

### 2️⃣ Gerente (`is_staff`)

```python
if request.user.is_staff:
    return True
```

➡️ Usuários com nível mais alto (Gerente) entram direto, sem mais verificações.

---

### 3️⃣ Supervisor

```python
return request.user.role in ['SUPERVISOR', 'GERENTE']
```

➡️ Libera acesso para Supervisores e Gerentes.

---

## 🛠️ Usando a permission na ViewSet

Agora vamos aplicar essa permission em uma API de produtos do estoque.

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsSupervisorOrGerente
    ]
```

Isso significa:

* O usuário precisa estar logado
* Precisa ser **Supervisor ou Gerente**

---

## 🔐 Exemplo prático de acesso

### Estoquista

❌ Não pode acessar esse endpoint

### Supervisor

✅ Pode acessar

### Gerente

✅ Pode acessar

---

## 💡 Separando permissões por responsabilidade

Nada impede que você tenha permissions diferentes:

* `IsEstoquista`
* `IsSupervisor`
* `IsGerente`

E use conforme o endpoint:

```python
permission_classes = [IsEstoquista]
```

Isso deixa o código:

* Mais legível
* Mais organizado
* Mais fácil de manter

---

## 🧠 Resumo mental rápido

Pense assim:

> “Antes de executar a ação, o DRF pergunta: esse usuário pode estar aqui?”

Se a permission responder **sim**, a request continua.
Se responder **não**, a API bloqueia.

---

## ✅ Conclusão

Permissions no Django Rest Framework são essenciais para:

* Garantir segurança
* Controlar acesso por perfil
* Evitar lógica de autorização espalhada pelo código
