from django.contrib import admin
from django.contrib.auth  import get_user_model
# Register your models here.
from .models import BusinessInfo


admin.site.register(BusinessInfo)
admin.site.register(get_user_model())