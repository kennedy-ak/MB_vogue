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
def initialize_payment(request):
    """Initialize Paystack payment"""
    # Get pending order data from session
    pending_order = request.session.get('pending_order')
    if not pending_order:
        messages.error(request, 'No pending order found. Please try again.')
        return redirect('core:cart_detail')

    # Check if user has profile
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'Please update your profile first.')
        return redirect('users:profile_edit')

    # Generate a unique reference
    reference = generate_reference()
    while Payment.objects.filter(reference=reference).exists():
        reference = generate_reference()

    # Calculate amount in kobo (Paystack uses lowest currency unit)
    from decimal import Decimal
    total_price = Decimal(pending_order['total_price'])
    amount_kobo = int(total_price * 100)

    # Prepare Paystack request data
    paystack_data = {
        'email': request.user.email,
        'amount': amount_kobo,
        'reference': reference,
        'callback_url': request.build_absolute_uri('/payments/callback/'),
        'metadata': {
            'user_id': request.user.id,
            'custom_fields': [
                {
                    'display_name': 'Customer Name',
                    'variable_name': 'customer_name',
                    'value': request.user.get_full_name() or request.user.username
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
            # Store payment reference in session
            request.session['payment_reference'] = reference
            request.session['payment_amount'] = str(total_price)

            # Redirect to Paystack payment page
            return redirect(response_data['data']['authorization_url'])
        else:
            messages.error(request, f"Payment initialization failed: {response_data.get('message', 'Unknown error')}")
            return redirect('core:cart_detail')

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Network error: {str(e)}")
        return redirect('core:cart_detail')


@login_required
def verify_payment(request, reference):
    """Verify payment with Paystack and create order"""
    # Get pending order from session
    pending_order = request.session.get('pending_order')
    if not pending_order:
        messages.error(request, 'No pending order found.')
        return redirect('core:home')

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
            from decimal import Decimal
            from core.models import ProductVariant, OrderItem
            from core.cart_utils import CartHandler

            # Create the order NOW (after payment is confirmed)
            profile = request.user.profile
            order = Order.objects.create(
                user=request.user,
                total_price=Decimal(pending_order['total_price']),
                full_name=request.user.get_full_name() or request.user.username,
                email=request.user.email,
                phone=profile.phone,
                address=profile.address,  # This will be the location
                city='',  # Not needed
                state='',  # Not needed
                postal_code='',  # Not needed
                country='Ghana',
                status='paid'  # Set to paid immediately
            )

            # Create order items
            for item_data in pending_order['cart_items']:
                variant = ProductVariant.objects.get(id=item_data['variant_id'])
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    price=Decimal(item_data['price']),
                    quantity=item_data['quantity']
                )

                # Update stock
                variant.stock -= item_data['quantity']
                variant.save()

            # Create payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                reference=reference,
                status='success',
                paystack_transaction_id=response_data['data']['id'],
                authorization_code=response_data['data'].get('authorization', {}).get('authorization_code'),
                response_data=response_data,
                verified_at=timezone.now()
            )

            # Clear cart
            cart_handler = CartHandler(request)
            cart_handler.clear()

            # Clear session data
            del request.session['pending_order']
            if 'payment_reference' in request.session:
                del request.session['payment_reference']

            # Send emails
            send_order_confirmation_email(order)
            send_payment_confirmation_email(order, payment)

            messages.success(request, f'Payment successful! Order {order.order_number} has been placed.')
            return redirect('core:order_detail', order_number=order.order_number)
        else:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('core:cart_detail')

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Network error during verification: {str(e)}")
        return redirect('core:cart_detail')
    except Exception as e:
        messages.error(request, f"Error creating order: {str(e)}")
        return redirect('core:cart_detail')


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
