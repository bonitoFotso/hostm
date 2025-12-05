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
        from datetime import datetime
        queryset = AnalyticsEvent.objects.filter(website__user=self.request.user)

        # Filtres
        website_id = self.request.query_params.get('website')
        event_type = self.request.query_params.get('event_type')
        start_date_param = self.request.query_params.get('start_date')
        end_date_param = self.request.query_params.get('end_date')
        days = self.request.query_params.get('days')

        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Filtrer par période
        if start_date_param and end_date_param:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=start_date, created_at__lte=end_date)
        elif days:
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)
        else:
            start_date = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=start_date)

        return queryset.order_by('-created_at')


class DailyStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les statistiques journalières"""

    serializer_class = DailyStatsSerializer
    permission_classes = [IsAuthenticated, HasAnalyticsFeature]

    def get_queryset(self):
        """Retourne les stats des sites web de l'utilisateur"""
        from datetime import datetime
        queryset = DailyStats.objects.filter(website__user=self.request.user)

        # Filtres
        website_id = self.request.query_params.get('website')
        start_date_param = self.request.query_params.get('start_date')
        end_date_param = self.request.query_params.get('end_date')
        days = self.request.query_params.get('days')

        if website_id:
            queryset = queryset.filter(website_id=website_id)

        # Filtrer par période
        if start_date_param and end_date_param:
            # Utiliser start_date et end_date si fournis
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
        elif days:
            # Sinon utiliser le paramètre days
            start_date = timezone.now().date() - timedelta(days=int(days))
            queryset = queryset.filter(date__gte=start_date)
        else:
            # Par défaut: 30 derniers jours
            start_date = timezone.now().date() - timedelta(days=30)
            queryset = queryset.filter(date__gte=start_date)

        return queryset.order_by('-date')


class AnalyticsStatsView(views.APIView):
    """Vue pour obtenir des statistiques agrégées"""

    permission_classes = [IsAuthenticated, HasAnalyticsFeature]

    def get(self, request):
        """Retourne les statistiques agrégées"""
        from datetime import datetime
        website_id = request.query_params.get('website')
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        days = request.query_params.get('days')

        # Filtrer les stats
        queryset = DailyStats.objects.filter(website__user=request.user)
        if website_id:
            queryset = queryset.filter(website_id=website_id)

        # Filtrer par période
        if start_date_param and end_date_param:
            start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)
        elif days:
            start_date = timezone.now().date() - timedelta(days=int(days))
            queryset = queryset.filter(date__gte=start_date)
        else:
            start_date = timezone.now().date() - timedelta(days=30)
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
        if start_date_param and end_date_param:
            events_start = datetime.strptime(start_date_param, '%Y-%m-%d')
            events_end = datetime.strptime(end_date_param, '%Y-%m-%d')
            events_queryset = AnalyticsEvent.objects.filter(
                website__user=request.user,
                created_at__gte=events_start,
                created_at__lte=events_end
            )
        else:
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
