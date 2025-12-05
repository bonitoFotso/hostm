from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactFormFieldViewSet, ContactMessageViewSet

router = DefaultRouter()
router.register(r'fields', ContactFormFieldViewSet, basename='contactformfield')
router.register(r'messages', ContactMessageViewSet, basename='contactmessage')

urlpatterns = [
    path('', include(router.urls)),
]
