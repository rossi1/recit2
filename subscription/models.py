
from django.db import models
from django.conf import settings

# Create your models here.
class SubscriptionPlan(models.Model):
    plan_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_plan')
    subscription_end_date = models.DateField(null=True)
    subscription_start_date = models.DateField(null=True)
    subscription_type = models.CharField(max_length=50, null=True)
    customer_id = models.CharField(max_length=50, null=True)
    can_switch = models.BooleanField(default=True)
    sub_switch_date = models.DateField(null=True)
    #card_source =  models.CharField(max_length=50, null=True)
    subscription_id = models.CharField(max_length=50, null=True)


    def __str__(self):
        return str(self.plan_id)



