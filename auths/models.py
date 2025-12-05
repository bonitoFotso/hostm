from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampedModel(models.Model):
    """
    Modèle abstrait pour ajouter des champs de timestamp
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Modifié le"))

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserManager(BaseUserManager):
    """
    Gestionnaire personnalisé pour le modèle User
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimestampedModel):
    """
    Modèle utilisateur personnalisé qui utilise l'email comme identifiant
    """
    email = models.EmailField(
        _('adresse email'),
        unique=True,
        error_messages={
            'unique': _("Un utilisateur avec cette adresse email existe déjà."),
        }
    )
    
    # Rendre username optionnel
    username = models.CharField(
        _('nom d\'utilisateur'),
        max_length=150,
        blank=True,
        null=True,
        unique=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Pas besoin de username obligatoire
    
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Générer un username automatiquement si non fourni
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username or self.email

    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.first_name or self.username or self.email.split('@')[0]