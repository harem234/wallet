from django.contrib import admin
from .models import Wallets, Transactions

class TransactionsInline(admin.TabularInline):
    model = Transactions

@admin.register(Wallets)
class WalletsAdmin(admin.ModelAdmin):
    inlines = (
        TransactionsInline,
    )

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    pass