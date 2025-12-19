from django.urls import path
from .views import (
    PrecatorioListView,
    PrecatorioCreateView,
    PrecatorioRetrieveView,
    PrecatorioUpdateView,
    PrecatorioDeleteView
)

urlpatterns = [
    path('precatorios/listar/', PrecatorioListView.as_view(), name='precatorio-list'),
    path('precatorios/criar/', PrecatorioCreateView.as_view(), name='precatorio-create'),
    path('precatorios/detalhes/<uuid:pk>', PrecatorioRetrieveView.as_view(), name='precatorio-detail'),
    path('precatorios/atualizar/<uuid:pk>', PrecatorioUpdateView.as_view(), name='precatorio-update'),
    path('precatorios/deletar/<uuid:pk>', PrecatorioDeleteView.as_view(), name='precatorio-delete'),
]