from rest_framework.serializers import Serializer
from rest_framework import serializers


from .models import BankDetails

class SecurePassword(Serializer):
    password = serializers.CharField(required=True)


class AddBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        exclude= ('bank_id',)

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request is not None and hasattr(request, 'user'):
            user = request.user
            save_data = BankDetails.objects.create(bank_id=user, **validated_data)
            return save_data

