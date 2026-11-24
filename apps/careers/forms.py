"""Forms for the careers app."""
from django import forms

from .models import Job, JobAlert, JobCategory


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'description', 'requirements', 'responsibilities',
                  'category', 'employment_type', 'experience_level',
                  'location_city', 'location_state', 'is_remote', 'is_wfh',
                  'salary_min', 'salary_max', 'is_salary_disclosed',
                  'skills_required', 'status', 'openings', 'application_deadline')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'location_city': forms.TextInput(attrs={'class': 'form-control'}),
            'location_state': forms.TextInput(attrs={'class': 'form-control'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_wfh': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_salary_disclosed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'skills_required': forms.TextInput(attrs={'class': 'form-control',
                                                       'placeholder': 'Tally, GST, Excel, ...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'openings': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'application_deadline': forms.DateTimeInput(attrs={'class': 'form-control',
                                                                 'type': 'datetime-local'}),
        }


class JobSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Job title, keyword, company...'}))
    category = forms.ModelChoiceField(queryset=JobCategory.objects.all(), required=False,
                                       empty_label='All categories',
                                       widget=forms.Select(attrs={'class': 'form-select'}))
    location = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'City or state'}))
    employment_type = forms.ChoiceField(choices=[('', 'Any')] + Job.EMPLOYMENT_TYPES,
                                         required=False,
                                         widget=forms.Select(attrs={'class': 'form-select'}))
    is_remote = forms.BooleanField(required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))


class JobAlertForm(forms.ModelForm):
    class Meta:
        model = JobAlert
        fields = ('keywords', 'category', 'location_city', 'is_remote',
                  'employment_type', 'min_salary', 'frequency')
        widgets = {
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location_city': forms.TextInput(attrs={'class': 'form-control'}),
            'is_remote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'min_salary': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
        }
