"""Forms for the profiles app."""
from django import forms

from .models import (
    Profile, Education, Experience, Certification,
    ProfileSkill, PortfolioItem, Skill,
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('current_title', 'current_company', 'industry',
                  'years_experience', 'website', 'linkedin', 'twitter',
                  'github', 'resume', 'is_open_to_work', 'is_open_to_mentor',
                  'is_open_to_speaking')
        widgets = {
            'current_title': forms.TextInput(attrs={'class': 'form-control',
                                                     'placeholder': 'e.g. Senior Accountant'}),
            'current_company': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'e.g. Accounting, Banking, FinTech'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_open_to_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_open_to_mentor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_open_to_speaking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('institution', 'degree', 'field_of_study', 'start_year',
                  'end_year', 'grade', 'description')
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ('title', 'company', 'employment_type', 'location',
                  'is_current', 'start_date', 'end_date', 'description')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ('name', 'issuing_body', 'is_statutory', 'issue_date',
                  'expiry_date', 'credential_id', 'credential_url')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'issuing_body': forms.TextInput(attrs={'class': 'form-control'}),
            'is_statutory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_id': forms.TextInput(attrs={'class': 'form-control'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ('title', 'item_type', 'description', 'url', 'image', 'completed_at')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'completed_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ProfileSkillForm(forms.ModelForm):
    """Add a skill to the current user's profile. Creates the Skill if new."""

    skill_name = forms.CharField(
        label='Skill', max_length=80,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'e.g. GST, Tally Prime, Financial Modelling'}),
    )

    class Meta:
        model = ProfileSkill
        fields = ('level',)
        widgets = {'level': forms.Select(attrs={'class': 'form-select'})}

    def save(self, commit=True):
        name = self.cleaned_data['skill_name'].strip()
        skill, _ = Skill.objects.get_or_create(name=name)
        profile_skill = super().save(commit=False)
        profile_skill.skill = skill
        if commit:
            profile_skill.save()
        return profile_skill
