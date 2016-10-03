from django.test import TestCase
from mock import Mock, MagicMock

from caffeine_oauth2.oauth2_server import CoffeestatsServer


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
