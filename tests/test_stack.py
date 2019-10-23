import re
import unittest

import ddt
import requests

import stackinabox.util.requests_mock
from stackinabox.stack import (
    StackInABox, ServiceAlreadyRegisteredError)
from stackinabox.services.service import *
from stackinabox.services.hello import HelloService


class ExceptionalServices(StackInABoxService):

    def __init__(self):
        super(ExceptionalServices, self).__init__('except')
        self.register(StackInABoxService.GET,
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
        StackInABox.reset_services()

    def test_double_service_registration(self):
        service1 = HelloService()
        service2 = HelloService()

        StackInABox.register_service(service1)
        with self.assertRaises(ServiceAlreadyRegisteredError):
            StackInABox.register_service(service2)

    @ddt.data(
        ('http://honeymoon/', 'honeymoon', '/'),
        ('https://honeymoon/', 'honeymoon', '/'),
        ('honeymoon/', 'honeymoon', '/')
    )
    @ddt.unpack
    def test_get_services_url(self, url, base, value):
        result = StackInABox.get_services_url(url, base)
        self.assertEqual(result, value)

    def test_service_exception(self):
        exceptional = ExceptionalServices()
        StackInABox.register_service(exceptional)

        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration('localhost')

            res = requests.get('http://localhost/except/')
            self.assertEqual(res.status_code, 596)
