"""
Stack-In-A-Box: Basic Test
"""
import collections
import json
import logging
import types
import unittest

import requests

from stackinabox.util.responses import decorator
from stackinabox.services.hello import HelloService

from tests.utils.services import AdvancedService


logger = logging.getLogger(__name__)


def responses_generator():
    yield HelloService()


def responses_list():
    return [
        HelloService()
    ]


def test_verify_generator():
    assert isinstance(responses_generator(), types.GeneratorType)


def test_verify_list():
    assert isinstance(responses_list(), collections.Iterable)


class TestDecoratorParameters(unittest.TestCase):

    def test_process_service_parameters(self):
        decor_instance = decorator.activate('localhost')
        with self.assertRaises(TypeError):
            decor_instance.process_service({}, raise_on_type=True)


@decorator.activate('localhost', HelloService())
def test_basic_responses():
    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'


@decorator.stack_activate('localhost', HelloService())
def test_deprecated():
    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'


@decorator.activate('localhost', responses_generator())
def test_basic_responses_and_generator():
    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'


@decorator.activate('localhost', responses_list())
def test_basic_responses_and_list():
    res = requests.get('http://localhost/hello/')
    assert res.status_code == 200
    assert res.text == 'Hello'


@decorator.activate('localhost', HelloService(),
                    200, value='Hello')
def test_basic_with_parameters(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value


@decorator.activate('localhost', responses_generator(),
                    200, value='Hello')
def test_basic_with_parameters_and_generator(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value


@decorator.activate('localhost', responses_list(),
                    200, value='Hello')
def test_basic_with_parameters_and_list(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value


@decorator.activate('localhost', HelloService(),
                    200, value='Hello',
                    access_services="stack")
def test_basic_with_stack_acccess(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    stack = kwargs.get('stack', None)
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value
    assert len(stack) == 1
    assert HelloService().name in stack
    assert isinstance(stack[list(stack.keys())[0]], HelloService)


@decorator.activate('localhost', responses_generator(),
                    200, value='Hello',
                    access_services="stack")
def test_basic_with_stack_acccess_and_generator(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    stack = kwargs.get('stack', None)
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value
    assert len(stack) == 1
    assert HelloService().name in stack
    assert isinstance(stack[list(stack.keys())[0]], HelloService)


@decorator.activate('localhost', responses_list(),
                    200, value='Hello',
                    access_services="stack")
def test_basic_with_stack_acccess_and_list(*args, **kwargs):
    # note: work-around for pytest + Py3 and a decorator
    response_code = args[0]
    value = kwargs.get('value', 'alpha')
    stack = kwargs.get('stack', None)
    res = requests.get('http://localhost/hello/')
    assert res.status_code == response_code
    assert res.text == value
    assert len(stack) == 1
    assert HelloService().name in stack
    assert isinstance(stack[list(stack.keys())[0]], HelloService)


@decorator.activate('localhost', AdvancedService())
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
