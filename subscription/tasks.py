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
def _send_email(message, message_body, email):
    return send_mail(message, message_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)

def extend_subscription_date():
    today_date = date.today()
    sub_expiry_date = today_date + relativedelta(days=+2)
    return sub_expiry_date



def update_freemium_plan_end_date():
    sub_type =  SubscriptionPlan.objects.filter(subscription_type='freemium_plan').all()

    for subs in sub_type:
        if subs.sub_end_date == date.today():
            subs.sub_start_date = date.today()
            subs.sub_end_date = extend_subscription_date()
            return subs.save()


def update_freelance_plan_end_date():
    sub_type =  SubscriptionPlan.objects.filter(subscription_type='freelance_plan').all()

    for subs in sub_type:
        if subs.is_trial and subs.trial_end_date == date.today():
            create_charge = charge_customer()
            subs.trial_end_date = None
            subs.is_trial = False
            subject = 'Recit Trial plan Ended'
            message = 'Your free trial  {} has ended and you would charge automatically to enable you to enjoy our services'.format(subs.subscription_type)
            _send_email(subject,  message, subs.plan_id.email)
            
            return subs.save()
        elif not subs.is_trial and subs.trial_end_date == date.today():
            subs.sub_start_date = date.today()
            subs.sub_end_date = extend_subscription_date()
            charge_customer()
            return subs.save()
            



def update_business_plan_end_date():
    sub_type =  SubscriptionPlan.objects.filter(subscription_type='business_plan').all()

    for subs in sub_type:
        if subs.is_trial and subs.trial_end_date == date.today():
            subs.trial_end_date = None
            subs.is_trial = False
            subject = 'Recit Trial plan Ended'
            message = 'Your free trial  {} has ended and you would charge automatically to enable you to enjoy our services'.format(subs.subscription_type)
            _send_email(subject,  message, subs.plan_id.email)
            charge_customer()
            return subs.save()
        
        
        
@periodic_task(
    run_every=(crontab(hour=9, minute=30)),
    name='task_send_automated_reminder',
    ignore_result=True
)
def subscriptions_plans():
    update_freemium_plan_end_date()
    update_freelance_plan_end_date()
    update_business_plan_end_date()

                    



