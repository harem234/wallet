from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Wallets, Transactions
from .serializers import WalletSerializer, TransactionsSerializer,DepositSerializer, TransferSerializer, UserWalletSerializer


class WalletViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving user's Wallet.
    """
    queryset = Wallets.objects.all()
    serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    
    permission_classes_by_action = {
        'create_user_wallet': [AllowAny],
        'get_wallet': [IsAuthenticated],
        'deposit': [IsAuthenticated],
        'transfer':[IsAuthenticated]
    }

    @action(detail=False, methods=['get'])
    def get_wallet(self, request, ):
        queryset = Wallets.objects.filter().select_for_update()
        wallet = get_object_or_404(queryset, user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def deposit(self, request, ):
        
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                queryset = Wallets.objects.filter().select_for_update()
                wallet = get_object_or_404(queryset, user=request.user)
                wallet.deposit(serializer.validated_data.get('amount', ))

        serializer = WalletSerializer(wallet)

        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def transfer(self, request, pk=None):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                queryset = Wallets.objects.filter().select_for_update()
                
                source_wallet = get_object_or_404(queryset, user=request.user)

                destination_user = serializer.validated_data.get('destination_user')
                destination_wallet = get_object_or_404(queryset, pk=destination_user.pk)

                amount = serializer.validated_data.get('amount')
                source_wallet.transfer(destination_wallet, amount,)
        
        serializer = WalletSerializer(source_wallet)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_user_wallet(self, request, ):
        serializer = UserWalletSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]