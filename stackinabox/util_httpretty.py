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
    """httpretty request handler.

    converts a call intercepted by httpretty to
    the stack-in-a-box infrastructure

    :param request: request object
    :param uri: the uri of the request
    :param headers: headers for the response

    :returns: tuple - (int, dict, string) containing:
                      int - the http response status code
                      dict - the headers for the http response
                      string - http string response

    """
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
    """httpretty handler registration.

    registers a handler for a given uri with httpretty
    so that it can be intercepted and handed to
    stack-in-a-box.

    :param uri: uri used for the base of the http requests

    :returns: n/a

    """

    # add the stack-in-a-box specific response codes to
    # http's status information
    status_data = {
        595: 'StackInABoxService - Unknown Route',
        596: 'StackInABox - Exception in Service Handler',
        597: 'StackInABox - Unknown Service'
    }
    for k, v in six.iteritems(status_data):
        if k not in httpretty.http.STATUSES:
            httpretty.http.STATUSES[k] = v

    # log the uri that is used to access the stack-in-a-box services
    logger.debug('Registering Stack-In-A-Box at {0} under Python HTTPretty'
                 .format(uri))
    # tell stack-in-a-box what uri to match with
    StackInABox.update_uri(uri)

    # build the regex for the uri and register all http verbs
    # with httpretty
    regex = re.compile('(http)?s?(://)?{0}:?(\d+)?/'.format(uri),
                       re.I)
    for method in HttpBaseClass.METHODS:
        register_uri(method, regex, body=httpretty_callback)
