from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("shop/", views.product_list, name="shop"),
    path("shop/<int:pk>/", views.product_detail, name="product_detail"),
]