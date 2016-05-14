"""
Stack-In-A-Box: Requests-Mock Support
"""
from __future__ import absolute_import

import contextlib
import functools
import io
import logging
import re
import sys
import threading
import types

import mock
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.response import HTTPResponse
import requests_mock
import requests_mock.compat
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

        json_data = None
        text_data = None
        content_data = None
        body_data = None

        # if the body is a string-type...
        if isinstance(body, six.string_types):
            # Try to convert it to JSON
            text_data = body
            try:
                json_data = json.dumps(text_data)
                text_data = json_data
            except:
                json_data = None
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
            json=json_data,
            text=text_data,
            content=content_data
        )


def requests_mock_session_registration(uri, session):
    """Requests-mock registration with a specific Session.

    :param uri: base URI to match against
    :param session: Python requests' Session object

    :returns: n/a
    """
    # log the URI that is used to access the Stack-In-A-Box services
    logger.debug('Registering Stack-In-A-Box at {0} under Python Requests-Mock'
                 .format(uri))
    logger.debug('Session has id {0}'.format(id(session)))

    # tell Stack-In-A-Box what URI to match with
    StackInABox.update_uri(uri)

    # Create a Python Requests Adapter object for handling the session
    StackInABox.hold_onto('adapter', requests_mock.Adapter())
    # Add the Request handler object for the URI
    StackInABox.hold_out('adapter').add_matcher(RequestMockCallable(uri))

    # Tell the session about the adapter and the URI
    session.mount('http://{0}'.format(uri), StackInABox.hold_out('adapter'))
    session.mount('https://{0}'.format(uri), StackInABox.hold_out('adapter'))


def requests_mock_registration(uri):
    """Requests-mock registrationn.

    :param uri: base URI to match against

    :returns: n/a
    """

    # Use a global session object, and then use the session variant
    requests_mock_session_registration(uri,
                                       local_sessions.session)


def requests_request(method, url, **kwargs):
    """Requests-mock requests.request wrapper."""
    session = local_sessions.session
    response = session.request(method=method, url=url, **kwargs)
    session.close()
    return response


def requests_get(url, **kwargs):
    """Requests-mock requests.get wrapper."""
    kwargs.setdefault('allow_redirects', True)
    return requests_request('get', url, **kwargs)


def requests_options(url, **kwargs):
    """Requests-mock requests.options wrapper."""
    kwargs.setdefault('allow_redirects', True)
    return reuests_request('options', url, **kwargs)


def requests_head(url, **kwargs):
    """Requests-mock requests.head wrapper."""
    kwargs.setdefault('allow_redirects', False)
    return reuests_request('options', url, **kwargs)


def requests_post(url, data=None, json=None, **kwargs):
    """Requests-mock requests.post wrapper."""
    return requests_request('post', url, data=data, json=json, **kwargs)


def requests_put(url, data=None, **kwargs):
    """Requests-mock requests.put wrapper."""
    return requests_request('put', url, data=data, **kwargs)


def requests_patch(url, data=None, **kwargs):
    """Requests-mock requests.patch wrapper."""
    return requests_request('patch', url, data=data, **kwargs)


def requests_delete(url, **kwargs):
    """Requests-mock requests.delete wrapper."""
    return requests_request('delete', url, **kwargs)


