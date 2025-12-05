from django.contrib import admin
from .models import Website


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'user', 'is_active', 'total_contacts', 'total_projects', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain', 'user__email', 'api_key']
    readonly_fields = ['api_key', 'total_contacts', 'total_projects', 'created_at', 'updated_at']
    fieldsets = (
        ('Informations', {
            'fields': ('user', 'name', 'domain', 'description')
        }),
        ('Configuration', {
            'fields': ('api_key', 'is_active', 'allowed_origins')
        }),
        ('Statistiques', {
            'fields': ('total_contacts', 'total_projects')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
