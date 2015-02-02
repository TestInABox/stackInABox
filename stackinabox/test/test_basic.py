"""
Stack-In-A-Box: Basic Test
"""
import unittest

import responses
import httpretty
import requests

import stackinabox.httpretty
import stackinabox.responses
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
        stackinabox.httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


@responses.activate
def test_basic_responses():
    StackInABox.reset_services()
    StackInABox.register_service(HelloService())
    stackinabox.responses.responses_registration('localhost')

    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'
