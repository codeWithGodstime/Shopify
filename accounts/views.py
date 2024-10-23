from django.views.generic import TemplateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from allauth.account.forms import ChangePasswordForm
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import Order, BillingAddress
from .forms import CustomUserChangeForm, BillingAddressForm

User = get_user_model()

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "account/dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_orders = Order.objects.filter(user=self.request.user).all()[:5]
        billingform = BillingAddressForm()
        context['orders'] = latest_orders
        context['billingAddressForm'] = billingform
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User  # The model to update (in this case, User model)
    form_class = CustomUserChangeForm  # The custom form for updating user profile
    template_name = 'account/setting.html'  # Template for rendering the form
    success_url = reverse_lazy('settings')  # URL to redirect after successful update

    def get_object(self, queryset=None):
        # Fetch the currently logged-in user
        return self.request.user
    
    def get_context_data(self, **kwargs):
        billing_address = BillingAddress.objects.filter(user=self.request.user).first()

        print(self.request.user.profile_image, self.request.user.profile_image)

        billingForm = BillingAddressForm(instance=billing_address)
        profileform = CustomUserChangeForm(instance=self.request.user)
        context = super().get_context_data(**kwargs)
        context['change_password_form'] = ChangePasswordForm()
        context['profile_form_data'] = profileform.initial
        context['billing_address_form'] = billingForm.initial
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
        print(self.request.user.profile_image)
        billing_address = BillingAddress.objects.filter(user=self.request.user).first()
        billingForm = BillingAddressForm(instance=billing_address)
        profileform = CustomUserChangeForm(instance=self.request.user)
        context = super().get_context_data(**kwargs)
        context['change_password_form'] = ChangePasswordForm()
        context['profile_form_data'] = profileform.initial
        context['billing_address_data'] = billingForm.initial
        return context