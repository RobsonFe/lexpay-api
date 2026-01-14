from rest_framework import permissions
from auth.models import TypeUserChoices 

class IsBrokerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        return request.user.type_user in [
            TypeUserChoices.BROKER, 
            TypeUserChoices.ADMINISTRADOR
        ]
    
class IsAdminOrAdvogado(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        return request.user.type_user in [
            TypeUserChoices.ADVOGADO, 
            TypeUserChoices.ADMINISTRADOR
        ]
    
class IsAdminBrokerOrAdvogado(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return user.type_user in [
            TypeUserChoices.ADVOGADO, 
            TypeUserChoices.ADMINISTRADOR,
            TypeUserChoices.BROKER
        ]

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.type_user == TypeUserChoices.ADMINISTRADOR