"""
Stack-In-A-Box Basic Test
"""
import unittest

import responses
import httpretty
import requests

import stackinabox.httpretty
import stackinabox.responses


@httpretty.activate
class TestHttpretty(unittest.TestCase):

    def setUp(self):
        super(TestHttpretty, self).setUp()

    def tearDown(self):
        super(TestHttpretty, self).tearDown()

    def test_basic(self):
        stackinabox.httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


@responses.activate
def test_basic_responses():
    stackinabox.responses.responses_registration('localhost')

    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'
