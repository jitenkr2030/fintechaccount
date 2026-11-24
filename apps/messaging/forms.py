"""Forms for the messaging app."""
from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                      'placeholder': 'Write a message...'}),
    )


class NewThreadForm(forms.Form):
    recipient = forms.IntegerField(
        widget=forms.HiddenInput,
    )
    subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Subject (optional)'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    )
