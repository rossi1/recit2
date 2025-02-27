import json
from collections import OrderedDict

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from accounts.serializer import generated_unique_id
from django.core.validators import FileExtensionValidator


from .models  import Invoice, ClientInfo, AutomatedReminder


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        exclude = ('user', 'created', 'is_pending', 'link', 'logo', 'can_create_reminder', 'client_id')

    def create(self, validated_data):
        request = self.context.get('request', '')
        user = getattr(request, 'user')

        if validated_data['invoice_type'] == 'One-Time':
            validated_data['invoice_type'] = settings.ONE_TIME
        else:
            recurring_method = validated_data['invoice_type'].split('-')
            if recurring_method[1].lower() == 'weekly':
                validated_data['invoice_type'] = settings.RECURRING_WEEKLY

            elif recurring_method[1].lower() == 'daily':
                validated_data['invoice_type'] = settings.RECURRING_DAILY

            elif recurring_method[1].lower() == 'monthly':
                validated_data['invoice_type'] = settings.RECURRING_MONTHLY
        
        data = validated_data['data']
        to_json = json.dumps({'data': data}, cls=DjangoJSONEncoder)

        validated_data['data'] = to_json

        return Invoice.objects.create(user=user,  **validated_data)
        #logo=user.buiness_info.business_logo,

    def to_representation(self, instance):
        client_details = OrderedDict()
        ret = super().to_representation(instance)
        try:
            client_details['client_address'] = invoice.client_id.client_address,
            client_details['client_name'] = invoice.client_id.client_email,
            client_details['client_phone_number'] = invoice.client_id.client_phone_number
        except:
            return ret

        return ret


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientInfo
        exclude = ('user',)

    def validate_name(self, instance):
        if instance  == self.context['request'].user.email:
            raise ValidationError('You cant add yourself as a client')
        return instance

class AutomatedReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomatedReminder
        exclude = ('invoice', 'days_of_the_week')


class ChargeBackSerializer(serializers.Serializer):
    invoice_id = serializers.CharField(max_length=50, required=True)
    contact_mail = serializers.EmailField(required=True)
    message = serializers.CharField(max_length=400, required=True)
    contact_name = serializers.CharField(max_length=50, required=True)
    dynamic_content = serializers.FileField(required=False)
