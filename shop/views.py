from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from .cart import (
    add_to_cart,
    clear_cart,
    get_cart_summary,
    get_wishlist_products,
    remove_from_cart,
    toggle_wishlist,
    update_cart_quantity,
    wishlist_contains,
)
from .models import Product, Tag


class HomeView(TemplateView):
    template_name = "shop/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = [
            {"name": "Fresh Fruit", "slug": "fresh fruit", "count": 165, "emoji": "🍎"},
            {"name": "Vegetables", "slug": "vegetables", "count": 132, "emoji": "🥬"},
            {"name": "Snacks", "slug": "snacks", "count": 54, "emoji": "🍿"},
            {"name": "Beverages", "slug": "beverages", "count": 88, "emoji": "🥤"},
            {"name": "Bakery", "slug": "bread & Bakery", "count": 41, "emoji": "🍞"},
            {"name": "Cooking", "slug": "cooking", "count": 76, "emoji": "🥩"},
            {"name": "Beauty", "slug": "beauty & health", "count": 37, "emoji": "🌿"},
            {"name": "Organic", "slug": "fresh fruit", "count": 120, "emoji": "🌿"},
        ]

        catalog = list(_product_queryset().order_by("-id"))
        if catalog:
            on_sale = [
                p
                for p in catalog
                if p.discount_price and p.discount_price > p.sale_price
            ]
            context["hot_deals"] = (on_sale or catalog)[:4]
            context["featured_products"] = catalog[:5]
        else:
            context["hot_deals"] = []
            context["featured_products"] = []
        return context


def _product_queryset():
    return Product.objects.prefetch_related("images", "tags").annotate(
        avg_rating=Avg("productreview__ratings")
    )


def product_list(request):
    products = _product_queryset()
    category = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "latest")

    if category:
        products = products.filter(category=category)
    if tag_slug:
        products = products.filter(tags__name__iexact=tag_slug)
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    sort_map = {
        "latest": "-id",
        "price_low": "sale_price",
        "price_high": "-sale_price",
        "name": "name",
    }
    products = products.order_by(sort_map.get(sort, "-id")).distinct()

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    sale_products = (
        _product_queryset()
        .filter(discount_price__gt=models.F("sale_price"))
        .order_by("-id")[:3]
    )

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "result_count": paginator.count,
        "categories": Product.CATEGORY,
        "tags": Tag.objects.order_by("name"),
        "sale_products": sale_products,
        "active_category": category,
        "active_tag": tag_slug,
        "query": query,
        "sort": sort,
    }
    return render(request, "shop/product-list.html", context)


def product_detail(request, pk):
    product = get_object_or_404(
        _product_queryset().prefetch_related(
            "productreview_set__reviewer",
            "images",
            "tags",
        ),
        pk=pk,
    )
    related_products = (
        _product_queryset()
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    reviews = product.productreview_set.select_related("reviewer").order_by("-date")[:6]
    review_count = product.productreview_set.count()
    avg_rating = product.avg_rating or 0

    context = {
        "product": product,
        "related_products": related_products,
        "reviews": reviews,
        "review_count": review_count,
        "avg_rating": round(avg_rating, 1) if avg_rating else 0,
        "full_stars": int(avg_rating) if avg_rating else 4,
    }
    context["in_wishlist"] = wishlist_contains(request.session, product.pk)
    return render(request, "shop/product-detail.html", context)


def _redirect_back(request, fallback_name="shop", **fallback_kwargs):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url:
        return redirect(next_url)
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect(reverse(fallback_name, kwargs=fallback_kwargs))


def cart_add(request, pk):
    if request.method != "POST":
        return redirect("product_detail", pk=pk)
    quantity = int(request.POST.get("quantity", 1) or 1)
    product = add_to_cart(request.session, pk, quantity)
    messages.success(request, f"Added {product.name} to your cart.")
    return _redirect_back(request, "product_detail", pk=pk)


def cart_remove(request, pk):
    if request.method == "POST":
        remove_from_cart(request.session, pk)
        messages.info(request, "Item removed from cart.")
    return _redirect_back(request, "cart")


def cart_update(request, pk):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1) or 1)
        update_cart_quantity(request.session, pk, quantity)
    return _redirect_back(request, "cart")


def cart_detail(request):
    summary = get_cart_summary(request.session)
    return render(
        request,
        "shop/cart.html",
        {"cart_items": summary["items"], "cart_total": summary["total"]},
    )


def checkout(request):
    summary = get_cart_summary(request.session)
    if request.method == "POST":
        if not summary["items"]:
            messages.warning(request, "Your cart is empty.")
            return redirect("shop")
        clear_cart(request.session)
        messages.success(
            request,
            "Order received! Payment processing is not enabled in this demo.",
        )
        return redirect("shop")

    if not summary["items"]:
        messages.info(request, "Add items to your cart before checkout.")
        return redirect("shop")

    return render(
        request,
        "shop/checkout.html",
        {"cart_items": summary["items"], "cart_total": summary["total"]},
    )


def wishlist(request):
    products = get_wishlist_products(request.session)
    return render(request, "shop/wishlist.html", {"products": products})


def wishlist_toggle(request, pk):
    if request.method != "POST":
        return redirect("product_detail", pk=pk)
    added = toggle_wishlist(request.session, pk)
    if added:
        messages.success(request, "Added to wishlist.")
    else:
        messages.info(request, "Removed from wishlist.")
    return _redirect_back(request, "wishlist")