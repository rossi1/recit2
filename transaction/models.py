from django.db import models
from django.conf import settings

# Create your models here.

class TransactionHistory(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    related_name='transaction_history')
    client_id = models.ForeignKey('invoice.ClientInfo', on_delete=models.CASCADE, 
    related_name='client_transact_history')
    invoice_id = models.IntegerField()
    transact_amount = models.DecimalField(decimal_places=2, max_digits=20)
    transact_data = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200)

    class Meta:
        ordering = ('-transact_amount',)
        

    def __str__(self):
        return str(self.user_id)

