from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from core.permissions import IsWebsiteOwner
from websites.models import Website
from .models import Category, Tag, Project, ProjectImage
from .serializers import (
    CategorySerializer,
    TagSerializer,
    ProjectSerializer,
    ProjectListSerializer,
    ProjectPublicSerializer,
    ProjectImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les catégories de projets"""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les catégories des sites web de l'utilisateur"""
        return Category.objects.filter(website__user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les tags de projets"""

    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les tags des sites web de l'utilisateur"""
        return Tag.objects.filter(website__user=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les projets"""

    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_serializer_class(self):
        """Utilise un serializer léger pour la liste"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        """Retourne les projets des sites web de l'utilisateur"""
        queryset = Project.objects.filter(website__user=self.request.user)

        # Filtres optionnels
        website_id = self.request.query_params.get('website')
        category_id = self.request.query_params.get('category')
        tag_id = self.request.query_params.get('tag')
        status_filter = self.request.query_params.get('status')
        is_featured = self.request.query_params.get('is_featured')

        if website_id:
            queryset = queryset.filter(website_id=website_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')

        return queryset.select_related('website', 'category').prefetch_related('tags', 'images')

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publie un projet"""
        project = self.get_object()
        project.status = 'published'
        project.save()

        return Response({
            'message': 'Projet publié avec succès',
            'data': ProjectSerializer(project).data
        })

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive un projet"""
        project = self.get_object()
        project.status = 'archived'
        project.save()

        return Response({
            'message': 'Projet archivé avec succès',
            'data': ProjectSerializer(project).data
        })

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Bascule le statut featured d'un projet"""
        project = self.get_object()
        project.is_featured = not project.is_featured
        project.save()

        return Response({
            'message': f"Projet {'mis en vedette' if project.is_featured else 'retiré de la vedette'}",
            'is_featured': project.is_featured,
            'data': ProjectSerializer(project).data
        })


class ProjectImageViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les images de projets"""

    serializer_class = ProjectImageSerializer
    permission_classes = [IsAuthenticated, IsWebsiteOwner]

    def get_queryset(self):
        """Retourne les images des projets de l'utilisateur"""
        return ProjectImage.objects.filter(project__website__user=self.request.user)


class ProjectPublicView(views.APIView):
    """
    Vue publique pour récupérer les projets publiés
    Nécessite une API key valide
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """Liste les projets publiés d'un site web"""
        website = request.website  # Injecté par le middleware

        # Filtres
        category_slug = request.query_params.get('category')
        tag_slug = request.query_params.get('tag')
        featured_only = request.query_params.get('featured') == 'true'

        queryset = Project.objects.filter(
            website=website,
            status='published'
        ).select_related('category').prefetch_related('tags', 'images')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        if featured_only:
            queryset = queryset.filter(is_featured=True)

        serializer = ProjectPublicSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class ProjectPublicDetailView(views.APIView):
    """
    Vue publique pour récupérer un projet spécifique par son slug
    Nécessite une API key valide
    """

    permission_classes = [AllowAny]

    def get(self, request, slug):
        """Récupère un projet par son slug"""
        website = request.website  # Injecté par le middleware

        project = get_object_or_404(
            Project,
            website=website,
            slug=slug,
            status='published'
        )

        # Incrémenter le compteur de vues
        project.increment_views()

        # TODO: Logger l'événement analytics

        serializer = ProjectPublicSerializer(project)
        return Response(serializer.data)
