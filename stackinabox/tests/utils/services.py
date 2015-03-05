import json
import logging

import six

from stackinabox.services.service import StackInABoxService


class AdvancedService(StackInABoxService):

    def __init__(self):
        super(AdvancedService, self).__init__('advanced')
        self.register(StackInABoxService.GET, '/',
                      AdvancedService.handler)
        self.register(StackInABoxService.GET, '/h',
                      AdvancedService.alternate_handler)
        self.register(StackInABoxService.GET, '/g',
                      AdvancedService.query_handler)

    def handler(self, request, uri, headers):
        return (200, headers, 'Hello')

    def alternate_handler(self, request, uri, headers):
        return (200, headers, 'Good-Bye')

    def query_handler(self, request, uri, headers):
        query = None
        if '?' in uri:
            path, querys = uri.split('?')
            querys = querys.replace(';', '&')
            query = {}
            for kv in querys.split('&'):
                k, v = kv.split('=')
                query[k] = v

            body = {}
            for k, v in six.iteritems(query):
                body[k] = '{0}: Good-Bye {1}'.format(k, v)

            return (200, headers, json.dumps(body))
        else:
            logger.debug('No query string')
            return (200, headers, 'Where did you go?')
