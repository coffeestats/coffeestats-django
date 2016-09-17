from __future__ import unicode_literals

import json

from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.test import TestCase
from mock import Mock, MagicMock

from core.oauth import CoffeestatsServer
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


class CoffeestatsServerTest(TestCase):
    def test_validate_authorization_request(self):
        testvalidator = Mock()
        typehandler = MagicMock()
        server = CoffeestatsServer(testvalidator)
        server.response_types['code'] = typehandler
        server.validate_authorization_request(
            'http://test.example.org/oauth2/authorize/?response_type=code',
            http_method='GET', body='', headers={})
        typehandler.validate_authorization_request.assert_called()
        args = typehandler.validate_authorization_request.call_args
        self.assertIsNotNone(args[0][0].scopes)
        self.assertEqual(args[0][0].scopes, [])
