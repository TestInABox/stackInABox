import json
import logging
import re

import requests
import requests_mock.response
import six

from stackinabox.stack import StackInABox
from stackinabox.util.tools import CaseInsensitiveDict

logger = logging.getLogger(__name__)


class RequestMockCallable(object):
    """Requests-Mock Callable object.

    Python callable object to interact with Requests-Mock
    """

    def __init__(self, uri):
        """object initialization

        :param uri: URI to match against
        """
        self.regex = re.compile(
            '(http)?s?(://)?{0}:?(\d+)?/'.format(uri), re.I)

    def __call__(self, request):
        """object callable interface.

        :param request: Python requests Request object

        :returns: Python requests Response object if handled
                  otherwise None
        """
        uri = request.url
        if self.regex.match(uri):
            return self.handle(request, uri)

        else:
            # We don't handle it
            return None

    @staticmethod
    def get_reason_for_status(status_code):
        """Lookup the HTTP reason text for a given status code.

        :param status_code: int - HTTP status code

        :returns: string - HTTP reason text
        """

        if status_code in requests.status_codes.codes:
            return requests.status_codes._codes[status_code][0].replace('_',
                                                                        ' ')
        else:
            return 'Unknown status code - {0}'.format(status_code)

    @staticmethod
    def split_status(status):
        """Split a HTTP Status and Reason code string into a tuple.

        :param status string containing the status and reason text or
                             the integer of the status code

        :returns: tuple - (int, string) containing the integer status code
                          and reason text string
        """

        # If the status is an integer, then lookup the reason text
        if isinstance(status, int):
            return (status, RequestMockCallable.get_reason_for_status(
                status))

        # otherwise, ensure it is a string and try to split it based on the
        # standard HTTP status and reason text format
        elif isinstance(status, str) or isinstance(status, bytes):
            code, reason = status.split(' ', 1)
            return (code, reason)

        # otherwise, return with a default reason code
        else:
            return (status, 'Unknown')

    def handle(self, request, uri):
        """Request handler interface.

        :param request: Python requests Request object
        :param uri: URI of the request
        """

        # Convert the call over to Stack-In-A-Box
        method = request.method
        headers = CaseInsensitiveDict()
        request_headers = CaseInsensitiveDict()
        request_headers.update(request.headers)
        request.headers = request_headers
        stackinabox_result = StackInABox.call_into(method,
                                                   request,
                                                   uri,
                                                   headers)

        # reformat the result for easier use
        status_code, output_headers, body = stackinabox_result

        text_data = None
        content_data = None
        body_data = None

        # if the body is a string-type...
        if isinstance(body, six.string_types):
            # Try to convert it to JSON
            text_data = body

        # if the body is binary, then it's the content
        elif isinstance(body, six.binary_type):
            content_data = body

        # by default, it's just body data
        else:
            # default to body data
            body_data = body

        # build the Python requests' Response object
        return requests_mock.response.create_response(
            request,
            headers=output_headers,
            status_code=status_code,
            body=body_data,
            json=None,
            text=text_data,
            content=content_data
        )
