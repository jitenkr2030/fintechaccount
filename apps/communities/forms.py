"""Forms for the communities app."""
from django import forms

from .models import Community, CommunityTopic, CommunityReply


class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ('name', 'description', 'category', 'visibility', 'icon')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'Accounting, Tax, FinTech...'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TopicForm(forms.ModelForm):
    class Meta:
        model = CommunityTopic
        fields = ('title', 'body')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = CommunityReply
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
