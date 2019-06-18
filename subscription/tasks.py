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

def cancel_restriction():
    subscription = SubscriptionPlan.objects.all()
    for subs in subscription:
        if not subs.can_switch:
            today = datetime.now()
            #today_unixtimestamp = datetime.timestamp(today)
            timestamp = subs.sub_switch_date
            if today == timestamp:
                subs.can_switch = True
                return subs.save()


"""
def update_freemium_plan_end_date():
    sub_type =  SubscriptionPlan.objects.filter(subscription_type='freemium_plan').all()

    for subs in sub_type:
        if subs.subscription_end_date == date.today():
            subs.subscription_start_date = date.today()
            subs.subscription_end_date = extend_subscription_date()
            return subs.save()

"""          




     
@periodic_task(
    run_every=(crontab(hour=11, minute=30)),
    name='task_send_automated_reminder',
    ignore_result=True
)
def subscriptions_plans():
    cancel_restriction()
                    



