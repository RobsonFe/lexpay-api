from django.urls import path
from .views import (
    DueDiligenceListCreateView, 
    DueDiligenceRetrieveUpdateView, 
    DueCreateView, 
    DueUpdateView, 
    DueListView, 
    DueListPrioridadeView,
    AnaliseDocumentoUpdateView,
    AnaliseDocumentoListView
    )

urlpatterns = [
    path('diligencias/', DueDiligenceListCreateView.as_view(), name='diligence-list-create'),
    path('diligencias/<uuid:pk>/', DueDiligenceRetrieveUpdateView.as_view(), name='diligence-detail-update'),
    path('criar/', DueCreateView.as_view(), name='due-create'),
    path('atualizar/<uuid:pk>/', DueUpdateView.as_view(), name='due-update'),
    path('listar/ativas/', DueListView.as_view(), name='due-list-active'),
    path('listar/status/', DueListPrioridadeView.as_view(), name='due-list-prioridade'),
    path('listar/documentos/', AnaliseDocumentoListView.as_view(), name='documento-list'),
    path('atualizar/documentos/<uuid:pk>/', AnaliseDocumentoUpdateView.as_view(), name='analise-documento-update'),
]