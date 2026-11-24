"""Forms for the assessments app."""
from django import forms
from django.forms.models import inlineformset_factory

from .models import Assessment, Question, Choice


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ('title', 'description', 'assessment_type', 'course', 'module',
                  'duration_minutes', 'passing_score_pct', 'max_attempts',
                  'is_published', 'shuffle_questions', 'show_answers_after')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assessment_type': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'passing_score_pct': forms.NumberInput(attrs={'class': 'form-control',
                                                            'min': 0, 'max': 100}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shuffle_questions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_answers_after': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('body', 'question_type', 'marks', 'explanation', 'order')
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ('body', 'is_correct', 'order')
        widgets = {
            'body': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


# Inline formsets for editing questions + choices together
ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm, extra=4, can_delete=True,
)


class TakeAssessmentForm(forms.Form):
    """Dynamic form: renders one field per question."""

    def __init__(self, *args, assessment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assessment = assessment
        if not assessment:
            return
        for question in assessment.questions.all():
            field_name = f'q_{question.id}'
            choices = [(c.id, c.body) for c in question.choices.all()]
            if question.question_type == Question.MULTIPLE:
                self.fields[field_name] = forms.MultipleChoiceField(
                    choices=choices, widget=forms.CheckboxSelectMultiple,
                    required=False, label=question.body,
                )
            elif question.question_type == Question.TEXT:
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
                    required=False, label=question.body,
                )
            else:  # single
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices, widget=forms.RadioSelect,
                    required=False, label=question.body,
                )
