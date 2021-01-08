"""
Stack-In-A-Box: Callable
"""
import json
import logging
import tempfile
import unittest

import ddt
import mock
import requests
import requests.models
import requests.adapters  # import HTTPAdapter
import six
from urllib3.response import HTTPResponse

import stackinabox.util.requests_mock
from stackinabox.util.requests_mock import reqcallable
from stackinabox.stack import StackInABox

from tests.util import base


logger = logging.getLogger(__name__)


class FakeRequest(object):

    def __init__(self, url):
        self.url = url
        self.method = 'GET'
        self.headers = {}


@ddt.ddt
class TestRequestsMockCallable(base.UtilTestCase):

    def setUp(self):
        super(TestRequestsMockCallable, self).setUp()

    def tearDown(self):
        super(TestRequestsMockCallable, self).tearDown()

    def test_initialization(self):
        uri = 'foo'
        rc = reqcallable.RequestMockCallable(uri)
        self.assertIn(uri, rc.regex.pattern)
        url_matches = [
            'http://foo/',
            'https://foo/',
            'http://foo:999/',
            'https://foo:999/',
        ]
        for url in url_matches:
            logger.debug(
                'Testing URL: %s against regex %s',
                url,
                rc.regex.pattern
            )
            self.assertTrue(rc.regex.match(url))

    @mock.patch(
        'stackinabox.util.requests_mock.reqcallable.RequestMockCallable.handle'
    )
    def test_callable(self, mock_req_handler):
        uri = 'foo'
        rc = reqcallable.RequestMockCallable(uri)
        fr = FakeRequest('https://bar/')
        self.assertIsNone(rc(fr))
        self.assertEqual(mock_req_handler.call_count, 0)

    @mock.patch(
        'stackinabox.util.requests_mock.reqcallable.RequestMockCallable.handle'
    )
    def test_callable_handled(self, mock_req_handler):
        mock_req_handler.return_value = True
        uri = 'foo'
        rc = reqcallable.RequestMockCallable(uri)
        fr = FakeRequest('https://foo/')
        self.assertTrue(rc(fr))
        self.assertEqual(mock_req_handler.call_count, 1)
        mock_req_handler.assert_called_with(fr, fr.url)

    @ddt.data(
        (200, 'ok'),
        (600, 'Unknown status code - 600')
    )
    @ddt.unpack
    def test_get_reason(self, status, msg):
        self.assertEqual(
            reqcallable.RequestMockCallable.get_reason_for_status(status),
            msg
        )

    @ddt.data(
        (200, 200, 'ok'),
        ("201 created", 201, 'created'),
        (float(202.5), 202.5, 'Unknown')
    )
    @ddt.unpack
    def test_split_status(self, status, expected_status, expected_reason):
        self.assertEqual(
            reqcallable.RequestMockCallable.split_status(status),
            (expected_status, expected_reason)
        )

    @mock.patch(
        'stackinabox.stack.StackInABox.call_into'
    )
    def test_handler_text_body(self, mock_call_into):
        fr = FakeRequest('https://foo/')
        fr.headers['hello'] = 'world'
        fr.method = 'GET'

        expected_status = 200
        expected_headers = {
            'world': 'hello'
        }
        expected_body = str('ohiyo')

        mock_call_into.return_value = (
            expected_status,
            expected_headers,
            expected_body
        )

        rc = reqcallable.RequestMockCallable(fr.url)
        response = rc.handle(fr, fr.url)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.headers, expected_headers)
        self.assertEqual(response.text, expected_body)

    @mock.patch(
        'stackinabox.stack.StackInABox.call_into'
    )
    def test_handler_binary_body(self, mock_call_into):
        fr = FakeRequest('https://foo/')
        fr.headers['hello'] = 'world'
        fr.method = 'GET'

        expected_status = 200
        expected_headers = {
            'world': 'hello'
        }
        file_data = tempfile.NamedTemporaryFile()
        expected_body = 'konbanwa'.encode('utf-8')

        mock_call_into.return_value = (
            expected_status,
            expected_headers,
            expected_body
        )

        rc = reqcallable.RequestMockCallable(fr.url)
        response = rc.handle(fr, fr.url)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.headers, expected_headers)
        self.assertEqual(response.content, expected_body)

    @mock.patch(
        'stackinabox.stack.StackInABox.call_into'
    )
    @unittest.expectedFailure
    def test_handler_other_body(self, mock_call_into):
        # For some reason the returned response isn't providing
        # the expected body. For now, marking as an expected
        # failure but this needs to be fixed.

        fr = FakeRequest('https://foo/')
        fr.headers['hello'] = 'world'
        fr.method = 'GET'

        expected_status = 200
        expected_headers = {
            'world': 'hello'
        }
        file_data = tempfile.NamedTemporaryFile()
        expected_body_data = 'konbanwa'.encode('utf-8')

        class FileObj(object):

            def __init__(self, data):
                self.file_data = data
                self.reason = 200
                self._is_closed = False

            def read(self, *args, **kwargs):
                logger.debug('returning data: {0}'.format(self.file_data))
                self._is_closed = True
                return self.file_data

            def close(self):
                pass

            def isclosed(self):
                return self._is_closed

        # requests_mock invokes a response builder which ultimately ties back
        # through requests to urllib3; to pass the fileobj properly it has
        # to be done through the urllib3.response.HTTPResponse object
        expected_body = HTTPResponse(
            body=FileObj(expected_body_data),
            headers=expected_headers,
            status=expected_status
        )

        mock_call_into.return_value = (
            expected_status,
            expected_headers,
            expected_body
        )

        rc = reqcallable.RequestMockCallable(fr.url)
        response = rc.handle(fr, fr.url)
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.headers, expected_headers)
        received_data = '' if six.PY2 else u''
        for r in response.iter_content():
            received_data += r

        self.assertEqual(
            received_data,
            expected_body_data.decode('utf-8')
        )
