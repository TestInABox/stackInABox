"""
Stack-In-A-Box: Basic Test
"""
import unittest

import httpretty
import requests
import responses
import six

import stackinabox.util_httpretty
import stackinabox.util_responses
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


@unittest.skipIf(six.PY3, 'Responses fails on PY3')
def test_basic_responses():

    @responses.activate
    def run():
        StackInABox.reset_services()
        StackInABox.register_service(HelloService())
        stackinabox.util_responses.responses_registration('localhost')

        res = requests.get('http://localhost/hello/')
        assert res.status_code == 200
        assert res.text == 'Hello'

    run()
