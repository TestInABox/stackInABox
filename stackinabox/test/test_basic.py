"""
Stack-In-A-Box: Basic Test
"""
import unittest

import responses
import httpretty
import requests

import stackinabox.util_httpretty
import stackinabox.util_responses
import stackinabox.util_requests_mock
from stackinabox.stack import StackInABox
from stackinabox.services.hello import HelloService


@httpretty.activate
class TestHttpretty(unittest.TestCase):

    def setUp(self):
        super(TestHttpretty, self).setUp()
        StackInABox.register_service(HelloService())

    def tearDown(self):
        super(TestHttpretty, self).tearDown()
        StackInABox.reset_services()

    def test_basic(self):
        stackinabox.util_httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


@responses.activate
def test_basic_responses():
    print('Starting Test Basic Response')
    StackInABox.reset_services()
    print('StackInABox Services Reset')
    StackInABox.register_service(HelloService())
    print('StackInABox Hello Service Registerd')
    stackinabox.util_responses.responses_registration('localhost')
    print('StackInABox Python Responses Configured')

    res = requests.get('http://localhost/hello/')
    print('Request completed. Examining results...')
    assert res.status_code == 200
    assert res.text == 'Hello'


class TestRequestsMock(unittest.TestCase):

    def setUp(self):
        super(TestRequestsMock, self).setUp()
        StackInABox.register_service(HelloService())
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestsMock, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_basic_requests_mock(self):
        stackinabox.util_requests_mock.requests_mock_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)

        import pdb
        pdb.set_trace()
        self.assertEqual(res.text, 'Hello')
