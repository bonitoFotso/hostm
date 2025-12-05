from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from core.permissions import HasAnalyticsFeature
from .models import AnalyticsEvent, DailyStats
from .serializers import (
    AnalyticsEventSerializer,
    DailyStatsSerializer,
    AnalyticsStatsSerializer
)


class AnalyticsEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les événements analytics (lecture seule)"""

    serializer_class = AnalyticsEventSerializer
    permission_classes = [IsAuthenticated, HasAnalyticsFeature]

    def get_queryset(self):
        """Retourne les événements des sites web de l'utilisateur"""
        queryset = AnalyticsEvent.objects.filter(website__user=self.request.user)

        # Filtres
        website_id = self.request.query_params.get('website')
        event_type = self.request.query_params.get('event_type')
        days = self.request.query_params.get('days', 30)

        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filtrer par période
        start_date = timezone.now() - timedelta(days=int(days))
        queryset = queryset.filter(created_at__gte=start_date)

        return queryset.order_by('-created_at')


class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les statistiques journalières"""

    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated, HasAnalyticsFeature]

    def get_queryset(self):
        """Retourne les stats des sites web de l'utilisateur"""
        queryset = DailyStats.objects.filter(website__user=self.request.user)

        # Filtres
        website_id = self.request.query_params.get('website')
        days = self.request.query_params.get('days', 30)

        if website_id:
            queryset = queryset.filter(website_id=website_id)

        # Filtrer par période
        start_date = timezone.now().date() - timedelta(days=int(days))
        queryset = queryset.filter(date__gte=start_date)

        return queryset.order_by('-date')


class AnalyticsStatsView(views.APIView):
    """Vue pour obtenir des statistiques agrégées"""

    permission_classes = [IsAuthenticated, HasAnalyticsFeature]

    def get(self, request):
        """Retourne les statistiques agrégées"""
        website_id = request.query_params.get('website')
        days = int(request.query_params.get('days', 30))

        # Filtrer les stats
        queryset = DailyStats.objects.filter(website__user=request.user)
        if website_id:
            queryset = queryset.filter(website_id=website_id)

        start_date = timezone.now().date() - timedelta(days=days)
        queryset = queryset.filter(date__gte=start_date)

        # Agréger les données
        aggregated = queryset.aggregate(
            total_contacts=Sum('contacts_count'),
            total_projects_views=Sum('projects_views'),
            total_api_calls=Sum('api_calls'),
            total_unique_visitors=Sum('unique_visitors')
        )

        # Stats par période
        period_stats = list(queryset.values('date').annotate(
            contacts=Sum('contacts_count'),
            views=Sum('projects_views'),
            calls=Sum('api_calls')
        ).order_by('date'))

        # Top événements
        events_queryset = AnalyticsEvent.objects.filter(
            website__user=request.user,
            created_at__gte=start_date
        )
        if website_id:
            events_queryset = events_queryset.filter(website_id=website_id)

        top_events = list(events_queryset.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5])

        data = {
            'total_contacts': aggregated['total_contacts'] or 0,
            'total_projects_views': aggregated['total_projects_views'] or 0,
            'total_api_calls': aggregated['total_api_calls'] or 0,
            'total_unique_visitors': aggregated['total_unique_visitors'] or 0,
            'period_stats': period_stats,
            'top_events': top_events
        }

        serializer = AnalyticsStatsSerializer(data)
        return Response(serializer.data)
