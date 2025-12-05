from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from subscriptions.models import Subscription


class Payment(models.Model):
    """Modèle pour suivre les paiements"""

    PAYMENT_METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),  # Pour plus tard
        ('manual', 'Manuel'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
        ('cancelled', 'Annulé'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Utilisateur")
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_("Abonnement")
    )

    # Détails du paiement
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Montant")
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("Devise")
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='paypal',
        verbose_name=_("Méthode de paiement")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Statut")
    )

    # Identifiants PayPal
    paypal_order_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("ID de commande PayPal")
    )
    paypal_capture_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("ID de capture PayPal")
    )
    paypal_payer_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("ID du payeur PayPal")
    )
    paypal_payer_email = models.EmailField(
        blank=True,
        verbose_name=_("Email du payeur PayPal")
    )

    # Métadonnées
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Métadonnées"),
        help_text=_("Données additionnelles du paiement")
    )

    # Dates
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Payé le")
    )
    refunded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Remboursé le")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = _("Paiement")
        verbose_name_plural = _("Paiements")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['paypal_order_id']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.get_status_display()}"

    def mark_as_completed(self):
        """Marque le paiement comme complété"""
        from django.utils import timezone
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])

    def mark_as_failed(self):
        """Marque le paiement comme échoué"""
        self.status = 'failed'
        self.save(update_fields=['status'])

    def mark_as_refunded(self):
        """Marque le paiement comme remboursé"""
        from django.utils import timezone
        self.status = 'refunded'
        self.refunded_at = timezone.now()
        self.save(update_fields=['status', 'refunded_at'])


class Invoice(models.Model):
    """Modèle pour les factures"""

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name=_("Utilisateur")
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoice',
        verbose_name=_("Paiement")
    )

    # Numérotation
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Numéro de facture")
    )

    # Détails
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Montant")
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name=_("Devise")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Statut")
    )

    # Ligne items (JSON)
    items = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Lignes de facturation"),
        help_text=_("Liste des items de la facture")
    )

    # Dates
    issue_date = models.DateField(
        verbose_name=_("Date d'émission")
    )
    due_date = models.DateField(
        verbose_name=_("Date d'échéance")
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de paiement")
    )

    # Fichier PDF
    pdf_file = models.FileField(
        upload_to='invoices/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Fichier PDF")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        verbose_name = _("Facture")
        verbose_name_plural = _("Factures")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['invoice_number']),
        ]

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de facture"""
        if not self.invoice_number:
            from django.utils import timezone
            now = timezone.now()
            count = Invoice.objects.filter(
                created_at__year=now.year,
                created_at__month=now.month
            ).count() + 1
            self.invoice_number = f"INV-{now.year}{now.month:02d}-{count:04d}"
        super().save(*args, **kwargs)

    def mark_as_paid(self):
        """Marque la facture comme payée"""
        from django.utils import timezone
        self.status = 'paid'
        self.paid_date = timezone.now().date()
        self.save(update_fields=['status', 'paid_date'])
