from django.contrib import admin

# Register your models here.

from .models import InventoryInvoices, InventoryProducts

admin.site.register(InventoryInvoices)
admin.site.register(InventoryProducts)
