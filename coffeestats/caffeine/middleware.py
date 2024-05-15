from urllib.parse import quote_plus

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


class EnforceTimezoneMiddleware:
    """
    Middleware to enforce that users have a time zone set.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Redirects to the time zone selection vie and passes the originally
        requested URL to that view if the current user does not have a time
        zone set.

        :param HttpRequest request: the current request
        :return: redirect or None
        """
        timezone_path = reverse("select_timezone")
        if (
            request.user.is_authenticated
            and not request.user.timezone
            and not request.path.startswith(settings.STATIC_URL)
            and not request.path.startswith(timezone_path)
        ):
            return HttpResponseRedirect(
                timezone_path + "?next=" + quote_plus(request.get_full_path())
            )
        return self.get_response(request)
