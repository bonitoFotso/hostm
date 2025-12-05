from django.db import models
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class ContactFormField(models.Model):
    """Modèle pour définir les champs personnalisés d'un formulaire de contact"""

    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('tel', 'Téléphone'),
        ('textarea', 'Textarea'),
        ('number', 'Number'),
        ('url', 'URL'),
        ('date', 'Date'),
        ('select', 'Select'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='contact_form_fields',
        verbose_name=_("Site web")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom du champ"),
        help_text=_("Nom technique du champ (ex: full_name)")
    )
    label = models.CharField(
        max_length=255,
        verbose_name=_("Label"),
        help_text=_("Label affiché à l'utilisateur")
    )
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPE_CHOICES,
        default='text',
        verbose_name=_("Type de champ")
    )
    placeholder = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Placeholder")
    )
    required = models.BooleanField(
        default=False,
        verbose_name=_("Requis")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Ordre d'affichage")
    )
    options = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Options"),
        help_text=_("Pour select/radio (ex: ['Option 1', 'Option 2'])")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_form_fields'
        verbose_name = _("Champ de formulaire")
        verbose_name_plural = _("Champs de formulaire")
        ordering = ['order', 'created_at']
        unique_together = ['website', 'name']

    def __str__(self):
        return f"{self.website.name} - {self.label}"


class ContactMessage(models.Model):
    """Modèle pour stocker les messages de contact reçus"""

    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('read', 'Lu'),
        ('replied', 'Répondu'),
        ('archived', 'Archivé'),
        ('spam', 'Spam'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='contact_messages',
        verbose_name=_("Site web")
    )

    # Données du formulaire (stockées en JSON pour flexibilité)
    form_data = models.JSONField(
        verbose_name=_("Données du formulaire")
    )

    # Champs standards (extraits du form_data pour faciliter les recherches)
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email")
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Nom")
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Sujet")
    )
    message = models.TextField(
        blank=True,
        verbose_name=_("Message")
    )

    # Métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name=_("Statut")
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("Adresse IP")
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User Agent")
    )

    # Notes internes
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes internes")
    )

    # Dates
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Lu le")
    )
    replied_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Répondu le")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_messages'
        verbose_name = _("Message de contact")
        verbose_name_plural = _("Messages de contact")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.website.name} - {self.name or self.email} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def mark_as_read(self):
        """Marque le message comme lu"""
        from django.utils import timezone
        if self.status == 'new':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save(update_fields=['status', 'read_at'])

    def mark_as_replied(self):
        """Marque le message comme répondu"""
        from django.utils import timezone
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_at'])

    def mark_as_spam(self):
        """Marque le message comme spam"""
        self.status = 'spam'
        self.save(update_fields=['status'])
