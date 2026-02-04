import requests
import hashlib
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from core.models import Order
from .models import Payment
from core.emails import send_payment_confirmation_email


def generate_reference():
    """Generate a unique transaction reference"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))


@login_required
def initialize_payment(request, order_id):
    """Initialize Paystack payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if payment already exists and is successful
    if hasattr(order, 'payment') and order.payment.is_successful():
        messages.info(request, 'Payment for this order has already been completed.')
        return redirect('core:order_detail', order_number=order.order_number)

    # Generate a unique reference
    reference = generate_reference()
    while Payment.objects.filter(reference=reference).exists():
        reference = generate_reference()

    # Calculate amount in kobo (Paystack uses lowest currency unit)
    amount_kobo = int(order.total_price * 100)

    # Prepare Paystack request data
    paystack_data = {
        'email': order.email,
        'amount': amount_kobo,
        'reference': reference,
        'callback_url': request.build_absolute_uri('/payments/callback/'),
        'metadata': {
            'order_id': order.id,
            'order_number': order.order_number,
            'custom_fields': [
                {
                    'display_name': 'Order Number',
                    'variable_name': 'order_number',
                    'value': order.order_number
                }
            ]
        }
    }

    # Make request to Paystack
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            json=paystack_data,
            headers=headers
        )
        response_data = response.json()

        if response_data.get('status'):
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                reference=reference,
                access_code=response_data['data']['access_code'],
                response_data=response_data
            )

            # Redirect to Paystack payment page
            return redirect(response_data['data']['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {response_data.get('message', 'Unknown error')}")
            return redirect('core:order_detail', order_number=order.order_number)

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Network error: {str(e)}")
        return redirect('core:order_detail', order_number=order.order_number)


@login_required
def verify_payment(request, reference):
    """Verify payment with Paystack (server-side)"""
    payment = get_object_or_404(Payment, reference=reference)

    if payment.is_successful():
        messages.info(request, 'Payment has already been verified.')
        return redirect('core:order_detail', order_number=payment.order.order_number)

    # Make request to Paystack to verify transaction
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers
        )
        response_data = response.json()

        if response_data.get('status') and response_data['data']['status'] == 'success':
            # Update payment record
            payment.status = 'success'
            payment.paystack_transaction_id = response_data['data']['id']
            payment.authorization_code = response_data['data'].get('authorization', {}).get('authorization_code')
            payment.response_data = response_data
            payment.verified_at = timezone.now()
            payment.save()

            # Update order status
            order = payment.order
            order.status = 'paid'
            order.save()

            # Update stock
            for item in order.items.all():
                if item.variant:
                    item.variant.stock -= item.quantity
                    item.variant.save()

            # Send payment confirmation email
            send_payment_confirmation_email(order, payment)

            messages.success(request, 'Payment verified successfully!')
        else:
            payment.status = 'failed'
            payment.response_data = response_data
            payment.save()

            payment.order.status = 'pending'
            payment.order.save()

            messages.error(request, "Payment verification failed.")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Network error during verification: {str(e)}")

    return redirect('core:order_detail', order_number=payment.order.order_number)


@login_required
def payment_callback(request):
    """Handle Paystack callback after payment"""
    reference = request.GET.get('reference')
    trxref = request.GET.get('trxref')

    # Use the reference that's available
    ref_to_use = reference or trxref

    if not ref_to_use:
        messages.error(request, 'No transaction reference found.')
        return redirect('core:home')

    # Verify the payment
    return verify_payment(request, ref_to_use)