class requests_session(requests.sessions.SessionRedirectMixin):
    """Requests-mock requests.Session wrapper."""

    def __init__(self):
        logger.debug('Session wrapper has id {0}'.format(id(self)))

    def __enter__(self):
        """requests.session.Session context entry wrapper."""
        return local_sessions.session

    def __exit__(self, *args):
        """requests.session.Session context exit wrapper."""
        local_sessions.session.close()

    def prepare_request(self, request):
        """Pyton requests.session.Session.prepare_request wrapper."""
        return local_sessions.session.prepare_request(request)

    def request(*args, **kwargs):
        """requests.session.Session.request wrapper."""
        return local_session.session.request(*args, **kwargs)

    def get(*args, **kwargs):
        """requests.session.Session.get wrapper."""
        return local_session.session.get(*args, **kwargs)

    def options(*args, **kwargs):
        """requests.session.Session.options wrapper."""
        return local_session.session.options(*args, **kwargs)

    def head(*args, **kwargs):
        """requests.session.Session.head wrapper."""
        return local_session.session.head(*args, **kwargs)

    def post(*args, **kwargs):
        """requests.session.Session.post wrapper."""
        return local_session.session.post(*args, **kwargs)

    def put(*args, **kwargs):
        """requests.session.Session.put wrapper."""
        return local_session.session.put(*args, **kwargs)

    def patch(*args, **kwargs):
        """requests.session.Session.patch wrapper."""
        return local_session.session.patch(*args, **kwargs)

    def delete(*args, **kwargs):
        """requests.session.Session.delete wrapper."""
        return local_session.session.delete(*args, **kwargs)

    def send(*args, **kwargs):
        """requests.session.Session.send wrapper."""
        return local_session.session.send(*args, **kwargs)

    def merge_environment_settings(*args, **kwargs):
        """requests.session.Session.merge_environment_settings wrapper."""
        return local_session.session.merge_environment_settings(*args,
                                                                **kwargs)

    def get_adapter(*args, **kwargs):
        """requests.session.Session.get_adapter wrapper."""
        return local_session.session.get_adapter(*args, **kwargs)

    def close(*args, **kwargs):
        """requests.session.Session.close wrapper."""
        return local_session.session.close(*args, **kwargs)

    def mount(*args, **kwargs):
        """requests.session.Session.mount wrapper."""
        return local_session.session.mount(*args, **kwargs)

    def __getstate__(*args, **kwargs):
        """requests.session.Session.__getstate__ wrapper."""
        return local_session.session.__getstate__(*args, **kwargs)

    def __setstate__(*args, **kwargs):
        """requests.session.Session.__setstate__ wrapper."""
        return local_session.session.__setstate__(*args, **kwargs)


def get_session():
    """Access the global session object."""
    return local_sessions.session


class activate(object):
    """Requests-mock context object for Stack-In-A-Box."""

    def __init__(self):
        # Keep track of all the original functions that will
        # get replaced during a context operation
        self.__replacements = {
            'requests.request': requests.request,
            'requests.get': requests.get,
            'requests.options': requests.options,
            'requests.head': requests.head,
            'requests.post': requests.post,
            'requests.put': requests.put,
            'requests.patch': requests.patch,
            'requests.delete': requests.delete,
            'requests.session': requests.session,
            'requests.Session': requests.Session,
            'requests.sessions.Session': requests.sessions.Session
        }

    def __enter__(self):
        """Setup the context to use the Stack-In-A-Box variants."""
        logger.debug('Using session with id {0}'
                     .format(id(local_sessions.session)))
        requests.request = requests_request
        requests.get = requests_get
        requests.options = requests_options
        requests.head = requests_head
        requests.post = requests_post
        requests.put = requests_put
        requests.patch = requests_patch
        requests.delete = requests_delete
        requests.session = local_sessions.session
        requests.Sesssion = requests_session
        requests.sessions.Sesssion = requests_session

    def __exit__(self, exc_type, exc_value, traceback):
        """Exiting the context and restore the originals"""
        logger.debug('Stopping session with id {0}'
                     .format(id(local_sessions.session)))
        requests.session = self.__replacements['requests.session']
        requests.Session = self.__replacements['requests.Session']
        requests.sessions.Session = self.__replacements[
            'requests.sessions.Session']

        requests.delete = self.__replacements['requests.delete']
        requests.patch = self.__replacements['requests.patch']
        requests.put = self.__replacements['requests.put']
        requests.post = self.__replacements['requests.post']
        requests.head = self.__replacements['requests.head']
        requests.options = self.__replacements['requests.options']
        requests.get = self.__replacements['requests.get']
        requests.request = self.__replacements['requests.request']

        # Create a new session for next time
        local_sessions.session = Session()


# the Global session data
local_sessions = threading.local()
local_sessions.session = Session()
