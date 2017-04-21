from django import forms
from .models import Key


class KeyRegistrationForm(forms.ModelForm):
    class Meta:
        model = Key
        fields = ['email', 'name', 'website', 'organization', 'usage']


class KeyConfirmationForm(forms.Form):
    email = forms.CharField(widget=forms.HiddenInput)
    key = forms.CharField(widget=forms.HiddenInput)
    confirm_hash = forms.CharField(widget=forms.HiddenInput)
