from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission personnalisée pour vérifier que l'utilisateur
    est le propriétaire de l'objet
    """

    def has_object_permission(self, request, view, obj):
        # Vérifier si l'objet a un attribut 'user'
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Pour les objets liés à un website
        if hasattr(obj, 'website'):
            return obj.website.user == request.user

        return False


class IsWebsiteOwner(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur possède le site web
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'website'):
            return obj.website.user == request.user
        return obj.user == request.user


class HasActiveSubscription(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur a un abonnement actif
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            subscription = request.user.subscription
            return subscription.status == 'active'
        except:
            return False


class HasAnalyticsFeature(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur a accès aux analytics
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            subscription = request.user.subscription
            return subscription.analytics and subscription.status == 'active'
        except:
            return False
