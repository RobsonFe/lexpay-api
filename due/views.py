from rest_framework import generics
from due.permissions import IsBrokerOrAdmin 
from due.models import DueDiligence, TypeUserChoices
from due.serializer import DueDiligenceSerializer

class DueDiligenceListCreateView(generics.ListCreateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsBrokerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            return DueDiligence.objects.all()
        return DueDiligence.objects.filter(analista=user)
    
    def perform_create(self, serializer):
        serializer.save(analista=self.request.user)


class DueDiligenceRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsBrokerOrAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        queryset = DueDiligence.objects.select_related('precatorio', 'analista', 'precatorio__tribunal','precatorio__ente_devedor')
        if user.is_staff or user.type_user == 'Administrador':
            return queryset.all()
        return queryset.filter(analista=user)