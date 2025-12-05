from rest_framework import serializers
from .models import AnalyticsEvent, DailyStats


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer pour les événements analytics"""

    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)

    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'website', 'event_type', 'event_type_display',
            'metadata', 'ip_address', 'user_agent', 'referer',
            'country', 'city', 'created_at'
        ]
        read_only_fields = ['created_at']


class DailyStatsSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques journalières"""

    website_name = serializers.CharField(source='website.name', read_only=True)

    class Meta:
        model = DailyStats
        fields = [
            'id', 'website', 'website_name', 'date',
            'contacts_count', 'projects_views', 'api_calls', 'unique_visitors',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AnalyticsStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques agrégées"""

    total_contacts = serializers.IntegerField()
    total_projects_views = serializers.IntegerField()
    total_api_calls = serializers.IntegerField()
    total_unique_visitors = serializers.IntegerField()

    # Stats par période
    period_stats = serializers.ListField(
        child=serializers.DictField()
    )

    # Top événements
    top_events = serializers.ListField(
        child=serializers.DictField()
    )
