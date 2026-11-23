from shop.cart import get_cart_summary


def cart(request):
    summary = get_cart_summary(request.session)
    return {
        "cart_items": summary["items"],
        "cart_count": summary["count"],
        "cart_total": summary["total"],
    }