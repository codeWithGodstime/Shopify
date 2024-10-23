from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("settings/", views.Settings.as_view(), name="settings"),
    path("orders/", views.OrderListView.as_view(), name="order-summary"),
    path("orders/<str:pk>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("profile/update/", views.UserProfileUpdateView.as_view(), name="profile-update")
]