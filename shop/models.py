from django.db import models
from django.conf import settings


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_image')
    alt = models.CharField(max_length=20)
    
    def __str__(self) -> str:
        return self.image.url


class Tag(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    CATEGORY = (
        ('fresh fruit', 'fresh fruit'),
        ('vegetables', 'vegetables'),
        ('cooking', 'cooking'),
        ('snacks', 'snacks'),
        ('beverages', 'beverages'),
        ('beauty & health', 'beauty & health'),
        ('bread & Bakery', 'bread & Bakery')
    )


    name = models.CharField(max_length = 200)
    sale_price = models.DecimalField(decimal_places = 2, max_digits = 10)
    discount_price = models.DecimalField(decimal_places = 2, max_digits = 10)
    description = models.TextField()
    brand = models.ImageField(upload_to='product_brand')
    category = models.CharField(max_length=20, choices = CATEGORY)
    tags = models.ManyToManyField(Tag)
    color = models.CharField(max_length=200)
    images = models.ManyToManyField(ProductImage, related_name='product')
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    

class ProductReview(models.Model):
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    comment = models.TextField()
    ratings = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name
