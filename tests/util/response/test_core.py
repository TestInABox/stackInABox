"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import requests
import responses
import six

import stackinabox.util.responses
from stackinabox.stack import StackInABox

from tests.utils.services import AdvancedService
from tests.utils.hello import HelloService


logger = logging.getLogger(__name__)


def test_basic_responses():

    @responses.activate
    def run():
        StackInABox.reset_services()
        StackInABox.register_service(HelloService())
        stackinabox.util.responses.registration('localhost')

        res = requests.get('http://localhost/hello/')
        assert res.status_code == 200
        assert res.text == 'Hello'

    run()


def test_advanced_responses():

    def run(use_deprecated):
        responses.mock.start()
        StackInABox.register_service(AdvancedService())
        if use_deprecated:
            stackinabox.util.responses.responses_registration('localhost')
        else:
            stackinabox.util.responses.registration('localhost')

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
        res = requests.get('http://localhost/advanced/g?bob=alice;'
                           'alice=bob&joe=jane')
        assert res.status_code == 200
        assert res.json() == expected_result

        res = requests.get('http://localhost/advanced/1234567890')
        assert res.status_code == 200
        assert res.text == 'okay'

        res = requests.get('http://localhost/advanced/_234567890')
        assert res.status_code == 595

        res = requests.put('http://localhost/advanced/h')
        assert res.status_code == 405

        res = requests.put('http://localhost/advanced2/i')
        assert res.status_code == 597

        StackInABox.reset_services()

        responses.mock.stop()
        responses.mock.reset()

    for deprecation_status in [True, False]:
        with responses.RequestsMock():
            run(deprecation_status)
