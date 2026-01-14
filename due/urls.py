from django.urls import path
from .views import (
    DueDiligenceListCreateView, 
    DueDiligenceRetrieveUpdateView, 
    DueCreateView
    )

urlpatterns = [
    path('diligencias/', DueDiligenceListCreateView.as_view(), name='diligence-list-create'),
    path('diligencias/<uuid:pk>/', DueDiligenceRetrieveUpdateView.as_view(), name='diligence-detail-update'),

    path('criar/', DueCreateView.as_view(), name='due-create'),

]