from django.contrib import admin

# Register your models here.
from .models import Invoice, AutomatedReminder, ClientInfo


admin.site.register(Invoice)
admin.site.register(AutomatedReminder)
admin.site.register(ClientInfo)