"""
Stack-In-A-Box: Basic Test
"""
import collections
import types
import unittest

import requests

from stackinabox.util.httpretty import decorator

from tests.utils.services import AdvancedService
from tests.utils.hello import HelloService


class TestHttprettyBasicWithDecoratorErrors(unittest.TestCase):

    def test_basic(self):

        decor_instance = decorator.activate('localhost')
        with self.assertRaises(TypeError):
            decor_instance.process_service({}, raise_on_type=True)

    @decorator.stack_activate('localhost', HelloService())
    def test_deprecated(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


class TestHttprettyBasicWithDecorator(unittest.TestCase):

    @decorator.activate('localhost', HelloService())
    def test_basic(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @decorator.activate('localhost', HelloService(),
                        200, value='Hello')
    def test_basic_with_parameters(self, response_code, value='alpha'):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)

    @decorator.activate('localhost', HelloService(),
                        200, value='Hello',
                        access_services="stack")
    def test_basic_with_stack_acccess(self, response_code, value='alpha',
                                      stack=None):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)
        self.assertEqual(len(stack), 1)
        self.assertTrue(HelloService().name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)


class TestHttprettyAdvancedWithDecorator(unittest.TestCase):

    @decorator.activate('localhost', AdvancedService())
    def test_basic(self):
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


def httpretty_generator():
    yield HelloService()


class TestHttprettyBasicWithDecoratorAndGenerator(unittest.TestCase):

    def test_verify_generator(self):
        self.assertIsInstance(httpretty_generator(), types.GeneratorType)

    @decorator.activate(
        'localhost',
        httpretty_generator()
    )
    def test_basic(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @decorator.activate(
        'localhost',
        httpretty_generator(),
        200, value='Hello'
    )
    def test_basic_with_parameters(self, response_code, value='alpha'):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)

    @decorator.activate(
        'localhost',
        httpretty_generator(),
        200, value='Hello',
        access_services="stack"
    )
    def test_basic_with_stack_acccess(self, response_code, value='alpha',
                                      stack=None):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)
        self.assertEqual(len(stack), 1)
        self.assertTrue(HelloService().name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)


def httpretty_list():
    return [
        HelloService()
    ]


class TestHttprettyBasicWithDecoratorAndList(unittest.TestCase):

    def test_verify_list(self):
        self.assertIsInstance(httpretty_list(), collections.Iterable)

    @decorator.activate(
        'localhost',
        httpretty_list()
    )
    def test_basic(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @decorator.activate(
        'localhost',
        httpretty_list(),
        200, value='Hello'
    )
    def test_basic_with_parameters(self, response_code, value='alpha'):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)

    @decorator.activate(
        'localhost',
        httpretty_list(),
        200, value='Hello',
        access_services="stack"
    )
    def test_basic_with_stack_acccess(self, response_code, value='alpha',
                                      stack=None):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)
        self.assertEqual(len(stack), 1)
        self.assertTrue(HelloService().name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)
