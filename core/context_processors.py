"""
Context processors for making data available across all templates
"""
from .cart_utils import CartHandler


def cart_context(request):
    """
    Add cart information to all template contexts
    """
    cart_handler = CartHandler(request)
    return {
        'cart_total_items': cart_handler.get_total_items(),
        'cart_total_price': cart_handler.get_total_price(),
    }
