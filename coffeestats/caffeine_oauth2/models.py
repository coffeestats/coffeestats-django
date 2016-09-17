from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import AbstractApplication


@python_2_unicode_compatible
class CoffeestatsApplication(AbstractApplication):
    """
    Custom application model for OAuth2 clients.

    """
    logo = models.ImageField(
        verbose_name=_('application logo'), upload_to='appimages')
    agree = models.BooleanField(verbose_name=_('API usage agreement'))
    website = models.URLField(
        verbose_name=_('application website'),
        help_text=_(
            'A website where interested users can find more information about'
            'the application and where to download it for their own use.'
        )
    )
    description = models.TextField(max_length=8192)

    class Meta(AbstractApplication.Meta):
        verbose_name = _('Coffeestats OAuth2 application')
        verbose_name_plural = _('Coffeestats OAuth2 applications')

    def __str__(self):
        return "{} {}".format(self.name, self.client_id)
