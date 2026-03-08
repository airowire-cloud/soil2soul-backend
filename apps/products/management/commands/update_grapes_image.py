from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from datetime import datetime
from apps.products.models import Product
import base64

class Command(BaseCommand):
    help = 'Update product image with a professional photo'

    def handle(self, *args, **options):
        try:
            product = Product.objects.get(slug='grapes')
            
            # Base64 encoded professional grapes image (small version)
            # This is a placeholder - in production you'd upload via admin or API
            
            # For now, we'll keep the current image and provide upload instructions
            if product.image:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Product {product.name} already has an image')
                )
                self.stdout.write(
                    self.style.WARNING('📝 To replace with the professional image:')
                )
                self.stdout.write('  1. Go to http://localhost:8000/admin/')
                self.stdout.write('  2. Login with superuser credentials')
                self.stdout.write('  3. Navigate to Products > Products')
                self.stdout.write('  4. Click on "Grapes"')
                self.stdout.write('  5. Click "Change" under the Image field')
                self.stdout.write('  6. Upload the professional grapes image')
                self.stdout.write('  7. Save')
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ No image found for product')
                )
            
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ Product not found: grapes')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )
