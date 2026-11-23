from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("shop/", views.product_list, name="shop"),
    path("shop/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/toggle/<int:pk>/", views.wishlist_toggle, name="wishlist_toggle"),
]