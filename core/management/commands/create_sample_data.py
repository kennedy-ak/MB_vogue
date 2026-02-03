from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Product, ProductVariant, ProductImage
from users.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Creates sample data for the MB Vogue e-commerce site'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create categories
        categories_data = [
            {
                'name': 'Dresses',
                'slug': 'dresses',
                'description': 'Beautiful dresses for every occasion',
            },
            {
                'name': 'Tops & Blouses',
                'slug': 'tops-blouses',
                'description': 'Stylish tops and blouses',
            },
            {
                'name': 'Pants & Trousers',
                'slug': 'pants-trousers',
                'description': 'Comfortable and stylish pants',
            },
            {
                'name': 'Skirts',
                'slug': 'skirts',
                'description': 'Elegant skirts for all occasions',
            },
            {
                'name': 'Jackets & Coats',
                'slug': 'jackets-coats',
                'description': 'Stay warm in style',
            },
            {
                'name': 'Traditional Wear',
                'slug': 'traditional-wear',
                'description': 'Beautiful traditional Nigerian outfits',
            },
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))

        # Create products
        products_data = [
            # Dresses
            {
                'name': 'Floral Maxi Dress',
                'slug': 'floral-maxi-dress',
                'category': categories[0],
                'description': 'A beautiful floral maxi dress perfect for summer occasions. Made from breathable fabric with a flattering silhouette.',
                'price': 15000,
                'featured': True,
                'variants': [
                    {'size': 'S', 'color': 'red', 'stock': 15},
                    {'size': 'M', 'color': 'red', 'stock': 20},
                    {'size': 'L', 'color': 'red', 'stock': 10},
                    {'size': 'S', 'color': 'blue', 'stock': 12},
                    {'size': 'M', 'color': 'blue', 'stock': 18},
                ]
            },
            {
                'name': 'Elegant Evening Gown',
                'slug': 'elegant-evening-gown',
                'category': categories[0],
                'description': 'Stunning evening gown for special events. Features intricate beading and a flowing design.',
                'price': 35000,
                'featured': True,
                'variants': [
                    {'size': 'M', 'color': 'black', 'stock': 8},
                    {'size': 'L', 'color': 'black', 'stock': 10},
                    {'size': 'M', 'color': 'navy', 'stock': 6},
                ]
            },
            {
                'name': 'Casual Sundress',
                'slug': 'casual-sundress',
                'category': categories[0],
                'description': 'Comfortable casual sundress for everyday wear. Easy to style and perfect for warm weather.',
                'price': 8500,
                'featured': False,
                'variants': [
                    {'size': 'XS', 'color': 'white', 'stock': 20},
                    {'size': 'S', 'color': 'white', 'stock': 25},
                    {'size': 'M', 'color': 'white', 'stock': 20},
                    {'size': 'S', 'color': 'yellow', 'stock': 15},
                    {'size': 'M', 'color': 'yellow', 'stock': 18},
                ]
            },
            # Tops
            {
                'name': 'Silk Blouse',
                'slug': 'silk-blouse',
                'category': categories[1],
                'description': 'Luxurious silk blouse with a elegant cut. Perfect for office or formal occasions.',
                'price': 12000,
                'featured': True,
                'variants': [
                    {'size': 'S', 'color': 'white', 'stock': 15},
                    {'size': 'M', 'color': 'white', 'stock': 20},
                    {'size': 'L', 'color': 'white', 'stock': 12},
                    {'size': 'S', 'color': 'pink', 'stock': 10},
                    {'size': 'M', 'color': 'pink', 'stock': 15},
                ]
            },
            {
                'name': 'Crop Top',
                'slug': 'crop-top',
                'category': categories[1],
                'description': 'Trendy crop top that pairs well with high-waisted bottoms.',
                'price': 5000,
                'featured': False,
                'variants': [
                    {'size': 'XS', 'color': 'black', 'stock': 25},
                    {'size': 'S', 'color': 'black', 'stock': 30},
                    {'size': 'XS', 'color': 'white', 'stock': 20},
                    {'size': 'S', 'color': 'red', 'stock': 18},
                ]
            },
            {
                'name': 'Peplum Blouse',
                'slug': 'peplum-blouse',
                'category': categories[1],
                'description': 'Stylish peplum blouse with a flattering fit.',
                'price': 9500,
                'featured': True,
                'variants': [
                    {'size': 'M', 'color': 'blue', 'stock': 15},
                    {'size': 'L', 'color': 'blue', 'stock': 12},
                    {'size': 'M', 'color': 'purple', 'stock': 10},
                ]
            },
            # Pants
            {
                'name': 'High-Waisted Trousers',
                'slug': 'high-waisted-trousers',
                'category': categories[2],
                'description': 'Classic high-waisted trousers that elongate the legs. Perfect for work or casual wear.',
                'price': 11000,
                'featured': True,
                'variants': [
                    {'size': 'M', 'color': 'black', 'stock': 20},
                    {'size': 'L', 'color': 'black', 'stock': 15},
                    {'size': 'XL', 'color': 'black', 'stock': 10},
                    {'size': 'M', 'color': 'navy', 'stock': 12},
                ]
            },
            {
                'name': 'Wide-Leg Pants',
                'slug': 'wide-leg-pants',
                'category': categories[2],
                'description': 'Comfortable wide-leg pants with a stylish drape.',
                'price': 9500,
                'featured': False,
                'variants': [
                    {'size': 'S', 'color': 'white', 'stock': 15},
                    {'size': 'M', 'color': 'white', 'stock': 18},
                    {'size': 'S', 'color': 'beige', 'stock': 12},
                ]
            },
            {
                'name': 'Skinny Jeans',
                'slug': 'skinny-jeans',
                'category': categories[2],
                'description': 'Classic skinny jeans with stretch for comfort.',
                'price': 8500,
                'featured': True,
                'variants': [
                    {'size': 'XS', 'color': 'blue', 'stock': 20},
                    {'size': 'S', 'color': 'blue', 'stock': 25},
                    {'size': 'M', 'color': 'blue', 'stock': 20},
                    {'size': 'S', 'color': 'black', 'stock': 15},
                ]
            },
            # Skirts
            {
                'name': 'Pencil Skirt',
                'slug': 'pencil-skirt',
                'category': categories[3],
                'description': 'Professional pencil skirt perfect for office wear.',
                'price': 8000,
                'featured': True,
                'variants': [
                    {'size': 'S', 'color': 'black', 'stock': 18},
                    {'size': 'M', 'color': 'black', 'stock': 22},
                    {'size': 'L', 'color': 'black', 'stock': 15},
                    {'size': 'S', 'color': 'gray', 'stock': 12},
                ]
            },
            {
                'name': 'Maxi Skirt',
                'slug': 'maxi-skirt',
                'category': categories[3],
                'description': 'Flowing maxi skirt with a comfortable elastic waist.',
                'price': 7500,
                'featured': False,
                'variants': [
                    {'size': 'M', 'color': 'white', 'stock': 15},
                    {'size': 'L', 'color': 'white', 'stock': 18},
                    {'size': 'M', 'color': 'red', 'stock': 10},
                ]
            },
            {
                'name': 'A-Line Skirt',
                'slug': 'a-line-skirt',
                'category': categories[3],
                'description': 'Flattering A-line skirt suitable for any occasion.',
                'price': 7000,
                'featured': True,
                'variants': [
                    {'size': 'S', 'color': 'pink', 'stock': 20},
                    {'size': 'M', 'color': 'pink', 'stock': 18},
                    {'size': 'S', 'color': 'yellow', 'stock': 15},
                ]
            },
            # Jackets
            {
                'name': 'Denim Jacket',
                'slug': 'denim-jacket',
                'category': categories[4],
                'description': 'Classic denim jacket that never goes out of style.',
                'price': 15000,
                'featured': True,
                'variants': [
                    {'size': 'M', 'color': 'blue', 'stock': 15},
                    {'size': 'L', 'color': 'blue', 'stock': 12},
                    {'size': 'M', 'color': 'white', 'stock': 10},
                ]
            },
            {
                'name': 'Blazer',
                'slug': 'blazer',
                'category': categories[4],
                'description': 'Professional blazer perfect for the office or formal events.',
                'price': 18000,
                'featured': True,
                'variants': [
                    {'size': 'S', 'color': 'black', 'stock': 12},
                    {'size': 'M', 'color': 'black', 'stock': 15},
                    {'size': 'L', 'color': 'black', 'stock': 10},
                    {'size': 'S', 'color': 'navy', 'stock': 8},
                ]
            },
            {
                'name': 'Leather Jacket',
                'slug': 'leather-jacket',
                'category': categories[4],
                'description': 'Edgy leather jacket to add style to any outfit.',
                'price': 25000,
                'featured': False,
                'variants': [
                    {'size': 'M', 'color': 'black', 'stock': 8},
                    {'size': 'L', 'color': 'black', 'stock': 10},
                ]
            },
            # Traditional Wear
            {
                'name': 'Ankara Dress',
                'slug': 'ankara-dress',
                'category': categories[5],
                'description': 'Beautiful Ankara dress featuring traditional Nigerian patterns.',
                'price': 18000,
                'featured': True,
                'variants': [
                    {'size': 'M', 'color': 'brown', 'stock': 12},
                    {'size': 'L', 'color': 'brown', 'stock': 15},
                    {'size': 'M', 'color': 'gold', 'stock': 10},
                ]
            },
            {
                'name': 'Kaftan',
                'slug': 'kaftan',
                'category': categories[5],
                'description': 'Elegant kaftan made from premium fabric.',
                'price': 22000,
                'featured': True,
                'variants': [
                    {'size': 'L', 'color': 'white', 'stock': 10},
                    {'size': 'XL', 'color': 'white', 'stock': 8},
                    {'size': 'L', 'color': 'purple', 'stock': 12},
                ]
            },
            {
                'name': 'Senator Wear',
                'slug': 'senator-wear',
                'category': categories[5],
                'description': 'Classic Nigerian senator wear for a sophisticated look.',
                'price': 25000,
                'featured': True,
                'variants': [
                    {'size': 'L', 'color': 'navy', 'stock': 10},
                    {'size': 'XL', 'color': 'navy', 'stock': 8},
                    {'size': 'L', 'color': 'black', 'stock': 12},
                    {'size': 'XL', 'color': 'black', 'stock': 10},
                ]
            },
        ]

        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    'name': prod_data['name'],
                    'category': prod_data['category'],
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'featured': prod_data['featured'],
                    'available': True,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))

                # Create variants
                for variant_data in prod_data['variants']:
                    ProductVariant.objects.create(
                        product=product,
                        size=variant_data['size'],
                        color=variant_data['color'],
                        stock=variant_data['stock']
                    )

        # Create sample admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mbvogue.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'phone': '08012345678',
                'address': '123 Admin Street',
                'city': 'Lagos',
                'state': 'Lagos',
                'postal_code': '100001',
                'country': 'Nigeria'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists: admin / admin123'))

        # Create sample regular users
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'customer{i}',
                defaults={
                    'email': f'customer{i}@example.com',
                    'first_name': f'Customer{i}',
                    'last_name': 'Test',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f'0801234567{i}',
                    'address': f'{i} Test Street',
                    'city': 'Lagos',
                    'state': 'Lagos',
                    'postal_code': f'10000{i}',
                    'country': 'Nigeria'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: customer{i} / password123'))

        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Customers: customer1-5 / password123')
