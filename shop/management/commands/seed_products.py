"""
Seed 50 organic grocery products into the local SQLite dev database.

Usage:
  python manage.py seed_products              # insert (skip existing names)
  python manage.py seed_products --clear      # wipe shop products first, then seed
  python manage.py seed_products --dry-run    # print plan without writing

Requires: DJANGO_SETTINGS_MODULE=shopify.settings (set automatically via manage.py).
No extra env vars. Uses Pillow (requirements.txt) for placeholder product images.
"""

from __future__ import annotations

import io
import random
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from shop.models import Product, ProductImage, Tag

# (name, category, sale_price, discount_price, color, description snippet, tags)
PRODUCTS = [
    ("Organic Honeycrisp Apples", "fresh fruit", "4.99", "6.49", "red", "Crisp, sweet apples from certified organic orchards.", ["Organic", "Local"]),
    ("Organic Bartlett Pears", "fresh fruit", "3.49", "4.99", "green", "Juicy pears perfect for snacking or salads.", ["Organic"]),
    ("Organic Valencia Oranges", "fresh fruit", "5.29", "6.99", "orange", "Sun-ripened citrus bursting with vitamin C.", ["Organic", "Vegan"]),
    ("Organic Blueberries", "fresh fruit", "6.99", "8.49", "blue", "Plump berries hand-picked at peak ripeness.", ["Organic", "Vegan"]),
    ("Organic Strawberries", "fresh fruit", "5.49", "7.49", "red", "Sweet berries grown without synthetic pesticides.", ["Organic", "Local"]),
    ("Organic Bananas Bunch", "fresh fruit", "2.49", "3.29", "yellow", "Fair-trade organic bananas, ripened naturally.", ["Organic", "Fair Trade"]),
    ("Organic Mangoes", "fresh fruit", "3.99", "5.49", "orange", "Tropical mangoes with rich, creamy flesh.", ["Organic", "Vegan"]),
    ("Organic Kiwi Pack", "fresh fruit", "4.49", "5.99", "green", "Tart-sweet kiwis packed with fiber.", ["Organic", "Vegan"]),
    ("Organic Seedless Grapes", "fresh fruit", "5.99", "7.99", "purple", "Sweet grape clusters ideal for lunchboxes.", ["Organic"]),
    ("Organic Pink Grapefruit", "fresh fruit", "2.99", "3.99", "pink", "Bright citrus with a balanced sweet-tart finish.", ["Organic", "Vegan"]),
    ("Organic Baby Spinach", "vegetables", "3.99", "4.99", "green", "Tender leaves washed and ready for salads.", ["Organic", "Vegan"]),
    ("Organic Rainbow Chard", "vegetables", "3.49", "4.49", "multicolor", "Colorful stems and earthy greens for sautéing.", ["Organic", "Local"]),
    ("Organic Heirloom Tomatoes", "vegetables", "5.49", "6.99", "red", "Vine-ripened tomatoes with deep flavor.", ["Organic", "Local"]),
    ("Organic Sweet Potatoes", "vegetables", "2.99", "3.79", "orange", "Beta-carotene rich roots for roasting.", ["Organic", "Vegan"]),
    ("Organic Baby Carrots", "vegetables", "2.49", "3.29", "orange", "Crunchy snack carrots, peeled and ready.", ["Organic", "Vegan"]),
    ("Organic Broccoli Crowns", "vegetables", "3.29", "4.29", "green", "Fresh crowns high in fiber and vitamin K.", ["Organic"]),
    ("Organic Zucchini", "vegetables", "2.79", "3.49", "green", "Mild squash great for grilling or spiralizing.", ["Organic", "Vegan"]),
    ("Organic Bell Peppers", "vegetables", "4.49", "5.99", "red", "Sweet peppers in mixed organic varieties.", ["Organic"]),
    ("Organic Avocados", "vegetables", "6.49", "7.99", "green", "Creamy Hass avocados, ripened for guacamole.", ["Organic", "Vegan"]),
    ("Organic Kale Bundle", "vegetables", "3.79", "4.79", "green", "Curly kale for smoothies, chips, or soups.", ["Organic", "Vegan"]),
    ("Organic Extra Virgin Olive Oil", "cooking", "12.99", "15.99", "gold", "Cold-pressed olive oil for dressings and sauté.", ["Organic", "Vegan"]),
    ("Organic Coconut Oil", "cooking", "9.99", "12.49", "white", "Unrefined coconut oil for baking and cooking.", ["Organic", "Vegan"]),
    ("Organic Quinoa", "cooking", "7.49", "9.49", "tan", "Protein-rich ancient grain, pre-washed.", ["Organic", "Gluten-Free"]),
    ("Organic Brown Rice", "cooking", "5.99", "7.49", "brown", "Whole-grain rice with nutty flavor.", ["Organic", "Gluten-Free"]),
    ("Organic Pasta Penne", "cooking", "4.49", "5.99", "tan", "Durum wheat penne from organic Italian wheat.", ["Organic"]),
    ("Organic Tomato Passata", "cooking", "3.99", "4.99", "red", "Smooth strained tomatoes for sauces.", ["Organic", "Vegan"]),
    ("Organic Vegetable Broth", "cooking", "3.29", "4.29", "amber", "Low-sodium broth for soups and risotto.", ["Organic", "Vegan"]),
    ("Organic Maple Syrup", "cooking", "14.99", "17.99", "amber", "Grade A dark maple syrup from small farms.", ["Organic", "Local"]),
    ("Organic Almond Flour", "cooking", "11.99", "14.49", "tan", "Blanched almond meal for gluten-free baking.", ["Organic", "Gluten-Free"]),
    ("Organic Sea Salt", "cooking", "4.99", "5.99", "white", "Coarse Celtic sea salt for finishing dishes.", ["Organic", "Vegan"]),
    ("Organic Almond Butter", "snacks", "8.99", "10.99", "tan", "Stone-ground almonds, no added sugar.", ["Organic", "Vegan"]),
    ("Organic Trail Mix", "snacks", "6.49", "7.99", "brown", "Nuts, seeds, and dried fruit with no sulfites.", ["Organic", "Gluten-Free"]),
    ("Organic Kale Chips", "snacks", "4.99", "6.49", "green", "Baked kale seasoned with nutritional yeast.", ["Organic", "Vegan"]),
    ("Organic Dark Chocolate Bar", "snacks", "3.99", "4.99", "brown", "72% cacao fair-trade chocolate.", ["Organic", "Fair Trade"]),
    ("Organic Rice Cakes", "snacks", "3.49", "4.49", "tan", "Lightly salted whole-grain rice cakes.", ["Organic", "Gluten-Free"]),
    ("Organic Granola", "snacks", "7.99", "9.99", "golden", "Oats, honey, and seeds baked in small batches.", ["Organic"]),
    ("Organic Dried Mango Slices", "snacks", "5.49", "6.99", "orange", "Chewy mango with no added sugar.", ["Organic", "Vegan"]),
    ("Organic Roasted Seaweed", "snacks", "2.99", "3.99", "green", "Single-serve nori sheets with sea salt.", ["Organic", "Vegan"]),
    ("Organic Cold Brew Coffee", "beverages", "4.99", "5.99", "brown", "Slow-steeped organic coffee, ready to drink.", ["Organic", "Vegan"]),
    ("Organic Green Tea", "beverages", "6.99", "8.49", "green", "Sencha green tea leaves in compostable bags.", ["Organic", "Vegan"]),
    ("Organic Almond Milk", "beverages", "3.99", "4.99", "white", "Unsweetened almond beverage, fortified.", ["Organic", "Vegan"]),
    ("Organic Oat Milk", "beverages", "4.49", "5.49", "cream", "Creamy oat drink for coffee and cereal.", ["Organic", "Vegan"]),
    ("Organic Kombucha Ginger", "beverages", "3.49", "4.49", "amber", "Live-culture fermented tea with ginger.", ["Organic", "Vegan"]),
    ("Organic Sparkling Water", "beverages", "1.99", "2.49", "clear", "Mineral water with a light citrus essence.", ["Organic", "Vegan"]),
    ("Organic Coconut Water", "beverages", "2.99", "3.99", "clear", "Hydrating coconut water with no added sugar.", ["Organic", "Vegan"]),
    ("Organic Herbal Sleep Tea", "beverages", "5.49", "6.99", "purple", "Chamomile and lavender blend for evenings.", ["Organic", "Vegan"]),
    ("Organic Face Moisturizer", "beauty & health", "18.99", "22.99", "white", "Plant-based daily moisturizer for all skin types.", ["Organic", "Vegan"]),
    ("Organic Shea Body Lotion", "beauty & health", "12.49", "15.49", "cream", "Rich shea butter lotion with lavender oil.", ["Organic"]),
    ("Organic Multivitamin", "beauty & health", "24.99", "29.99", "green", "Whole-food derived daily vitamins for adults.", ["Organic", "Vegan"]),
    ("Organic Sourdough Loaf", "bread & Bakery", "6.49", "7.99", "golden", "Naturally leavened bread baked fresh daily.", ["Organic", "Local"]),
    ("Organic Whole Wheat Bread", "bread & Bakery", "4.99", "5.99", "brown", "Soft sandwich loaf with organic whole wheat.", ["Organic"]),
    ("Organic Blueberry Muffins", "bread & Bakery", "5.99", "7.49", "blue", "Bakery muffins with wild organic blueberries.", ["Organic", "Local"]),
]

