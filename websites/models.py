import secrets
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def generate_api_key():
    """Génère une clé API unique"""
    return f"hm_{secrets.token_urlsafe(32)}"


class Website(models.Model):
    """Modèle pour gérer les sites web des utilisateurs"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='websites',
        verbose_name=_("Utilisateur")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom du site")
    )
    domain = models.CharField(
        max_length=255,
        verbose_name=_("Domaine"),
        help_text=_("Ex: example.com")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )

    # API Key unique pour chaque site
    api_key = models.CharField(
        max_length=100,
        unique=True,
        default=generate_api_key,
        editable=False,
        verbose_name=_("Clé API")
    )

    # Configuration
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif")
    )
    allowed_origins = models.TextField(
        blank=True,
        verbose_name=_("Origines autorisées (CORS)"),
        help_text=_("Une origine par ligne. Ex: https://example.com")
    )

    # Compteurs
    total_contacts = models.IntegerField(
        default=0,
        verbose_name=_("Total de contacts reçus")
    )
    total_projects = models.IntegerField(
        default=0,
        verbose_name=_("Total de projets")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'websites'
        verbose_name = _("Site web")
        verbose_name_plural = _("Sites web")
        ordering = ['-created_at']
        unique_together = ['user', 'domain']

    def __str__(self):
        return f"{self.name} ({self.domain})"

    def regenerate_api_key(self):
        """Régénère une nouvelle clé API"""
        self.api_key = generate_api_key()
        self.save(update_fields=['api_key'])
        return self.api_key

    def get_allowed_origins_list(self):
        """Retourne la liste des origines autorisées"""
        if not self.allowed_origins:
            return []
        return [origin.strip() for origin in self.allowed_origins.split('\n') if origin.strip()]

    def is_origin_allowed(self, origin):
        """Vérifie si une origine est autorisée"""
        if not self.allowed_origins:
            return True  # Si aucune restriction, tout est autorisé
        allowed = self.get_allowed_origins_list()
        return origin in allowed
