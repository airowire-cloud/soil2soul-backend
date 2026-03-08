from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
from io import BytesIO
from apps.products.models import Product

class Command(BaseCommand):
    help = 'Add images to products'

    def create_grape_image(self):
        """Create a simple gradient image for grapes"""
        # Create image
        img = Image.new('RGB', (400, 400), color=(34, 139, 34))  # Dark green background
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Draw purple grapes (circles)
        colors = [(138, 43, 226), (128, 0, 128), (147, 112, 219), (186, 85, 211)]
        positions = [
            (100, 100), (150, 120), (200, 100), (250, 110),
            (120, 180), (180, 190), (240, 170),
            (140, 260), (200, 270), (260, 250),
            (100, 320), (160, 330), (220, 320), (280, 310)
        ]
        
        for i, (x, y) in enumerate(positions):
            color = colors[i % len(colors)]
            # Draw grape (circle)
            draw.ellipse(
                [(x-25, y-25), (x+25, y+25)],
                fill=color,
                outline=(100, 0, 100)
            )
        
        # Convert to bytes
        image_bytes = BytesIO()
        img.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        return image_bytes
    
    def handle(self, *args, **options):
        try:
            product = Product.objects.get(slug='grapes')
            
            # Generate image
            image_bytes = self.create_grape_image()
            
            # Save image
            product.image.save(
                'grapes.png',
                ContentFile(image_bytes.getvalue()),
                save=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Added image to: {product.name}')
            )
            
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ Product not found: grapes')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error adding image: {str(e)}')
            )
