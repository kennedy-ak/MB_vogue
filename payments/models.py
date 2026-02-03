from django.db import models
from core.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('abandoned', 'Abandoned'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paystack_transaction_id = models.CharField(max_length=200, blank=True, null=True)
    access_code = models.CharField(max_length=200, blank=True, null=True)
    authorization_code = models.CharField(max_length=200, blank=True, null=True)

    # Paystack response data (stored as JSON for reference)
    response_data = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.get_status_display()}"

    def is_successful(self):
        return self.status == 'success'
