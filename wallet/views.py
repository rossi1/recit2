from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, RetrieveAPIView, get_object_or_404

from accounts.authentication import JwtAuthentication
from accounts.utils import encode_user_payload


from .serializer import SecurePassword, AddBankSerializer
from .permission import SecureView
from .models import  BankDetails



@permission_classes([IsAuthenticated,])
@api_view(['POST'])
def gain_secure_token(request):
    serializer = SecurePassword(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(email=request.user.email, password=serializer.validated_data['password'])
    if user is None:
        return Response({'invalid credentials': 'invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        token = encode_user_payload(user)
        has_uploaded_bank = False
        try:
            user = BankDetails.objects.get(bank_id=request.user)
        except BankDetails.DoesNotExist:
            pass
        else:
            has_uploaded_bank = True
        return Response(data={'token': token, 'wallet_balance': request.user.wallet_balance.balance, 'bank_details_uploaded': has_uploaded_bank, 'pk': user.pk}, 
        status=status.HTTP_200_OK)


class AddBankDetails(CreateAPIView):
    permission_classes = (IsAuthenticated ,SecureView)
    queryset = BankDetails
    serializer_class = AddBankSerializer

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateBank(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, SecureView)
    queryset = BankDetails
    serializer_class = AddBankSerializer
    lookup_url_kwarg = 'pk'

