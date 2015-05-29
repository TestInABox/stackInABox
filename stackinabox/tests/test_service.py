import re
import unittest

import httpretty
import requests

from stackinabox.stack import StackInABox
from stackinabox.services.service import *
import stackinabox.util_httpretty


class TestServiceRegex(unittest.TestCase):

    def setUp(self):
        super(TestServiceRegex, self).setUp()

    def tearDown(self):
        super(TestServiceRegex, self).tearDown()

    def test_instantiation(self):
        name = 'test-service'

        service = StackInABoxService(name)
        self.assertEqual(service.name, name)
        self.assertTrue(service.base_url.startswith('/'))
        self.assertTrue(service.base_url.endswith(name))
        self.assertEqual(len(service.base_url),
                         (len(name) + 1))
        self.assertEqual(len(service.routes), 0)

    def test_stackinabox_validate_regex(self):

        positive_cases = [
            re.compile('^/$')
        ]

        negative_cases = [
            re.compile('^/'),
            re.compile('/$')
        ]

        for case in positive_cases:
            StackInABoxService.validate_regex(case, False)

        for case in negative_cases:
            with self.assertRaises(InvalidRouteRegexError):
                StackInABoxService.validate_regex(case, False)

    def test_stackinabox_service_regex(self):

        case_regex = [
            re.compile('^/$')
        ]

        case_nonregex = [
            '/',
        ]

        for case in case_regex:
            self.assertEqual(StackInABoxService.get_service_regex('base',
                                                                  case,
                                                                  False),
                             case)

        for case in case_nonregex:
            case_regex = re.compile('^{0}$'.format(case))
            self.assertEqual(StackInABoxService.get_service_regex('base',
                                                                  case,
                                                                  False),
                             case_regex)


class AnotherAdvancedService(StackInABoxService):

    def __init__(self):
        super(AnotherAdvancedService, self).__init__('aas')
        self.register(StackInABoxService.GET, '/',
                      AnotherAdvancedService.first_handler)

    def first_handler(self, request, uri, headers):
        return (200, headers, 'hello')

    def second_handler(self, request, uri, headers):
        return (200, headers, 'howdy')


class YetAnotherService(StackInABoxService):

    def __init__(self):
        super(YetAnotherService, self).__init__('yaas')
        self.register(StackInABoxService.GET, '^/french$',
                      YetAnotherService.yaas_handler)

    def yaas_handler(self, request, uri, headers):
        return (200, headers, 'bonjour')


class TestServiceRouteRegistration(unittest.TestCase):

    def setUp(self):
        super(TestServiceRouteRegistration, self).setUp()

    def tearDown(self):
        super(TestServiceRouteRegistration, self).tearDown()
        StackInABox.reset_services()

    def test_bad_registration(self):

        service = AnotherAdvancedService()

        with self.assertRaises(RouteAlreadyRegisteredError):
            service.register(StackInABoxService.GET, '/',
                             AnotherAdvancedService.second_handler)

    @httpretty.activate
    def test_subservice_registration(self):
        service = AnotherAdvancedService()
        subservice = YetAnotherService()
        service.register_subservice(re.compile('^/french'),
                                    subservice)

        StackInABox.register_service(service)

        stackinabox.util_httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/aas/french')
        self.assertEqual(res.status_code,
                         200)
        self.assertEqual(res.text,
                         'bonjour')
