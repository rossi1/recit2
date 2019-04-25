from django.db import models
from django.conf import settings

# Create your models here.
class SubscriptionPlan(models.Model):
    plan_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_plan')
    is_trial = models.BooleanField(default=False)
    trial_end_date = models.DateField(null=True)
    subscription_type = models.CharField(max_length=50, null=True)
    sub_end_date = models.DateField(null=True)
    customer_card_id = models.CharField(max_length=50, null=True)


    def __str__(self):
        return str(self.plan_id)