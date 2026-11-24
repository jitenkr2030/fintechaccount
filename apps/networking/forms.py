"""Forms for the networking app."""
from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('post_type', 'title', 'body', 'image', 'link_url')
        widgets = {
            'post_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Title (optional)'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                          'placeholder': "What's on your mind?"}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'link_url': forms.URLInput(attrs={'class': 'form-control',
                                              'placeholder': 'https://'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                          'placeholder': 'Write a comment...'}),
        }
