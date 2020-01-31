from django.core.mail import EmailMessage
from django.conf import settings



def charge_back_mail(subject, message, attach):
    mail = EmailMessage(subject, message, settings.EMAIL_HOST_USER, settings.EMAIL_ADMINS)
    mail.attach(attach.name, attach.read(), attach.content_type)
    return mail.send()