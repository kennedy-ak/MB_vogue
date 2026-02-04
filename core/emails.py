"""
Email utility functions for sending order and payment notifications
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer after order is placed
    """
    subject = f'Order Confirmation - {order.order_number}'

    # Render HTML email
    html_message = render_to_string('emails/order_confirmation.html', {
        'order': order,
        'order_items': order.items.all(),
    })

    # Plain text version
    plain_message = f"""
Dear {order.full_name},

Thank you for your order at MB Vogue!

Order Number: {order.order_number}
Order Total: GH₵{order.total_price}

Order Details:
"""
    for item in order.items.all():
        plain_message += f"\n- {item.variant.product.name} ({item.variant.get_color_display()} - {item.variant.get_size_display()}) x{item.quantity} = GH₵{item.get_total_price()}"

    plain_message += f"""

Shipping Address:
{order.full_name}
{order.address}
{order.city}, {order.state} {order.postal_code}
{order.country}

Please complete your payment to process this order.

Thank you for shopping with MB Vogue!

Best regards,
MB Vogue Team
"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        return False


def send_payment_confirmation_email(order, payment):
    """
    Send payment confirmation email after successful payment
    """
    subject = f'Payment Confirmed - Order {order.order_number}'

    # Render HTML email
    html_message = render_to_string('emails/payment_confirmation.html', {
        'order': order,
        'payment': payment,
        'order_items': order.items.all(),
    })

    # Plain text version
    plain_message = f"""
Dear {order.full_name},

Your payment has been successfully received!

Order Number: {order.order_number}
Payment Reference: {payment.reference}
Amount Paid: GH₵{payment.amount}
Payment Status: {payment.get_status_display()}

Order Details:
"""
    for item in order.items.all():
        plain_message += f"\n- {item.variant.product.name} ({item.variant.get_color_display()} - {item.variant.get_size_display()}) x{item.quantity} = GH₵{item.get_total_price()}"

    plain_message += f"""

Your order is now being processed and will be shipped soon.

Shipping Address:
{order.full_name}
{order.address}
{order.city}, {order.state} {order.postal_code}
{order.country}

You can track your order status in your account dashboard.

Thank you for shopping with MB Vogue!

Best regards,
MB Vogue Team
"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending payment confirmation email: {e}")
        return False


def send_order_status_update_email(order, old_status, new_status):
    """
    Send email when order status changes (e.g., shipped, delivered)
    """
    subject = f'Order Status Update - {order.order_number}'

    status_messages = {
        'processing': 'Your order is now being processed.',
        'shipped': 'Your order has been shipped!',
        'delivered': 'Your order has been delivered!',
        'cancelled': 'Your order has been cancelled.',
    }

    status_message = status_messages.get(new_status, f'Your order status has been updated to {new_status}.')

    plain_message = f"""
Dear {order.full_name},

{status_message}

Order Number: {order.order_number}
Status: {order.get_status_display()}

You can view your order details and track the status in your account dashboard.

Thank you for shopping with MB Vogue!

Best regards,
MB Vogue Team
"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending order status update email: {e}")
        return False
