from decimal import Decimal


from django.db import models
from django.conf import settings

# Create your models here.
class InventoryProducts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory_product')
    product_id = models.IntegerField()
    title = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    is_avaliable = models.BooleanField(default=False)
    link = models.URLField()
    price = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal('0.00'))
    tax = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    weight = models.CharField(max_length=50,blank=True, null=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.product_id)


class InventoryInvoices(models.Model):
    inventories = models.ForeignKey(InventoryProducts, on_delete=models.CASCADE, related_name='inventory_invoicesss')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory_productss')
    created = models.DateTimeField(auto_now_add=True)
    link = models.URLField()
    product_id = models.IntegerField()
    

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.user)