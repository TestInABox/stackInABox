"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import requests

import stackinabox.util.requests_mock.decorator as stack_decorator
from stackinabox.services.hello import HelloService
from stackinabox.tests.utils.services import AdvancedService


logger = logging.getLogger(__name__)


class TestRequestsMockBasic(unittest.TestCase):

    def setUp(self):
        super(TestRequestsMockBasic, self).setUp()

    def tearDown(self):
        super(TestRequestsMockBasic, self).tearDown()

    @stack_decorator.stack_activate('localhost', HelloService())
    def test_basic_requests_mock(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


class TestRequestMockAdvanced(unittest.TestCase):

    def setUp(self):
        super(TestRequestMockAdvanced, self).setUp()

    def tearDown(self):
        super(TestRequestMockAdvanced, self).tearDown()

    @stack_decorator.stack_activate('localhost', AdvancedService(),
                                    session="session")
    def test_basic(self, session):
        res = session.get('http://localhost/advanced/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

        res = session.get('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Good-Bye')

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = session.get('http://localhost/advanced/g?bob=alice;'
                          'alice=bob&joe=jane')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)

        res = session.get('http://localhost/advanced/1234567890')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'okay')

        res = session.get('http://localhost/advanced/_234567890')
        self.assertEqual(res.status_code, 595)

        res = session.put('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 405)

        res = session.put('http://localhost/advanced2/i')
        self.assertEqual(res.status_code, 597)

        session.close()
