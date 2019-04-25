from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.validators import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, get_object_or_404

from  .serializer import ProductSerializer, ProductInvoicerSerializer
from  .models import InventoryProducts, InventoryInvoices

class ProductCreationView(CreateAPIView):
    #authentication_classes = (SessionAuthentication,)
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
    #authentication_classes = (SessionAuthentication,)
    serializer_class = ProductSerializer
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
    serializer_class = ProductSerializer
    queryset = InventoryProducts
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'


@api_view(['GET'])
@permission_classes([IsAuthenticated,])
def update_product_quantity_view_to_not_available(request, product_id):
    try:
        InventoryProducts.objects.get(product_id=product_id).update(is_avaliable=False)
    except InventoryProducts.DoesNotExist:
        raise ValidationError('Product Does Not Exist')
 
    else:
        return Response(data={'response': 'success', 'message': 'product updated succesfully'}, 
        status=status.HTTP_200_OK)

class InvoiceProductCreateView(ProductCreationView):
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