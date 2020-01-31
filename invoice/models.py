import uuid

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import HStoreField, JSONField
from django.utils import timezone


# Create your models here.

class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    invoice_id = models.IntegerField()
    invoice_type = models.CharField(max_length=20)
    created = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=timezone.now)
    is_pending = models.BooleanField(default=True)
    #approved  = models.BooleanField(default=False)
    data = JSONField()
    description = models.TextField(blank=True)
    link = models.URLField()
    logo = models.ImageField(blank=True)
    client_name = models.CharField(max_length=50,blank=True, null=True)
    client_email = models.EmailField(unique=True, blank=True, null=True)
    client_phone_number = models.CharField(max_length=50, blank=True, null=True)
    client_address = models.CharField(max_length=50, blank=True, null=True)
    
    client_id = models.ForeignKey('ClientInfo', on_delete=models.CASCADE, related_name='client', null=True)

    project_amount = models.DecimalField(decimal_places=2, max_digits=20)
    #set_payment = models.CharField(max_length=20, blank=True)
    currency =  models.CharField(max_length=20)
    tax =  models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    shipping_fee =  models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    can_create_reminder = models.BooleanField(default=True)


    def __str__(self):
        return str(self.invoice_id)

    def default_date(self):
        date = datetime.date(timezone.now())
        return date
        



class AutomatedReminder(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='invoice_reminder')
    #cancel = models.BooleanField(default=False)
    message = models.CharField(max_length=100, blank=True)
    medium = models.CharField(max_length=50)
    reminder_type =  models.CharField(max_length=50, blank=True, default='')
    reminder_set_day = models.CharField(max_length=50, blank=True, default='')
    days_of_the_week = models.IntegerField(default=0)


    def __str__(self):
        return str(self.invoice)


class ClientInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_info')
    client_name = models.CharField(max_length=50)
    client_email = models.EmailField(unique=True)
    client_phone_number = models.CharField(max_length=50)
    client_address = models.CharField(max_length=50, blank=True)
    

