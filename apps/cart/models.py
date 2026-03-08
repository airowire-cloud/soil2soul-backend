from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Cart(models.Model):
    """Shopping cart for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual items in the cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of adding
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        db_table = 'cart_items'
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.product.name} in {self.cart.user.username}'s cart"
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.price = self.product.price
        super().save(*args, **kwargs)
