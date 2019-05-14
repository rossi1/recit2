from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from subscription.models import SubscriptionPlan

from .models import BusinessInfo


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_business_account_for_new_user(sender, created, instance, **kwargs):
    if created:
        BusinessInfo.objects.create(user=instance)
        SubscriptionPlan.objects.create(plan_id=instance)
