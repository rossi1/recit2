from rest_framework import serializers
from .models import TransactionHistory

class TransactionClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        exclude = ('user_id',)


class TransactionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        exclude = ('user_id',)
