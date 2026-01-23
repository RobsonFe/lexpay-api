# 1. Objetivo do Projeto
O projeto LexPay é uma API REST para gestão e negociação de precatórios (títulos judiciais) que conecta cedentes (titulares), brokers, advogados e administradores, permitindo cadastro do ativo, anexação de documentos, execução de due diligence e geração de propostas de antecipação com cálculo financeiro e trilha de histórico.

# 2. Entidades Principais (ERD Mental)
User -> relaciona-se com Address via OneToMany (endereços do usuário).
User -> relaciona-se com Precatorio como Cedente/Advogado/Broker via ForeignKey (três papéis distintos no ativo).
Tribunal -> relaciona-se com Precatorio via OneToMany (tribunal do processo).
EnteDevedor -> relaciona-se com Precatorio via OneToMany (ente público devedor).
Precatorio -> core do sistema; relaciona-se com Documento via OneToMany (documentos do ativo).
Precatorio -> relaciona-se com DueDiligence via OneToMany (diligências associadas).
DueDiligence -> relaciona-se com AnaliseDocumento via OneToMany (análises dos documentos da diligência).
Precatorio -> relaciona-se com Proposal via OneToMany (propostas de antecipação).
Proposal -> relaciona-se com ProposalHistory via OneToMany (histórico de mudanças).

# 3. Principais Funcionalidades (API Surface)
- Autenticação e Usuário: registro, login/logout via JWT, leitura/atualização/remoção do usuário autenticado.
- Endereços: CRUD de endereços vinculados ao usuário autenticado.
- Precatórios (Ofício): listagem com filtros/paginação/ordenação, criação, detalhamento, atualização parcial e exclusão.
- Due Diligence: criação/listagem/atualização de diligências, filtros por prioridade e listagem de diligências ativas.
- Análise de Documentos: listagem e atualização de análises vinculadas a diligências e documentos.
- Propostas: criação com cálculos financeiros, listagem por perfil, atualização, exclusão, aceite e ranking de oportunidades por score.

# 4. Pontos de Atenção Técnica (Code Review)
Segurança:
- JWT com `rest_framework_simplejwt` e `DEFAULT_PERMISSION_CLASSES = IsAuthenticated`, mais permissões customizadas por perfil de usuário.
- Signal em `auth` eleva automaticamente privilégios quando `type_user = Administrador`.
- Risco: `DEBUG = True`, `ALLOWED_HOSTS = ['*']` e `SECRET_KEY` em `settings.py` expostos para produção.

Performance:
- Uso de `select_related` e `prefetch_related` no `BasePrecatorioView` e em queries de Due Diligence.
- Paginação padrão ativada no DRF; filtros e busca em precatórios via `django-filter` e `SearchFilter`.
- Ponto de atenção: serializers aninhados e respostas densas (ex.: `AnaliseDocumentoSerializer` inclui `DueDiligence` e `Precatorio` detalhados) podem impactar payload e tempo de resposta.

Complexidade:
- Camada de Service (`ProposalService`) com transação e lock pessimista (`select_for_update`) para aceite de proposta e rejeição concorrente.
- Signals em `proposal` para auditoria (`ProposalHistory`) e cálculo de transição de status.
- Validações de regra de negócio centralizadas em serializers (ex.: precatório disponível e due diligence aprovada para criar propostas).