CATEGORY_COLORS = {
    "fresh fruit": (220, 60, 60),
    "vegetables": (60, 160, 80),
    "cooking": (180, 140, 60),
    "snacks": (150, 100, 50),
    "beverages": (80, 150, 200),
    "beauty & health": (200, 180, 220),
    "bread & Bakery": (210, 170, 100),
}


def _placeholder_png(category: str, label: str) -> bytes:
    rgb = CATEGORY_COLORS.get(category, (120, 150, 100))
    img = Image.new("RGB", (400, 400), rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _brand_png() -> bytes:
    img = Image.new("RGB", (120, 40), (34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class Command(BaseCommand):
    help = "Seed 50 organic Shopery-style products (shop.Product model)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing shop products, images, and tags before seeding.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without writing to the database.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of products to seed (default: 50, max in catalog: %(default)s).",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        clear = options["clear"]
        count = min(options["count"], len(PRODUCTS))
        catalog = PRODUCTS[:count]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no database changes."))
            if clear:
                self.stdout.write("Would clear: Product, ProductImage, Tag")
            existing = Product.objects.filter(name__in=[p[0] for p in catalog]).count()
            self.stdout.write(f"Would create up to {count} products ({existing} names already exist).")
            for row in catalog:
                self.stdout.write(f"  - {row[0]} ({row[1]}) ${row[2]}")
            return

        with transaction.atomic():
            if clear:
                Product.objects.all().delete()
                ProductImage.objects.all().delete()
                Tag.objects.all().delete()
                self.stdout.write(self.style.WARNING("Cleared existing products, images, and tags."))

            tag_cache: dict[str, Tag] = {}
            brand_bytes = _brand_png()
            created = 0
            skipped = 0

            for (
                name,
                category,
                sale_price,
                discount_price,
                color,
                description,
                tag_names,
            ) in catalog:
                if Product.objects.filter(name=name).exists():
                    skipped += 1
                    continue

                product = Product(
                    name=name,
                    sale_price=Decimal(sale_price),
                    discount_price=Decimal(discount_price),
                    description=description,
                    category=category,
                    color=color,
                    stock=random.randint(12, 120),
                )
                product.brand.save(
                    f"brand_{created}.png",
                    ContentFile(brand_bytes),
                    save=False,
                )

                img = ProductImage(alt=name[:20])
                img.image.save(
                    f"product_{created}.png",
                    ContentFile(_placeholder_png(category, name)),
                    save=True,
                )

                product.save()

                for tag_name in tag_names:
                    if tag_name not in tag_cache:
                        tag_cache[tag_name], _ = Tag.objects.get_or_create(name=tag_name)
                    product.tags.add(tag_cache[tag_name])

                product.images.add(img)
                created += 1

        total = Product.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} products ({skipped} skipped as duplicates). "
                f"Total products in DB: {total}."
            )
        )