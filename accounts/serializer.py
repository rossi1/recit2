import re
import random 


from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.response import Response

from .models import BusinessInfo

def generated_unique_id(unique_number_count):
    unique_id = ''.join(str(random.randint(2, 8)) for x in range(unique_number_count))
    return unique_id


def create_user(**kwargs):
    user = get_user_model().objects.create_user(email=kwargs['email'],
                                                first_name=kwargs['first_name'],
                                                last_name=kwargs['last_name'],
                                                user_id=generated_unique_id(6))
    user.set_password(kwargs['password'])
    user.save()
    return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

        

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(required=True)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)


class BusinessSerializer(serializers.ModelSerializer):
    account = UserSerializer()
    class Meta:
        model = BusinessInfo
        exclude = ('user', 'approved_account', 'has_uploaded_bank_details' )

    def create(self, validated_data):
        account = create(**validated_data.pop("account"))
        return BusinessInfo(user=account, **validated_data)
        

