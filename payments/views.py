from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwner
from .models import Payment, Invoice
from .serializers import (
    PaymentSerializer,
    InvoiceSerializer,
    PayPalOrderCreateSerializer,
    PayPalOrderCaptureSerializer
)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les paiements (lecture seule)"""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Retourne les paiements de l'utilisateur"""
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les factures (lecture seule)"""

    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Retourne les factures de l'utilisateur"""
        return Invoice.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharge le PDF d'une facture"""
        invoice = self.get_object()

        if not invoice.pdf_file:
            return Response({
                'error': 'PDF non disponible pour cette facture'
            }, status=status.HTTP_404_NOT_FOUND)

        # TODO: Retourner le fichier PDF
        return Response({
            'message': 'Téléchargement de facture',
            'invoice_number': invoice.invoice_number,
            'pdf_url': invoice.pdf_file.url if invoice.pdf_file else None
        })


class PayPalCreateOrderView(views.APIView):
    """Vue pour créer une commande PayPal"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Crée une commande PayPal pour un abonnement"""
        serializer = PayPalOrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            plan = serializer.validated_data['plan']
            billing_period = serializer.validated_data['billing_period']

            # Calculer le montant
            from django.conf import settings
            plans = settings.HOSTMAIL_PLANS
            plan_config = plans.get(plan, {})

            if billing_period == 'monthly':
                amount = plan_config.get('price_monthly', 0)
            else:
                amount = plan_config.get('price_yearly', 0)

            # TODO: Créer la commande PayPal via l'API
            # import paypalrestsdk
            # paypalrestsdk.configure({
            #     "mode": settings.PAYPAL_MODE,
            #     "client_id": settings.PAYPAL_CLIENT_ID,
            #     "client_secret": settings.PAYPAL_CLIENT_SECRET
            # })
            #
            # payment = paypalrestsdk.Payment({
            #     "intent": "sale",
            #     "payer": {"payment_method": "paypal"},
            #     "redirect_urls": {
            #         "return_url": "http://localhost:8000/api/payments/execute",
            #         "cancel_url": "http://localhost:8000/api/payments/cancel"
            #     },
            #     "transactions": [{
            #         "amount": {"total": str(amount), "currency": "USD"},
            #         "description": f"HostMail - Plan {plan.title()} ({billing_period})"
            #     }]
            # })
            #
            # if payment.create():
            #     order_id = payment.id
            #     approve_url = next(link.href for link in payment.links if link.rel == "approval_url")
            # else:
            #     return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

            # Créer le paiement en base
            payment_obj = Payment.objects.create(
                user=request.user,
                subscription=request.user.subscription,
                amount=amount,
                currency='USD',
                payment_method='paypal',
                status='pending',
                # paypal_order_id=order_id  # À décommenter avec l'API PayPal
            )

            return Response({
                'message': 'Commande créée (mode simulation)',
                'payment_id': payment_obj.id,
                'amount': amount,
                'currency': 'USD',
                'plan': plan,
                'billing_period': billing_period,
                # 'approve_url': approve_url,  # À décommenter avec l'API PayPal
                'note': 'Intégration PayPal complète à implémenter'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayPalCaptureOrderView(views.APIView):
    """Vue pour capturer une commande PayPal"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Capture une commande PayPal après approbation de l'utilisateur"""
        serializer = PayPalOrderCaptureSerializer(data=request.data)

        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']

            # TODO: Capturer le paiement PayPal
            # import paypalrestsdk
            # payment = paypalrestsdk.Payment.find(order_id)
            #
            # if payment.execute({"payer_id": request.data.get('payer_id')}):
            #     # Paiement réussi
            #     pass
            # else:
            #     return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

            # Mettre à jour le paiement
            try:
                payment = Payment.objects.get(paypal_order_id=order_id, user=request.user)
                payment.mark_as_completed()

                # Upgrade l'abonnement
                subscription = request.user.subscription
                # TODO: Mettre à jour le plan et les limites

                return Response({
                    'message': 'Paiement capturé avec succès',
                    'payment_id': payment.id,
                    'status': 'completed'
                })
            except Payment.DoesNotExist:
                return Response({
                    'error': 'Paiement introuvable'
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
