from django.contrib import admin
from .models import Review, ReviewImage

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'title', 'verified_purchase', 'created_at']
    search_fields = ['user__username', 'product__name', 'title']
    list_filter = ['rating', 'verified_purchase', 'created_at']
    inlines = [ReviewImageInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['review', 'created_at']
    search_fields = ['review__user__username', 'review__product__name']
