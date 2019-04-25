import jwt


from django.conf import settings

from rest_framework.permissions import BasePermission

class SecureView(BasePermission):
    def has_permission(self, request, view):
        token = request.query_params.get('secure_token', None)
        if token is None:
            return False
        else:
            try:
                jwt.decode(token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM)
            except jwt.ExpiredSignatureError:
                return False
            except jwt.DecodeError:
                return  False
            else:
                return True


