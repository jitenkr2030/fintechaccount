"""Forms for the employers app."""
from django import forms

from .models import EmployerProfile


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'tagline', 'about', 'logo', 'website',
                  'linkedin', 'industry', 'company_size', 'headquarters_city',
                  'headquarters_state', 'country', 'contact_name',
                  'contact_email', 'contact_phone')
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'company_size': forms.Select(attrs={'class': 'form-select'},
                                          choices=[('', 'Select'),
                                                   ('1-10', '1-10'),
                                                   ('11-50', '11-50'),
                                                   ('51-200', '51-200'),
                                                   ('201-1000', '201-1000'),
                                                   ('1000+', '1000+')]),
            'headquarters_city': forms.TextInput(attrs={'class': 'form-control'}),
            'headquarters_state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class BecomeEmployerForm(forms.Form):
    company_name = forms.CharField(max_length=200,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    industry = forms.CharField(max_length=100, required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'placeholder': 'e.g. Accounting, Banking, FinTech'}))
    headquarters_city = forms.CharField(max_length=100, required=False,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_email = forms.EmailField(required=False,
                                      widget=forms.EmailInput(attrs={'class': 'form-control'}))
