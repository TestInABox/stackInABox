"""
Stack-In-A-Box: HTTPretty Support
"""
import logging
import re

from httpretty import register_uri
from httpretty.http import HttpBaseClass
import httpretty.http
import six

from stackinabox.stack import StackInABox
from stackinabox.utils import CaseInsensitiveDict


logger = logging.getLogger(__name__)


def httpretty_callback(request, uri, headers):
    method = request.method
    response_headers = CaseInsensitiveDict()
    response_headers.update(headers)
    request_headers = CaseInsensitiveDict()
    request_headers.update(request.headers)
    request.headers = request_headers
    return StackInABox.call_into(method,
                                 request,
                                 uri,
                                 response_headers)


def httpretty_registration(uri):

    status_data = {
        595: 'StackInABoxService - Unknown Route',
        596: 'StackInABox - Exception in Service Handler',
        597: 'StackInABox - Unknown Service'
    }
    for k, v in six.iteritems(status_data):
        if k not in httpretty.http.STATUSES:
            httpretty.http.STATUSES[k] = v

    logger.debug('Registering Stack-In-A-Box at {0} under Python HTTPretty'
                 .format(uri))
    StackInABox.update_uri(uri)
    regex = re.compile('(http)?s?(://)?{0}:?(\d+)?/'.format(uri),
                       re.I)
    for method in HttpBaseClass.METHODS:
        register_uri(method, regex, body=httpretty_callback)
