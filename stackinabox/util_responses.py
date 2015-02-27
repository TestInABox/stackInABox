"""
Stack-In-A-Box: Python Responses Support
"""
import logging
import re

import responses

from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


def responses_callback(request):
    method = request.method
    headers = request.headers
    uri = request.url
    return StackInABox.call_into(method,
                                 request,
                                 uri,
                                 headers)


def responses_registration(uri):
    logger.debug('Registering Stack-In-A-Box at {0} under Python Responses'
                 .format(uri))
    StackInABox.update_uri(uri)
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
