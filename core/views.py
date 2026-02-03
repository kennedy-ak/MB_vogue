from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from .models import Category, Product, ProductVariant, Cart, CartItem, Order, OrderItem, Wishlist, WishlistItem
from .forms import AddToCartForm, CheckoutForm


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


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('variant__product').all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'core/cart.html', context)


@login_required
def cart_add(request, variant_id=None):
    # Handle POST request with variant_id from form data
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')

    if not variant_id:
        messages.error(request, 'Please select a product variant.')
        return redirect('core:product_list')

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if not variant.is_available():
        messages.error(request, 'This variant is out of stock.')
        return redirect('core:product_detail', slug=variant.product.slug)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant
    )

    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)
        try:
            quantity = int(quantity)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f'{quantity} item(s) added to cart.')
                return redirect('core:cart_detail')
        except ValueError:
            pass

    if not created:
        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            messages.error(request, 'Maximum stock reached for this item.')
    else:
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, 'Item added to cart.')

    return redirect('core:cart_detail')


@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
        if quantity > 0 and quantity <= cart_item.variant.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        elif quantity > cart_item.variant.stock:
            messages.error(request, f'Only {cart_item.variant.stock} items available.')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    except ValueError:
        messages.error(request, 'Invalid quantity.')

    return redirect('core:cart_detail')


@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('core:cart_detail')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('variant__product').all()

    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('core:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
                notes=form.cleaned_data.get('notes', '')
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    price=item.variant.get_price(),
                    quantity=item.quantity
                )

            # Clear cart
            cart_items.delete()

            # Redirect to payment initialization
            messages.success(request, f'Order {order.order_number} created. Please complete payment.')
            return redirect('payments:initialize_payment', order_id=order.id)
    else:
        # Pre-fill form with user profile data if available
        initial_data = {}
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
                'email': request.user.email,
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'postal_code': profile.postal_code,
                'country': profile.country,
            }
        form = CheckoutForm(initial=initial_data)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
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
