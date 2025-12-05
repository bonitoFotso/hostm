"""
Middleware personnalisés pour HostMail
"""
from django.http import JsonResponse
from websites.models import Website


class APIKeyMiddleware:
    """
    Middleware pour valider l'API key sur les endpoints publics
    L'API key doit être fournie dans le header: X-API-Key
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si la requête est pour un endpoint public
        if request.path.startswith('/api/public/'):
            # Récupérer l'API key depuis les headers
            api_key = request.headers.get('X-API-Key') or request.headers.get('X-Api-Key')

            if not api_key:
                return JsonResponse({
                    'error': 'API key manquante',
                    'detail': 'Veuillez fournir une API key valide dans le header X-API-Key'
                }, status=401)

            # Valider l'API key
            try:
                website = Website.objects.select_related('user', 'user__subscription').get(
                    api_key=api_key,
                    is_active=True
                )

                # Vérifier que l'abonnement est actif
                if website.user.subscription.status != 'active':
                    return JsonResponse({
                        'error': 'Abonnement inactif',
                        'detail': 'Votre abonnement n\'est pas actif'
                    }, status=403)

                # Injecter le website dans la requête
                request.website = website

            except Website.DoesNotExist:
                return JsonResponse({
                    'error': 'API key invalide',
                    'detail': 'L\'API key fournie est invalide ou le site est désactivé'
                }, status=401)

        response = self.get_response(request)
        return response
