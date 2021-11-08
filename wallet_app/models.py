from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models.constraints import CheckConstraint
from django.db.models.query_utils import Q
from django.utils.translation import gettext as _

from .errors import InsufficientBalance

USER_MODEL = get_user_model()


class Wallets(models.Model):

    user = models.OneToOneField(verbose_name=_("user's wallet"), to=USER_MODEL, on_delete=models.SET_NULL, null=True)

    # This stores the wallet's current balance. Also acts
    # like a cache to the wallet's balance as well.
    current_balance = models.DecimalField(verbose_name=(
        'Balance'), default=0, decimal_places=2, max_digits=12, validators=(MinValueValidator(Decimal('0.00')), ))

    # The date/time of the creation of this wallet.
    created_at = models.DateTimeField(auto_now_add=True)

    def deposit(self, value):
        """
        Deposits a value to the wallet.
        Also creates a new transaction with the deposit
        value.
        """
        self.transactions_set.create(
            value= value,
            running_balance=self.current_balance + value
        )
        self.current_balance += value
        self.save()

    def withdraw(self, value):
        """
        Withdraw's a value from the wallet.
        Also creates a new transaction with the withdraw
        value.
        Should the withdrawn amount is greater than the
        balance this wallet currently has, it raises an
        :mod:`InsufficientBalance` error. This exception
        inherits from :mod:`django.db.IntegrityError`. So
        that it automatically rolls-back during a
        transaction lifecycle.
        """
        if value > self.current_balance:
            raise InsufficientBalance('This wallet has insufficient balance.')

        self.transactions_set.create(
            value= -value,
            running_balance=self.current_balance - value
        )
        self.current_balance -= value
        self.save()

    def transfer(self, wallet, value):
        """Transfers an value to another wallet.
        Uses `deposit` and `withdraw` internally.
        """
        self.withdraw(value)
        wallet.deposit(value)

    def __str__(self):
        return f"{self.user} balance: {self.current_balance}"

    class Meta:

        constraints = (
            CheckConstraint(
                check=Q(current_balance__gte=Decimal('0.00')),
                name="%(app_label)s_%(class)s_balance_is_zero_or_positive",
            ),
        )


class Transactions(models.Model):
    # The wallet that holds this transaction.
    wallet = models.ForeignKey(Wallets, on_delete=models.SET_NULL, null=True)

    # The value of this transaction.
    value = models.DecimalField(verbose_name=(
        'Value'), default=0, decimal_places=2, max_digits=12, validators=(MinValueValidator(Decimal('0.00')), ))

    # The value of the wallet at the time of this
    # transaction. Useful for displaying transaction
    # history.
    running_balance = models.DecimalField(verbose_name=(
        'Running Balance'), default=0, decimal_places=2, max_digits=12, validators=(MinValueValidator(Decimal('0.00')), ))

    # The date/time of the creation of this transaction.
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"user: {self.wallet.user.pk} running_balance: {self.running_balance}"
