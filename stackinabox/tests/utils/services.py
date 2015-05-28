import json
import logging
import re

import six
from six.moves.urllib import parse

from stackinabox.services.service import StackInABoxService


logger = logging.getLogger(__name__)


class AdvancedService(StackInABoxService):

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
