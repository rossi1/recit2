import json
from datetime import timedelta, datetime, date


from dateutil.relativedelta import *

from django.conf import settings
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder

from cashtarg._celery import app

from celery import shared_task
from celery.schedules import crontab
from celery.decorators import periodic_task


from .models import SubscriptionPlan


    
@shared_task
def _send_email(subject, message_body, email):
    return send_mail(subject, message_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)

def extend_subscription_date():
    today_date = date.today()
    sub_expiry_date = today_date + relativedelta(days=+1)
    return sub_expiry_date



def update_freemium_plan_end_date():
    sub_type =  SubscriptionPlan.objects.filter(subscription_type='freemium_plan').all()

    for subs in sub_type:
        if subs.subscription_end_date == date.today():
            subs.subscription_start_date = date.today()
            subs.subscription_end_date = extend_subscription_date()
            return subs.save()

            




        
        
@periodic_task(
    run_every=(crontab(hour=9, minute=30)),
    name='task_send_automated_reminder',
    ignore_result=True
)
def subscriptions_plans():
    update_freemium_plan_end_date()

                    



