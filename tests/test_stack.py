import re
import unittest

import ddt
import httpretty
import mock
import requests

from stackinabox import stack
from stackinabox.services import (
    hello,
    service
)
import stackinabox.util.httpretty

from tests.utils import services as test_services


class ExceptionalServices(service.StackInABoxService):

    def __init__(self):
        super(ExceptionalServices, self).__init__('except')
        self.register(service.StackInABoxService.GET,
                      '/',
                      ExceptionalServices.handler)

    def handler(self, request, uri, headers):
        raise Exception('Exceptional Service Failure')


@ddt.ddt
class TestStack(unittest.TestCase):

    def setUp(self):
        super(TestStack, self).setUp()

    def tearDown(self):
        super(TestStack, self).tearDown()
        stack.StackInABox.reset_services()

    def test_reset_services(self):
        with mock.patch('stackinabox.stack.StackInABox.reset') as mock_reset:
            stack.StackInABox.reset_services()
            self.assertEqual(mock_reset.call_count, 1)

    def test_register_service(self):
        with mock.patch(
            'stackinabox.stack.StackInABox.register'
        ) as mock_register:
            data = hello.HelloService()
            stack.StackInABox.register_service(data)
            mock_register.assert_called_once_with(data)

    def test_call_into(self):
        with mock.patch('stackinabox.stack.StackInABox.call') as mock_call:
            data = ('GET', 'wedding', '/matrimoney', {'reception': 'tbd'})
            stack.StackInABox.call_into(*data)
            mock_call.assert_called_once_with(*data)

    def test_hold_onto(self):
        with mock.patch(
            'stackinabox.stack.StackInABox.into_hold'
        ) as mock_hold:
            name = 'emo'
            data = 'Fearless'
            stack.StackInABox.hold_onto(name, data)
            mock_hold.assert_called_once_with(name, data)

    def test_hold_out(self):
        with mock.patch(
            'stackinabox.stack.StackInABox.from_hold'
        ) as mock_hold:
            name = 'emo'
            data = 'Fearless'
            mock_hold.return_value = data
            self.assertEqual(
                stack.StackInABox.hold_out(name),
                data
            )
            mock_hold.assert_called_once_with(name)

    def test_update_uri(self):
        with mock.patch('stackinabox.stack.StackInABox.base_url') as mock_url:
            new_url = '/getaway'
            stack.StackInABox.update_uri(new_url)
            self.assertEqual(
                stack.local_store.instance.base_url,
                new_url
            )

    def test_instantiation(self):
        theStack = stack.StackInABox()
        self.assertEqual(theStack.base_url, '/')
        self.assertEqual(theStack.services, {})
        self.assertEqual(theStack.holds, {})

    def test_global_instance(self):
        self.assertTrue(hasattr(stack, "local_store"))
        self.assertTrue(hasattr(stack.local_store, "instance"))
        self.assertIsInstance(stack.local_store.instance, stack.StackInABox)

    @ddt.data(
        ('http://honeymoon/', 'honeymoon', '/'),
        ('https://honeymoon/', 'honeymoon', '/'),
        ('honeymoon/', 'honeymoon', '/')
    )
    @ddt.unpack
    def test_get_services_url(self, url, base, value):
        result = stack.StackInABox.get_services_url(url, base)
        self.assertEqual(result, value)

    def test_base_url_no_services(self):
        theStack = stack.StackInABox()
        self.assertEqual(theStack.base_url, '/')
        self.assertEqual(theStack.services, {})
        new_url = 'https://matrimony'
        theStack.base_url = new_url
        self.assertEqual(theStack.base_url, new_url)

    def test_base_url_with_services(self):
        theStack = stack.StackInABox()
        theStack.register(hello.HelloService())
        self.assertEqual(theStack.base_url, '/')
        new_url = 'https://matrimony'
        theStack.base_url = new_url
        self.assertEqual(theStack.base_url, new_url)

    @ddt.data(
        (0, 0), (1, 0), (0, 1), (1, 1), (2, 3), (3, 2), (5, 5)
    )
    @ddt.unpack
    def test_reset(self, service_count, hold_count):
        theStack = stack.StackInABox()
        self.assertEqual(theStack.services, {})
        self.assertEqual(theStack.holds, {})
        for service_number in range(service_count):
            name = 'service{0}'.format(service_number)
            theStack.services[name] = (service_number, hello.HelloService())

        for hold_number in range(hold_count):
            hold_key = 'hold{0}'.format(hold_number)
            theStack.holds[hold_key] = hold_number

        self.assertEqual(len(theStack.services), service_count)
        self.assertEqual(len(theStack.holds), hold_count)

        theStack.reset()
        self.assertEqual(theStack.services, {})
        self.assertEqual(theStack.holds, {})

    def test_register(self):
        service = hello.HelloService()
        theStack = stack.StackInABox()
        self.assertEqual(theStack.services, {})
        theStack.register(service)
        self.assertIn(service.name, theStack.services)
        self.assertEqual(len(theStack.services[service.name]), 2)
        matcher, stored_service = theStack.services[service.name]
        self.assertEqual(service, stored_service)
        self.assertIsInstance(matcher, type(re.compile('')))

    def test_double_service_registration(self):
        service1 = hello.HelloService()
        service2 = hello.HelloService()

        theStack = stack.StackInABox()

        theStack.register(service1)
        with self.assertRaises(stack.ServiceAlreadyRegisteredError):
            theStack.register(service2)

    @ddt.data(
        [],
        [hello.HelloService()]
    )
    def test_call_no_service_matches(self, services_to_register):
        theStack = stack.StackInABox()
        theStack.base_url = 'localhost'
        for svc in services_to_register:
            theStack.register(svc)
        result = theStack.call(
            'GET', mock.MagicMock(), 'localhost/except/', {}
        )
        self.assertEqual(len(result), 3)
        status_code, headers, msg = result
        self.assertEqual(status_code, 597)
        self.assertEqual(headers, {})
        self.assertIn('Unknown service', msg)

    def test_call_service_exception(self):
        theStack = stack.StackInABox()
        exceptional = ExceptionalServices()
        theStack.register(exceptional)
        theStack.base_url = 'localhost'

        result = theStack.call(
            'GET', mock.MagicMock(), 'localhost/except/', {}
        )
        self.assertEqual(len(result), 3)
        status_code, headers, msg = result
        self.assertEqual(status_code, 596)
        self.assertEqual(headers, {})
        self.assertIn('Service Handler had an error', msg)

    def test_call_basic(self):
        theStack = stack.StackInABox()
        theStack.register(hello.HelloService())
        theStack.base_url = 'localhost'
        result = theStack.call('GET', mock.MagicMock(), 'localhost/hello/', {})
        self.assertEqual(len(result), 3)
        status_code, headers, msg = result
        self.assertEqual(status_code, 200)
        self.assertEqual(headers, {})
        self.assertEqual('Hello', msg)

    def test_into_hold(self):
        theStack = stack.StackInABox()
        self.assertEqual(theStack.holds, {})

        item_name = 'ring'
        item_value = 'wedding-band'

        theStack.into_hold(item_name, item_value)
        self.assertIn(item_name, theStack.holds)
        self.assertEqual(item_value, theStack.holds[item_name])

    def test_from_hold(self):
        theStack = stack.StackInABox()
        self.assertEqual(theStack.holds, {})

        item_name = 'ring'
        item_value = 'engagement-band'

        theStack.holds[item_name] = item_value
        self.assertEqual(theStack.from_hold(item_name), item_value)
