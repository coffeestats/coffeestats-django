import json
from datetime import datetime, timedelta
from functools import wraps

from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import available_attrs
from django.utils.translation import ugettext as _

from core.utils import json_response

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
API_ERROR_MISSING_PARAM_TIME = _(
    "`time' field is missing. You must specify the time YYYY-mm-dd HH:MM "
    "(and optionally :SS)"
)
API_ERROR_NO_USERNAME = _('No username was given')
API_ERROR_NO_TOKEN = _('No API token was given')
API_WARNING_TIMEZONE_NOT_SET = _(
    'Your timezone is not set, please set it from the web interface!'
)


def api_token_required(func):
    """
    Decorator to force authentication with an on-the-run token.

    """
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


@csrf_exempt
@require_POST
@api_token_required
@json_response
def random_users(request, **_):
    """
    Return a list of random user data.

    :param HttpRequest request: POST request
    :return: list of users

    """
    data = []
    for user in User.objects.random_users(int(request.POST.get('count', 5))):
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
    """
    Submit a caffeinated beverage.

    :param HttpRequest request: POST request
    :param User userinfo: :py:class:`caffeine.models.User`
    :param dict messages: message dictionary
    :return: messages array or :py:class:`django.http.HttpResponseBadRequest`

    """

    ctype = request.POST.get('beverage')
    drinktime = request.POST.get('time')
    time = None
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
        if time is not None and time > datetime.now() + timedelta(minutes=1):
            messages.setdefault('error', []).append(API_ERROR_FUTURE_DATETIME)
    if 'error' in messages:
        return HttpResponseBadRequest(json.dumps(messages), 'text/json')
    data = {'date': time.date(), 'time': time.time()}
    form = SubmitCaffeineForm(userinfo, getattr(DRINK_TYPES, ctype), data)
    form.date = time.date()
    form.time = time.time()
    if not form.is_valid():
        for key in form.errors:
            messages.setdefault('error', []).extend(form.errors[key])
        return HttpResponseBadRequest(json.dumps(messages), 'text/json')
    drink = form.save()
    messages['success'] = _('Your %(drink)s has been registered!') % {
        'drink': drink
    }
    return messages
