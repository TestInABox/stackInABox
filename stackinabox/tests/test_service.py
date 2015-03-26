import re
import unittest


from stackinabox.services.service import *


class TestServiceRegex(unittest.TestCase):

    def setUp(self):
        super(TestServiceRegex, self).setUp()

    def tearDown(self):
        super(TestServiceRegex, self).tearDown()

    def test_stackinabox_service_regex(self):

        positive_cases = [
            re.compile('^/$')
        ]

        negative_cases = [
            re.compile('^/'),
            re.compile('/$')
        ]

        for case in positive_cases:
            StackInABoxService.validate_regex(case)

        for case in negative_cases:
            with self.assertRaises(InvalidRouteRegexError):
                StackInABoxService.validate_regex(case)


class AnotherAdvancedService(StackInABoxService):

    def __init__(self):
        super(AnotherAdvancedService, self).__init__('aas')
        self.register(StackInABoxService.GET, '/',
                      AnotherAdvancedService.first_handler)

    def first_handler(self, request, uri, headers):
        return (200, headers, 'hello')

    def second_handler(self, request, uri, headers):
        return (200, headers, 'howdy')


class TestServiceRouteRegistration(unittest.TestCase):

    def setUp(self):
        super(TestServiceRouteRegistration, self).setUp()

    def tearDown(self):
        super(TestServiceRouteRegistration, self).tearDown()

    def test_bad_registration(self):

        service = AnotherAdvancedService()

        with self.assertRaises(RouteAlreadyRegisteredError):
            service.register(StackInABoxService.GET, '/',
                             AnotherAdvancedService.second_handler)
