from rest_framework import serializers
from .models import Website


class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle Website"""

    allowed_origins_list = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False,
        help_text="Liste des origines autorisées pour CORS"
    )

    class Meta:
        model = Website
        fields = [
            'id', 'user', 'name', 'domain', 'description',
            'api_key', 'is_active', 'allowed_origins', 'allowed_origins_list',
            'total_contacts', 'total_projects',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'api_key', 'total_contacts', 'total_projects', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Validation personnalisée"""
        # Convertir la liste d'origines en texte multi-lignes
        if 'allowed_origins_list' in attrs:
            origins_list = attrs.pop('allowed_origins_list')
            attrs['allowed_origins'] = '\n'.join(origins_list)

        # Vérifier la limite de sites web
        request = self.context.get('request')
        if request and not self.instance:  # Création uniquement
            subscription = request.user.subscription
            if not subscription.can_add_website():
                raise serializers.ValidationError(
                    f"Limite de sites web atteinte ({subscription.websites_limit}). "
                    f"Passez à un plan supérieur pour créer plus de sites."
                )

        return attrs

    def to_representation(self, instance):
        """Ajouter la liste des origines dans la réponse"""
        data = super().to_representation(instance)
        data['allowed_origins_list'] = instance.get_allowed_origins_list()
        return data


class WebsitePublicSerializer(serializers.ModelSerializer):
    """Serializer public pour les détails basiques d'un site web"""

    class Meta:
        model = Website
        fields = ['id', 'name', 'domain', 'is_active']


class WebsiteRegenerateKeySerializer(serializers.Serializer):
    """Serializer pour régénérer l'API key"""

    confirm = serializers.BooleanField(
        required=True,
        help_text="Confirmation de régénération de l'API key"
    )

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("Vous devez confirmer la régénération de l'API key.")
        return value
