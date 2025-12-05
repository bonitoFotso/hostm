from rest_framework import serializers
from .models import Category, Tag, Project, ProjectImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de projets"""

    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'website', 'name', 'slug', 'description', 'order',
            'projects_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_projects_count(self, obj):
        return obj.projects.filter(status='published').count()

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value


class TagSerializer(serializers.ModelSerializer):
    """Serializer pour les tags de projets"""

    projects_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            'id', 'website', 'name', 'slug', 'color',
            'projects_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']

    def get_projects_count(self, obj):
        return obj.projects.filter(status='published').count()

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de projet"""

    class Meta:
        model = ProjectImage
        fields = ['id', 'project', 'image', 'caption', 'order', 'created_at']
        read_only_fields = ['created_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer complet pour les projets"""

    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_data = TagSerializer(source='tags', many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Pour l'écriture
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Project
        fields = [
            'id', 'website', 'title', 'slug', 'description', 'content',
            'thumbnail', 'featured_image', 'demo_url', 'github_url', 'external_url',
            'category', 'category_name', 'tags', 'tags_data', 'tag_ids',
            'technologies', 'custom_fields',
            'status', 'status_display', 'is_featured', 'order', 'views_count',
            'start_date', 'end_date', 'published_at',
            'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'views_count', 'published_at', 'created_at', 'updated_at'
        ]

    def validate_website(self, value):
        """Vérifie que l'utilisateur possède ce site web"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("Ce site web ne vous appartient pas.")
        return value

    def validate_category(self, value):
        """Vérifie que la catégorie appartient au même site web"""
        website = self.initial_data.get('website')
        if value and website and value.website_id != int(website):
            raise serializers.ValidationError("Cette catégorie n'appartient pas au même site web.")
        return value

    def validate(self, attrs):
        """Validation globale"""
        # Vérifier la limite de projets
        request = self.context.get('request')
        if request and not self.instance:  # Création uniquement
            website = attrs.get('website')
            if website:
                subscription = request.user.subscription
                if not subscription.can_add_project(website):
                    raise serializers.ValidationError(
                        f"Limite de projets atteinte ({subscription.projects_limit}). "
                        f"Passez à un plan supérieur pour créer plus de projets."
                    )

        # Gérer les tags
        if 'tag_ids' in attrs:
            tag_ids = attrs.pop('tag_ids')
            website = attrs.get('website') or (self.instance.website if self.instance else None)
            if website:
                # Valider que tous les tags appartiennent au même site web
                tags = Tag.objects.filter(id__in=tag_ids, website=website)
                if tags.count() != len(tag_ids):
                    raise serializers.ValidationError("Certains tags n'appartiennent pas à ce site web.")
                attrs['_tags'] = tags

        return attrs

    def create(self, validated_data):
        """Création avec gestion des tags"""
        tags = validated_data.pop('_tags', None)
        project = super().create(validated_data)
        if tags:
            project.tags.set(tags)
        return project

    def update(self, instance, validated_data):
        """Mise à jour avec gestion des tags"""
        tags = validated_data.pop('_tags', None)
        project = super().update(instance, validated_data)
        if tags is not None:
            project.tags.set(tags)
        return project


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des projets"""

    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_data = TagSerializer(source='tags', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'category', 'category_name', 'tags_data','tags',
            'is_featured', 'status', 'status_display', 'views_count',
            'published_at', 'created_at'
        ]


class ProjectPublicSerializer(serializers.ModelSerializer):
    """Serializer public pour l'API publique"""

    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_data = TagSerializer(source='tags', many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'content',
            'thumbnail', 'featured_image', 'demo_url', 'github_url', 'external_url',
            'category_name', 'tags_data', 'technologies',
            'is_featured', 'views_count', 'start_date', 'end_date',
            'published_at', 'images'
        ]
