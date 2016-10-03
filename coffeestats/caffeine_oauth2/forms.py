from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from caffeine_oauth2.models import CoffeestatsApplication


class CoffeestatsApplicationForm(forms.ModelForm):
    class Meta:
        model = CoffeestatsApplication
        fields = (
            'name', 'description', 'website', 'agree', 'client_type',
            'authorization_grant_type', 'redirect_uris')

    def clean_agree(self):
        agree_value = self.cleaned_data['agree']
        if not agree_value:
            raise ValidationError(
                _('You have to agree to our API usage agreement'),
                code='not_agreed')
        return agree_value


class CoffeestatsApplicationRejectionForm(forms.ModelForm):
    reasoning = forms.CharField(
        min_length=10, max_length=4000, widget=forms.Textarea())

    class Meta:
        model = CoffeestatsApplication
        fields = []


class CoffeestatsApplicationApprovalForm(forms.ModelForm):
    class Meta:
        model = CoffeestatsApplication
        fields = ['name', 'description', 'website', 'client_type',
                  'authorization_grant_type']
