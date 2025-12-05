from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    InvoiceViewSet,
    PayPalCreateOrderView,
    PayPalCaptureOrderView
)

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('', include(router.urls)),
    path('create-order/', PayPalCreateOrderView.as_view(), name='paypal-create-order'),
    path('capture-order/', PayPalCaptureOrderView.as_view(), name='paypal-capture-order'),
]
