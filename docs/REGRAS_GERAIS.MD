# Projeto LexPay

## Descrição:

Esse projeto tem como objetivo aproximar o desenvolvedor do sistema Celer com cálculos de Precatórios e documentos judiciais. 

### Entrega:

Previsão de Entrega: até o dia 10/01/26
Revisor: Robson Ferreira da Silva

### Regras: 

Seguir o `GitFlow` para desenvolvimento. 

1 - Baixar o projeto na sua máquina 
2 - Leia o `README.md` e as instruções de desenvolvimento. 
3 - Antes de começar a desenvolver, deve abrir uma nova branch a partir da `develop` e colocar as iniciais do seu nome.

**Exemplo:**

```git
rf-feat-new-implementation
```

`fr`- Robson Ferreira
`feat` - flow do gitflow (Feature)- Leia sobre gitflow
`new-implementation` - nome da implementação que será feita. 

**IMPORTANTE**

NUNCA mergear direto na main, SEMPRE abrir `Pull Request`para a branch de `develop`

### **Observações:** 

- É necessário criar o hábito de atualizar a branch diariamente. 

Processo: 

```git
git fetch
```
--- 
```git
git pull origin develop
```

Se houver conflitos, resolver, mas caso cada um esteja desenvolvendo no seu próprio arquivo ou app, dificilmente terá conflitos. 

### Regras Gerais de Software

- Não gerar comentários inline, sempre em docstring
- Toda a implementação deve está alinhada com as convenções do Python e Django
- Seguir sempre as boas práticas de programação.
- Evitar códigos verbosos e difícil de entender.
- Evitar erros de N+1
- Todo Endpoint precisa de documentação com o `drf spectacular`
- Todo Endpoint precisa de validações e o usuário deve estar autenticado.



### Como Fica cada App ?

**Marinaldo** : `Due`
**Everton** : `Proposal`

Ao final do projeto, irei avaliar os PR's, sugerir correções e unir os dois apps.