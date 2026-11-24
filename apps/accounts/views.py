"""Views for the accounts app - Phase 1 Foundation."""
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, UpdateView, TemplateView, ListView, View,
)

from .models import User, Role
from .forms import SignUpForm, LoginForm, UserProfileForm, RoleSelectionForm


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Account created. Please log in with your email and password.'
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'signup'
        return ctx


class LoginView(View):
    """Email-based login view."""

    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {'form': form, 'nav_active': 'login'})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next') or request.POST.get('next') or '/dashboard/'
            return redirect(next_url)
        return render(request, self.template_name, {'form': form, 'nav_active': 'login'})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('/')


# ---------------------------------------------------------------------------
# Profile management (fields on User; extended profile in profiles app)
# ---------------------------------------------------------------------------
class MyProfileView(LoginRequiredMixin, TemplateView):
    """Read-only view of the current user's account + profile."""

    template_name = 'accounts/my_profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'profile'
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:my_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'profile'
        return ctx


class RoleEditView(LoginRequiredMixin, View):
    """Let a user add or remove their own roles."""

    template_name = 'accounts/role_edit.html'

    def get(self, request, *args, **kwargs):
        form = RoleSelectionForm(user=request.user)
        return render(request, self.template_name, {'form': form, 'nav_active': 'profile'})

    def post(self, request, *args, **kwargs):
        form = RoleSelectionForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Roles updated.')
            return redirect('accounts:my_profile')
        return render(request, self.template_name, {'form': form, 'nav_active': 'profile'})


# ---------------------------------------------------------------------------
# Professional Directory (Phase 1)
# ---------------------------------------------------------------------------
class DirectoryView(ListView):
    """Public directory of platform members - browse professionals."""

    template_name = 'accounts/directory.html'
    context_object_name = 'users'
    paginate_by = 24

    def get_queryset(self):
        qs = User.objects.filter(is_active=True).exclude(is_superuser=True)
        q = self.request.GET.get('q')
        role = self.request.GET.get('role')
        city = self.request.GET.get('city')
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
                | Q(headline__icontains=q) | Q(city__icontains=q)
            )
        if role:
            qs = qs.filter(roles__name=role)
        if city:
            qs = qs.filter(city__icontains=city)
        return qs.distinct().order_by('-is_premium', '-last_active')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'directory'
        ctx['roles'] = Role.ROLE_CHOICES
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_role'] = self.request.GET.get('role', '')
        ctx['city_filter'] = self.request.GET.get('city', '')
        return ctx
