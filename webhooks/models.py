from django.db import models
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class Webhook(models.Model):
    """Modèle pour configurer les webhooks"""

    EVENT_CHOICES = [
        ('contact.received', 'Contact reçu'),
        ('contact.read', 'Contact lu'),
        ('contact.replied', 'Contact répondu'),
        ('project.created', 'Projet créé'),
        ('project.updated', 'Projet mis à jour'),
        ('project.deleted', 'Projet supprimé'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='webhooks',
        verbose_name=_("Site web")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom du webhook")
    )
    url = models.URLField(
        verbose_name=_("URL de callback"),
        help_text=_("URL qui recevra les données du webhook")
    )
    events = models.JSONField(
        verbose_name=_("Événements à surveiller"),
        help_text=_("Liste des événements qui déclencheront ce webhook")
    )
    secret = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Secret"),
        help_text=_("Secret pour signer les requêtes webhook (HMAC)")
    )

    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif")
    )
    retry_on_failure = models.BooleanField(
        default=True,
        verbose_name=_("Réessayer en cas d'échec")
    )
    max_retries = models.IntegerField(
        default=3,
        verbose_name=_("Nombre maximum de tentatives")
    )

    # Headers personnalisés (optionnel)
    custom_headers = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Headers personnalisés"),
        help_text=_("Headers HTTP additionnels à envoyer")
    )

    # Statistiques
    total_calls = models.IntegerField(
        default=0,
        verbose_name=_("Total d'appels")
    )
    successful_calls = models.IntegerField(
        default=0,
        verbose_name=_("Appels réussis")
    )
    failed_calls = models.IntegerField(
        default=0,
        verbose_name=_("Appels échoués")
    )
    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Dernier déclenchement")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhooks'
        verbose_name = _("Webhook")
        verbose_name_plural = _("Webhooks")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.website.name} - {self.name}"

    def increment_success(self):
        """Incrémente le compteur de succès"""
        from django.utils import timezone
        self.total_calls += 1
        self.successful_calls += 1
        self.last_triggered_at = timezone.now()
        self.save(update_fields=['total_calls', 'successful_calls', 'last_triggered_at'])

    def increment_failure(self):
        """Incrémente le compteur d'échecs"""
        from django.utils import timezone
        self.total_calls += 1
        self.failed_calls += 1
        self.last_triggered_at = timezone.now()
        self.save(update_fields=['total_calls', 'failed_calls', 'last_triggered_at'])


class WebhookLog(models.Model):
    """Modèle pour logger les appels de webhooks"""

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('success', 'Succès'),
        ('failed', 'Échoué'),
        ('retrying', 'Nouvelle tentative'),
    ]

    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_("Webhook")
    )
    event_type = models.CharField(
        max_length=50,
        verbose_name=_("Type d'événement")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_("Statut")
    )

    # Payload envoyé
    payload = models.JSONField(
        verbose_name=_("Données envoyées")
    )

    # Réponse reçue
    response_status_code = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Code de statut HTTP")
    )
    response_body = models.TextField(
        blank=True,
        verbose_name=_("Corps de la réponse")
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_("Message d'erreur")
    )

    # Tentatives
    attempt_number = models.IntegerField(
        default=1,
        verbose_name=_("Numéro de tentative")
    )

    # Durée de l'appel
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Durée (ms)")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhook_logs'
        verbose_name = _("Log de webhook")
        verbose_name_plural = _("Logs de webhooks")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', 'status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.webhook.name} - {self.event_type} - {self.get_status_display()}"
