from rest_framework.permissions import BasePermission

class IsNotFreemiumUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.subscription_plan.subscription_type == 'freemium_plan':
            return False
        return True