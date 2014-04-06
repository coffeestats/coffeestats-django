from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.http import urlquote_plus


class EnforceTimezoneMiddleware(object):
    def process_request(self, request):
        timezonepath = reverse('selecttimezone')
        if (request.user.is_authenticated() and
                not request.user.timezone and
                not request.path.startswith(timezonepath)):
            return HttpResponseRedirect(
                timezonepath + '?next=' +
                urlquote_plus(request.get_full_path()))
