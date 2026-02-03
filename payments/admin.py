from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'reference', 'status', 'is_successful', 'created_at', 'verified_at']
    list_filter = ['status', 'created_at', 'verified_at']
    search_fields = ['reference', 'order__order_number', 'paystack_transaction_id']
    readonly_fields = ['order', 'amount', 'reference', 'paystack_transaction_id', 'access_code',
                      'authorization_code', 'response_data', 'created_at', 'updated_at', 'verified_at']

    fieldsets = (
        ('Payment Information', {
            'fields': ('order', 'amount', 'reference', 'status')
        }),
        ('Paystack Details', {
            'fields': ('paystack_transaction_id', 'access_code', 'authorization_code')
        }),
        ('Response Data', {
            'fields': ('response_data',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at')
        }),
    )

    def is_successful(self, obj):
        if obj.is_successful():
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    is_successful.short_description = 'Success'
    is_successful.allow_tags = True
