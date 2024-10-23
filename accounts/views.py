from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.forms import ChangePasswordForm

from .models import Order
from .forms import CustomUserChangeForm, BillingAddressForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "account/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_orders = Order.objects.filter(user=self.request.user).all()[:5]
        billingform = BillingAddressForm()
        context['orders'] = latest_orders
        context['billingAddressForm'] = billingform
        return context


class OrderListView(LoginRequiredMixin, ListView):
    context_object_name ="orders"
    template_name = "account/dashboard/order_history.html"
    queryset = Order.objects.all()


class OrderDetailView(LoginRequiredMixin, DetailView):
    context_object_name = "order"
    template_name = "account/dashboard/order_detail.html"
    queryset = Order.objects.all()


class Settings(LoginRequiredMixin, TemplateView):
    template_name = "account/setting.html"

    def get_context_data(self, **kwargs):
        billingForm = BillingAddressForm()
        context = super().get_context_data(**kwargs)
        context['change_password_form'] = ChangePasswordForm()
        context['profile_change_form'] = CustomUserChangeForm()
        context['billing_address_form'] = BillingAddressForm()
        return context