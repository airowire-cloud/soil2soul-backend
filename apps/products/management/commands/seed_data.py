"""
Management command to seed sample data
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.products.models import Category, Product
from apps.users.models import UserProfile

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            {'name': 'Fresh Vegetables', 'slug': 'fresh-vegetables', 'description': 'Organic fresh vegetables'},
            {'name': 'Fresh Fruits', 'slug': 'fresh-fruits', 'description': 'Seasonal fresh fruits'},
            {'name': 'Grains & Cereals', 'slug': 'grains-cereals', 'description': 'Organic grains and cereals'},
            {'name': 'Dairy & Eggs', 'slug': 'dairy-eggs', 'description': 'Fresh dairy products'},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': cat_data['slug'],
                    'description': cat_data['description']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully'))
