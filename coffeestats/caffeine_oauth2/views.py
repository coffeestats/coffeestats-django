from django.forms.models import modelform_factory

from oauth2_provider.views import ApplicationRegistration
from oauth2_provider.models import get_application_model


class CoffeestatsApplicationRegistration(ApplicationRegistration):

    def get_form_class(self):
        """
        Returns a customized form class for the coffeestats application model.

        """
        return modelform_factory(
            get_application_model(),
            fields=(
                # 'logo',
                'name', 'description', 'website', 'agree', 'client_id',
                'client_secret', 'client_type', 'authorization_grant_type',
                'redirect_uris'))
