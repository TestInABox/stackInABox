import re

import ddt

from stackinabox.services import (
    exceptions,
    service,
    router
)

from tests.services import base


class FakeRouter(object):

    def __init__(self, is_subservice, return_value=None):
        self.is_subservice = is_subservice
        self.called_with = []
        self.return_value = return_value
        self.side_effects = None

    def __call__(self, *args, **kwargs):
        self.called_with.append(
            {
                'args': args,
                'kwargs': kwargs
            }
        )
        return_value = None
        if self.side_effects:
            return_value = self.side_effects.pop(0)
        else:
            return_value = self.return_value
        return return_value


@ddt.ddt
class TestStackInABoxService(base.TestCase):

    def setUp(self):
        super(TestStackInABoxService, self).setUp()

    def tearDown(self):
        super(TestStackInABoxService, self).tearDown()

    def test_initialization(self):
        name = 'fake-it'
        instance = service.StackInABoxService(name)
        self.assertEqual(instance.name, name)
        self.assertEqual(instance.routes, {})

    @ddt.data(
        ('requiem', False),
        (re.compile('^/$'), True)
    )
    @ddt.unpack
    def test_is_regex(self, regex_statement, valid_regex):
        self.assertEqual(
            service.StackInABoxService.is_regex(regex_statement),
            valid_regex
        )

    @ddt.data(
        (re.compile('^/$'), True, False),
        (re.compile('^/'), False, False),
        (re.compile('/$'), False, False),
        (re.compile('^/'), True, True),
        (re.compile('^/$'), False, True)
    )
    @ddt.unpack
    def test_validate_regex(
        self, regex_value, regex_valid, is_subservice
    ):

        if regex_valid:
            service.StackInABoxService.validate_regex(
                regex_value,
                is_subservice
            )

        else:
            with self.assertRaises(exceptions.InvalidRouteRegexError):
                service.StackInABoxService.validate_regex(
                    regex_value,
                    is_subservice
                )

    @ddt.data(
        ('/', re.compile('^/$'), False, '^/$'),
        ('/', re.compile('^/'), True, '^/'),
        ('/', '/hello', False, '^/hello$'),
    )
    @ddt.unpack
    def test_get_service_regex(
        self, base_url, service_url, sub_service, expected_regex
    ):
        result = service.StackInABoxService.get_service_regex(
            base_url, service_url, sub_service
        )
        self.assertIsInstance(result, type(re.compile('')))
        self.assertEqual(
            result.pattern,
            expected_regex
        )

    @ddt.data(
        {},
        {
            'breakpoint': {
                'regex': re.compile('^/helix$'),
                'uri': '/helix',
                'handlers': FakeRouter(False)
            }
        }
    )
    def test_base_url(self, route_table):
        name = 'fake-it'
        instance = service.StackInABoxService(name)
        instance.routes = route_table

        original_url = '/{0}'.format(name)
        self.assertEqual(instance.base_url, original_url)

        new_url = '/ti-ekaf'
        instance.base_url = new_url
        self.assertEqual(instance.base_url, new_url)

        instance.reset()
        self.assertEqual(instance.base_url, original_url)

    @ddt.data(
        ({}, '/'),
        ({
            'breakpoint': {
                'regex': re.compile('^/helix$'),
                'uri': '/helix',
                'handlers': FakeRouter(False)
            }
        }, '/')
    )
    @ddt.unpack
    def test_try_handle_route_failure(self, route_table, uri):
        instance = service.StackInABoxService('throw-away-595')
        instance.routes = route_table
        input_headers = {'golden-ratio': '3-4-5'}
        result = instance.try_handle_route(
            uri, 'GET', None, uri, input_headers
        )

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status_code, headers, message = result
        self.assertEqual(status_code, 595)
        self.assertEqual(headers, input_headers)
        self.assertIsInstance(message, str)

    @ddt.data(
        '/helix',
        '/helix?double=True'
    )
    def test_try_handle_route_success(self, uri):
        # NOTE: This cannot be merged into `test_request` because
        # of additional parameter required
        instance = service.StackInABoxService('throw-away-200')
        input_headers = {'golden-ratio': '3-4-5'}

        message_result = 'helios'
        instance.routes = {
            'breakpoint': {
                'regex': re.compile('^/helix$'),
                'uri': uri,
                'handlers': FakeRouter(
                    False,
                    return_value=(
                        200, input_headers, message_result
                    )
                )
            }
        }

        result = instance.try_handle_route(
            uri, 'GET', None, uri, input_headers
        )

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status_code, headers, message = result
        self.assertEqual(status_code, 200)
        self.assertEqual(headers, input_headers)
        self.assertEqual(message, message_result)

    @ddt.data(
        ('/helix', 'request'),
        ('/helix?double=True', 'request'),
        ('/helix', 'sub_request'),
        ('/helix?double=True', 'sub_request'),
    )
    @ddt.unpack
    def test_request(self, uri, method_to_call):
        instance = service.StackInABoxService('throw-away-200')
        input_headers = {'golden-ratio': '3-4-5'}

        message_result = 'helios'
        instance.routes = {
            'breakpoint': {
                'regex': re.compile('^/helix$'),
                'uri': uri,
                'handlers': FakeRouter(
                    False,
                    return_value=(
                        200, input_headers, message_result
                    )
                )
            }
        }

        callee = getattr(instance, method_to_call)
        result = callee('GET', None, uri, input_headers)

        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)
        status_code, headers, message = result
        self.assertEqual(status_code, 200)
        self.assertEqual(headers, input_headers)
        self.assertEqual(message, message_result)

    def test_create_route_existing(self):
        instance = service.StackInABoxService(__name__)
        instance.routes['hero'] = 'phalzbottom'
        instance.create_route('hero', False)
        self.assertFalse(isinstance(instance.routes['hero'], dict))

    def test_create_route_new(self):
        instance = service.StackInABoxService(__name__)
        uri = '/hero'
        instance.create_route(uri, False)
        self.assertIn(uri, instance.routes)
        self.assertIsInstance(instance.routes[uri], dict)
        self.assertIn('regex', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['regex'],
            type(re.compile(''))
        )
        self.assertEqual(
            instance.routes[uri]['regex'].pattern,
            '^{0}$'.format(uri)
        )
        self.assertIn('uri', instance.routes[uri])
        self.assertEqual(instance.routes[uri]['uri'], uri)
        self.assertIn('handlers', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['handlers'],
            router.StackInABoxServiceRouter
        )

    def test_register(self):
        method = 'HASHTAG'
        uri = '/images'

        def call_me():
            pass

        instance = service.StackInABoxService('period')
        self.assertEqual(instance.routes, {})
        instance.register(method, uri, call_me)
        self.assertIn(uri, instance.routes)
        self.assertIsInstance(instance.routes[uri], dict)
        self.assertIn('regex', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['regex'],
            type(re.compile(''))
        )
        self.assertEqual(
            instance.routes[uri]['regex'].pattern,
            '^{0}$'.format(uri)
        )
        self.assertIn('uri', instance.routes[uri])
        self.assertEqual(instance.routes[uri]['uri'], uri)
        self.assertIn('handlers', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['handlers'],
            router.StackInABoxServiceRouter
        )

    def test_sub_register(self):
        uri = '/numeric'
        instance = service.StackInABoxService('conjunction')
        instance2 = service.StackInABoxService('terminator')
        self.assertEqual(instance.routes, {})
        instance.register_subservice(uri, instance2)
        self.assertIn(uri, instance.routes)
        self.assertIsInstance(instance.routes[uri], dict)
        self.assertIn('regex', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['regex'],
            type(re.compile(''))
        )
        self.assertEqual(
            instance.routes[uri]['regex'].pattern,
            '^{0}$'.format(uri)
        )
        self.assertIn('uri', instance.routes[uri])
        self.assertEqual(instance.routes[uri]['uri'], uri)
        self.assertIn('handlers', instance.routes[uri])
        self.assertIsInstance(
            instance.routes[uri]['handlers'],
            router.StackInABoxServiceRouter
        )
