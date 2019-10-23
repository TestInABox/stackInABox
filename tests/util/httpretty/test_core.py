"""
Stack-In-A-Box: Basic Test
"""
import logging
import sys
import unittest

import httpretty
import requests
import six

import stackinabox.util.httpretty
from stackinabox.stack import StackInABox
from stackinabox.services.hello import HelloService

from tests.utils.services import AdvancedService


logger = logging.getLogger(__name__)


@unittest.skipIf(sys.version_info >= (3, 0), "Httpretty not supported by Py3")
@httpretty.activate
class TestHttprettyBasic(unittest.TestCase):

    def setUp(self):
        super(TestHttprettyBasic, self).setUp()
        StackInABox.register_service(HelloService())

    def tearDown(self):
        super(TestHttprettyBasic, self).tearDown()
        StackInABox.reset_services()

    def test_basic(self):
        stackinabox.util.httpretty.registration('localhost')

        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


@unittest.skipIf(sys.version_info >= (3, 0), "Httpretty not supported by Py3")
@httpretty.activate
class TestHttprettyAdvanced(unittest.TestCase):

    def setUp(self):
        super(TestHttprettyAdvanced, self).setUp()
        StackInABox.register_service(AdvancedService())

    def tearDown(self):
        super(TestHttprettyAdvanced, self).tearDown()
        StackInABox.reset_services()

    def test_basic(self):
        stackinabox.util.httpretty.registration('localhost')

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

        res = requests.get('http://localhost/advanced/1234567890')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'okay')

        res = requests.get('http://localhost/advanced/_234567890')
        self.assertEqual(res.status_code, 595)

        res = requests.put('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 405)

        res = requests.put('http://localhost/advanced2/i')
        self.assertEqual(res.status_code, 597)
