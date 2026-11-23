from decimal import Decimal

from django.shortcuts import get_object_or_404

from .models import Product

SESSION_CART_KEY = "cart"
SESSION_WISHLIST_KEY = "wishlist"


def _cart_data(session):
    return session.setdefault(SESSION_CART_KEY, {})


def _wishlist_data(session):
    return session.setdefault(SESSION_WISHLIST_KEY, [])


def add_to_cart(session, product_id, quantity=1):
    product = get_object_or_404(Product, pk=product_id)
    cart = _cart_data(session)
    key = str(product_id)
    current = int(cart.get(key, 0))
    cart[key] = min(current + max(1, int(quantity)), product.stock or 99)
    session.modified = True
    return product


def remove_from_cart(session, product_id):
    cart = _cart_data(session)
    key = str(product_id)
    if key in cart:
        del cart[key]
        session.modified = True


def update_cart_quantity(session, product_id, quantity):
    cart = _cart_data(session)
    key = str(product_id)
    if quantity <= 0:
        remove_from_cart(session, product_id)
        return
    product = get_object_or_404(Product, pk=product_id)
    cart[key] = min(int(quantity), product.stock or 99)
    session.modified = True


def clear_cart(session):
    session[SESSION_CART_KEY] = {}
    session.modified = True


def get_cart_items(session):
    cart = session.get(SESSION_CART_KEY) or {}
    if not cart:
        return []

    product_ids = [int(pk) for pk in cart.keys()]
    products = Product.objects.filter(pk__in=product_ids).prefetch_related("images")
    product_map = {p.pk: p for p in products}

    items = []
    for pk_str, qty in cart.items():
        product = product_map.get(int(pk_str))
        if not product:
            continue
        quantity = int(qty)
        line_total = Decimal(product.sale_price) * quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "line_total": line_total,
            }
        )
    return items


def get_cart_summary(session):
    items = get_cart_items(session)
    total = sum((item["line_total"] for item in items), Decimal("0.00"))
    return {
        "items": items,
        "count": sum(item["quantity"] for item in items),
        "total": total,
    }


def toggle_wishlist(session, product_id):
    get_object_or_404(Product, pk=product_id)
    wishlist = _wishlist_data(session)
    product_id = int(product_id)
    if product_id in wishlist:
        wishlist.remove(product_id)
        added = False
    else:
        wishlist.append(product_id)
        added = True
    session.modified = True
    return added


def get_wishlist_products(session):
    ids = session.get(SESSION_WISHLIST_KEY) or []
    if not ids:
        return Product.objects.none()
    return Product.objects.filter(pk__in=ids).prefetch_related("images")


def wishlist_contains(session, product_id):
    return int(product_id) in (session.get(SESSION_WISHLIST_KEY) or [])