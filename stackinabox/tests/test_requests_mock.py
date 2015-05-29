"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import requests
import six

import stackinabox.util_requests_mock
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
        stackinabox.util_requests_mock.requests_mock_session_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    def test_context_requests_mock(self):
        with stackinabox.util_requests_mock.activate():

            stackinabox.util_requests_mock.requests_mock_registration(
                'localhost')

            res = requests.get('http://localhost/hello/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')


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
        stackinabox.util_requests_mock.requests_mock_session_registration(
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
        self.assertEqual(res.status_code, 599)

        res = self.session.put('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 405)

        res = self.session.put('http://localhost/advanced2/i')
        self.assertEqual(res.status_code, 599)

    def test_context_requests_mock(self):
        with stackinabox.util_requests_mock.activate():
            stackinabox.util_requests_mock.requests_mock_registration(
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
