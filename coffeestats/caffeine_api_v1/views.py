import json
from datetime import datetime
from functools import wraps

from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.views.decorators.http import (
    require_GET,
    require_POST,
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from caffeine.forms import SubmitCaffeineForm
from caffeine.models import (
    DRINK_TYPES,
    User,
)

API_ERROR_AUTH_REQUIRED = _('API operation requires authentication')
API_ERROR_FUTURE_DATETIME = _('You can not enter dates in the future!')
API_ERROR_INVALID_BEVERAGE = _(
    "`beverage' contains an invalid value. Acceptable values are `coffee'"
    " and `mate'."
)
API_ERROR_INVALID_CREDENTIALS = _('Invalid username or API token')
API_ERROR_INVALID_DATETIME = _(
    'No valid date/time information. Expected format YYYY-mm-dd HH:MM:ss'
)
API_ERROR_MISSING_PARAM_BEVERAGE = _(
    "`beverage' field missing. You must specify one of `coffee' or `mate'."
)
API_ERROR_MISSING_PARAM_COUNT = 'missing parameter "count"'
API_ERROR_MISSING_PARAM_TIME = _(
    "`time' field is missing. You must specify the time YYYY-mm-dd HH:MM "
    "(and optionally :SS)"
)
API_ERROR_NO_USERNAME = _('No username was given')
API_ERROR_NO_TOKEN = _('No API token was given')
API_WARNING_TIMEZONE_NOT_SET = _(
    'Your timezone is not set, please set it form the web interface!'
)


def json_response(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        return HttpResponse(json.dumps(result), content_type="text/json")
    return inner


def api_token_required(func):
    @wraps(func, assigned=available_attrs(func))
    def inner(request, *args, **kwargs):
        messages = {'success': False}
        if not request.POST.get('u'):
            messages.setdefault('error', []).append(API_ERROR_NO_USERNAME)
        if not request.POST.get('t'):
            messages.setdefault('error', []).append(API_ERROR_NO_TOKEN)
        if 'error' in messages:
            messages['error'].append(API_ERROR_AUTH_REQUIRED)
            return HttpResponseForbidden(
                json.dumps(messages), 'text/json')
        user = None
        try:
            user = User.objects.get(
                username=request.POST.get('u'),
                token=request.POST.get('t'))
        except:
            messages.setdefault('error', []).append(
                API_ERROR_INVALID_CREDENTIALS)
            return HttpResponseBadRequest(
                json.dumps(messages), 'text/json')
        if not user.timezone:
            messages.setdefault('warning', []).append(
                API_WARNING_TIMEZONE_NOT_SET)
        kwargs['userinfo'] = user
        kwargs['messages'] = messages
        return func(request, *args, **kwargs)
    return inner


@login_required
@require_GET
@json_response
def random_users(request):
    if 'count' not in request.GET:
        return HttpResponseBadRequest(API_ERROR_MISSING_PARAM_COUNT)
    data = []
    for user in User.objects.random_users(int(request.GET['count'])):
        data.append({
            'username': user.username,
            'name': user.get_full_name(),
            'location': user.location,
            'profile': request.build_absolute_uri(
                reverse('public', kwargs={'username': user.username})),
            'coffees': user.coffees,
            'mate': user.mate})
    return data


def _parse_drinktime(drinktime, messages):
    try:
        time = datetime.strptime(drinktime, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            time = datetime.strptime(drinktime, '%Y-%m-%d %H:%M')
        except ValueError:
            time = None
            messages.setdefault('error', []).append(API_ERROR_INVALID_DATETIME)
    return time


@csrf_exempt
@require_POST
@api_token_required
@json_response
def add_drink(request, userinfo, messages, *args, **kwargs):
    ctype = request.POST.get('beverage')
    drinktime = request.POST.get('time')
    if not ctype:
        messages.setdefault('error', []).append(
            API_ERROR_MISSING_PARAM_BEVERAGE)
    elif not hasattr(DRINK_TYPES, ctype):
        messages.setdefault('error', []).append(
            API_ERROR_INVALID_BEVERAGE)
    if not drinktime:
        messages.setdefault('error', []).append(
            API_ERROR_MISSING_PARAM_TIME)
    else:
        time = _parse_drinktime(drinktime, messages)
        if time is not None and time > datetime.now():
            messages.setdefault('error', []).append(API_ERROR_FUTURE_DATETIME)
    if 'error' in messages:
        return HttpResponseBadRequest(json.dumps(messages), 'text/json')
    data = {'date': time}
    form = SubmitCaffeineForm(userinfo, getattr(DRINK_TYPES, ctype), data)
    form.date = time
    if not form.is_valid():
        for key in form.errors:
            messages.setdefault('error', []).extend(form.errors[key])
        return HttpResponseBadRequest(json.dumps(messages), 'text/json')
    drink = form.save()
    messages['success'] = _('Your %(drink)s has been registered!') % {
        'drink': drink
    }
    return messages
