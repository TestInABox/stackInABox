"""
Stack-In-A-Box: HTTPretty Support
"""
import io
import logging
import re
import types

import requests
import requests_mock

from stackinabox.stack import StackInABox


logger = logging.getLogger(__name__)


class MockRequestFileObject(object):

    def __init__(self, data_to_wrap):
        self.data = data_to_wrap
        self.is_str = isinstance(self.data, types.StringTypes)
        self.is_bytes = isinstance(self.data, bytes)
        self.is_text = self.is_str or self.is_bytes
        self.is_file = isinstance(self.data, types.FileType)
        self.is_generator = isinstance(self.data, types.GeneratorType)
        self.is_iterable = hasattr(self.data, '__iter__')

        if not (self.is_str or
                self.is_bytes or
                self.is_generator):
            raise ValueError(
                'Message body must by str, bytes, generator, iterable, '
                'or file type')

    def iterable_to_generator(self):
        for next_chunk in self.data:
            yield next_chunk

    def iterable_text(self, chunk_size):
        data_position = 0

        while data_position < len(self.data):
            end_position = data_position + chunk_size
            yield self.data[data_position:end_position]

            data_position = end_position

    def read(self, chunk_size):
        if self.is_text:
            try:
                next_chunk = self.iterable_text(chunk_size)
                return next_chunk
            except StopIteration:
                return None

        if self.is_file:
            return self.data.read(chunk_size)

        # Must be either a generator or an iterable
        if self.is_generator:
            try:
                next_chunk = self.data.next()
                return next_chunk
            except StopIteration:
                return None

        if self.is_iterable:
            try:
                next_chunk = self.iterable_to_generator()
                return next_chunk
            except StopIteration:
                return None

        return None

    def close(self):
        self.data_position = 0

    def release_conn(self):
        pass

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

        response = requests.Response()
        response.url = request.url
        response.headers['server'] = 'StackInABox/Requests-Mock'
        response.headers.update(output_headers)
        response.status_code, response.reason =\
            RequestMockCallable.split_status(status_code)


        if body is not None:
            response.raw = MockRequestFileObject(body)

        return response


def requests_mock_registration(uri, session):
    logger.debug('Registering Stack-In-A-Box at {0} under Python Requests-Mock'
                 .format(uri))

    StackInABox.update_uri(uri)
    StackInABox.hold_onto('adapter', requests_mock.Adapter())
    StackInABox.hold_out('adapter').add_matcher(RequestMockCallable(uri))

    session.mount('http://{0}'.format(uri), StackInABox.hold_out('adapter'))
    session.mount('https://{0}'.format(uri), StackInABox.hold_out('adapter'))
