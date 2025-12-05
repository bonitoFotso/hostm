from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import AuthViewSet, CustomTokenObtainPairView

app_name = 'auths'

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')

urlpatterns = [
    # JWT Authentication
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Auth & Profile endpoints
    path('', include(router.urls)),
]

"""Endpoints disponibles:
POST   /api/v1/auth/                          → Inscription
POST   /api/v1/auth/login/                    → Connexion (obtenir tokens)
POST   /api/v1/auth/token/refresh/            → Rafraîchir le token
POST   /api/v1/auth/token/verify/             → Vérifier le token

GET    /api/v1/auth/me/                       → Mon profil
PATCH  /api/v1/auth/me/                       → Mettre à jour mon profil
POST   /api/v1/auth/change-password/          → Changer mon mot de passe
POST   /api/v1/auth/request-password-reset/   → Réinitialiser mot de passe
DELETE /api/v1/auth/delete-account/           → Supprimer mon compte

"""