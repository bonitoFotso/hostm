from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription
from .serializers import SubscriptionSerializer, SubscriptionUpgradeSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour gérer les abonnements
    GET /api/subscriptions/me/ - Récupérer mon abonnement
    POST /api/subscriptions/upgrade/ - Upgrade de plan
    POST /api/subscriptions/cancel/ - Annuler l'abonnement
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retourne uniquement l'abonnement de l'utilisateur connecté"""
        return Subscription.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Récupère l'abonnement de l'utilisateur connecté"""
        try:
            subscription = request.user.subscription
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'Aucun abonnement trouvé. Veuillez contacter le support.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def upgrade(self, request):
        """
        Upgrade le plan de l'utilisateur
        Nécessite un paiement pour les plans Pro et Agency
        """
        serializer = SubscriptionUpgradeSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            new_plan = serializer.validated_data['plan']
            billing_period = serializer.validated_data['billing_period']

            # Si le nouveau plan est gratuit, pas besoin de paiement
            if new_plan == 'free':
                subscription = request.user.subscription
                subscription.plan = new_plan
                subscription.billing_period = billing_period
                subscription.set_plan_limits()
                subscription.save()

                return Response({
                    'message': 'Plan modifié avec succès',
                    'subscription': SubscriptionSerializer(subscription).data
                })

            # Pour les plans payants, rediriger vers le processus de paiement
            return Response({
                'message': 'Paiement requis',
                'plan': new_plan,
                'billing_period': billing_period,
                'next_step': 'create_payment',
                'redirect_url': '/api/payments/create-order/'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """Annule l'abonnement de l'utilisateur"""
        from django.utils import timezone

        subscription = request.user.subscription

        if subscription.plan == 'free':
            return Response({
                'error': 'Impossible d\'annuler un plan gratuit'
            }, status=status.HTTP_400_BAD_REQUEST)

        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.save()

        return Response({
            'message': 'Abonnement annulé avec succès',
            'subscription': SubscriptionSerializer(subscription).data
        })

    @action(detail=False, methods=['get'])
    def plans(self, request):
        """Retourne la liste des plans disponibles"""
        from django.conf import settings

        plans = settings.HOSTMAIL_PLANS
        return Response(plans)
