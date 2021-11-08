from django.urls import path, include
from rest_framework import routers

from .views import WalletViewSet
# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'wallet', WalletViewSet)

urlpatterns = [
    path('', include(router.urls)),
]