from django.contrib import admin
from .models import Category, Product, ProductImage, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'status', 'average_rating', 'created_at']
    search_fields = ['name', 'category__name']
    list_filter = ['status', 'category', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'total_reviews', 'created_at', 'updated_at']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
