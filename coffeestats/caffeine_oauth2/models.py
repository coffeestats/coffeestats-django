from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from oauth2_provider.models import AbstractApplication


@python_2_unicode_compatible
class CoffeestatsApplication(AbstractApplication):
    """
    Custom application model for OAuth2 clients.

    """
    logo = models.ImageField(
        verbose_name=_('application logo'), upload_to='appimages')
    agree = models.BooleanField(
        verbose_name=_('accept API usage agreement'),
        help_text=mark_safe(
            _('You have to agree to the <a href="%s">API usage agreement</a>'
              ' to use our APIs.') % settings.API_USAGE_AGREEMENT))
    website = models.URLField(
        verbose_name=_('application website'),
        help_text=_(
            'A website where interested users can find more information about'
            'the application and where to download it for their own use.'
        )
    )
    description = models.TextField(max_length=8192)
    approved = models.BooleanField(
        verbose_name=_('approved by coffeestats team'),
        default=False
    )
    approved_on = models.DateTimeField(
        verbose_name=_('time of approval by the coffeestats team'),
        blank=True, null=True
    )
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    class Meta(AbstractApplication.Meta):
        verbose_name = _('Coffeestats OAuth2 application')
        verbose_name_plural = _('Coffeestats OAuth2 applications')
        permissions = (
            ('can_approve', _('Can approve applications')),
        )

    def __str__(self):
        return "{} {}".format(self.name, self.client_id)

    def approve(self, approver):
        self.approved = True
        self.approved_by = approver
        self.approved_on = timezone.now()
        return self

    def reject(self):
        self.delete()
