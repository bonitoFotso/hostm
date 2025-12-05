from rest_framework import serializers
from .models import Webhook, WebhookLog
import secrets


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer pour les webhooks"""

    class Meta:
        model = Webhook
        fields = [
            'id', 'website', 'name', 'url', 'events', 'secret',
            'is_active', 'retry_on_failure', 'max_retries', 'custom_headers',
            'total_calls', 'successful_calls', 'failed_calls', 'last_triggered_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_calls', 'successful_calls', 'failed_calls', 'last_triggered_at',
            'created_at', 'updated_at'
        ]

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value

    def validate_events(self, value):
        """Valide que la liste d'événements n'est pas vide"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Vous devez spécifier au moins un événement.")

        # Valider que les événements sont valides
        valid_events = [choice[0] for choice in Webhook.EVENT_CHOICES]
        for event in value:
            if event not in valid_events:
                raise serializers.ValidationError(f"Événement invalide : {event}")

        return value

    def create(self, validated_data):
        """Génère automatiquement un secret si non fourni"""
        if not validated_data.get('secret'):
            validated_data['secret'] = secrets.token_urlsafe(32)
        return super().create(validated_data)


class WebhookLogSerializer(serializers.ModelSerializer):
    """Serializer pour les logs de webhook"""

    webhook_name = serializers.CharField(source='webhook.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WebhookLog
        fields = [
            'id', 'webhook', 'webhook_name', 'event_type',
            'status', 'status_display', 'payload',
            'response_status_code', 'response_body', 'error_message',
            'attempt_number', 'duration_ms',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WebhookTestSerializer(serializers.Serializer):
    """Serializer pour tester un webhook"""

    event_type = serializers.ChoiceField(
        choices=[choice[0] for choice in Webhook.EVENT_CHOICES]
    )
    test_payload = serializers.JSONField(
        required=False,
        help_text="Payload de test personnalisé (optionnel)"
    )
