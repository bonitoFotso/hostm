from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.conf import settings
from core.permissions import IsWebsiteOwner
from websites.models import Website
from .models import ContactFormField, ContactMessage
from .serializers import (
    ContactFormFieldSerializer,
    ContactMessageSerializer,
    ContactMessageSubmitSerializer,
    ContactMessageUpdateStatusSerializer
)


class ContactFormFieldViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les champs de formulaire de contact"""

    serializer_class = ContactFormFieldSerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les champs des sites web de l'utilisateur"""
        return ContactFormField.objects.filter(website__user=self.request.user)

    def perform_create(self, serializer):
        """Vérifie la propriété du site web lors de la création"""
        website = serializer.validated_data['website']
        if website.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Ce site web ne vous appartient pas.")
        serializer.save()


class ContactMessageViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les messages de contact"""

    serializer_class = ContactMessageSerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les messages des sites web de l'utilisateur"""
        queryset = ContactMessage.objects.filter(website__user=self.request.user)

        # Filtres optionnels
        website_id = self.request.query_params.get('website')
        status_filter = self.request.query_params.get('status')

        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('website').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Met à jour le statut d'un message"""
        message = self.get_object()
        serializer = ContactMessageUpdateStatusSerializer(data=request.data)

        if serializer.is_valid():
            message.status = serializer.validated_data['status']
            if 'notes' in serializer.validated_data:
                message.notes = serializer.validated_data['notes']

            # Mettre à jour les dates selon le statut
            if message.status == 'read' and not message.read_at:
                message.mark_as_read()
            elif message.status == 'replied':
                message.mark_as_replied()
            else:
                message.save()

            return Response({
                'message': 'Statut mis à jour avec succès',
                'data': ContactMessageSerializer(message).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_as_spam(self, request, pk=None):
        """Marque un message comme spam"""
        message = self.get_object()
        message.mark_as_spam()

        return Response({
            'message': 'Message marqué comme spam',
            'data': ContactMessageSerializer(message).data
        })


@method_decorator(ratelimit(key='ip', rate=settings.RATELIMIT_CONTACT_SUBMIT, method='POST'), name='post')
class ContactSubmitPublicView(views.APIView):
    """
    Vue publique pour soumettre un message de contact
    Nécessite une API key valide dans les headers
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Soumet un message de contact"""
        # L'API key est validée par le middleware
        website = request.website  # Injecté par le middleware

        # Vérifier la limite de contacts
        subscription = website.user.subscription
        if not subscription.can_receive_contact():
            return Response({
                'error': 'Limite de contacts mensuelle atteinte',
                'limit': subscription.contacts_per_month,
                'current': subscription.current_month_contacts
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Valider et créer le message
        serializer = ContactMessageSubmitSerializer(
            data=request.data,
            context={'website': website, 'request': request}
        )

        if serializer.is_valid():
            message = serializer.save()

            # Incrémenter le compteur
            subscription.increment_contact_count()
            website.total_contacts += 1
            website.save(update_fields=['total_contacts'])

            # TODO: Envoyer email de notification
            # TODO: Trigger webhooks

            return Response({
                'success': True,
                'message': 'Message envoyé avec succès',
                'id': message.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
