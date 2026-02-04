"""
Management command to set all product and variant prices to 1 cedi
"""
from django.core.management.base import BaseCommand
from core.models import Product, ProductVariant


class Command(BaseCommand):
    help = 'Set all product and variant prices to 1 cedi (GH₵1.00)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm the price update',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will change ALL product prices to GH₵1.00\n'
                    'Run with --confirm to proceed'
                )
            )
            return

        # Update all products
        products_updated = Product.objects.all().update(price=1.00)

        # Update all product variants that have price overrides
        variants_updated = ProductVariant.objects.filter(
            price_override__isnull=False
        ).update(price_override=1.00)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated:\n'
                f'  - {products_updated} products to GH₵1.00\n'
                f'  - {variants_updated} variant price overrides to GH₵1.00'
            )
        )
