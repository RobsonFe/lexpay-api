# App Proposal (Propostas)

## Descrição:

Esse app será responsável pelo gerenciamento de propostas de compra de precatórios. Ele irá calcular propostas baseadas em taxas, juros, descontos e outros fatores financeiros. O sistema permitirá que brokers e investidores criem propostas para precatórios disponíveis, calculem valores líquidos considerando taxas e juros, e listem os precatórios mais atrativos para compra baseado em critérios de rentabilidade.

### Estrutura da model

**Proposal**
- id (UUID, primary key)
- precatorio (relacionamento ForeignKey com Precatorio)
- proponente (relacionamento ForeignKey com User - tipo Broker)
- valor_proposto (DecimalField, max_digits=18, decimal_places=2)
- taxa_desconto (DecimalField, max_digits=5, decimal_places=2)
- taxa_juros_anual (DecimalField, max_digits=5, decimal_places=2)
- prazo_pagamento_meses (IntegerField)
- valor_liquido_cedente (DecimalField, max_digits=18, decimal_places=2, calculado)
- valor_liquido_proponente (DecimalField, max_digits=18, decimal_places=2, calculado)
- margem_lucro_percentual (DecimalField, max_digits=5, decimal_places=2, calculado)
- status (choices: Rascunho, Enviada, Aceita, Rejeitada, Expirada)
- data_vencimento (DateField)
- observacoes (TextField, null/blank)
- created_at (DateTimeField, auto_now_add)
- updated_at (DateTimeField, auto_now)

**ProposalHistory**
- id (UUID, primary key)
- proposal (relacionamento ForeignKey com Proposal, CASCADE)
- status_anterior (CharField)
- status_novo (CharField)
- valor_anterior (DecimalField, null/blank)
- valor_novo (DecimalField, null/blank)
- alterado_por (relacionamento ForeignKey com User)
- motivo_alteracao (TextField, null/blank)
- created_at (DateTimeField, auto_now_add)

### Regras de Negócio

**Criação de Proposta:**
- Apenas usuários tipo Broker podem criar propostas
- Só pode criar proposta para precatórios com status "Disponível"
- Precatório deve ter Due Diligence aprovada (verificar relacionamento)
- Valor proposto não pode ser maior que valor_principal do precatório
- Taxa de desconto deve estar entre 0% e 100%
- Taxa de juros anual deve estar entre 0% e 50%
- Prazo de pagamento deve estar entre 1 e 120 meses
- Status inicial é sempre "Rascunho"
- Data de vencimento deve ser futura (pelo menos 30 dias a partir da criação)

**Cálculos de Proposta:**
- Valor líquido cedente = valor_proposto - (valor_proposto * taxa_desconto / 100) - honorários
- Honorários = valor_proposto * (percentual_honorarios do precatório / 100)
- Valor líquido proponente = valor_principal - valor_proposto - (valor_proposto * taxa_juros_anual / 100 * prazo_pagamento_meses / 12)
- Margem de lucro = ((valor_principal - valor_proposto) / valor_proposto) * 100
- Se prazo_pagamento_meses > 0, aplicar juros compostos: valor_final = valor_proposto * (1 + taxa_juros_anual/100) ^ (prazo_pagamento_meses/12)

**Status da Proposta:**
- Rascunho: proposta ainda não enviada, pode ser editada
- Enviada: proposta enviada ao cedente, aguardando resposta
- Aceita: cedente aceitou a proposta, precatório muda status para "Em Negociação"
- Rejeitada: cedente rejeitou a proposta
- Expirada: data_vencimento passou e status ainda é "Enviada"

**Listagem de Precatórios Mais Atrativos:**
- Ordenar por margem de lucro (maior para menor)
- Filtrar apenas precatórios com status "Disponível"
- Considerar taxa de desconto (menor é melhor)
- Considerar prazo de pagamento (menor é melhor)
- Considerar valor principal (maior pode ser mais atrativo)
- Score de atratividade = (margem_lucro * 0.4) + ((100 - taxa_desconto) * 0.3) + ((120 - prazo_pagamento_meses) * 0.2) + (valor_principal_normalizado * 0.1)

**Validações:**
- Não pode criar proposta para precatório que já tem proposta aceita
- Não pode editar proposta com status diferente de "Rascunho"
- Não pode enviar proposta sem preencher todos os campos obrigatórios
- Valor proposto deve ser positivo
- Taxa de desconto + taxa de juros não pode ultrapassar 100%
- Ao aceitar proposta, todas as outras propostas do mesmo precatório devem ser rejeitadas automaticamente
- Ao aceitar proposta, status do precatório muda para "Em Negociação"

**Histórico de Proposta:**
- Criar registro em ProposalHistory sempre que status mudar
- Criar registro quando valor_proposto for alterado
- Registrar quem fez a alteração e motivo (se houver)
- Histórico não pode ser editado ou deletado

**Relacionamentos:**
- Proposal pertence a um Precatorio (PROTECT)
- Proposal pertence a um User (proponente - PROTECT)
- ProposalHistory pertence a uma Proposal (CASCADE)
- ProposalHistory referencia User que fez alteração (PROTECT)
