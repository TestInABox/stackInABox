"""
Stack-In-A-Box: HTTPretty Support
"""
import logging
import re

from httpretty import register_uri
from httpretty.http import HttpBaseClass

from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


def httpretty_callback(request, uri, headers):
    method = request.method
    return StackInABox.call_into(method,
                                 request,
                                 uri,
                                 headers)


def httpretty_registration(uri):
    logger.debug('Registering Stack-In-A-Box at {0} under Python HTTPretty'
                 .format(uri))
    StackInABox.update_uri(uri)
    regex = re.compile('(http)?s?(://)?{0}:?(\d+)?/'.format(uri),
                       re.I)
    for method in HttpBaseClass.METHODS:
        register_uri(method, regex, body=httpretty_callback)
