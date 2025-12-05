from rest_framework import serializers
from .models import Payment, Invoice
from subscriptions.models import Subscription


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer pour les paiements"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'subscription', 'amount', 'currency',
            'payment_method', 'payment_method_display',
            'status', 'status_display',
            'paypal_order_id', 'paypal_capture_id', 'paypal_payer_id', 'paypal_payer_email',
            'metadata', 'paid_at', 'refunded_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'status', 'paypal_capture_id', 'paypal_payer_id', 'paypal_payer_email',
            'paid_at', 'refunded_at', 'created_at', 'updated_at'
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer pour les factures"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_id = serializers.IntegerField(source='payment.id', read_only=True, allow_null=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'user', 'payment', 'payment_id', 'invoice_number',
            'amount', 'currency', 'description',
            'status', 'status_display', 'items',
            'issue_date', 'due_date', 'paid_date', 'pdf_file',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'invoice_number', 'paid_date', 'pdf_file',
            'created_at', 'updated_at'
        ]


class PayPalOrderCreateSerializer(serializers.Serializer):
    """Serializer pour créer une commande PayPal"""

    plan = serializers.ChoiceField(choices=['pro', 'agency'])
    billing_period = serializers.ChoiceField(choices=['monthly', 'yearly'])

    def validate_plan(self, value):
        """Valide que le plan n'est pas gratuit"""
        if value == 'free':
            raise serializers.ValidationError("Le plan gratuit ne nécessite pas de paiement.")
        return value


class PayPalOrderCaptureSerializer(serializers.Serializer):
    """Serializer pour capturer une commande PayPal"""

    order_id = serializers.CharField(
        max_length=255,
        help_text="ID de la commande PayPal"
    )


class SubscriptionPaymentSerializer(serializers.Serializer):
    """Serializer pour le paiement d'un abonnement"""

    plan = serializers.ChoiceField(choices=['pro', 'agency'])
    billing_period = serializers.ChoiceField(choices=['monthly', 'yearly'])
    payment_method = serializers.ChoiceField(choices=['paypal'], default='paypal')

    def get_amount(self):
        """Calcule le montant selon le plan et la période"""
        from django.conf import settings

        plan = self.validated_data['plan']
        billing_period = self.validated_data['billing_period']

        plans = settings.HOSTMAIL_PLANS
        plan_config = plans.get(plan, {})

        if billing_period == 'monthly':
            return plan_config.get('price_monthly', 0)
        else:
            return plan_config.get('price_yearly', 0)
