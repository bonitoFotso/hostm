from django.contrib import admin
from .models import ContactFormField, ContactMessage


@admin.register(ContactFormField)
class ContactFormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'name', 'field_type', 'website', 'required', 'order']
    list_filter = ['field_type', 'required', 'website']
    search_fields = ['name', 'label', 'website__name']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'website', 'status', 'created_at']
    list_filter = ['status', 'website', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['form_data', 'ip_address', 'user_agent', 'read_at', 'replied_at', 'created_at', 'updated_at']
