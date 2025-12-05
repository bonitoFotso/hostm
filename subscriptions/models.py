from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Subscription(models.Model):
    """Modèle pour gérer les abonnements des utilisateurs"""

    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
        ('agency', 'Agency'),
    ]

    BILLING_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_("Utilisateur")
    )
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='free',
        verbose_name=_("Plan")
    )
    billing_period = models.CharField(
        max_length=20,
        choices=BILLING_PERIOD_CHOICES,
        default='monthly',
        verbose_name=_("Période de facturation")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_("Statut")
    )

    # Limites du plan
    websites_limit = models.IntegerField(
        default=1,
        verbose_name=_("Limite de sites web"),
        help_text=_("-1 pour illimité")
    )
    contacts_per_month = models.IntegerField(
        default=50,
        verbose_name=_("Messages de contact par mois")
    )
    projects_limit = models.IntegerField(
        default=5,
        verbose_name=_("Limite de projets"),
        help_text=_("-1 pour illimité")
    )
    storage_mb = models.IntegerField(
        default=100,
        verbose_name=_("Stockage en MB")
    )

    # Fonctionnalités
    analytics = models.BooleanField(
        default=False,
        verbose_name=_("Analytics activé")
    )
    integrations = models.BooleanField(
        default=False,
        verbose_name=_("Intégrations activées")
    )
    custom_domain = models.BooleanField(
        default=False,
        verbose_name=_("Domaine personnalisé")
    )
    white_label = models.BooleanField(
        default=False,
        verbose_name=_("White label")
    )
    priority_support = models.BooleanField(
        default=False,
        verbose_name=_("Support prioritaire")
    )

    # Compteurs d'utilisation du mois en cours
    current_month_contacts = models.IntegerField(
        default=0,
        verbose_name=_("Messages du mois")
    )
    current_storage_mb = models.FloatField(
        default=0,
        verbose_name=_("Stockage utilisé (MB)")
    )

    # Dates
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de début")
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date d'expiration")
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date d'annulation")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = _("Abonnement")
        verbose_name_plural = _("Abonnements")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_plan_display()}"

    def save(self, *args, **kwargs):
        """Définir les limites selon le plan sélectionné"""
        if not self.pk:  # Nouvelle création
            self.set_plan_limits()
        super().save(*args, **kwargs)

    def set_plan_limits(self):
        """Configure les limites selon le plan"""
        plans = {
            'free': {
                'websites_limit': 1,
                'contacts_per_month': 50,
                'projects_limit': 5,
                'storage_mb': 100,
                'analytics': False,
                'integrations': False,
                'custom_domain': False,
                'white_label': False,
                'priority_support': False,
            },
            'pro': {
                'websites_limit': 3,
                'contacts_per_month': 500,
                'projects_limit': -1,
                'storage_mb': 1000,
                'analytics': True,
                'integrations': True,
                'custom_domain': False,
                'white_label': False,
                'priority_support': False,
            },
            'agency': {
                'websites_limit': -1,
                'contacts_per_month': 5000,
                'projects_limit': -1,
                'storage_mb': 10000,
                'analytics': True,
                'integrations': True,
                'custom_domain': True,
                'white_label': True,
                'priority_support': True,
            },
        }

        plan_config = plans.get(self.plan, plans['free'])
        for key, value in plan_config.items():
            setattr(self, key, value)

    def can_add_website(self):
        """Vérifie si l'utilisateur peut ajouter un site web"""
        if self.websites_limit == -1:
            return True
        return self.user.websites.count() < self.websites_limit

    def can_add_project(self, website):
        """Vérifie si l'utilisateur peut ajouter un projet"""
        if self.projects_limit == -1:
            return True
        return website.projects.count() < self.projects_limit

    def can_receive_contact(self):
        """Vérifie si l'utilisateur peut recevoir un nouveau contact"""
        return self.current_month_contacts < self.contacts_per_month

    def can_upload_file(self, file_size_mb):
        """Vérifie si l'utilisateur peut uploader un fichier"""
        return (self.current_storage_mb + file_size_mb) <= self.storage_mb

    def increment_contact_count(self):
        """Incrémente le compteur de contacts du mois"""
        self.current_month_contacts += 1
        self.save(update_fields=['current_month_contacts'])

    def reset_monthly_counters(self):
        """Réinitialise les compteurs mensuels"""
        self.current_month_contacts = 0
        self.save(update_fields=['current_month_contacts'])
