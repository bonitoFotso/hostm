from rest_framework import serializers
from .models import Subscription
from django.contrib.auth import get_user_model

User = get_user_model()


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Subscription"""

    user_email = serializers.EmailField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='get_plan_display', read_only=True)
    billing_period_name = serializers.CharField(source='get_billing_period_display', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)

    # Informations d'utilisation
    websites_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_email', 'plan', 'plan_name',
            'billing_period', 'billing_period_name', 'status', 'status_name',
            'websites_limit', 'contacts_per_month', 'projects_limit', 'storage_mb',
            'analytics', 'integrations', 'custom_domain', 'white_label', 'priority_support',
            'current_month_contacts', 'current_storage_mb',
            'websites_count', 'projects_count',
            'started_at', 'expires_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'websites_limit', 'contacts_per_month', 'projects_limit', 'storage_mb',
            'analytics', 'integrations', 'custom_domain', 'white_label', 'priority_support',
            'current_month_contacts', 'current_storage_mb',
            'started_at', 'created_at', 'updated_at'
        ]

    def get_websites_count(self, obj):
        """Retourne le nombre de sites web de l'utilisateur"""
        return obj.user.websites.count()

    def get_projects_count(self, obj):
        """Retourne le nombre total de projets de l'utilisateur"""
        return sum(website.projects.count() for website in obj.user.websites.all())


class SubscriptionUpgradeSerializer(serializers.Serializer):
    """Serializer pour l'upgrade de subscription"""

    plan = serializers.ChoiceField(choices=Subscription.PLAN_CHOICES)
    billing_period = serializers.ChoiceField(choices=Subscription.BILLING_PERIOD_CHOICES)

    def validate_plan(self, value):
        """Valide que le nouveau plan est différent de l'actuel"""
        request = self.context.get('request')
        if request and request.user.subscription.plan == value:
            raise serializers.ValidationError("Vous êtes déjà sur ce plan.")
        return value
