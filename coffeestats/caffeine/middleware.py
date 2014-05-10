from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote_plus


class EnforceTimezoneMiddleware(object):
    """
    Middleware to enforce that users have a time zone set.

    """
    def process_request(self, request):
        """
        Redirects to the time zone selection vie and passes the originally
        requested URL to that view if the current user does not have a time
        zone set.

        :param HttpRequest request: the current request
        :return: redirect or None
        """
        timezonepath = reverse('selecttimezone')
        if (request.user.is_authenticated() and
                not request.user.timezone and
                not request.path.startswith(timezonepath)):
            return HttpResponseRedirect(
                timezonepath + '?next=' +
                urlquote_plus(request.get_full_path()))
