from collections import OrderedDict
import json


from django.forms.models import model_to_dict
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
from django.core import serializers

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.validators import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, get_object_or_404

from  .serializer import ProductSerializer, ProductInvoicerSerializer, ProductSerializerLising
from  .models import InventoryProducts, InventoryInvoices

class ProductCreationView(CreateAPIView):
    authentication_classes = (SessionAuthentication,)
    queryset =  InventoryProducts
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)


    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = self.generate_product_link(serializer.validated_data['product_id'], request.user.user_id, request)
        self.perform_create(serializer, link)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def generate_product_link(product_id, user_id, request):
        if request.query_params.get('invoice') is not None:
            link = getattr(settings, 'PRODUCT_INVENTORY_LINK')
        else:
            link = getattr(settings, 'PRODUCT_INVENTORY_LINK')
           
        url = '{}/{}/?user_id={}'.format(link, product_id, user_id)
        return url 

    def perform_create(self, serializer, link):
        serializer.save(user=self.request.user, link=link)



class ProductListingView(ListAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = ProductSerializerLising
    queryset = InventoryProducts
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.objects.filter(user=self.request.user).all()


class ProductDeleteView(DestroyAPIView):
    serializer_class = ProductSerializer
    queryset = InventoryProducts
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'

class ProductEditView(RetrieveUpdateAPIView):
    authentication_classes = (SessionAuthentication,)
    serializer_class = ProductSerializer
    queryset = InventoryProducts
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'


@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def update_product_quantity_view_to_not_available(request, product_id):
    product =  get_object_or_404(InventoryProducts, product_id=product_id) #InventoryProducts.objects.filter(product_id=product_id)
    if  product.is_avaliable:
        product.is_avaliable = False
        product.save()
    elif  not product.is_avaliable:
        product.is_avaliable = True
        product.save()

    return Response(data={'response': 'success', 'message': 'product updated succesfully'}, status=status.HTTP_200_OK)

class InvoiceProductCreateView(ProductCreationView):
    authentication_classes = (SessionAuthentication,)
    queryset = InventoryInvoices
    serializer_class = ProductInvoicerSerializer

    


class InvoiceProductListView(ProductListingView):
    authentication_classes = (SessionAuthentication,)
    queryset = InventoryInvoices
    serializer_class = ProductInvoicerSerializer

    def get_queryset(self):
        return self.queryset.objects.filter(user=self.request.user).all()


class InvoiceProductDeleteView(ProductDeleteView):
    queryset = InventoryInvoices
    serializer_class = ProductInvoicerSerializer




@api_view(['GET'])
@permission_classes([AllowAny,])
def view_product_for_payment(request, product_id):
    user_id = request.query_params.get('user_id', None)
    if user_id is None:
        raise ValidationError('user id missing')

    data = OrderedDict()
    
    
    
    try:
        user = get_user_model().objects.get(user_id=user_id)
        product = InventoryInvoices.objects.get(product_id=product_id)
    except get_user_model().DoesNotExist:
       
        raise  ValidationError('user is invalid')
    



    user_detail = {
        'business_name': user.buiness_info.business_name,
        'business_number': user.buiness_info.business_number,
        'business_address': user.buiness_info.business_address,
        'business_email': user.email
    }


    
    
    data['user'] = user_detail
    prods = ProductInvoicerSerializer(product)
    to_json = serializers.serialize('json', product) 
    data['product_detail'] = to_json
    print(data)
    return Response(data)
