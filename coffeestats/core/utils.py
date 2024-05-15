import json
from functools import wraps

from django.http import HttpResponse


def json_response(func):
    """
    Decorator for wrapping the result of a function in a JSON response object.

    """

    @wraps(func)
    def inner(request, *args, **kwargs):
        result = func(request, *args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        return HttpResponse(json.dumps(result), content_type="text/json")

    return inner
