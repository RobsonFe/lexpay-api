from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from due.permissions import (IsBrokerOrAdmin, IsAdminOrAdvogado, IsAdminBrokerOrAdvogado, IsAdmin, IsAdvogadoOrBrokerOrCedente)
from due.models import DueDiligence, TypeUserChoices, AnaliseDocumento
from due.serializer import DueDiligenceSerializer, DueDiligenceCreateSerializer, AnaliseDocumentoSerializer, AnaliseDocumentoUpdateSerializer
from auth.models import TypeUserChoices

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiRequest
)

@extend_schema_view(
    post=extend_schema(
        summary="Criar Due Diligence (Admin/Advogado)",
        description="Criação de diligências somente para Admin ou Advogado.",
        responses={
            201: DueDiligenceCreateSerializer,
            400: OpenApiResponse(description="Erro de validação nos campos enviados."),
            403: OpenApiResponse(description="Permissão negada para o usuário."),
        },
        tags=["Due Diligence"]
    ),
    get=extend_schema(
        summary="Listar todas as Diligências",
        description="Lista com todas de diligências.",
        responses={200: DueDiligenceCreateSerializer(many='True')},
        tags=["Due Diligence"]
    ),
)
class DueListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        return DueDiligence.objects.select_related('analista','precatorio').all()

