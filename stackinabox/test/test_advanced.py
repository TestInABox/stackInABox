"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import responses
import httpretty
import requests

import stackinabox.httpretty
import stackinabox.responses
from stackinabox.stack import StackInABox
from stackinabox.services.service import StackInABoxService


logger = logging.getLogger(__name__)


class AdvancedService(StackInABoxService):

    def __init__(self):
        super(AdvancedService, self).__init__('advanced')
        self.register(StackInABoxService.GET, '/', AdvancedService.handler)
        self.register(StackInABoxService.GET, '/h', AdvancedService.alternate_handler)
        self.register(StackInABoxService.GET, '/g', AdvancedService.query_handler)

    def handler(self, request, uri, headers):
        return (200, headers, 'Hello')

    def alternate_handler(self, request, uri, headers):
        return (200, headers, 'Good-Bye')

    def query_handler(self, request, uri, headers):
        query = None
        if '?' in uri:
            path, querys = uri.split('?')
            querys = querys.replace(';', '&')
            query = {}
            for kv in querys.split('&'):
                k, v = kv.split('=')
                query[k] = v

            body = {}
            for k, v in query.items():
                body[k] = '{0}: Good-Bye {1}'.format(k, v)

            return (200, headers, json.dumps(body))
        else:
            logger.debug('No query string')
            return (200, headers, 'Where did you go?')


@httpretty.activate
class TestHttpretty(unittest.TestCase):

    def setUp(self):
        super(TestHttpretty, self).setUp()
        StackInABox.register_service(AdvancedService())

    def tearDown(self):
        super(TestHttpretty, self).tearDown()
        StackInABox.reset_services()

    def test_basic(self):
        stackinabox.httpretty.httpretty_registration('localhost')

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
        res = requests.get('http://localhost/advanced/g?bob=alice;alice=bob&joe=jane')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)


def tb_responses_setup():
    StackInABox.register_service(AdvancedService())

def tb_responses_teardown():
    StackInABox.reset_services()

@responses.activate
def tb_basic_responses():
    stackinabox.responses.responses_registration('localhost')

    res = requests.get('http://localhost/advanced/')
    assert res.status_code == 200
    assert res.text == 'Hello'

    res = requests.get('http://localhost/advanced/h')
    assert res.status_code == 200
    assert res.text == 'Good-Bye'

    expected_result = {
        'bob': 'bob: Good-Bye alice',
        'alice': 'alice: Good-Bye bob',
        'joe': 'joe: Good-Bye jane'
    }
    res = requests.get('http://localhost/advanced/g?bob=alice;alice=bob&joe=jane')
    assert res.status_code == 200
    assert res.json() == expected_result

test_basic_responses = unittest.FunctionTestCase(tb_basic_responses,
                                                 setUp=tb_responses_setup,
                                                 tearDown=tb_responses_teardown)
