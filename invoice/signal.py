from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

from .models import ClientInfo, Invoice

