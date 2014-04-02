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


@register.simple_tag(takes_context=True)
def ontherunurl(context, user=None):
    if user is None:
        user = context['profileuser']
    request = context['request']
    return request.build_absolute_uri(reverse('ontherun', kwargs={
        'username': user.username,
        'token': user.token}))


@register.filter
def messagetags(value, tag):
    return [message for message in value if tag in message.tags]
