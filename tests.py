"""
Tests for Soil & Soul project
Run with: python manage.py test
"""

from django.test import TestCase
from django.contrib.auth.models import User
from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_user_profile_created(self):
        self.assertTrue(hasattr(self.user, 'profile'))


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Test Description',
            price=100.00,
            stock=10
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, 100.00)
    
    def test_product_in_stock(self):
        self.assertTrue(self.product.in_stock)


class CartTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='cartuser',
            password='testpass123'
        )
        self.cart = Cart.objects.create(user=self.user)
        
        self.category = Category.objects.create(
            name='Test',
            slug='test'
        )
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            slug='test-product',
            description='Test',
            price=50.00,
            stock=10
        )
    
    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
    
    def test_add_to_cart(self):
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            price=50.00
        )
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(self.cart.total_price, 100.00)
