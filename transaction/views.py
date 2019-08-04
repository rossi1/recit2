import datetime

from django.db.models import Sum

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.validators import ValidationError
from rest_framework.generics import ListAPIView,  get_object_or_404
from rest_framework.views import APIView

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


class View(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    



    def get(self, request, *args, **kwargs):
        
        query =  TransactionHistory.objects.filter(user_id=request.user)

        a_day_ago = query.filter(transact_date__day__lte=1).aggregate(Sum('transact_amount'))
        a_week_ago = query.filter(transact_date__week__lte=1).aggregate(Sum('transact_amount'))
        a_month_ago = query.filter(transact_date__month__lte=1).aggregate(Sum('transact_amount'))
        six_month_ago = query.filter(transact_date__month__lte=6).aggregate(Sum('transact_amount'))
        a_year_ago = query.filter(transact_date__month__lte=6).aggregate(Sum('transact_amount'))
        
        return Response({'a_day_ago': a_day_ago['transact_amount__sum'], 
        'a_week_ago': a_week_ago['transact_amount__sum'],
        'a_month_ago': a_month_ago['transact_amount__sum'],
        'six_month_ago': six_month_ago['transact_amount__sum'],
        'a_year_ago': a_year_ago['transact_amount__sum']
         }, status=status.HTTP_200_OK)
