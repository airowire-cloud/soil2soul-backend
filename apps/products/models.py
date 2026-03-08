from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    """Product categories"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product listing model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Original price
    discount_percentage = models.FloatField(default=0)
    
    image = models.ImageField(upload_to='products/')
    
    stock = models.PositiveIntegerField(default=0)
    weight = models.CharField(max_length=100, blank=True)  # e.g., "1kg", "500g"
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Ratings and reviews
    average_rating = models.FloatField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """Additional product images"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        db_table = 'product_images'
    
    def __str__(self):
        return f"Image for {self.product.name}"


class Wishlist(models.Model):
    """User wishlist"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='in_wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        db_table = 'wishlists'
    
    def __str__(self):
        return f"Wishlist of {self.user.username}"
