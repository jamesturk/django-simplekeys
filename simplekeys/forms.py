from django.forms import ModelForm
from .models import Key


class KeyRegistrationForm(ModelForm):
    class Meta:
        model = Key
        fields = ['email', 'name', 'organization']
