from decimal import Decimal
from django.core import validators
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from .models import Transactions, Wallets

USER_MODEL = get_user_model()

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallets
        fields = "__all__"

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = "__all__"

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=12, decimal_places=2, validators=(validators.MinValueValidator(Decimal(0.00)),))

class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(required=True, max_digits=12, decimal_places=2, validators=(validators.MinValueValidator(Decimal(0.00)),))
    destination_user = serializers.PrimaryKeyRelatedField(required=True, queryset=USER_MODEL.objects.all())
    
class UserWalletSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = USER_MODEL
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = USER_MODEL.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        user.set_password(validated_data['password'])
        user.save()

        Wallets.objects.create(
            user=user
        )
        
        return user