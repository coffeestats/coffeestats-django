import json

from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.test import TestCase

from core.utils import json_response


class JsonResponseTest(TestCase):

    def test_wrap_plain_function(self):
        def testfun(request):
            return ['bla']
        respfun = json_response(testfun)
        result = respfun(HttpRequest)
        self.assertIsInstance(result, HttpResponse)
        self.assertEqual(result['content-type'], 'text/json')
        self.assertEqual(
            json.loads(respfun(HttpRequest()).content),
            ['bla']
        )

    def test_wrap_httpresponse(self):
        testresp = HttpResponse('foo')

        def testfun(request):
            return testresp
        respfun = json_response(testfun)
        self.assertEqual(respfun(HttpRequest()), testresp)
