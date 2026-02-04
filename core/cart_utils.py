"""
Utility functions for handling both session-based (anonymous) and database (authenticated) carts
"""
from .models import Cart, CartItem, ProductVariant
from django.shortcuts import get_object_or_404


class CartHandler:
    """
    Handles cart operations for both authenticated and anonymous users
    """

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.user = request.user

        # Initialize session cart if it doesn't exist
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, variant_id, quantity=1, override=False):
        """
        Add a product variant to the cart
        override: if True, set quantity instead of incrementing
        """
        variant_id = str(variant_id)
        variant = get_object_or_404(ProductVariant, id=variant_id)

        if not variant.is_available():
            return False, 'This variant is out of stock.'

        if self.user.is_authenticated:
            # Database cart for authenticated users
            cart, created = Cart.objects.get_or_create(user=self.user)
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                variant=variant
            )

            if override:
                cart_item.quantity = quantity
            else:
                if not item_created:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = quantity

            # Check stock limit
            if cart_item.quantity > variant.stock:
                cart_item.quantity = variant.stock
                cart_item.save()
                return False, f'Maximum stock reached. Only {variant.stock} items available.'

            cart_item.save()
            return True, 'Item added to cart successfully.'
        else:
            # Session cart for anonymous users
            if variant_id in self.cart:
                if override:
                    self.cart[variant_id]['quantity'] = quantity
                else:
                    self.cart[variant_id]['quantity'] += quantity

                # Check stock limit
                if self.cart[variant_id]['quantity'] > variant.stock:
                    self.cart[variant_id]['quantity'] = variant.stock
                    self.save()
                    return False, f'Maximum stock reached. Only {variant.stock} items available.'
            else:
                self.cart[variant_id] = {
                    'quantity': quantity,
                    'price': str(variant.get_price())
                }

            self.save()
            return True, 'Item added to cart successfully.'

    def remove(self, variant_id):
        """Remove a product from the cart"""
        variant_id = str(variant_id)

        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                cart_item = CartItem.objects.get(cart=cart, variant_id=variant_id)
                cart_item.delete()
                return True, 'Item removed from cart.'
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return False, 'Item not found in cart.'
        else:
            if variant_id in self.cart:
                del self.cart[variant_id]
                self.save()
                return True, 'Item removed from cart.'
            return False, 'Item not found in cart.'

    def update(self, variant_id, quantity):
        """Update quantity of a cart item"""
        variant_id = str(variant_id)
        quantity = int(quantity)

        if quantity <= 0:
            return self.remove(variant_id)

        variant = get_object_or_404(ProductVariant, id=variant_id)

        if quantity > variant.stock:
            return False, f'Only {variant.stock} items available.'

        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                cart_item = CartItem.objects.get(cart=cart, variant_id=variant_id)
                cart_item.quantity = quantity
                cart_item.save()
                return True, 'Cart updated successfully.'
            except (Cart.DoesNotExist, CartItem.DoesNotExist):
                return False, 'Item not found in cart.'
        else:
            if variant_id in self.cart:
                self.cart[variant_id]['quantity'] = quantity
                self.save()
                return True, 'Cart updated successfully.'
            return False, 'Item not found in cart.'

    def clear(self):
        """Clear the entire cart"""
        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                cart.items.all().delete()
            except Cart.DoesNotExist:
                pass
        else:
            self.session['cart'] = {}
            self.save()

    def get_items(self):
        """Get all cart items with product details"""
        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                return cart.items.select_related('variant__product').all()
            except Cart.DoesNotExist:
                return []
        else:
            # Build cart items from session
            items = []
            for variant_id, item_data in self.cart.items():
                try:
                    variant = ProductVariant.objects.select_related('product').get(id=variant_id)
                    items.append({
                        'variant': variant,
                        'quantity': item_data['quantity'],
                        'total_price': variant.get_price() * item_data['quantity']
                    })
                except ProductVariant.DoesNotExist:
                    continue
            return items

    def get_total_price(self):
        """Calculate total price of cart"""
        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                return cart.get_total_price()
            except Cart.DoesNotExist:
                return 0
        else:
            total = 0
            for variant_id, item_data in self.cart.items():
                try:
                    variant = ProductVariant.objects.get(id=variant_id)
                    total += variant.get_price() * item_data['quantity']
                except ProductVariant.DoesNotExist:
                    continue
            return total

    def get_total_items(self):
        """Get total number of items in cart"""
        if self.user.is_authenticated:
            try:
                cart = Cart.objects.get(user=self.user)
                return cart.get_total_items()
            except Cart.DoesNotExist:
                return 0
        else:
            return sum(item['quantity'] for item in self.cart.values())

    def save(self):
        """Mark session as modified"""
        self.session.modified = True

    def merge_session_cart_to_user(self):
        """
        Merge anonymous session cart into user's database cart
        Called after user logs in
        """
        if not self.user.is_authenticated or not self.cart:
            return

        cart, created = Cart.objects.get_or_create(user=self.user)

        for variant_id, item_data in self.cart.items():
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    variant=variant
                )

                if not created:
                    # Add session quantity to existing quantity
                    cart_item.quantity += item_data['quantity']
                else:
                    cart_item.quantity = item_data['quantity']

                # Ensure we don't exceed stock
                if cart_item.quantity > variant.stock:
                    cart_item.quantity = variant.stock

                cart_item.save()
            except ProductVariant.DoesNotExist:
                continue

        # Clear session cart after merging
        self.session['cart'] = {}
        self.save()
