from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.text import slugify
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
from core.models import Category, Product, ProductVariant, ProductImage, Order, OrderItem
from payments.models import Payment
from users.models import UserProfile
from .forms import (
    CategoryForm, ProductForm, ProductVariantForm,
    ProductImageForm, OrderStatusForm
)


# ==================== AUTHENTICATION ====================

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_page = request.GET.get('next')
            return redirect(next_page) if next_page else redirect('admin_panel:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'admin_panel/login.html')


@login_required(login_url='admin_panel:login')
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('admin_panel:login')


# ==================== DASHBOARD ====================

@login_required(login_url='admin_panel:login')
def dashboard(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:home')

    # Get date ranges
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    # Statistics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = UserProfile.objects.count()
    total_orders = Order.objects.count()

    # Orders by status
    pending_orders = Order.objects.filter(status='pending').count()
    paid_orders = Order.objects.filter(status='paid').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()

    # Revenue calculations
    total_revenue = Order.objects.filter(status__in=['paid', 'processing', 'shipped', 'delivered']).aggregate(
        total=Sum('total_price'))['total'] or 0

    revenue_today = Order.objects.filter(
        created_at__date=today,
        status__in=['paid', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    revenue_last_7_days = Order.objects.filter(
        created_at__gte=last_7_days,
        status__in=['paid', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    revenue_last_30_days = Order.objects.filter(
        created_at__gte=last_30_days,
        status__in=['paid', 'processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Low stock alerts
    low_stock_variants = ProductVariant.objects.filter(
        stock__lt=5
    ).select_related('product').order_by('stock')[:10]

    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum(F('variants__orderitem__quantity'))
    ).filter(
        variants__orderitem__isnull=False
    ).order_by('-total_sold')[:10]

    # Payment statistics
    total_payments = Payment.objects.count()
    successful_payments = Payment.objects.filter(status='success').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    failed_payments = Payment.objects.filter(status='failed').count()

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_last_7_days': revenue_last_7_days,
        'revenue_last_30_days': revenue_last_30_days,
        'recent_orders': recent_orders,
        'low_stock_variants': low_stock_variants,
        'top_products': top_products,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
    }

    return render(request, 'admin_panel/dashboard.html', context)


# ==================== CATEGORIES ====================

@login_required(login_url='admin_panel:login')
def category_list(request):
    if not request.user.is_staff:
        return redirect('core:home')

    categories = Category.objects.all().order_by('name')
    search_query = request.GET.get('search', '')

    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'categories': categories,
        'search_query': search_query,
        'section': 'categories',
    }
    return render(request, 'admin_panel/categories/list.html', context)


@login_required(login_url='admin_panel:login')
def category_create(request):
    if not request.user.is_staff:
        return redirect('core:home')

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'section': 'categories',
    }
    return render(request, 'admin_panel/categories/form.html', context)


@login_required(login_url='admin_panel:login')
def category_edit(request, category_id):
    if not request.user.is_staff:
        return redirect('core:home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('admin_panel:category_list')
    else:
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category,
        'section': 'categories',
    }
    return render(request, 'admin_panel/categories/form.html', context)


@login_required(login_url='admin_panel:login')
def category_delete(request, category_id):
    if not request.user.is_staff:
        return redirect('core:home')

    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
        return redirect('admin_panel:category_list')

    context = {
        'category': category,
        'section': 'categories',
    }
    return render(request, 'admin_panel/categories/delete.html', context)


# ==================== PRODUCTS ====================

@login_required(login_url='admin_panel:login')
def product_list(request):
    if not request.user.is_staff:
        return redirect('core:home')

    products = Product.objects.select_related('category').all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_filter:
        products = products.filter(category_id=category_filter)

    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/list.html', context)


@login_required(login_url='admin_panel:login')
def product_create(request):
    if not request.user.is_staff:
        return redirect('core:home')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Generate slug if not provided
            if not form.cleaned_data.get('slug'):
                form.cleaned_data['slug'] = slugify(form.cleaned_data['name'])

            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully.')
            return redirect('admin_panel:product_edit', product_id=product.id)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/form.html', context)


@login_required(login_url='admin_panel:login')
def product_edit(request, product_id):
    if not request.user.is_staff:
        return redirect('core:home')

    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()
    images = product.images.all()

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('admin_panel:product_edit', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'variants': variants,
        'images': images,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/form.html', context)


@login_required(login_url='admin_panel:login')
def product_delete(request, product_id):
    if not request.user.is_staff:
        return redirect('core:home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product "{product.name}" deleted successfully.')
        return redirect('admin_panel:product_list')

    context = {
        'product': product,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/delete.html', context)


# ==================== PRODUCT VARIANTS ====================

@login_required(login_url='admin_panel:login')
def variant_add(request, product_id):
    if not request.user.is_staff:
        return redirect('core:home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            messages.success(request, f'Variant added successfully.')
            return redirect('admin_panel:product_edit', product_id=product.id)
    else:
        form = ProductVariantForm()

    context = {
        'form': form,
        'product': product,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/variant_form.html', context)


@login_required(login_url='admin_panel:login')
def variant_edit(request, variant_id):
    if not request.user.is_staff:
        return redirect('core:home')

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Variant updated successfully.')
            return redirect('admin_panel:product_edit', product_id=variant.product.id)
    else:
        form = ProductVariantForm(instance=variant)

    context = {
        'form': form,
        'variant': variant,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/variant_form.html', context)


@login_required(login_url='admin_panel:login')
def variant_delete(request, variant_id):
    if not request.user.is_staff:
        return redirect('core:home')

    variant = get_object_or_404(ProductVariant, id=variant_id)
    product_id = variant.product.id

    if request.method == 'POST':
        variant.delete()
        messages.success(request, f'Variant deleted successfully.')
        return redirect('admin_panel:product_edit', product_id=product_id)

    context = {
        'variant': variant,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/variant_delete.html', context)


# ==================== PRODUCT IMAGES ====================

@login_required(login_url='admin_panel:login')
def image_add(request, product_id):
    if not request.user.is_staff:
        return redirect('core:home')

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            messages.success(request, f'Image added successfully.')
            return redirect('admin_panel:product_edit', product_id=product.id)
    else:
        form = ProductImageForm()

    context = {
        'form': form,
        'product': product,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/image_form.html', context)


@login_required(login_url='admin_panel:login')
def image_delete(request, image_id):
    if not request.user.is_staff:
        return redirect('core:home')

    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id

    if request.method == 'POST':
        image.delete()
        messages.success(request, f'Image deleted successfully.')
        return redirect('admin_panel:product_edit', product_id=product_id)

    context = {
        'image': image,
        'section': 'products',
    }
    return render(request, 'admin_panel/products/image_delete.html', context)


@login_required(login_url='admin_panel:login')
def image_set_primary(request, image_id):
    if not request.user.is_staff:
        return redirect('core:home')

    image = get_object_or_404(ProductImage, id=image_id)

    # Unset all primary images for this product
    ProductImage.objects.filter(product=image.product).update(is_primary=False)

    # Set this image as primary
    image.is_primary = True
    image.save()

    messages.success(request, f'Primary image updated.')
    return redirect('admin_panel:product_edit', product_id=image.product.id)


# ==================== ORDERS ====================

@login_required(login_url='admin_panel:login')
def order_list(request):
    if not request.user.is_staff:
        return redirect('core:home')

    orders = Order.objects.select_related('user').prefetch_related('items__variant').all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
        'section': 'orders',
    }
    return render(request, 'admin_panel/orders/list.html', context)


@login_required(login_url='admin_panel:login')
def order_detail(request, order_id):
    if not request.user.is_staff:
        return redirect('core:home')

    order = get_object_or_404(Order, id=order_id)
    items = order.items.select_related('variant__product').all()

    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order.status = form.cleaned_data['status']
            order.save()
            messages.success(request, f'Order status updated to "{order.get_status_display()}".')
            return redirect('admin_panel:order_detail', order_id=order.id)
    else:
        form = OrderStatusForm(initial={'status': order.status})

    context = {
        'order': order,
        'items': items,
        'form': form,
        'section': 'orders',
    }
    return render(request, 'admin_panel/orders/detail.html', context)


@login_required(login_url='admin_panel:login')
def order_update_status(request, order_id):
    if not request.user.is_staff:
        return redirect('core:home')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to "{order.get_status_display()}".')
        else:
            messages.error(request, 'Invalid status.')

    return redirect('admin_panel:order_detail', order_id=order.id)


# ==================== CUSTOMERS ====================

@login_required(login_url='admin_panel:login')
def customer_list(request):
    if not request.user.is_staff:
        return redirect('core:home')

    customers = UserProfile.objects.select_related('user').all().order_by('-created_at')
    search_query = request.GET.get('search', '')

    if search_query:
        customers = customers.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(city__icontains=search_query)
        )

    context = {
        'customers': customers,
        'search_query': search_query,
        'section': 'customers',
    }
    return render(request, 'admin_panel/customers/list.html', context)


@login_required(login_url='admin_panel:login')
def customer_detail(request, customer_id):
    if not request.user.is_staff:
        return redirect('core:home')

    profile = get_object_or_404(UserProfile, id=customer_id)
    orders = Order.objects.filter(user=profile.user).order_by('-created_at')[:10]

    context = {
        'profile': profile,
        'orders': orders,
        'section': 'customers',
    }
    return render(request, 'admin_panel/customers/detail.html', context)


# ==================== PAYMENTS ====================

@login_required(login_url='admin_panel:login')
def payment_list(request):
    if not request.user.is_staff:
        return redirect('core:home')

    payments = Payment.objects.select_related('order__user').all().order_by('-created_at')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    if status_filter:
        payments = payments.filter(status=status_filter)

    if search_query:
        payments = payments.filter(
            Q(reference__icontains=search_query) |
            Q(order__order_number__icontains=search_query)
        )

    context = {
        'payments': payments,
        'status_filter': status_filter,
        'search_query': search_query,
        'section': 'payments',
    }
    return render(request, 'admin_panel/payments/list.html', context)
