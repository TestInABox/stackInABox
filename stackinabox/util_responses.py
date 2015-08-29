"""
Stack-In-A-Box: Python Responses Support
"""
import logging
import re

import responses

from stackinabox.stack import StackInABox
from stackinabox.utils import CaseInsensitiveDict


logger = logging.getLogger(__name__)


def responses_callback(request):
    """Responses Request Handler

    Converts a call intercepted by Responses to
    the Stack-In-A-Box infrastructure

    :parameter: request - request object

    :returns: tuple - (int, dict, string) containing:
                      int - the HTTP response status code
                      dict - the headers for the HTTP response
                      string - HTTP string response
    """
    method = request.method
    headers = CaseInsensitiveDict()
    request_headers = CaseInsensitiveDict()
    request_headers.update(request.headers)
    request.headers = request_headers
    uri = request.url
    return StackInABox.call_into(method,
                                 request,
                                 uri,
                                 headers)


def responses_registration(uri):
    """Responses handler registration

    Registers a handler for a given URI with Responses
    so that it can be intercepted and handed to
    Stack-In-A-Box.

    :parameter: uri - URI used for the base of the HTTP requests

    :returns: n/a
    """

    # log the URI that is used to access the Stack-In-A-Box services
    logger.debug('Registering Stack-In-A-Box at {0} under Python Responses'
                 .format(uri))
    # tell Stack-In-A-Box what URI to match with
    StackInABox.update_uri(uri)

    # Build the regex for the URI and register all HTTP verbs
    # with Responses
    regex = re.compile('(http)?s?(://)?{0}:?(\d+)?/'.format(uri),
                       re.I)
    METHODS = [
        responses.DELETE,
        responses.GET,
        responses.HEAD,
        responses.OPTIONS,
        responses.PATCH,
        responses.POST,
        responses.PUT
    ]
    for method in METHODS:
        responses.add_callback(method,
                               regex,
                               callback=responses_callback)
