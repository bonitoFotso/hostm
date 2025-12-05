from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsEventViewSet, DailyStatsViewSet, AnalyticsStatsView

router = DefaultRouter()
router.register(r'events', AnalyticsEventViewSet, basename='analyticevent')
router.register(r'daily-stats', DailyStatsViewSet, basename='dailystats')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', AnalyticsStatsView.as_view(), name='stats'),
]
