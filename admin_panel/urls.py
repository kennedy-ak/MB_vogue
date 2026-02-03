from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),

    # Product Variants
    path('products/<int:product_id>/variants/add/', views.variant_add, name='variant_add'),
    path('variants/<int:variant_id>/edit/', views.variant_edit, name='variant_edit'),
    path('variants/<int:variant_id>/delete/', views.variant_delete, name='variant_delete'),

    # Product Images
    path('products/<int:product_id>/images/add/', views.image_add, name='image_add'),
    path('images/<int:image_id>/delete/', views.image_delete, name='image_delete'),
    path('images/<int:image_id>/set-primary/', views.image_set_primary, name='image_set_primary'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.order_update_status, name='order_update_status'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),

    # Payments
    path('payments/', views.payment_list, name='payment_list'),
]
