from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookViewSet, WebhookLogViewSet

router = DefaultRouter()
router.register(r'', WebhookViewSet, basename='webhook')
router.register(r'logs', WebhookLogViewSet, basename='webhooklog')

urlpatterns = [
    path('', include(router.urls)),
]
