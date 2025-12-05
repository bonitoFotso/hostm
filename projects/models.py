from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from websites.models import Website


class Category(models.Model):
    """Modèle pour les catégories de projets"""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='project_categories',
        verbose_name=_("Site web")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom")
    )
    slug = models.SlugField(
        max_length=100,
        blank=True,
        verbose_name=_("Slug")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Ordre")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_categories'
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ['order', 'name']
        unique_together = ['website', 'slug']

    def __str__(self):
        return f"{self.website.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Modèle pour les tags de projets"""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='project_tags',
        verbose_name=_("Site web")
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Nom")
    )
    slug = models.SlugField(
        max_length=50,
        blank=True,
        verbose_name=_("Slug")
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name=_("Couleur"),
        help_text=_("Code hexadécimal (ex: #3B82F6)")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_tags'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']
        unique_together = ['website', 'slug']

    def __str__(self):
        return f"{self.website.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """Modèle pour les projets"""

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_("Site web")
    )

    # Champs standards
    title = models.CharField(
        max_length=255,
        verbose_name=_("Titre")
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        verbose_name=_("Slug")
    )
    description = models.TextField(
        verbose_name=_("Description")
    )
    content = models.TextField(
        blank=True,
        verbose_name=_("Contenu détaillé")
    )

    # Images
    thumbnail = models.ImageField(
        upload_to='projects/thumbnails/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Image miniature")
    )
    featured_image = models.ImageField(
        upload_to='projects/images/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_("Image principale")
    )

    # Liens
    demo_url = models.URLField(
        blank=True,
        verbose_name=_("URL de démo")
    )
    github_url = models.URLField(
        blank=True,
        verbose_name=_("URL GitHub")
    )
    external_url = models.URLField(
        blank=True,
        verbose_name=_("URL externe")
    )

    # Classification
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_("Catégorie")
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='projects',
        verbose_name=_("Tags")
    )

    # Technologies utilisées (liste JSON)
    technologies = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Technologies"),
        help_text=_("Ex: ['Python', 'Django', 'React']")
    )

    # Champs personnalisés (données additionnelles en JSON)
    custom_fields = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Champs personnalisés")
    )

    # Métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_("Statut")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Projet vedette")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Ordre d'affichage")
    )
    views_count = models.IntegerField(
        default=0,
        verbose_name=_("Nombre de vues")
    )

    # Dates
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de début")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin")
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Publié le")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ['-order', '-created_at']
        unique_together = ['website', 'slug']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['is_featured', '-order']),
        ]

    def __str__(self):
        return f"{self.website.name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-publish
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def increment_views(self):
        """Incrémente le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProjectImage(models.Model):
    """Modèle pour les images additionnelles d'un projet"""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_("Projet")
    )
    image = models.ImageField(
        upload_to='projects/gallery/%Y/%m/',
        verbose_name=_("Image")
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Légende")
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_("Ordre")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_images'
        verbose_name = _("Image de projet")
        verbose_name_plural = _("Images de projet")
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"
