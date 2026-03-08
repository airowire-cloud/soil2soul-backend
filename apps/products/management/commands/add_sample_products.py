from django.core.management.base import BaseCommand
from apps.products.models import Category, Product


class Command(BaseCommand):
    help = 'Add sample products to the database'

    def handle(self, *args, **options):
        # Create categories
        fruits, _ = Category.objects.get_or_create(
            name='Fruits',
            defaults={'slug': 'fruits'}
        )
        vegetables, _ = Category.objects.get_or_create(
            name='Vegetables',
            defaults={'slug': 'vegetables'}
        )
        grains, _ = Category.objects.get_or_create(
            name='Grains',
            defaults={'slug': 'grains'}
        )

        # Sample products
        products_data = [
            {
                'name': 'Grapes',
                'slug': 'grapes',
                'description': 'Fresh, juicy organic grapes - sweet and delicious',
                'short_description': 'Sweet organic grapes',
                'category': fruits,
                'price': 120,
                'stock': 200,
                'status': 'active',
            },
        ]

        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults=product_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⊚ Product already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully added {created_count} sample products!')
        )
