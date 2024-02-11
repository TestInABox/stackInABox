"""
Stack-In-A-Box: Basic Test
"""
import json
import logging

import ddt
import requests
import requests.models
import requests.adapters  # import HTTPAdapter
import six

import stackinabox.util.requests_mock
from stackinabox.util.requests_mock import core
from stackinabox.stack import StackInABox

from tests.util import base


logger = logging.getLogger(__name__)


@ddt.ddt
class TestRequestsMockBasic(base.UtilTestCase):

    def setUp(self):
        super(TestRequestsMockBasic, self).setUp()
        StackInABox.register_service(self.hello_service)
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestsMockBasic, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    @ddt.data(True, False)
    def test_basic_requests_mock(self, use_deprecated):
        if use_deprecated:
            stackinabox.util.requests_mock.requests_mock_session_registration(
                'localhost', self.session)
        else:
            stackinabox.util.requests_mock.session_registration(
                'localhost', self.session)

        res = self.session.get('http://localhost/hello/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

    @ddt.data(True, False)
    def test_context_requests_mock(self, use_deprecated):
        with stackinabox.util.requests_mock.activate():

            if use_deprecated:
                stackinabox.util.requests_mock.requests_mock_registration(
                    'localhost')
            else:
                stackinabox.util.requests_mock.registration(
                    'localhost')

            res = requests.get('http://localhost/hello/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')

    def test_requests_session(self):
        session = core.requests_session()

        with session as mock_session:
            self.assertNotEqual(type(session), type(mock_session))

            stackinabox.util.requests_mock.registration(
                'localhost')

            request_model = requests.models.Request(
                method='GET',
                url='http://localhost/hello/'
            )
            prepared_request = session.prepare_request(request_model)
            res = session.send(prepared_request)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')

    def test_requests_get_session_access(self):
        session = core.get_session()

    def test_requests_session_state(self):
        session = core.requests_session()
        getstate = session.__getstate__

        stuff = getstate()

        replicated = core.requests_session()
        setstate = replicated.__setstate__
        setstate(stuff)

    def test_requests_session_merge_environment(self):
        session = core.requests_session()
        v = session.merge_environment_settings(
            'http://localhost/hello', None, None, False, None
        )


class TestRequestMockAdapter(base.UtilTestCase):

    def setUp(self):
        super(TestRequestMockAdapter, self).setUp()
        StackInABox.register_service(self.hello_service)
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestMockAdapter, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_adapter(self):
        session = core.requests_session()
        adapter = requests.adapters.HTTPAdapter()
        session.mount('field://', adapter)
        self.assertEqual(session.get_adapter('field://'), adapter)
        session.close()


@ddt.ddt
class TestRequestMockAdvanced(base.UtilTestCase):

    def setUp(self):
        super(TestRequestMockAdvanced, self).setUp()
        StackInABox.register_service(self.advanced_service)
        self.session = requests.Session()

    def tearDown(self):
        super(TestRequestMockAdvanced, self).tearDown()
        StackInABox.reset_services()
        self.session.close()

    def test_basic(self):
        stackinabox.util.requests_mock.session_registration(
            'localhost', self.session)

        res = self.session.get('http://localhost/advanced/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Hello')

        res = self.session.get('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'Good-Bye')

        expected_result = {
            'bob': 'bob: Good-Bye alice',
            'alice': 'alice: Good-Bye bob',
            'joe': 'joe: Good-Bye jane'
        }
        res = self.session.get(
            'http://localhost/advanced/g?bob=alice&alice=bob&joe=jane'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), expected_result)

        res = self.session.get('http://localhost/advanced/1234567890')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text, 'okay')

        res = self.session.get('http://localhost/advanced/_234567890')
        self.assertEqual(res.status_code, 595)

        res = self.session.put('http://localhost/advanced/h')
        self.assertEqual(res.status_code, 405)

        res = self.session.put('http://localhost/advanced2/i')
        self.assertEqual(res.status_code, 597)

    def test_context_requests_mock(self):
        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

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
            res = requests.get(
                'http://localhost/advanced/g?bob=alice&alice=bob&joe=jane'
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json(), expected_result)

    @ddt.data(
        ('head', 204, ''),
        ('delete', 204, ''),
        ('post', 200, 'created'),
        ('put', 200, 'updated'),
        ('patch', 200, 'patched'),
        ('options', 200, 'options'),
    )
    @ddt.unpack
    def test_extra_http_verbs(self, http_verb, response_status, response_body):
        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

            method_call = getattr(requests, http_verb)
            res = method_call('http://localhost/advanced/')
            self.assertEqual(res.status_code, response_status)
            self.assertEqual(res.text, response_body)

    @ddt.data(
        ('head', 204, ''),
        ('delete', 204, ''),
        ('get', 200, 'Hello'),
        ('post', 200, 'created'),
        ('put', 200, 'updated'),
        ('patch', 200, 'patched'),
        ('options', 200, 'options'),
    )
    @ddt.unpack
    def test_requests_session_by_verb(
        self, http_verb, response_status, response_body
    ):
        session = core.requests_session()

        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

            method_call = getattr(session, http_verb)
            res = method_call('http://localhost/advanced/')
            self.assertEqual(res.status_code, response_status)
            self.assertEqual(res.text, response_body)

    @ddt.data(
        ('head', 204, ''),
        ('delete', 204, ''),
        ('get', 200, 'Hello'),
        ('post', 200, 'created'),
        ('put', 200, 'updated'),
        ('patch', 200, 'patched'),
        ('options', 200, 'options'),
    )
    @ddt.unpack
    def test_requests_session_request(
        self, http_verb, response_status, response_body
    ):
        session = core.requests_session()

        with stackinabox.util.requests_mock.activate():
            stackinabox.util.requests_mock.registration(
                'localhost')

            res = session.request(http_verb, 'http://localhost/advanced/')
            self.assertEqual(res.status_code, response_status)
            self.assertEqual(res.text, response_body)
