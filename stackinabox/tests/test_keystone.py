"""
Stack-In-A-Box: Basic Test
"""
import unittest

import httpretty
import requests

import stackinabox.util_httpretty
from stackinabox.stack import StackInABox
from stackinabox.services.keystone.v2 import KeystoneV2Service


@httpretty.activate
class TestHttpretty(unittest.TestCase):

    def setUp(self):
        super(TestHttpretty, self).setUp()
        self.keystone = KeystoneV2Service()
        self.headers = {
            'x-auth-token': self.keystone.backend.get_admin_token()
        }
        StackInABox.register_service(self.keystone)

    def tearDown(self):
        super(TestHttpretty, self).tearDown()
        StackInABox.reset_services()

    def test_tenant_listing(self):
        stackinabox.util_httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/keystone/v2.0/tenants',
                           headers=self.headers)
        self.assertEqual(res.status_code, 200)
        tenant_data = res.json()

        # There is always 1 tenant - the system
        self.assertEqual(len(tenant_data['tenants']), 1)

        self.keystone.backend.add_tenant(tenantname='neo',
                                         description='The One')

        res = requests.get('http://localhost/keystone/v2.0/tenants',
                           headers=self.headers)
        self.assertEqual(res.status_code, 200)
        tenant_data = res.json()

        self.assertEqual(len(tenant_data['tenants']), 2)
        self.assertEqual(tenant_data['tenants'][1]['name'], 'neo')
        self.assertEqual(tenant_data['tenants'][1]['description'], 'The One')
        self.assertTrue(tenant_data['tenants'][1]['enabled'])

    def test_user_listing(self):
        stackinabox.util_httpretty.httpretty_registration('localhost')

        neo_tenant_id = self.keystone.backend.add_tenant(tenantname='neo',
                                                         description='The One')
        tom = self.keystone.backend.add_user(neo_tenant_id,
                                             'tom',
                                             'tom@theone.matrix',
                                             'bluepill',
                                             'iamnottheone',
                                             enabled=True)
        self.keystone.backend.add_user_role_by_rolename(neo_tenant_id,
                                                        tom,
                                                        'identity:user-admin')

        self.keystone.backend.add_token(neo_tenant_id, tom)
        user_data = self.keystone.backend.get_token_by_userid(tom)
        self.headers['x-auth-token'] = user_data['token']
        res = requests.get('http://localhost/keystone/v2.0/users',
                           headers=self.headers)
        print(res.text)
        self.assertEqual(res.status_code, 200)
        user_data = res.json()

        self.assertEqual(len(user_data['users']), 1)

        self.keystone.backend.add_user(neo_tenant_id,
                                       'neo',
                                       'neo@theone.matrix',
                                       'redpill',
                                       'iamtheone',
                                       enabled=True)

        res = requests.get('http://localhost/keystone/v2.0/users',
                           headers=self.headers)
        self.assertEqual(res.status_code, 200)
        user_data = res.json()

        self.assertEqual(len(user_data['users']), 2)
        StackInABox.reset_services()
