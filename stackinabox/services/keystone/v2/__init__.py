"""
Stack-In-A-Box: OpenStack Keystone v2 Support
"""
import json
import logging
import uuid

from stackinabox.services.service import StackInABoxService
from stackinabox.services.keystone.backend import KeystoneBackend


logger = logging.getLogger(__name__)


class KeystoneV2Service(StackInABoxService):

    def __init__(self):
        super(KeystoneV2Service, self).__init__('keystone/v2.0')
        self.__id = uuid.uuid4()
        self.__backend = KeystoneBackend()

        self.register(StackInABoxService.GET, '/tenants', KeystoneV2Service.handle_list_tenants)
        self.register(StackInABoxService.GET, '/users', KeystoneV2Service.handle_list_users)

    @property
    def backend(self):
        return self.__backend

    @backend.setter
    def backend(self, value):
        if isinstance(value, KeystoneBackend):
            self.__backend = value
        else:
            raise TypeError('backend is not an instance of KeystoneBackend')

    def handle_list_tenants(self, request, uri, headers):
        req_headers = request.headers
        '''

        200, 203 -> OK
        400 -> Bad Request: one or more required parameters is missing or invalid
        401 -> not authorized
        403 -> forbidden (no permission)
        404 -> Not found
        405 -> Invalid Method
        413 -> Over Limit - too many items requested
        503 -> Service Fault
        '''
        logger.debug('KeystoneV2Service({0}): Received request {1}'
                     .format(self.__id, uri))
        logger.debug('KeystoneV2Service({0}): Received headers {1}'
                     .format(self.__id, request.headers))

        if 'x-auth-token' in req_headers:
            if req_headers['x-auth-token'] == self.backend.get_admin_token():
                """
                Body on success:
                body = {
                    'tenants' : [ {'id': 01234, 'name': 'bob', 'description': 'joe bob', 'enabled': True }]
                    'tenants_links': []
                }
                """
                response_body = {
                    'tenants' : [tenant_info for tenant_info in self.backend.get_tenants()],
                    'tenants_links': []
                }
                return (200, headers, json.dumps(response_body))

            else:
                return (401, headers, 'Not Authorized')

        else:
            return (403, headers, 'Forbidden')

    def handle_list_users(self, request, uri, headers):
        req_headers = request.headers
        '''
        '''
        logger.debug('KeystoneV2Service({0}): received request {1}'
                     .format(self.__id, uri))
        logger.debug('KeystoneV2Service({0}): Received headers {1}'
                     .format(self.__id, request.headers))

        def user_data_filter(user):
            logger.debug('Filtering data on {0}'.format(user))
            return {
                'userid': user['userid'],
                'enabled': user['enabled'],
                'username': user['username'],
                'email': user['email'],
            }

        if 'x-auth-token' in req_headers:
            try:
                user_data = self.backend.validate_token_admin(req_headers['x-auth-token']) 
                if user_data:
                    logger.debug('KeystoneV2Service({0}): Token Valid for tenantid {1}'
                                 .format(self.__id, user_data['tenantid']))
                    response_body = {
                        'users': [user_data_filter(user_info)
                                  for user_info in
                                  self.backend.get_users_for_tenant_id(user_data['tenantid'])]
                    }
                    return (200, headers, json.dumps(response_body))

                else:
                    return (200, headers, json.dumps({'users': []}))

            except Exception as ex:
                return (401, headers, 'Not Authorized - {0} {1}'.format(ex, type(ex)))
        else:
            return (403, headers, 'Forbidden')
