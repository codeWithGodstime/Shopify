from django.core.paginator import Paginator
from django.db import models
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from .models import Product, Tag


class HomeView(TemplateView):
    template_name = "shop/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = [
            {"name": "Fresh Fruit", "count": 165, "emoji": "🍎"},
            {"name": "Vegetables", "count": 132, "emoji": "🥬"},
            {"name": "Dairy & Eggs", "count": 98, "emoji": "🥚"},
            {"name": "Meat & Fish", "count": 76, "emoji": "🥩"},
            {"name": "Snacks", "count": 54, "emoji": "🍿"},
            {"name": "Beverages", "count": 88, "emoji": "🥤"},
            {"name": "Bakery", "count": 41, "emoji": "🍞"},
            {"name": "Organic", "count": 120, "emoji": "🌿"},
            {"name": "Spices", "count": 37, "emoji": "🌶️"},
            {"name": "Frozen", "count": 62, "emoji": "🧊"},
        ]
        context["hot_deals"] = [
            {"title": "Green Apple", "price": "14.99", "original_price": "20.99", "rating": 4, "image": ""},
            {"title": "Chinese Cabbage", "price": "12.00", "original_price": "17.00", "rating": 5, "image": ""},
            {"title": "Green Lettuce", "price": "9.50", "original_price": None, "rating": 4, "image": ""},
            {"title": "Eggplant", "price": "11.25", "original_price": "15.00", "rating": 5, "image": ""},
        ]
        context["featured_products"] = [
            {"title": "Big seasoned potatoes", "price": "18.00", "original_price": "24.00", "rating": 5, "image": ""},
            {"title": "Red hot tomatoes", "price": "7.50", "original_price": None, "rating": 4, "image": ""},
            {"title": "Green capsicum", "price": "8.99", "original_price": "11.99", "rating": 5, "image": ""},
            {"title": "Organic ginger", "price": "6.40", "original_price": None, "rating": 4, "image": ""},
            {"title": "Fresh corn", "price": "5.99", "original_price": "8.99", "rating": 5, "image": ""},
        ]
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
        _product_queryset().prefetch_related("productreview_set__reviewer"),
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
    return render(request, "shop/product-detail.html", context)