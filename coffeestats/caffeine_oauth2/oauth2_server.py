"""
This module provides coffeestats specific oauth2 customizations.
"""
from oauthlib.common import Request
from oauthlib.oauth2.rfc6749.endpoints.base import \
    catch_errors_and_unavailability
from oauthlib.oauth2.rfc6749.endpoints.pre_configured import Server


class CoffeestatsServer(Server):
    """
    Modified version of the pre configured OAuth2 server from oauthlib.

    """

    @catch_errors_and_unavailability
    def validate_authorization_request(self, uri, http_method='GET', body=None,
                                       headers=None):
        """Extract response_type and route to the designated handler."""
        request = Request(
            uri, http_method=http_method, body=body, headers=headers)
        request.scopes = []
        response_type_handler = self.response_types.get(
            request.response_type, self.default_response_type_handler)
        return response_type_handler.validate_authorization_request(request)
