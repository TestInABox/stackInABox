"""
Stack-In-A-Box: Basic Test
"""
import collections
import json
import logging
import types

import requests

from stackinabox.util.requests_mock import decorator

from tests.util import base
from tests.utils.services import AdvancedService
from tests.utils.hello import HelloService


logger = logging.getLogger(__name__)


class TestRequestsMockBasicWithDecoratorErrors(base.UtilTestCase):

    def test_basic(self):

        decor_instance = decorator.activate('localhost')
        with self.assertRaises(TypeError):
            decor_instance.process_service({}, raise_on_type=True)

    @decorator.stack_activate('localhost', HelloService())
    def test_deprecated(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')


class TestRequestsMockBasic(base.UtilTestCase):

    def setUp(self):
        super(TestRequestsMockBasic, self).setUp()

    def tearDown(self):
        super(TestRequestsMockBasic, self).tearDown()

    @decorator.activate('localhost', HelloService())
    def test_basic_requests_mock(self):
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
        self.assertTrue(self.hello_service.name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)


class TestRequestMockAdvanced(base.UtilTestCase):

    def setUp(self):
        super(TestRequestMockAdvanced, self).setUp()

    def tearDown(self):
        super(TestRequestMockAdvanced, self).tearDown()

    @decorator.activate('localhost', AdvancedService(),
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


def requests_mock_generator():
    yield HelloService()


class TestRequestsMockBasicWithDecoratorAndGenerator(base.UtilTestCase):

    def test_verify_generator(self):
        self.assertIsInstance(requests_mock_generator(), types.GeneratorType)

    @decorator.activate('localhost', requests_mock_generator())
    def test_basic_requests_mock(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @decorator.activate('localhost', requests_mock_generator(),
                        200, value='Hello')
    def test_basic_with_parameters(self, response_code, value='alpha'):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)

    @decorator.activate('localhost', requests_mock_generator(),
                        200, value='Hello',
                        access_services="stack")
    def test_basic_with_stack_acccess(self, response_code, value='alpha',
                                      stack=None):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)
        self.assertEqual(len(stack), 1)
        self.assertTrue(self.hello_service.name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)


def requests_mock_list():
    return [
        HelloService()
    ]


class TestRequestsMockBasicWithDecoratorAndGenerator(base.UtilTestCase):

    def test_verify_list(self):
        self.assertIsInstance(requests_mock_list(), collections.Iterable)

    @decorator.activate('localhost', requests_mock_list())
    def test_basic_requests_mock(self):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @decorator.activate('localhost', requests_mock_list(),
                        200, value='Hello')
    def test_basic_with_parameters(self, response_code, value='alpha'):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)

    @decorator.activate('localhost', requests_mock_list(),
                        200, value='Hello',
                        access_services="stack")
    def test_basic_with_stack_acccess(self, response_code, value='alpha',
                                      stack=None):
        res = requests.get('http://localhost/hello/')
        self.assertEqual(res.status_code, response_code)
        self.assertEqual(res.text, value)
        self.assertEqual(len(stack), 1)
        self.assertTrue(self.hello_service.name in stack)
        self.assertIsInstance(stack[list(stack.keys())[0]], HelloService)
