from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from core.models import Cart, Wishlist
from users.models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile_and_cart(sender, instance, created, **kwargs):
    """Auto-create UserProfile, Cart and Wishlist when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)
        Cart.objects.create(user=instance)
        Wishlist.objects.create(user=instance)
