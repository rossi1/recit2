from rest_framework import serializers

from .models import InventoryProducts, InventoryInvoices


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryProducts
        exclude = ('user', 'link')

class ProductSerializerLising(serializers.ModelSerializer):
    class Meta:
        model = InventoryProducts
        exclude = ('user',) 


class ProductInvoicerSerializer(serializers.ModelSerializer):
    inventories = ProductSerializer()

    class Meta:
        model = InventoryInvoices
        fields = '__all__'