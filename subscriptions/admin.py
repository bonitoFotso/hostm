from django.contrib import admin
from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'billing_period', 'status', 'started_at', 'expires_at']
    list_filter = ['plan', 'status', 'billing_period']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Plan', {
            'fields': ('plan', 'billing_period', 'status')
        }),
        ('Limites', {
            'fields': (
                'websites_limit', 'contacts_per_month', 'projects_limit', 'storage_mb'
            )
        }),
        ('Fonctionnalités', {
            'fields': (
                'analytics', 'integrations', 'custom_domain', 'white_label', 'priority_support'
            )
        }),
        ('Utilisation', {
            'fields': ('current_month_contacts', 'current_storage_mb')
        }),
        ('Dates', {
            'fields': ('started_at', 'expires_at', 'cancelled_at', 'created_at', 'updated_at')
        }),
    )
