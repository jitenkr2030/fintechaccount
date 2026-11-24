"""Forms for the moderation app."""
from django import forms

from .models import Report, ModerationAction


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('target_type', 'target_id', 'target_url', 'reason', 'description')
        widgets = {
            'target_type': forms.Select(attrs={'class': 'form-select'}),
            'target_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'target_url': forms.URLInput(attrs={'class': 'form-control'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ModerationActionForm(forms.ModelForm):
    class Meta:
        model = ModerationAction
        fields = ('action', 'notes')
        widgets = {
            'action': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
