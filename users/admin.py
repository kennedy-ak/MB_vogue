from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['phone', 'address', 'city', 'state', 'postal_code', 'country', 'date_of_birth', 'profile_picture']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone']
    list_select_related = ['profile']

    def get_phone(self, obj):
        return obj.profile.phone if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Phone'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'state', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    list_filter = ['country', 'state', 'created_at']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
