from rest_framework import serializers
from .models import ContactFormField, ContactMessage


class ContactFormFieldSerializer(serializers.ModelSerializer):
    """Serializer pour les champs de formulaire de contact"""

    class Meta:
        model = ContactFormField
        fields = [
            'id', 'website', 'name', 'label', 'field_type',
            'placeholder', 'required', 'order', 'options',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages de contact"""

    website_name = serializers.CharField(source='website.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ip_address = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'website', 'website_name', 'form_data',
            'email', 'name', 'subject', 'message',
            'status', 'status_display', 'ip_address', 'user_agent',
            'notes', 'read_at', 'replied_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user_agent', 'read_at', 'replied_at',
            'created_at', 'updated_at'
        ]

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value


class ContactMessageSubmitSerializer(serializers.Serializer):
    """Serializer pour la soumission publique de messages de contact"""

    form_data = serializers.JSONField(
        help_text="Données du formulaire au format JSON"
    )

    def validate_form_data(self, value):
        """Valide que form_data est un dictionnaire"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("form_data doit être un objet JSON.")
        return value

    def create(self, validated_data):
        """Crée un message de contact avec extraction des champs standards"""
        website = self.context['website']
        request = self.context['request']

        form_data = validated_data['form_data']

        # Extraire les champs standards pour faciliter les recherches
        message = ContactMessage.objects.create(
            website=website,
            form_data=form_data,
            email=form_data.get('email', ''),
            name=form_data.get('name', '') or form_data.get('full_name', ''),
            subject=form_data.get('subject', ''),
            message=form_data.get('message', ''),
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        return message

    def get_client_ip(self, request):
        """Récupère l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactMessageUpdateStatusSerializer(serializers.Serializer):
    """Serializer pour mettre à jour le statut d'un message"""

    status = serializers.ChoiceField(
        choices=ContactMessage.STATUS_CHOICES
    )
    notes = serializers.CharField(required=False, allow_blank=True)
