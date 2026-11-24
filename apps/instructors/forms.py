"""Forms for the instructors app."""
from django import forms

from .models import InstructorProfile


class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = ('title', 'bio', 'expertise', 'years_teaching',
                  'certifications', 'website', 'linkedin', 'youtube',
                  'commission_pct')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'expertise': forms.TextInput(attrs={'class': 'form-control',
                                                 'placeholder': 'GST, IFRS, FinTech'}),
            'years_teaching': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'certifications': forms.TextInput(attrs={'class': 'form-control',
                                                      'placeholder': 'CA, CMA, ...'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control'}),
            'commission_pct': forms.NumberInput(attrs={'class': 'form-control',
                                                        'step': '0.01', 'min': 0, 'max': 100}),
        }
