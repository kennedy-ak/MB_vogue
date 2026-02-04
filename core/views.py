from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from .models import Category, Product, ProductVariant, Cart, CartItem, Order, OrderItem, Wishlist, WishlistItem
from .forms import AddToCartForm, CheckoutForm
from .cart_utils import CartHandler
from .emails import send_order_confirmation_email


def home(request):
    featured_products = Product.objects.filter(available=True, featured=True)[:8]
    new_arrivals = Product.objects.filter(available=True)[:8]
    categories = Category.objects.all()[:6]

    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    }
    return render(request, 'core/home.html', context)


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    # Get filter parameters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'newest')

    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search functionality
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'category_slug': category_slug,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'core/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    images = product.images.all()
    variants = product.variants.filter(stock__gt=0)

    # Group variants by color
    colors = variants.values_list('color', flat=True).distinct()

    # Get all available sizes for default color
    available_variants = {}
    for color in colors:
        available_variants[color] = {
            variant.size: variant
            for variant in variants.filter(color=color)
        }

    # Get available sizes for first color
    first_color = colors.first() if colors else None
    available_sizes = variants.filter(color=first_color).values_list('size', flat=True).distinct() if first_color else []

    # Get first available variant as default
    first_variant = variants.first() if variants else None

    context = {
        'product': product,
        'images': images,
        'variants': variants,
        'available_variants': available_variants,
        'colors': colors,
        'available_sizes': available_sizes,
        'first_color': first_color,
        'first_variant': first_variant,
    }
    return render(request, 'core/product_detail.html', context)


def cart_detail(request):
    cart_handler = CartHandler(request)
    cart_items = cart_handler.get_items()
    total_price = cart_handler.get_total_price()
    total_items = cart_handler.get_total_items()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
    }
    return render(request, 'core/cart.html', context)


def cart_add(request, variant_id=None):
    # Handle POST request with variant_id from form data
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')

    if not variant_id:
        messages.error(request, 'Please select a product variant.')
        return redirect('core:product_list')

    try:
        variant = ProductVariant.objects.get(id=variant_id)
    except ProductVariant.DoesNotExist:
        messages.error(request, 'Product variant not found.')
        return redirect('core:product_list')

    cart_handler = CartHandler(request)

    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)
        try:
            quantity = int(quantity)
            if quantity > 0:
                success, message = cart_handler.add(variant_id, quantity, override=True)
                if success:
                    messages.success(request, f'{quantity} item(s) added to cart.')
                else:
                    messages.warning(request, message)
                return redirect('core:cart_detail')
        except ValueError:
            messages.error(request, 'Invalid quantity.')
            return redirect('core:product_detail', slug=variant.product.slug)

    # GET request - add 1 item
    success, message = cart_handler.add(variant_id, 1)
    if success:
        messages.success(request, message)
    else:
        messages.warning(request, message)

    return redirect('core:cart_detail')


def cart_update(request, item_id):
    if request.method != 'POST':
        return redirect('core:cart_detail')

    quantity = request.POST.get('quantity')
    cart_handler = CartHandler(request)

    try:
        quantity = int(quantity)
        # item_id is actually variant_id in our session-based system
        success, message = cart_handler.update(item_id, quantity)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
    except ValueError:
        messages.error(request, 'Invalid quantity.')

    return redirect('core:cart_detail')


def cart_remove(request, item_id):
    cart_handler = CartHandler(request)
    # item_id is actually variant_id in our session-based system
    success, message = cart_handler.remove(item_id)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('core:cart_detail')


@login_required
def checkout(request):
    # Check if user has profile with required info
    if not hasattr(request.user, 'profile') or not request.user.profile.phone:
        messages.warning(request, 'Please update your profile with phone number and delivery location first.')
        return redirect('users:profile_edit')

    # Get cart using CartHandler for consistency
    cart_handler = CartHandler(request)
    cart_items = cart_handler.get_items()
    total_price = cart_handler.get_total_price()
    total_items = cart_handler.get_total_items()

    if total_items == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('core:product_list')

    # Store cart data in session for order creation after payment
    request.session['pending_order'] = {
        'cart_items': [
            {
                'variant_id': item.variant.id if hasattr(item, 'variant') else item['variant'].id,
                'quantity': item.quantity,
                'price': str(item.variant.get_price() if hasattr(item, 'variant') else item['variant'].get_price())
            }
            for item in cart_items
        ],
        'total_price': str(total_price),
    }

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'user_profile': request.user.profile,
    }
    return render(request, 'core/checkout.html', context)


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    context = {
        'order': order,
    }
    return render(request, 'core/order_detail.html', context)


@login_required
def order_success(request):
    return render(request, 'core/order_success.html')


# ==================== WISHLIST ====================

@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.select_related('product__category').all()

    context = {
        'wishlist_items': wishlist_items,
        'section': 'wishlist',
    }
    return render(request, 'core/wishlist.html', context)


@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Check if product already in wishlist
    if wishlist.items.filter(product=product).exists():
        messages.info(request, f'{product.name} is already in your wishlist.')
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        messages.success(request, f'{product.name} added to your wishlist.')

    return redirect('core:product_detail', slug=product.slug)


@login_required
def wishlist_remove(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    messages.success(request, f'{product_name} removed from your wishlist.')

    return redirect('core:wishlist')


@login_required
def wishlist_toggle(request, product_id):
    """Toggle product in wishlist (AJAX-friendly)"""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wishlist_item = wishlist.items.filter(product=product).first()

    if wishlist_item:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from wishlist'})
    else:
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        return JsonResponse({'status': 'added', 'message': 'Added to wishlist'})
