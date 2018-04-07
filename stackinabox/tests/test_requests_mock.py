"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import ddt
import requests
import six

import stackinabox.util.requests_mock
from stackinabox.stack import StackInABox
from stackinabox.services.hello import HelloService
from stackinabox.tests.utils.services import AdvancedService


logger = logging.getLogger(__name__)


class TestRequestsMockBasic(unittest.TestCase):

    def setUp(self):
        super(TestRequestsMockBasic, self).setUp()
        StackInABox.register_service(HelloService())
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestsMockBasic, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_basic_requests_mock(self):
        stackinabox.util.requests_mock.session_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    def test_context_requests_mock(self):
        with stackinabox.util.requests_mock.activate():

            stackinabox.util.requests_mock.registration(
                'localhost')

            res = requests.get('http://localhost/hello/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')


@ddt.ddt
class TestRequestMockAdvanced(unittest.TestCase):

    def setUp(self):
        super(TestRequestMockAdvanced, self).setUp()
        StackInABox.register_service(AdvancedService())
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestMockAdvanced, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_basic(self):
        stackinabox.util.requests_mock.session_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/advanced/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

        res = self.session.get('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Good-Bye')

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = self.session.get('http://localhost/advanced/g?bob=alice;'
                               'alice=bob&joe=jane')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)

        res = self.session.get('http://localhost/advanced/1234567890')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'okay')

        res = self.session.get('http://localhost/advanced/_234567890')
        self.assertEqual(res.status_code, 595)

        res = self.session.put('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 405)

        res = self.session.put('http://localhost/advanced2/i')
        self.assertEqual(res.status_code, 597)

    def test_context_requests_mock(self):
        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

            res = requests.get('http://localhost/advanced/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')

            res = requests.get('http://localhost/advanced/h')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Good-Bye')

            expected_result = {
                'bob': 'bob: Good-Bye alice',
                'alice': 'alice: Good-Bye bob',
                'joe': 'joe: Good-Bye jane'
            }
            res = requests.get('http://localhost/advanced/g?bob=alice;'
                               'alice=bob&joe=jane')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json(), expected_result)

    @ddt.data(
        ('head', 204, ''),
        ('delete', 204, ''),
        ('post', 200, 'created'),
        ('put', 200, 'updated'),
        ('patch', 200, 'patched'),
        ('options', 200, 'options'),
    )
    @ddt.unpack
    def test_extra_http_verbs(self, http_verb, response_status, response_body):
        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

            method_call = getattr(requests, http_verb)
            res = method_call('http://localhost/advanced/')
            self.assertEqual(res.status_code, response_status)
            self.assertEqual(res.text, response_body)
