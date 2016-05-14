"""
Stack-In-A-Box: Basic Test
"""
import json
import logging
import unittest

import requests

import stackinabox.util.responses.decorator as stack_decorator
from stackinabox.services.hello import HelloService
from stackinabox.tests.utils.services import AdvancedService


logger = logging.getLogger(__name__)


@stack_decorator.stack_activate('localhost', HelloService())
def test_basic_responses():
    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'


@stack_decorator.stack_activate('localhost', HelloService(),
                                200, value='Hello')
def test_basic_with_parameters(response_code, value='alpha'):
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value


@stack_decorator.stack_activate('localhost', HelloService(),
                                200, value='Hello',
                                access_services="stack")
def test_basic_with_stack_acccess(response_code, value='alpha',
                                  stack=None):
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value
    assert len(stack) == 1
    assert HelloService().name in stack
    assert isinstance(stack[list(stack.keys())[0]], HelloService)


@stack_decorator.stack_activate('localhost', AdvancedService())
def test_advanced_responses():
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
