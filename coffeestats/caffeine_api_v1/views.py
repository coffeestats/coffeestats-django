import json

from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
)
from django.utils.http import urlquote_plus
from django.contrib.auth.decorators import login_required

from caffeine.models import User


@login_required
def random_users(request):
    if 'count' not in request.GET:
        return HttpResponseBadRequest('missing parameter "count"')
    data = []
    for user in User.objects.random_users(int(request.GET['count'])):
        data.append({
            'username': user.username,
            'name': user.get_full_name(),
            'location': user.location,
            'profile': request.build_absolute_uri(
                reverse('profile')) + '?u=' + urlquote_plus(
                user.username),
            'coffees': user.coffees,
            'mate': user.mate})
    return HttpResponse(json.dumps(data), content_type="text/json")
