# Uso de `url_path` no Django Rest Framework (DRF)

Esta documentação tem como objetivo explicar **de forma simples e prática** como funciona o uso de **URL Path (`url_path`)** no Django Rest Framework, utilizando como exemplo uma **API de Produtos**.

O foco aqui **não é ser excessivamente técnico**, mas sim **facilitar o entendimento** para desenvolvedores que estão começando ou que ainda têm dúvidas sobre como criar URLs personalizadas em uma API REST.

---

## 📌 O que é `url_path`?

No Django Rest Framework, quando usamos **ViewSets**, o DRF cria automaticamente algumas rotas padrão, como:

* Listar produtos
* Criar produto
* Buscar produto por ID
* Atualizar produto
* Deletar produto

Porém, em muitos cenários reais, precisamos criar **ações personalizadas**, como:

* Download de um arquivo
* Ativar ou desativar um produto
* Ver detalhes extras de um produto

É exatamente nesse momento que usamos o **`@action` junto com o `url_path`**.

---

## 🛍️ Cenário do exemplo: API de Produtos

Imagine que temos uma API de produtos e queremos criar uma rota específica para **baixar a ficha técnica de um produto**.

Algo como:

```
GET /api/produtos/10/ficha-tecnica/download/
```

Essa rota:

* Está relacionada a **um produto específico**
* Não é uma operação padrão de CRUD
* Executa uma ação personalizada

---

## 🧩 Estrutura básica do ViewSet

Vamos supor que já temos um `ProductViewSet`:

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer
```

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

Até aqui, o DRF já cria automaticamente rotas como:

* `GET /api/produtos/`
* `GET /api/produtos/{id}/`

---

## ✨ Criando uma rota personalizada com `url_path`

Agora vamos criar a funcionalidade de **download da ficha técnica do produto**.

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(
        detail=True,
        methods=["get"],
        url_path="ficha-tecnica/download"
    )
    def download_ficha_tecnica(self, request, pk=None):
        return Response({
            "message": f"Download da ficha técnica do produto {pk}"
        })
```

---

## 🔍 Entendendo cada parte (sem complicação)

### `@action`

Indica que estamos criando uma **ação personalizada** dentro do ViewSet.

---

### `detail=True`

Significa que essa rota está relacionada a **um item específico**.

✔️ O ID do produto será obrigatório na URL.

Exemplo:

```
/api/produtos/10/ficha-tecnica/download/
```

Se fosse `detail=False`, a rota não teria ID.

---

### `methods=["get"]`

Define quais métodos HTTP essa rota aceita.

Neste caso:

* Apenas **GET**

---

### `url_path="ficha-tecnica/download"`

Aqui está o ponto mais importante.

O `url_path` define **como a URL será montada depois do ID do produto**.

Ou seja:

```
/produtos/{id}/ficha-tecnica/download/
```

👉 Você pode usar barras (`/`) dentro do `url_path` para deixar a URL mais organizada e semântica.

---

### `pk=None`

O `pk` representa o **ID do produto** que veio pela URL.

No exemplo:

```
/produtos/10/ficha-tecnica/download/
```

O valor de `pk` será `10`.

---

## 🗺️ Como essa rota fica no projeto?

Supondo que você registrou o ViewSet no router:

```python
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r"produtos", ProductViewSet)
```

A rota final será:

```
GET /produtos/{id}/ficha-tecnica/download/
```

Exemplo real:

```
GET /produtos/5/ficha-tecnica/download/
```

---

## 💡 Quando usar `url_path`?

Use `url_path` quando:

* A ação **não é um CRUD padrão**
* Você quer uma URL mais clara e descritiva
* Precisa de ações específicas, como:

  * Download
  * Ativar / Desativar
  * Visualizar detalhes extras

---

## 🧠 Resumo mental rápido

Pense assim:

> "Eu já tenho meus produtos, agora quero criar uma ação especial para um produto específico. Essa ação precisa de um nome claro na URL. Para isso, uso `@action` com `url_path`."

---

## ✅ Conclusão

O `url_path` no Django Rest Framework permite criar **rotas personalizadas**, legíveis e organizadas, sem complicar a estrutura da API.

Em APIs reais, como uma **API de Produtos**, isso ajuda muito a deixar as URLs:

* Mais intuitivas
* Mais fáceis de manter
* Mais claras para quem consome a API

Se quiser, posso gerar:

* Diagramas de URL
* Exemplos com `detail=False`
* Comparação entre rotas padrão e personalizadas
