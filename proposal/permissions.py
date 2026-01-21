from rest_framework import permissions


class IsAdminOrBroker(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        return request.user.role in[
            'ADMINISTRADOR', 
            'BROKER'
        ]
        

class IsBrokerOrCedenteOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return request.user.role in[
            'BROKER',
            'CEDENTE',
            'ADMINISTRADOR'
        ]
        