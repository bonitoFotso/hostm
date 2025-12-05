"""
Signals pour la gestion automatique des abonnements
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """
    Crée automatiquement un abonnement gratuit lors de l'inscription d'un utilisateur
    """
    if created:
        Subscription.objects.create(
            user=instance,
            plan='free',
            billing_period='monthly',
            status='active'
        )


@receiver(post_save, sender=User)
def save_user_subscription(sender, instance, **kwargs):
    """
    Sauvegarde l'abonnement si l'utilisateur est mis à jour
    """
    if hasattr(instance, 'subscription'):
        instance.subscription.save()
