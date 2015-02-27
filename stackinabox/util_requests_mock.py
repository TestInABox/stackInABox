"""
Stack-In-A-Box: HTTPretty Support
"""
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


def requests_mock_session_registration(uri, session):
    logger.debug('Registering Stack-In-A-Box at {0} under Python Requests-Mock'
                 .format(uri))
    logger.debug('Session has id {0}'.format(id(session)))

    StackInABox.update_uri(uri)
    StackInABox.hold_onto('adapter', requests_mock.Adapter())
    StackInABox.hold_out('adapter').add_matcher(RequestMockCallable(uri))

    session.mount('http://{0}'.format(uri), StackInABox.hold_out('adapter'))
    session.mount('https://{0}'.format(uri), StackInABox.hold_out('adapter'))


def requests_mock_registration(uri):
    requests_mock_session_registration(uri,
                                       local_sessions.session)


def requests_request(method, url,**kwargs):
    session = local_sessions.session
    response = session.request(method=method, url=url, **kwargs)
    session.close()
    return response

def requests_get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return requests_request('get', url, **kwargs)

def requests_options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return reuests_request('options', url, **kwargs)

def requests_head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return reuests_request('options', url, **kwargs)

def requests_post(url, data=None, json=None, **kwargs):
    return requests_request('post', url, data=data, json=json, **kwargs)

def requests_put(url, data=None, **kwargs):
    return requests_request('put', url, data=data, **kwargs)

def requests_patch(url, data=None, **kwargs):
    return requests_request('patch', url, data=data, **kwargs)

def requests_delete(url, **kwargs):
    return requests_request('delete', url, **kwargs)
    


class requests_session(requests.sessions.SessionRedirectMixin):

    def __init__(self):
        logger.debug('Session wrapper has id {0}'.format(id(self)))

    def __enter__(self):
        return local_sessions.session

    def __exit__(self, *args):
        local_sessions.session.close()

    def prepare_request(self, request):
        return local_sessions.session.prepare_request(request)

    def request(*args, **kwargs):
        return local_session.session.request(*args, **kwargs)

    def get(*args, **kwargs):
        return local_session.session.get(*args, **kwargs)

    def options(*args, **kwargs):
        return local_session.session.options(*args, **kwargs)

    def head(*args, **kwargs):
        return local_session.session.head(*args, **kwargs)

    def post(*args, **kwargs):
        return local_session.session.post(*args, **kwargs)

    def put(*args, **kwargs):
        return local_session.session.put(*args, **kwargs)

    def patch(*args, **kwargs):
        return local_session.session.patch(*args, **kwargs)

    def delete(*args, **kwargs):
        return local_session.session.delete(*args, **kwargs)

    def send(*args, **kwargs):
        return local_session.session.send(*args, **kwargs)

    def merge_environment_settings(*args, **kwargs):
        return local_session.session.merge_environment_settings(*args, **kwargs)

    def get_adapter(*args, **kwargs):
        return local_session.session.get_adapter(*args, **kwargs)

    def close(*args, **kwargs):
        return local_session.session.close(*args, **kwargs)

    def mount(*args, **kwargs):
        return local_session.session.mount(*args, **kwargs)

    def __getstate__(*args, **kwargs):
        return local_session.session.__getstate__(*args, **kwargs)

    def __setstate__(*args, **kwargs):
        return local_session.session.__setstate__(*args, **kwargs)


def get_session():
    return local_sessions.session


class activate(object):

    def __init__(self):
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
        logger.debug('Stopping session with id {0}'
                     .format(id(local_sessions.session)))
        requests.session = self.__replacements['requests.session']
        requests.Session = self.__replacements['requests.Session']
        requests.sessions.Session = self.__replacements['requests.sessions.Session']
        
        requests.delete = self.__replacements['requests.delete']
        requests.patch = self.__replacements['requests.patch']
        requests.put = self.__replacements['requests.put']
        requests.post = self.__replacements['requests.post']
        requests.head = self.__replacements['requests.head']
        requests.options = self.__replacements['requests.options']
        requests.get = self.__replacements['requests.get']
        requests.request = self.__replacements['requests.request']

        local_sessions.session = Session()


local_sessions = threading.local()
local_sessions.session = Session()
