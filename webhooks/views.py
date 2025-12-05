from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsWebsiteOwner
from .models import Webhook, WebhookLog
from .serializers import (
    WebhookSerializer,
    WebhookLogSerializer,
    WebhookTestSerializer
)


class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les webhooks"""

    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les webhooks des sites web de l'utilisateur"""
        queryset = Webhook.objects.filter(website__user=self.request.user)

        # Filtres
        website_id = self.request.query_params.get('website')
        is_active = self.request.query_params.get('is_active')

        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset.select_related('website')

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Teste un webhook en envoyant une requête de test"""
        webhook = self.get_object()
        serializer = WebhookTestSerializer(data=request.data)

        if serializer.is_valid():
            event_type = serializer.validated_data['event_type']
            test_payload = serializer.validated_data.get('test_payload', {
                'event': event_type,
                'test': True,
                'timestamp': '2024-01-01T00:00:00Z',
                'data': {}
            })

            # TODO: Implémenter l'envoi du webhook test
            # from webhooks.utils import send_webhook
            # result = send_webhook(webhook, event_type, test_payload)

            return Response({
                'message': 'Webhook de test envoyé',
                'webhook': webhook.name,
                'event_type': event_type,
                'payload': test_payload,
                'note': 'Implémentation réelle à venir'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Récupère les logs d'un webhook"""
        webhook = self.get_object()
        logs = webhook.logs.all().order_by('-created_at')[:50]
        serializer = WebhookLogSerializer(logs, many=True)

        return Response({
            'webhook': webhook.name,
            'total_calls': webhook.total_calls,
            'successful_calls': webhook.successful_calls,
            'failed_calls': webhook.failed_calls,
            'logs': serializer.data
        })


class WebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les logs de webhooks (lecture seule)"""

    serializer_class = WebhookLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retourne les logs des webhooks de l'utilisateur"""
        queryset = WebhookLog.objects.filter(webhook__website__user=self.request.user)

        # Filtres
        webhook_id = self.request.query_params.get('webhook')
        status_filter = self.request.query_params.get('status')

        if webhook_id:
            queryset = queryset.filter(webhook_id=webhook_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('webhook').order_by('-created_at')
