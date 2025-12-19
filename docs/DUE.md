# App Due (Due Diligence)

## Descrição:

Esse app será responsável pelo processo de Due Diligence (diligência prévia) dos precatórios. Ele irá gerenciar a análise, aprovação e repactuação de documentos relacionados aos precatórios. O sistema permitirá que administradores e analistas avaliem a documentação, aprovem ou solicitem ajustes nos documentos, e gerenciem o fluxo administrativo de análise dos ofícios requisitórios.

### Estrutura da model

**DueDiligence**
- id (UUID, primary key)
- precatorio (relacionamento ForeignKey com Precatorio)
- analista (relacionamento ForeignKey com User - tipo Administrador ou Broker)
- status_analise (choices: Pendente, Em Análise, Aprovado, Repactuado, Rejeitado)
- data_inicio_analise (DateTimeField)
- data_conclusao_analise (DateTimeField, null/blank)
- observacoes (TextField, null/blank)
- documento_aprovado (BooleanField, default=False)
- motivo_repactuacao (TextField, null/blank)
- created_at (DateTimeField, auto_now_add)
- updated_at (DateTimeField, auto_now)

**AnaliseDocumento**
- id (UUID, primary key)
- due_diligence (relacionamento ForeignKey com DueDiligence, CASCADE)
- documento (relacionamento ForeignKey com Documento do app oficio)
- status (choices: Pendente, Aprovado, Repactuado, Rejeitado)
- observacoes_analise (TextField, null/blank)
- data_analise (DateTimeField, null/blank)
- analisado_por (relacionamento ForeignKey com User)
- created_at (DateTimeField, auto_now_add)
- updated_at (DateTimeField, auto_now)

### Regras de Negócio

**Due Diligence:**
- Um precatório pode ter apenas uma Due Diligence ativa por vez
- Apenas usuários do tipo Administrador ou Broker podem criar/analisar Due Diligence
- Quando uma Due Diligence é criada, o status inicial é "Pendente"
- Ao iniciar a análise, o status muda para "Em Análise" e data_inicio_analise é preenchida
- Para aprovar: todos os documentos devem estar aprovados e documento_aprovado = True
- Para repactuar: deve preencher motivo_repactuacao e status = "Repactuado"
- Quando repactuado, o status do precatório relacionado deve voltar para "Em Análise"
- Data de conclusão só é preenchida quando status for Aprovado ou Rejeitado
- Um precatório só pode ter status "Disponível" se tiver Due Diligence aprovada

**Análise de Documento:**
- Cada documento do precatório pode ter uma análise associada
- Ao criar análise de documento, status inicial é "Pendente"
- Apenas o analista responsável pela Due Diligence pode analisar os documentos
- Para aprovar documento: status = "Aprovado" e data_analise é preenchida
- Para repactuar documento: status = "Repactuado", deve preencher observacoes_analise
- Documento repactuado deve ter observações explicando o que precisa ser ajustado
- Quando um documento é repactuado, a Due Diligence volta para status "Em Análise"
- Todos os documentos devem estar aprovados para a Due Diligence ser aprovada

**Validações:**
- Não pode criar nova Due Diligence se já existir uma ativa (status diferente de Rejeitado)
- Não pode aprovar Due Diligence se houver documentos pendentes ou repactuados
- Não pode concluir análise sem preencher observações se status for Repactuado ou Rejeitado
- Data de conclusão não pode ser anterior à data de início

**Relacionamentos:**
- DueDiligence pertence a um Precatorio (PROTECT - não pode deletar precatório com due ativa)
- AnaliseDocumento pertence a uma DueDiligence (CASCADE - deleta análises se deletar due)
- AnaliseDocumento referencia um Documento do app oficio (PROTECT)
