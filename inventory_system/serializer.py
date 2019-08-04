from collections import OrderedDict

from rest_framework import serializers

from .models import InventoryProducts, InventoryInvoices


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryProducts
        exclude = ('user',)

class ProductSerializerLising(serializers.ModelSerializer):
    class Meta:
        model = InventoryProducts
        exclude = ('user',) 


class ProductInvoicerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InventoryInvoices
        exclude = ['user', 'created', 'link'] 
    
    def to_representation(self, obj):
        products = []
        ret = super(ProductInvoicerSerializer, self).to_representation(obj)
        product_ids = obj.product_list
        ret.pop('product_list')
        
        for ids in product_ids:
            products.append(InventoryProducts.objects.filter(pk=ids).values('title',
            'description', 'quantity', 'is_avaliable', 'price', 'tax', 'weight'))
    
        ret['products'] = products
 
        return ret
    