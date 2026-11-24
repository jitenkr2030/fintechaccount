"""Forms for the courses app."""
from django import forms

from .models import Course, Module, Lesson, CourseReview


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('title', 'subtitle', 'description', 'category', 'level',
                  'delivery', 'status', 'cover_image', 'promo_video_url',
                  'is_free', 'price', 'discount_price', 'starts_at', 'ends_at',
                  'duration_hours', 'is_featured', 'is_certified', 'is_corporate')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'delivery': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'promo_video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'starts_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'ends_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_certified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_corporate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ('title', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ('title', 'content_type', 'body', 'video_url',
                  'duration_minutes', 'is_preview', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content_type': forms.Select(attrs={'class': 'form-select'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'video_url': forms.URLInput(attrs={'class': 'form-control',
                                                'placeholder': 'https://youtube.com/...'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = CourseReview
        fields = ('rating', 'body')
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control',
                                                'min': 1, 'max': 5, 'step': 1}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
