from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator

class UserProfile(models.Model):
    """Extended user profile model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True, validators=[URLValidator()])
    
    # Address information
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} Profile"


class Address(models.Model):
    """Multiple delivery addresses for users"""
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        db_table = 'addresses'
    
    def __str__(self):
        return f"{self.user.username} - {self.address_type}"


class UserActivity(models.Model):
    """Track user activities for analytics"""
    ACTIVITY_TYPES = [
        ('view', 'Product View'),
        ('add_cart', 'Add to Cart'),
        ('remove_cart', 'Remove from Cart'),
        ('purchase', 'Purchase'),
        ('wishlist', 'Add to Wishlist'),
        ('review', 'Write Review'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content_type = models.CharField(max_length=50, blank=True)  # 'product', 'order', etc.
    object_id = models.PositiveIntegerField(blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        db_table = 'user_activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
