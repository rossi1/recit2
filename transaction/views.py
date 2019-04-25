from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.validators import ValidationError
from rest_framework.generics import ListAPIView,  get_object_or_404

from invoice.models import ClientInfo
from .models import TransactionHistory
from .serializers import TransactionClientSerializer, TransactionUserSerializer

class ViewClientHistory(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TransactionHistory
    serializer_class = TransactionClientSerializer

    def get_queryset(self):
        client_id = self.request.query_params.get('client_id', None)
        if client_id is not None:
            client = get_object_or_404(ClientInfo, pk=client_id)
            return self.queryset.objects.filter(client_id=client).all()
        return ValidationError("client_id params required")


class ViewUserHistory(ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TransactionHistory
    serializer_class = TransactionUserSerializer

    def get_queryset(self):
        return self.queryset.objects.filter(user_id=self.request.user).all()


