import json
import logging
import re

import six
from six.moves.urllib import parse

from stackinabox.services.service import StackInABoxService


logger = logging.getLogger(__name__)


class AdvancedService(StackInABoxService):

    # extra methods to test for in validating the provided utilities
    # when applicable (f.e request-mock)
    POTENTIAL_RESPONSES = {
        'head': (204, ''),
        'post': (200, 'created'),
        'put': (200, 'updated'),
        'patch': (200, 'patched'),
        'options': (200, 'options'),
        'delete': (204, '')
    }

    def __init__(self):
        super(AdvancedService, self).__init__('advanced')
        self.register(StackInABoxService.GET, '/',
                      AdvancedService.handler)
        self.register(StackInABoxService.GET, '/h',
                      AdvancedService.alternate_handler)
        self.register(StackInABoxService.GET, '/g',
                      AdvancedService.query_handler)
        self.register(StackInABoxService.GET,
                      re.compile('^/\d+$'),
                      AdvancedService.regex_handler)

        for key in self.POTENTIAL_RESPONSES.keys():
            self.register(key.upper(), '/',
                          AdvancedService.extra_method_handler)

    def extra_method_handler(self, request, uri, headers):
        # generic handler so look-up the real METHOD and provide
        # an appropriate response
        method = request.method.lower()

        try:
            status_code, response_body = self.POTENTIAL_RESPONSES[method]
            response = (
                status_code,
                headers,
                response_body
            )

        except LookupError:
            response = (589, headers, 'unknown method: {0}'.format(method))

        return response

    def handler(self, request, uri, headers):
        return (200, headers, 'Hello')

    def alternate_handler(self, request, uri, headers):
        return (200, headers, 'Good-Bye')

    def query_handler(self, request, uri, headers):
        parsed_uri = parse.urlparse(uri)
        query = parsed_uri.query

        if len(query) > 0:
            queries = parse.parse_qsl(query)

            body = {}
            for k, v in queries:
                body[k] = '{0}: Good-Bye {1}'.format(k, v)

            return (200, headers, json.dumps(body))
        else:
            logger.debug('No query string')
            return (200, headers, 'Where did you go?')

    def regex_handler(self, request, uri, headers):
        return (200, headers, 'okay')
