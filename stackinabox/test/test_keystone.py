"""
Stack-In-A-Box: Basic Test
"""
import unittest

import httpretty
import requests

import stackinabox.httpretty
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

    def test_tenant_listing(self):
        stackinabox.httpretty.httpretty_registration('localhost')

        res = requests.get('http://localhost/keystone/v2.0/tenants',
                           headers=self.headers)
        self.assertEqual(res.status_code, 200)
        tenant_data = res.json()

        self.assertEqual(len(tenant_data['tenants']), 0)

        self.keystone.backend.add_tenant(tenantname='neo', description='The One')

        res = requests.get('http://localhost/keystone/v2.0/tenants',
                           headers=self.headers)
        self.assertEqual(res.status_code, 200)
        tenant_data = res.json()

        self.assertEqual(len(tenant_data['tenants']), 1)
        self.assertEqual(tenant_data['tenants'][0]['name'], 'neo')
        self.assertEqual(tenant_data['tenants'][0]['description'], 'The One')
        self.assertTrue(tenant_data['tenants'][0]['enabled'])
