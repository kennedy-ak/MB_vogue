from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductVariant, Cart, CartItem, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'stock', 'price_override']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'featured', 'available', 'thumbnail_preview', 'created_at']
    list_filter = ['category', 'featured', 'available', 'created_at']
    list_editable = ['featured', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    inlines = [ProductImageInline, ProductVariantInline]

    def thumbnail_preview(self, obj):
        if obj.images.first():
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;"/>',
                             obj.images.first().image.url)
        return "No Image"
    thumbnail_preview.short_description = 'Image'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock', 'get_price', 'is_available']
    list_filter = ['size', 'color', 'product__category']
    search_fields = ['product__name']
    raw_id_fields = ['product']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['variant', 'quantity', 'get_total_price']
    can_delete = False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_items', 'get_total_price', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'created_at', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['variant', 'price', 'quantity', 'get_total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'email']
    readonly_fields = ['order_number', 'user', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_price')
        }),
        ('Shipping Information', {
            'fields': ('full_name', 'email', 'phone', 'address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    actions = ['mark_as_paid', 'mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
    mark_as_paid.short_description = 'Mark selected orders as paid'

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = 'Mark selected orders as processing'

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = 'Mark selected orders as shipped'

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = 'Mark selected orders as delivered'
