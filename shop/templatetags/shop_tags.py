from django import template

register = template.Library()


@register.filter
def discount_percent(product):
    if not product.discount_price or product.discount_price <= product.sale_price:
        return 0
    return int(
        (float(product.discount_price) - float(product.sale_price))
        / float(product.discount_price)
        * 100
    )


@register.filter
def star_count(value):
    try:
        return max(0, min(5, int(float(value or 0))))
    except (TypeError, ValueError):
        return 4


@register.filter
def product_image_url(product):
    image = product.images.first()
    if image:
        return image.image.url
    return ""