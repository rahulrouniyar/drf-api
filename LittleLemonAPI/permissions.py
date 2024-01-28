from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    """
    Custom permission to check if the user belongs to the 'Manager' group.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()
    
class IsDeliveryCrew(BasePermission):
    """
    Custom permission to check if the user belongs to the 'DeliveryCrew' group.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='DeliveryCrew').exists()
