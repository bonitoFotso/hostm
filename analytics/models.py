from django.db import models
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class AnalyticsEvent(models.Model):
    """Modèle pour suivre les événements analytics"""

    EVENT_TYPE_CHOICES = [
        ('contact_received', 'Contact reçu'),
        ('contact_read', 'Contact lu'),
        ('contact_replied', 'Contact répondu'),
        ('project_viewed', 'Projet consulté'),
        ('project_created', 'Projet créé'),
        ('project_updated', 'Projet mis à jour'),
        ('api_call', 'Appel API'),
        ('form_submission', 'Soumission de formulaire'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='analytics_events',
        verbose_name=_("Site web")
    )
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        verbose_name=_("Type d'événement")
    )

    # Métadonnées de l'événement
    metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Métadonnées"),
        help_text=_("Données additionnelles de l'événement")
    )

    # Informations de requête
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("Adresse IP")
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User Agent")
    )
    referer = models.URLField(
        blank=True,
        verbose_name=_("Referer")
    )

    # Géolocalisation (optionnel)
    country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name=_("Pays (code ISO)")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Ville")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_events'
        verbose_name = _("Événement Analytics")
        verbose_name_plural = _("Événements Analytics")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['website', 'event_type', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.website.name} - {self.get_event_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class DailyStats(models.Model):
    """Modèle pour les statistiques journalières agrégées"""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='daily_stats',
        verbose_name=_("Site web")
    )
    date = models.DateField(
        verbose_name=_("Date")
    )

    # Compteurs
    contacts_count = models.IntegerField(
        default=0,
        verbose_name=_("Nombre de contacts")
    )
    projects_views = models.IntegerField(
        default=0,
        verbose_name=_("Vues de projets")
    )
    api_calls = models.IntegerField(
        default=0,
        verbose_name=_("Appels API")
    )
    unique_visitors = models.IntegerField(
        default=0,
        verbose_name=_("Visiteurs uniques")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_stats'
        verbose_name = _("Statistiques journalières")
        verbose_name_plural = _("Statistiques journalières")
        ordering = ['-date']
        unique_together = ['website', 'date']

    def __str__(self):
        return f"{self.website.name} - {self.date}"
