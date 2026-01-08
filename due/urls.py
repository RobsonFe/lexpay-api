from django.urls import path
from .views import DueDiligenceListCreateView, DueDiligenceRetrieveUpdateView

urlpatterns = [
    path('diligencias/', DueDiligenceListCreateView.as_view(), name='diligence-list-create'),
    path('diligencias/<uuid:pk>/', DueDiligenceRetrieveUpdateView.as_view(), name='diligence-detail-update'),
]