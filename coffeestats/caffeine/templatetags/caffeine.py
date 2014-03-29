from django import template
from django.utils.http import urlquote_plus
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def publicurl(context, username=None):
    if username is None:
        username = context['profileuser'].username
    request = context['request']
    return '%s?u=%s' % (request.build_absolute_uri(reverse('profile')),
                        urlquote_plus(username))
