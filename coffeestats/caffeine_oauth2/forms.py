from django import forms

from caffeine_oauth2.models import CoffeestatsApplication


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
