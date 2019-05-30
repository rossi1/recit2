from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings


#import cloudinary
#from cloudinary.models import CloudinaryField

from rest_framework import exceptions


from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=120, unique=True)
    user_id = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    last_name  = models.CharField(max_length=250)
    password = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


    
    def __str__(self):
        return str(self.email)






class BusinessInfo(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    related_name='buiness_info'
    )
    business_name = models.CharField(max_length=250)
    business_description = models.TextField()
    business_number = models.CharField(max_length=250, blank=True)
    business_address = models.CharField(max_length=250)
    business_type = models.CharField(max_length=250, blank=True)
    business_size = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    business_website = models.URLField(blank=True)
    business_logo = models.ImageField()
    cac_number  = models.CharField(max_length=250, blank=True)
    approved_account = models.BooleanField(default=False)
    has_uploaded_bank_details = models.BooleanField(default=False)
    address = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    gender = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250)


    def __str__(self):
        return str(self.user)
