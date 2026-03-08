from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    """Product reviews and ratings"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    verified_purchase = models.BooleanField(default=False)
    
    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ('user', 'product')
        indexes = [
            models.Index(fields=['product', 'rating']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_product_rating()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_product_rating()
    
    def update_product_rating(self):
        """Update product's average rating"""
        reviews = Review.objects.filter(product=self.product)
        if reviews.exists():
            avg_rating = sum(r.rating for r in reviews) / reviews.count()
            self.product.average_rating = round(avg_rating, 2)
            self.product.total_reviews = reviews.count()
        else:
            self.product.average_rating = 0
            self.product.total_reviews = 0
        self.product.save()


class ReviewImage(models.Model):
    """Images attached to reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Review Image'
        verbose_name_plural = 'Review Images'
        db_table = 'review_images'
    
    def __str__(self):
        return f"Image for review by {self.review.user.username}"