@extend_schema(
    tags=["Due Diligence"],
    summary="Listar diligências ativas",
    description="Retorna a lista com todas as diligênicas com status diferente de rejeitado e aprovado",
    responses={
        200: OpenApiResponse(
            description="Lista de diligências ativas",
            response=DueDiligenceSerializer(many=True),
            examples=[
                OpenApiExample(
                    name="Lista de diligencias",
                    summary="apenas as ativas",
                    value=[
                        {
                            "id": "449661cb-50b4-40b1-90e1-fefc7a7320c1",
                            "status_analise": "PENDENTE",
                            "precatorio_detalhes": {
                                "numero_processo": "0002938-99.2025.8.26.0675",
                                "valor_principal": "190000.00",
                                "tribunal": {"nome": "TJSP", "sigla": "TJSP"}
                            },
                            "user_detalhes": {
                                "name": "Mario Advogado",
                                "email": "mario@lexpay.com.br"
                            }
                        },
                        {
                            "id": "a1743a3e-51d4-4482-a988-e003aca13e26",
                            "status_analise": "EM_ANALISE",
                            "precatorio_detalhes": {
                                "numero_processo": "111555-88.2024.8.26.0000",
                                "valor_principal": "50000.00",
                                "tribunal": {"nome": "TRF3", "sigla": "TRF3"}
                            },
                            "user_detalhes": {
                                "name": "Mario Advogado",
                                "email": "mario@lexpay.com.br"
                            }
                        }
                    ]
                )
            ]
        ),
        403: OpenApiResponse(description="Somente Admin ou Advogados podem realizar esta ação.")
    }
)
class DueListView(generics.ListAPIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = DueDiligenceSerializer
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        queryset = DueDiligence.objects.select_related('precatorio','analista').exclude(
            ~Q(status_analise__in = [
                    DueDiligence.StatusAnalise.APROVADO,
                    DueDiligence.StatusAnalise.REJEITADO
                ])
            )
        user = self.request.user
        if user.type_user == TypeUserChoices.ADVOGADO:
            return queryset.filter(analista=user)
        return queryset

@extend_schema(
    summary="Listar Diligências por prioridade ou todas que pertencem ao user logado",
    description="Lista as diligências do usuário logado, se for passado o parâmetro (ALTA, MEDIO, BAIXO) e feito um filtro nas diligências conforme a prioridade. Se não tiver vai retorna todas que pertencem ao user logado.",
    tags=["Due Diligence"],
    parameters=[
        OpenApiParameter(
            name='prioridade',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="A prioridade é opcional (ALTA, MEDIA, BAIXA)",
            enum=['alta', 'media', 'baixa']
        )
    ],
    responses={
        200: OpenApiResponse(
            description="lista criada com sucesso.",
            response=DueDiligenceSerializer(many=True),
            examples=[
                OpenApiExample(
                    name="Filtro (ALTA)",
                    summary="/due/listar/status/?prioridade=alta - o valor ´?prioridade´é passada na requsição",
                    value=[
                        {
                            "id": "4b6dc310-13fd-4da0-8924-75345b65a687",
                            "prioridade": "ALTA",
                            "status_analise": "EM_ANALISE",
                            "precatorio_detalhes": { "numero_processo": "0002938-99..." },
                            "analista": { "name": "Lucia" }
                        }
                    ]
                ),
                OpenApiExample(
                    name="Sem Filtro - retorna tudo que for seu",
                    summary="due/listar/status/ - Se não envia parâmetros vai retornar tudo que é seu",
                    value=[
                        {
                            "id": "4b6dc310...",
                            "prioridade": "ALTA",
                            "status_analise": "EM_ANALISE",
                            "analista": { "name": "Lucia" }
                        },
                        {
                            "id": "b2854b4f...",
                            "prioridade": "BAIXA",
                            "status_analise": "PENDENTE",
                            "analista": { "name": "Dr. Michelle" }
                        }
                    ]
                )
            ]
        ),
        401: OpenApiResponse(description="Não autenticado"),
        403: OpenApiResponse(description="Sem permissão."),
        404: OpenApiResponse(description="Nada encontrado.")
    }
)
class DueListPrioridadeView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DueDiligenceSerializer

    queryset = DueDiligence.objects.none()

    def get_queryset(self):
        user = self.request.user
        queryset = DueDiligence.objects.select_related('precatorio', 'analista').all()

        if user.type_user != TypeUserChoices.ADMINISTRADOR:
            filter_map = {
                TypeUserChoices.ADVOGADO: 'analista',
                TypeUserChoices.CEDENTE: 'precatorio__cedente',
                TypeUserChoices.BROKER: 'precatorio__broker'
            }

            campo_de_filtro = filter_map.get(user.type_user)

            if campo_de_filtro:
                queryset = queryset.filter(**{campo_de_filtro: user})
            else:
                return DueDiligence.objects.none()

        raw_prioridade = self.request.query_params.get('prioridade')

        if raw_prioridade:
            raw_prioridade = raw_prioridade.lower()

            mapa_prioridade = {
                'alta': DueDiligence.PrioridadeType.ALTA,
                'baixa': DueDiligence.PrioridadeType.BAIXA,
                'media': DueDiligence.PrioridadeType.MEDIA,
                'média': DueDiligence.PrioridadeType.MEDIA,
            }

            prioridade_db = mapa_prioridade.get(raw_prioridade)

            if prioridade_db:
                queryset = queryset.filter(prioridade=prioridade_db)
            else:
                return DueDiligence.objects.none()
        return queryset


class DueAprovadasViewSet(ModelViewSet):
    permission_classes = [IsAdvogadoOrBrokerOrCedente]
    serializer_class = DueDiligenceSerializer
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        return DueDiligence.objects.select_related(
            'analista','precatorio','precatorio__broker','precatorio__cedente'
        ).all()

    @extend_schema(
        summary="Listagem de Diligencias aprovadas",
        description="Lista as diligencias aprovadas com base no perfil, um advogado só consegue visualizar as diligencias que ele esta envolvido. Um broker e/ou cedente só visualizam com base nos precatórios que estão envolvidos, somente o Administrador vê tudo.",
        tags=['Due Diligence'],
        responses={
            200: OpenApiResponse(
                description="Listagem feita com sucesso.",
                response=DueDiligenceSerializer(many=True),
                examples=[
                    OpenApiExample(
                        name="Listagem de Due Paginada",
                        summary="Os dados que são devolvidos no Json retornam nesse padrão.",
                        value={
                            "count": 20,
                            "next": "http://127.0.0.1:8000/api/v1/due/aprovadas/listar-diligencias/?page=2",
                            "previous": None,
                            "results": [
                                {
                                    "id": "cb6ebea6-68d3-4733-9b09-6efd4c7fd570",
                                    "precatorio": "3ab28033-12f6-4ef1-9257-f88f09575521",
                                    "precatorio_detalhes": {
                                        "id": "3ab28033-12f6-4ef1-9257-f88f09575521",
                                        "numero_processo": "0002938-99.2025.8.26.0678",
                                        "natureza": "Alimentar",
                                        "valor_principal": "190000.00",
                                        "valor_venda": "100000.00",
                                        "tribunal": {
                                            "id": "38bc8e2f-...",
                                            "nome": "Tribunal Regional Federal da 5ª Região",
                                            "sigla": "TRF5",
                                            "uf": "PE"
                                        },
                                        "cedente": {
                                            "id": "f83e8737-...",
                                            "name": "Mario J",
                                            "email": "mario@lexpay.com",
                                            "type_user": "Cedente"
                                        },
                                        "documentos": [
                                            {
                                                "id": "76f1d019-...",
                                                "titulo": "mario docs",
                                                "arquivo": "http://.../docs/2026/01/EN_rjM3adL.pdf"
                                            }
                                        ]
                                    },
                                    "analista": "4f1fc912-3111-461e-8094-0aef157cdbe6",
                                    "status_analise": "APROVADO",
                                    "observacoes": "Atualização da due por nova rota 22/01/2026.",
                                    "created_at": "19-01-2026 08:55",
                                    "user_detalhes": {
                                        "name": "Mario adm",
                                        "email": "administrador@lexpay.com.br",
                                        "type_user": "Administrador"
                                    }
                                },
                                {
                                    "id": "449661cb-50b4-40b1-90e1-fefc7a7320c1",
                                    "precatorio_detalhes": {
                                        "numero_processo": "0002938-99.2025.8.26.0675",
                                        "tribunal": {"sigla": "TJSP", "uf": "SP"},
                                        "cedente": {"name": "Mario Cedente"}
                                    },
                                    "status_analise": "APROVADO",
                                    "observacoes": "Precatório liberado 12/01/2026"
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )

    @action(detail=False, methods=['get'], url_path="listar-diligencias")
    def listar_due_aprovadas(self, request):

        user = request.user
        status = DueDiligence.StatusAnalise.APROVADO
        """
            Acessando diretamente o get_queryset(), acessamos o nosso queryset personalizado que já busca os dados que vamos usar.
        """
        queryset = self.get_queryset().filter(status_analise=status)

        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            qs = queryset

        elif user.type_user == TypeUserChoices.ADVOGADO:
            qs = queryset.filter(analista=user)

        elif user.type_user == TypeUserChoices.BROKER:
            qs = queryset.filter(precatorio__broker=user)

        elif user.type_user == TypeUserChoices.CEDENTE:
            qs = queryset.filter(precatorio__cedente=user)
        else:
            qs = queryset.none()

        paginacao = self.paginate_queryset(queryset=qs)
        if paginacao is not None:
            serializer = self.get_serializer(paginacao, many=True)
            return self.get_paginated_response(data=serializer.data)

        serializer = self.get_serializer(qs, many=True)
        return Response({'results': serializer.data})


    @extend_schema(
        summary="Editar Diligencias com o PATCH",
        description="Atualização de campos de uma diligencia, advogados podem alteram suas próprias diligencias e o admin altera qualquer uma.",
        tags=['Due Diligence'],
        request=OpenApiRequest(
            request=DueDiligenceSerializer,
            examples=[
                OpenApiExample(
                    name="Exemplo de envio de dados na requisição",
                    summary="Atualizando os campos de observação e status de um diligencia",
                    description="Exemplo de envio para aprovar uma Due.",
                    value={
                        "observacoes": "Documentação foi verificada e aprovada com sucesso, podemos seguir com o processo.",
                        "status_analise": "APROVADO"
                    }
                )
            ]
        ),
        responses={
            200: OpenApiResponse(
                description="Diligência atualizada com sucesso.",
                response=DueDiligenceSerializer,
                examples=[
                    OpenApiExample(
                        name="Resposta de Sucesso",
                        value={
                            "id": "cb6ebea6-68d3-4733-9b09-6efd4c7fd570",
                            "status_analise": "APROVADO",
                            "observacoes": "Análise concluída. Documentação validada.",
                            "updated_at": "22-01-2026 14:30",
                            "analista": "4f1fc912-3111-461e-8094-0aef157cdbe6"
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description="Permissão negada (Não é o dono ou perfil inválido)."),
            404: OpenApiResponse(description="Due Diligence não encontrada.")
        }
    )
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        """
            O self.get_object() faz de forma implicita a busca do objeto, o método chamado faz a seguinta chamada:
            try:
                instance = DueDiligence.objects.get(id=pk)
            except DueDiligence.DoesNotExist:
                return Response(status=404)

            Usando o get_object() ele já faz isso e ainda retorna um 404 caso o objeto não exista e faz a checagem de permissões com check_object_permissions.

        """
        instance = self.get_object()

        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            pass
        elif user.type_user == TypeUserChoices.ADVOGADO:
            if instance.analista != user:
                return Response({"error":"Somente as Diligencias sobre sua responsabilidade podem ser editadas."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(
                {"error":"Você não tem permissão para edição."},
                status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

@extend_schema(
    summary="Edição de Diligencias - Admin",
    description="Somente usuários Admin podem realizer alterações nas diligencias.",
    tags=["Due Diligence"],
    responses={
        200: OpenApiResponse(
            response=DueDiligenceSerializer,
            description='Diligencia atualizada com sucesso'
            ),
        401: OpenApiResponse(
            description="Não autenticado"
        ),
        403: OpenApiResponse(
            description="Você não tem permissão para editar diligencias"
        ),
        404: OpenApiResponse(
            description="Diligencia não localizada na base."
        )
    }
)
class DueUpdateView(generics.UpdateAPIView):
    queryset = DueDiligence.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = DueDiligenceSerializer
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        try:
           response = super().update(request, *args, **kwargs)
           return Response(
               {
                "message": "Diligencia ataualizada com sucesso",
                "result": response.data
               }, status=status.HTTP_200_OK
           )
        except ValidationError as e:
            return Response(
                {
                "message": "Erro de validação",
                "erros": e.detail
                },status=status.HTTP_400_BAD_REQUEST
            )
        except NotFound:
            return Response(
                {
                "message":"Diligencia não localizada"
                },
                status=status.HTTP_404_NOT_FOUND
            )

@extend_schema_view(
    get=extend_schema(
        summary="Listar Diligências por usuário",
        description="Lista as diligências do usuário que solicita, caso o usuário seja Administrador, consegue ver tudo.",
        responses={200: DueDiligenceSerializer(many='True')},
        tags=["Due Diligence"]
    ),
    post=extend_schema(
        summary="Criar Diligência",
        description="Cria uma diligência e popula ao usuário logado (campo 'analista').",
        responses={
            201: DueDiligenceSerializer,
            400: OpenApiResponse(description="Dados inválidos."),
            403: OpenApiResponse(description="Permissão negada."),
        },
        tags=["Due Diligence"]
    ),
)
class DueDiligenceListCreateView(generics.ListCreateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsBrokerOrAdmin]
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            return DueDiligence.objects.all()
        return DueDiligence.objects.filter(analista=user)

    def perform_create(self, serializer):
        serializer.save(analista=self.request.user)

@extend_schema_view(
    get=extend_schema(
        summary="Detalhar Diligência",
        description="Retorna uma diligência específica.",
        tags=["Due Diligence"]
    ),
    patch=extend_schema(
        summary="Atualizar Diligência-PATCH",
        description="Atualiza parcialmente campos.",
        tags=["Due Diligence"]
    )
)
class DueDiligenceRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsAdminBrokerOrAdvogado]
    queryset = DueDiligence.objects.all()

    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        queryset = DueDiligence.objects.select_related(
            'precatorio', 'analista', 'precatorio__tribunal', 'precatorio__ente_devedor'
        )

        is_admin = user.is_staff or (user.type_user == TypeUserChoices.ADMINISTRADOR)

        if is_admin:
            return queryset.all()
        return queryset.filter(analista=user)

@extend_schema(
    summary="Criar Diligencias Admin/Adv",
    description="Criaçao de diligencias somente para  - Admin/Adv",
    tags=["Due Diligence"],
    request=DueDiligenceCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Diligencia criada com sucesso",
            response=DueDiligenceCreateSerializer,
            examples=[
                OpenApiExample(
                name="Criado com sucesso",
                summary="Requisição foi criada com sucesso.",
                value={
                    "id": "1d54a382-f053-40c3-a481-75c4bb743728",
                    "precatorio": "550e8400-e29b-41d4-a716-446655440000",
                    "prioridade": "ALTA",
                    "analista": "4f1fc912-3111-461e-8094-0aef157cdbe6",
                    "observacoes": "Observação referente a due.",
                    "status_analise": "PENDENTE",
                    "created_at": "2026-01-14"
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    name="Erro de validação",
                    summary="Precátorio já esta em análise",
                    value={
                        "precatorio":["Esse precatório já esta em diligencia."]
                    }
                )
            ]
        ),
    }
)
class DueCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            """Invoca o metôdo pai de CreateAPIView e encaminha o resquest para que seja feita a mentagem o Response"""
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "message": "Due Diligence criada com sucesso",
                    "result": response.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {
                    "message": "Erro de validação",
                    "errors": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except IntegrityError:
            return Response(
                {
                    "message": "Erro ao criar due diligence",
                    "errors": {
                        "precatorio": ["Já existe uma Due Diligence ativa para este precatório."]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        user = self.request.user
        try:
            serializer.save(analista=user)
        except IntegrityError:
            raise ValidationError({'error':'Diligencia já cadastrada no sistema'})

@extend_schema(
    summary="Listar Analises de Documentos",
    description="Lista analises por responsável, somente para Advogados e Brokers.",
    tags=["Due Diligence"],
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description="ID da analise do documento",
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Lista de analise de documentos.",
            response=AnaliseDocumentoSerializer(many=True),
            examples=[
                OpenApiExample(
                    name="Minhas Analises",
                    summary="Lista de analises de documentos do usuário logado",
                    value=[
                        {
			"id": "445eea4b-0cd7-4b29-a765-850d5a0f91d3",
			"status": "PENDENTE",
			"observacoes_analise": 'null',
			"data_analise": 'null',
			"documento": "c6003d02-bf64-477a-b459-0b41f207ac76",
			"due_diligence": "96c42a6b-292d-4e1e-9ac8-3fad68c48817",
			"analisado_por": 'null',
			"due_diligence_detalhes": {
				"id": "96c42a6b-292d-4e1e-9ac8-3fad68c48817",
				"precatorio": "1889cc4c-40f9-43e5-ba87-7e3a5948c962",
				"precatorio_detalhes": {
					"id": "1889cc4c-40f9-43e5-ba87-7e3a5948c962",
					"numero_processo": "0002938-99.2025.8.26.0542",
					"natureza": "Alimentar",
					"natureza_display": "Alimentar",
					"valor_principal": "100000.00",
					"valor_venda": "80000.00",
					"percentual_honorarios": "10.00",
					"data_expedicao": "01-02-2024",
					"ano_orcamentario": 2025,
					"status": "Disponível",
					"status_display": "Disponível",
					"descricao": "Precatório alimentar PE",
					"tribunal": {
						"id": "3fe3cdce-b0f0-404b-af24-cd2f7a1e55b9",
						"nome": "Tribunal de Justiça de São Paulo",
						"sigla": "TJSP",
						"uf": "SP"
					},
					"ente_devedor": {
						"id": "398af7c2-0d66-4a2f-a215-09640807e6ed",
						"nome": "Fazenda do Estado de São Paulo",
						"cnpj": "46.379.400/0001-50",
						"esfera": "Estadual"
					},
					"cedente": {
						"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
						"name": "Ana Broker",
						"email": "analista@lexpay.com.br",
						"type_user": "Broker",
						"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
					},
					"advogado": 'null',
					"documentos": [
						{
							"id": "c6003d02-bf64-477a-b459-0b41f207ac76",
							"precatorio": "1889cc4c-40f9-43e5-ba87-7e3a5948c962",
							"titulo": "teste insomnia31",
							"arquivo": "http://127.0.0.1:8000/media/precatorios/docs/2026/01/EN_1eifO2I.pdf",
							"enviado_em": "07-01-2026 14:44",
							"extension": ".pdf",
							"size_mb": 0.2
						}
					],
					"created_at": "07-01-2026 14:44",
					"updated_at": "07-01-2026 14:47"
				},
				"analista": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
				"status_analise": "APROVADO",
				"data_inicio_analise": 'null',
				"data_conclusao_analise": "07-01-2026 14:47",
				"observacoes": "Precatório liberado",
				"documento_aprovado": 'true',
				"motivo_repactuacao": 'null',
				"created_at": "07-01-2026 14:45",
				"updated_at": "07-01-2026 14:47",
				"user_detalhes": {
					"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
					"name": "Ana Broker",
					"email": "analista@lexpay.com.br",
					"type_user": "Broker",
					"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
				}
			},
			"precatorio_detalhes": {
				"id": "1889cc4c-40f9-43e5-ba87-7e3a5948c962",
				"numero_processo": "0002938-99.2025.8.26.0542",
				"natureza": "Alimentar",
				"natureza_display": "Alimentar",
				"valor_principal": "100000.00",
				"valor_venda": "80000.00",
				"percentual_honorarios": "10.00",
				"data_expedicao": "01-02-2024",
				"ano_orcamentario": 2025,
				"status": "Disponível",
				"status_display": "Disponível",
				"descricao": "Precatório alimentar PE",
				"tribunal": {
					"id": "3fe3cdce-b0f0-404b-af24-cd2f7a1e55b9",
					"nome": "Tribunal de Justiça de São Paulo",
					"sigla": "TJSP",
					"uf": "SP"
				},
				"ente_devedor": {
					"id": "398af7c2-0d66-4a2f-a215-09640807e6ed",
					"nome": "Fazenda do Estado de São Paulo",
					"cnpj": "46.379.400/0001-50",
					"esfera": "Estadual"
				},
				"cedente": {
					"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
					"name": "Ana Broker",
					"email": "analista@lexpay.com.br",
					"type_user": "Broker",
					"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
				},
				"advogado": 'null',
				"documentos": [
					{
						"id": "c6003d02-bf64-477a-b459-0b41f207ac76",
						"precatorio": "1889cc4c-40f9-43e5-ba87-7e3a5948c962",
						"titulo": "teste insomnia31",
						"arquivo": "http://127.0.0.1:8000/media/precatorios/docs/2026/01/EN_1eifO2I.pdf",
						"enviado_em": "07-01-2026 14:44",
						"extension": ".pdf",
						"size_mb": 0.2
					}
				],
				"created_at": "07-01-2026 14:44",
				"updated_at": "07-01-2026 14:47"
			},
			"detalhes_usuario": 'null'
		},
		{
			"id": "41087950-7e2d-4da3-a6de-89c3a147ac42",
			"status": "PENDENTE",
			"observacoes_analise": 'null',
			"data_analise": 'null',
			"documento": "64331e52-1916-4799-b3b4-1170524603a5",
			"due_diligence": "9b0af39d-b559-4071-8354-8f39d612b46d",
			"analisado_por": 'null',
			"due_diligence_detalhes": {
				"id": "9b0af39d-b559-4071-8354-8f39d612b46d",
				"precatorio": "c68b9240-a7f1-4b99-9400-84a0bc11a2d0",
				"precatorio_detalhes": {
					"id": "c68b9240-a7f1-4b99-9400-84a0bc11a2d0",
					"numero_processo": "0002938-99.2025.8.26.0550",
					"natureza": "Alimentar",
					"natureza_display": "Alimentar",
					"valor_principal": "100000.00",
					"valor_venda": "80000.00",
					"percentual_honorarios": "10.00",
					"data_expedicao": "01-02-2024",
					"ano_orcamentario": 2025,
					"status": "Disponível",
					"status_display": "Disponível",
					"descricao": "Precatório alimentar PE",
					"tribunal": {
						"id": "3fe3cdce-b0f0-404b-af24-cd2f7a1e55b9",
						"nome": "Tribunal de Justiça de São Paulo",
						"sigla": "TJSP",
						"uf": "SP"
					},
					"ente_devedor": {
						"id": "398af7c2-0d66-4a2f-a215-09640807e6ed",
						"nome": "Fazenda do Estado de São Paulo",
						"cnpj": "46.379.400/0001-50",
						"esfera": "Estadual"
					},
					"cedente": {
						"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
						"name": "Ana Broker",
						"email": "analista@lexpay.com.br",
						"type_user": "Broker",
						"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
					},
					"advogado": 'null',
					"documentos": [
						{
							"id": "64331e52-1916-4799-b3b4-1170524603a5",
							"precatorio": "c68b9240-a7f1-4b99-9400-84a0bc11a2d0",
							"titulo": "teste erro",
							"arquivo": "http://127.0.0.1:8000/media/precatorios/docs/2026/01/EN_sAGXuqE.pdf",
							"enviado_em": "07-01-2026 15:17",
							"extension": ".pdf",
							"size_mb": 0.2
						}
					],
					"created_at": "07-01-2026 15:14",
					"updated_at": "07-01-2026 15:18"
				},
				"analista": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
				"status_analise": "APROVADO",
				"data_inicio_analise": 'null',
				"data_conclusao_analise": "07-01-2026 15:18",
				"observacoes": "Precatório liberado",
				"documento_aprovado": 'true',
				"motivo_repactuacao": 'null',
				"created_at": "07-01-2026 15:17",
				"updated_at": "07-01-2026 15:36",
				"user_detalhes": {
					"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
					"name": "Ana Broker",
					"email": "analista@lexpay.com.br",
					"type_user": "Broker",
					"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
				}
			},
			"precatorio_detalhes": {
				"id": "c68b9240-a7f1-4b99-9400-84a0bc11a2d0",
				"numero_processo": "0002938-99.2025.8.26.0550",
				"natureza": "Alimentar",
				"natureza_display": "Alimentar",
				"valor_principal": "100000.00",
				"valor_venda": "80000.00",
				"percentual_honorarios": "10.00",
				"data_expedicao": "01-02-2024",
				"ano_orcamentario": 2025,
				"status": "Disponível",
				"status_display": "Disponível",
				"descricao": "Precatório alimentar PE",
				"tribunal": {
					"id": "3fe3cdce-b0f0-404b-af24-cd2f7a1e55b9",
					"nome": "Tribunal de Justiça de São Paulo",
					"sigla": "TJSP",
					"uf": "SP"
				},
				"ente_devedor": {
					"id": "398af7c2-0d66-4a2f-a215-09640807e6ed",
					"nome": "Fazenda do Estado de São Paulo",
					"cnpj": "46.379.400/0001-50",
					"esfera": "Estadual"
				},
				"cedente": {
					"id": "c951fd85-8a05-478b-99a1-2b465ad25d4e",
					"name": "Ana Broker",
					"email": "analista@lexpay.com.br",
					"type_user": "Broker",
					"avatar": "http://127.0.0.1:8000/media/avatars/default.png"
				},
				"advogado": 'null',
				"documentos": [
					{
						"id": "64331e52-1916-4799-b3b4-1170524603a5",
						"precatorio": "c68b9240-a7f1-4b99-9400-84a0bc11a2d0",
						"titulo": "teste erro",
						"arquivo": "http://127.0.0.1:8000/media/precatorios/docs/2026/01/EN_sAGXuqE.pdf",
						"enviado_em": "07-01-2026 15:17",
						"extension": ".pdf",
						"size_mb": 0.2
					}
				],
				"created_at": "07-01-2026 15:14",
				"updated_at": "07-01-2026 15:18"
			},
			"detalhes_usuario": 'null'
		}
                    ]
                )
            ]
        ),
        403: OpenApiResponse(description="Acesso não autorizado"),
        404: OpenApiResponse(description="Documento não localizada")
    }
)
class AnaliseDocumentoListView(APIView):
    permission_classes = [IsAdminBrokerOrAdvogado]

    def get(self, request):
        user = request.user
        queryset = AnaliseDocumento.objects.select_related('due_diligence', 'due_diligence__precatorio', 'documento', 'analisado_por', )

        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            queryset
        if user.type_user == TypeUserChoices.ADVOGADO or user.type_user == TypeUserChoices.BROKER:
            queryset.filter(analisado_por=user)

        serializer = AnaliseDocumentoSerializer(queryset, many=True)
        return Response({
            'results':serializer.data
        },status=status.HTTP_200_OK)

@extend_schema(
    summary="Ataualização de analise de documentos.",
    description="Atualizar os dados da analise de documento, podendo atualizar os dados de forma geral ou parcial.",
    tags=["Due Diligence"],
    request=OpenApiRequest(
        request=AnaliseDocumentoUpdateSerializer,
        examples=[
            OpenApiExample(
                name="Envio da payload",
                summary="Campos que serão enviados",
                description="Dados que serão enviados par atualizar a analise",
                value={
                    "status": "APROVADO",
                    "observacoes_analise": "Documento aprovado na diligencia.",
                    "motivo_repactuacao": ""
                }
            )
        ]
    ),
    responses={
        200: OpenApiResponse(
            description="Sucesso na requisição.",
            response=AnaliseDocumentoSerializer,
            examples=[
                OpenApiExample(
                    name="Sucesso na execução da requisição",
                    summary="Retorno da execução",
                    value={
                        "result": {
                                "id": "445eea4b-0cd7-4b29-a765-850d5a0f91d3",
                        "due_diligence": "96c42a6b-292d-4e1e-9ac8-3fad68c48817",
                        "documento": "c6003d02-bf64-477a-b459-0b41f207ac76",
                        "status": "APROVADO",
                        "observacoes_analise": "Documento aprovado na diligencia.",
                        "data_analise": "19-01-2026 15:33",
                        "analisado_por": "4f1fc912-3111-461e-8094-0aef157cdbe6",
                            "detalhes_usuario": {
                                "id": "4f1fc912-3111-461e-8094-0aef157cdbe6",
                                "name": "Mario adm",
                                "email": "email@lexpay.com.br",
                                "type_user": "user_default",
                                "avatar": "http://127.0.0.1:8000/media/avatars/default.png"
                            }
                        }
                    }
                )
            ]
        ),
        400:OpenApiResponse("Verifique os campos e tente novamente."),
        403:OpenApiResponse(description="Somento o dono desse ativo pode realizar edições.")
    }

)
class AnaliseDocumentoUpdateView(APIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = AnaliseDocumentoUpdateSerializer
    http_method_names = ['patch']

    def patch(self, request, pk):
        user = request.user
        queryset = get_object_or_404(
            AnaliseDocumento.objects.select_related('due_diligence__precatorio__advogado'),
            pk=pk
        )

        if user.type_user == TypeUserChoices.ADVOGADO:
            advogado_oficio = queryset.due_diligence.precatorio.advogado
            if advogado_oficio != user:
                return Response({
                    "error":'Somente o dono pode alterar.'
                },status=status.HTTP_403_FORBIDDEN)

        serializer = AnaliseDocumentoSerializer(instance=queryset, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'result':serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
