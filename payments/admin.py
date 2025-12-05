from django.contrib import admin
from .models import Payment, Invoice


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'currency', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'paypal_order_id', 'paypal_payer_email']
    readonly_fields = ['paypal_order_id', 'paypal_capture_id', 'paid_at', 'refunded_at', 'created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'user', 'amount', 'status', 'issue_date', 'due_date']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'user__email']
    readonly_fields = ['invoice_number', 'paid_date', 'created_at', 'updated_at']
