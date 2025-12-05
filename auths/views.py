from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'authentification JWT
    Retourne access token et refresh token avec les infos utilisateur
    """
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    create=extend_schema(
        summary="Inscription",
        description="Créer un nouveau compte utilisateur",
        tags=['Authentification']
    ),
    retrieve=extend_schema(
        summary="Mon profil",
        description="Récupérer les informations de mon profil",
        tags=['Profil']
    ),
    partial_update=extend_schema(
        summary="Mettre à jour mon profil",
        description="Modifier mes informations personnelles",
        tags=['Profil']
    ),
)
class AuthViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    ViewSet pour l'authentification et la gestion du profil utilisateur
    
    Endpoints:
    - POST /api/v1/auth/ : Inscription
    - GET /api/v1/auth/me/ : Mon profil
    - PATCH /api/v1/auth/me/ : Mettre à jour mon profil
    - POST /api/v1/auth/change-password/ : Changer mon mot de passe
    - POST /api/v1/auth/request-password-reset/ : Réinitialiser mon mot de passe
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        serializer_map = {
            'create': UserRegistrationSerializer,
            'retrieve': UserProfileSerializer,
            'update': UserUpdateSerializer,
            'partial_update': UserUpdateSerializer,
            'change_password': PasswordChangeSerializer,
            'request_password_reset': PasswordResetRequestSerializer,
            'me': UserProfileSerializer,
        }
        return serializer_map.get(self.action, UserProfileSerializer)

    def get_permissions(self):
        """Définit les permissions selon l'action"""
        if self.action in ['create', 'request_password_reset']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        """Retourne toujours l'utilisateur connecté pour les actions de profil"""
        if self.action in ['retrieve', 'update', 'partial_update', 'change_password', 'me']:
            return self.request.user
        return super().get_object()

    def create(self, request, *args, **kwargs):
        """
        Inscription d'un nouvel utilisateur
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Optionnel : Générer automatiquement les tokens JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response(
            {
                'message': 'Inscription réussie',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        summary="Mon profil",
        description="Récupérer les informations de l'utilisateur connecté",
        tags=['Profil']
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retourne les informations de l'utilisateur connecté
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Changer mon mot de passe",
        description="Modifier le mot de passe de l'utilisateur connecté",
        tags=['Profil']
    )
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Changer le mot de passe de l'utilisateur connecté
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': 'Mot de passe modifié avec succès'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Réinitialiser mon mot de passe",
        description="Envoyer un email pour réinitialiser le mot de passe",
        tags=['Authentification']
    )
    @action(detail=False, methods=['post'], url_path='request-password-reset')
    def request_password_reset(self, request):
        """
        Demander la réinitialisation du mot de passe par email
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Implémenter l'envoi d'email
        # Exemple avec Django email:
        # from django.core.mail import send_mail
        # send_mail(
        #     'Réinitialisation de mot de passe',
        #     'Voici votre lien de réinitialisation...',
        #     'from@example.com',
        #     [user.email],
        # )
        
        return Response(
            {
                'message': 'Si cet email existe, vous recevrez un lien de réinitialisation',
                'detail': 'Vérifiez votre boîte mail'
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Supprimer mon compte",
        description="Désactiver définitivement mon compte",
        tags=['Profil']
    )
    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        """
        Désactiver le compte de l'utilisateur connecté
        """
        user = request.user
        user.is_active = False
        user.save()
        
        return Response(
            {'message': 'Compte désactivé avec succès'},
            status=status.HTTP_204_NO_CONTENT
        )