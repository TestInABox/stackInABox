"""
Stack-In-A-Box: HTTPretty Support
"""
import io
import logging
import re
import sys
import types

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.response import HTTPResponse
import requests_mock

from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


class RequestMockCallable(object):

    def __init__(self, uri):
        self.regex = re.compile(
            '(http)?s?(://)?{0}:?(\d+)?/'.format(uri), re.I)

    def __call__(self, request):
        uri = request.url
        if self.regex.match(uri):
            return self.handle(request, uri)

        else:
            # We don't handle it
            return None

    @staticmethod
    def __is_string_type(s):
        
        if int(sys.version[0]) > 2:
            return isinstance(s, str)
            
        else:
            return isinstance(s, types.StringTypes)

    @staticmethod
    def get_reason_for_status(status_code):

        if status_code in requests.status_codes.codes:
            return requests.status_codes._codes[status_code][0].replace('_', ' ')
        else:
            return 'Unknown status code - {0}'.format(status_code)

    @staticmethod
    def split_status(status):
        if isinstance(status, int):
            return (status, RequestMockCallable.get_reason_for_status(
                status))

        elif isinstance(status, str) or isinstance(status, bytes):
            code, reason = status.split(' ', 1)
            return (code, reason)

        else:
            return (status, 'Unknown')


    def handle(self, request, uri):
        method = request.method
        headers = request.headers
        stackinabox_result = StackInABox.call_into(method,
                                                   request,
                                                   uri,
                                                   headers)

        status_code, output_headers, body = stackinabox_result
        if RequestMockCallable.__is_string_type(body):
            body = body.encode()

        response = HTTPResponse(status=status_code,
                                body=io.BytesIO(body),
                                headers=output_headers,
                                preload_content=False)

        adapter = HTTPAdapter()
        response = adapter.build_response(request, response)

        return response


def requests_mock_registration(uri, session):
    logger.debug('Registering Stack-In-A-Box at {0} under Python Requests-Mock'
                 .format(uri))

    StackInABox.update_uri(uri)
    StackInABox.hold_onto('adapter', requests_mock.Adapter())
    StackInABox.hold_out('adapter').add_matcher(RequestMockCallable(uri))

    session.mount('http://{0}'.format(uri), StackInABox.hold_out('adapter'))
    session.mount('https://{0}'.format(uri), StackInABox.hold_out('adapter'))
