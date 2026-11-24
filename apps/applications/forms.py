"""Forms for the applications app."""
from django import forms

from .models import JobApplication


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ('cover_letter', 'resume', 'expected_salary',
                  'notice_period_days', 'consent_verify_credentials')
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                                  'placeholder': 'Tell the employer why you are a great fit...'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'expected_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0,
                                                         'placeholder': 'Annual INR'}),
            'notice_period_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'consent_verify_credentials': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
        }
