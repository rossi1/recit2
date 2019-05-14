import json
from datetime import timedelta, datetime
from twilio.rest import Client

from django.conf import settings
from django.core.mail import send_mail
from django.core.serializers.json import DjangoJSONEncoder

from cashtarg._celery import app

from celery import shared_task
from celery.schedules import crontab
#from celery.schedules import contrab
from celery.decorators import periodic_task
from invoice.models import AutomatedReminder





@shared_task    
def send_sms(invoice_link, number):
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message = client.messages.create(
            body='Invoice link {}'.format(invoice_link),
            from_='+12013409296',
            to=str(number)
        )
    return json.dumps({'side': message}, cls=DjangoJSONEncoder)

    
@shared_task
def _send_email(message, message_body, email):
    return send_mail(message, message_body, settings.EMAIL_HOST_USER, [email], fail_silently=False)



def schedule_reminder(remind):
    link = remind.invoice.link
    message_body = 'invoice link {}'.format(link)
    if remind.medium.lower() == 'sms':
        number = None
        try:
            number = remind.invoice.client_id.client_phone_number
        except AttributeError:
            number = remind.invoice.client_phone_number

        send_sms(message_body, number)
    elif remind.medium.lower() == 'email':
        email = None
        try:
            email = remind.invoice.client_id.email
        except AttributeError:
            email = remind.invoice.client_email

        _send_email.delay('Reminder', message_body,  email)
            
    elif remind.medium.lower() == 'emailsms':
        email = None
        number = None
         
        
        try:
            email = remind.invoice.client_id.email
            number = remind.invoice.client_id.client_phone_number
        except AttributeError:
            email = remind.invoice.client_email
            number = remind.invoice.client_phone_number


        send_sms.delay(message_body, number)
        _send_email.delay('Reminder', message_body,  email)




"""
@periodic_task(
    run_every=(timedelta(minutes=30)),
    name='task_send_automated_reminder',
    ignore_result=True
)
def send_automated_reminder():
    reminder = AutomatedReminder.objects.all()
    for remind in reminder:
        if not remind.cancel:
            link = remind.invoice.link
            message_body = 'invoice link {}'.format(link)
            if remind.medium.lower() == 'sms':
                send_sms(message_body, remind.invoice.client_phone_number)
            elif remind.medium.lower() == 'email':
                
                _send_email.delay('Reminder', message_body,  remind.invoice.client_email)
            
            elif remind.medium.lower() == 'emailsms':
                send_sms.delay(message_body, remind.invoice.client_phone_number)
                _send_email.delay('Reminder', message_body,  remind.invoice.client_email)

"""

@periodic_task(
    run_every=(crontab(hour=7, minute=30)),
    name='task_send_automated_reminder',
    ignore_result=True
)
def send_reminder_once():
    reminder = AutomatedReminder.objects.all()
    for remind in reminder:
        if remind.reminder_type.upper() == 'ONCE':
            today = datetime.today().weekday()
            if today == remind.days_of_the_week:
                schedule_reminder(remind)
                remind.invoice.can_create_reminder = True
                remind.invoice.save()
                remind.delete()

        else:
            schedule_reminder(remind)


                    



