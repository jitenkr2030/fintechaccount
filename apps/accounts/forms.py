"""Forms for the accounts app."""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import User, Role


# ---------------------------------------------------------------------------
# Auth forms
# ---------------------------------------------------------------------------
class SignUpForm(UserCreationForm):
    """Registration form. Email is the username; pick one or more roles."""

    password1 = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label=_('Confirm Password'), widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'headline',
                  'city', 'state')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'e.g. CA Finalist | GST Practitioner'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
        }

    role = forms.MultipleChoiceField(
        label=_('I am a (select all that apply)'),
        choices=Role.ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text=_('You can be a learner, an instructor and an employer at the same time.'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default 'role' field, then re-add with role choices properly
        # (Already added above; nothing to do)

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            for role_name in self.cleaned_data.get('role', []):
                user.add_role(role_name)
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('Email'), widget=forms.EmailInput(attrs={'class': 'form-control', 'autofocus': True})
    )
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class UserProfileForm(forms.ModelForm):
    """Edit profile fields that live directly on the User model."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'headline', 'bio',
                  'avatar', 'city', 'state', 'country')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'headline': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RoleSelectionForm(forms.Form):
    """Let the user add or remove roles on their own account."""

    roles = forms.MultipleChoiceField(
        choices=Role.ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['roles'].initial = [r.name for r in user.roles.all()]

    def save(self):
        if not self.user:
            return
        selected = set(self.cleaned_data.get('roles', []))
        existing = {r.name for r in self.user.roles.all()}
        # Add new
        for name in selected - existing:
            self.user.add_role(name)
        # Remove unchecked (but never remove admin role from superusers)
        for name in existing - selected:
            if name == Role.ADMIN and self.user.is_superuser:
                continue
            self.user.remove_role(name)
