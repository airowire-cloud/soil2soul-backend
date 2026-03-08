from django.contrib import admin
from .models import UserProfile, Address, UserActivity

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'created_at']
    search_fields = ['user__username', 'phone_number', 'city']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'city', 'is_default']
    search_fields = ['user__username', 'city', 'country']
    list_filter = ['address_type', 'is_default', 'country']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'content_type', 'timestamp']
    search_fields = ['user__username', 'activity_type']
    list_filter = ['activity_type', 'timestamp']
    readonly_fields = ['timestamp']
