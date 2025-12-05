from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwner
from .models import Website
from .serializers import (
    WebsiteSerializer,
    WebsitePublicSerializer,
    WebsiteRegenerateKeySerializer
)


class WebsiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les sites web
    """

    serializer_class = WebsiteSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Retourne uniquement les sites web de l'utilisateur connecté"""
        return Website.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Assigne automatiquement l'utilisateur connecté au site web"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def regenerate_key(self, request, pk=None):
        """Régénère l'API key d'un site web"""
        website = self.get_object()

        serializer = WebsiteRegenerateKeySerializer(data=request.data)
        if serializer.is_valid():
            new_key = website.regenerate_api_key()

            return Response({
                'message': 'API key régénérée avec succès',
                'api_key': new_key,
                'warning': 'Pensez à mettre à jour votre clé sur tous vos sites'
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Récupère les statistiques d'un site web"""
        website = self.get_object()

        return Response({
            'total_contacts': website.total_contacts,
            'total_projects': website.total_projects,
            'contacts_this_month': website.contact_messages.filter(
                created_at__month=request.query_params.get('month'),
                created_at__year=request.query_params.get('year')
            ).count() if request.query_params.get('month') else 0,
        })
