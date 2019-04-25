from decimal import Decimal


from django.db import models
from django.conf import settings 

# Create your models here.
class WalletBalance(models.Model):
    balance_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    related_name='wallet_balance'
    )
    balance = models.DecimalField(decimal_places=2, max_digits=20, default=Decimal('0.00'))

    def __str__(self):
        return str(self.balance_id)




class BankDetails(models.Model):
    bank_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    related_name='bank_details'
    )
    bank_name = models.CharField(max_length=250)
    bank_account_name = models.CharField(max_length=250)
    bank_account_number = models.CharField(max_length=250)
    bvn_number = models.CharField(max_length=250)
    

    def __str__(self):
        return str(self.bank_id)

