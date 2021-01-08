import re

import ddt
import mock

from stackinabox.services import (
    exceptions,
    service,
    router
)

from tests.services import base
from tests.utils import hello


@ddt.ddt
class TestStackInABoxRouter(base.TestCase):

    def setUp(self):
        super(TestStackInABoxRouter, self).setUp()
        self.name = 'foo'
        self.uri = 'bar'
        self.hello_service = hello.HelloService()

    def tearDown(self):
        super(TestStackInABoxRouter, self).tearDown()

    @ddt.data(
        (None, None),
        (None, object()),
        (object(), None),
        (object(), object())
    )
    @ddt.unpack
    def test_instantiation(self, obj, parent_obj):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            obj,
            parent_obj
        )
        self.assertEqual(instance.service_name, self.name)
        self.assertEqual(instance.uri, self.uri)
        self.assertEqual(instance.obj, obj)
        self.assertEqual(instance.parent_obj, parent_obj)
        self.assertEqual(instance.methods, {})

    def test_instantiation_circular_reference_check(self):
        with self.assertRaises(exceptions.CircularReferenceError):
            same_obj = object()
            router.StackInABoxServiceRouter(
                self.name,
                self.uri,
                same_obj,
                same_obj
            )

    @ddt.data(
        (None, False),
        (object(), True)
    )
    @ddt.unpack
    def test_is_subservice(self, obj, subservice_status):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            obj,
            None
        )
        self.assertEqual(instance.obj, obj)
        self.assertEqual(instance.is_subservice, subservice_status)

    def test_set_subservice_already_registered(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            object(),
            None
        )
        with self.assertRaises(exceptions.RouteAlreadyRegisteredError):
            instance.set_subservice(self.hello_service)

    def test_set_subservice_circular_reference_check(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            self.hello_service
        )
        with self.assertRaises(exceptions.CircularReferenceError):
            instance.set_subservice(self.hello_service)

    @ddt.data(
        {},
        {'GET': 'Hello'}
    )
    def test_set_subservice_success(self, existing_methods):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            None
        )
        instance.methods = existing_methods
        instance.set_subservice(self.hello_service)

    @ddt.data(False, True)
    def test_update_uris(self, has_object):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            self.hello_service if has_object else None,
            None
        )
        instance.update_uris('/bar')

    def test_register_method_already_exists(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            None
        )
        http_method = 'GET'
        instance.methods = {http_method: 'Hello'}
        with self.assertRaises(exceptions.RouteAlreadyRegisteredError):
            instance.register_method(http_method, None)

    def test_register_method_success(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            None
        )

        def fn():
            pass

        http_method = 'GET'
        instance.register_method(http_method, fn)
        self.assertIn(http_method, instance.methods)
        self.assertEqual(instance.methods[http_method], fn)

    def test_call_bad_route(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            None
        )
        headers = {'Jackie': 'O'}
        result = instance('GET', None, '/', headers)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 405)
        self.assertEqual(result[1], headers)

    def test_call_sub_object(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            None
        )
        instance.set_subservice(self.hello_service)
        headers = {'Jackie': 'O'}
        result = instance('GET', None, '/', headers)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 200)
        self.assertEqual(result[1], headers)
        self.assertEqual(result[2], 'Hello')

    def test_call_method(self):
        instance = router.StackInABoxServiceRouter(
            self.name,
            self.uri,
            None,
            self.hello_service
        )
        headers = {'Jackie': 'O'}
        http_method = 'GET'
        http_uri = '/'
        expected_result = (600, headers, 'bear trap')

        mock_fn = mock.MagicMock()
        mock_fn.return_value = expected_result

        mock_req = mock.MagicMock()

        instance.methods[http_method] = mock_fn
        result = instance(http_method, mock_req, http_uri, headers)
        self.assertEqual(result, expected_result)
        mock_fn.assert_called_with(
            self.hello_service,
            mock_req,
            http_uri,
            headers
        )
