from django.contrib import admin

# Register your models here.

from .models import TransactionHistory

admin.site.register(TransactionHistory)
