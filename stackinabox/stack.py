"""
Stack-In-A-Box: Stack Management
"""
import logging
import re
import uuid

import threading


logger = logging.getLogger(__name__)


class ServiceAlreadyRegisteredError(Exception):
    pass


class StackInABox(object):

    @classmethod
    def reset_services(cls):
        logger.debug('Resetting services')
        return local_store.instance.reset()

    @classmethod
    def register_service(cls, service):
        logger.debug('Registering service {0}'.format(service.name))
        return local_store.instance.register(service)

    @classmethod
    def call_into(cls, method, request, uri, headers):
        logger.debug('Request: {0} - {1}'.format(method, uri))
        return local_store.instance.call(method,
                                         request,
                                         uri,
                                         headers)

    @classmethod
    def update_uri(cls, uri):
        logger.debug('Request: Update URI to {0}'.format(uri))
        local_store.instance.base_url = uri

    def __init__(self):
        self.__id = uuid.uuid4()
        self.__base_url = '/'
        self.services = {
        }

    @staticmethod
    def __get_service_url(base_url, service_name):
        return '{0}/{1}'.format(base_url, service_name)

    @staticmethod
    def __get_services_url(url, base_url):
        length = len(base_url)
        checks = ['http://', 'https://']
        for check in checks:
            if url.startswith(check):
                length = length + len(check)
                break

        result = url[length:]
        logger.debug('{0} from {1} equals {2}'
                     .format(base_url, url, result))
        return result

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
        logger.debug('StackInABox({0}): Updating URL from {1} to {2}'
                     .format(self.__id, self.__base_url, value))
        self.__base_url = value
        for k, v in self.services.items():
            matcher, service = v
            service.base_url = StackInABox.__get_service_url(value,
                                                             service.name)
            logger.debug('StackInABox({0}): Service {1} has url {2}'
                         .format(self.__id, service.name, service.base_url))

    def reset(self):
        logger.debug('StackInABox({0}): Resetting...'
                     .format(self.__id))
        for k, v in self.services.items():
            matcher, service = v
            logger.debug('StackInABox({0}): Resetting Service {1}'
                         .format(self.__id, service.name))
            service.reset()

        self.services = {}

        logger.debug('StackInABox({0}): Reset Complete'
                     .format(self.__id))

    def register(self, service):
        if service.name not in self.services.keys():
            logger.debug('StackInABox({0}): Registering Service {1}'
                         .format(self.__id, service.name))
            regex = '^/{0}'.format(service.name)
            self.services[service.name] = [
                re.compile(regex),
                service
            ]
            service.base_url = StackInABox.__get_service_url(self.base_url,
                                                             service.name)
            logger.debug('StackInABox({0}): Service {1} has url {2}'
                         .format(self.__id, service.name, service.base_url))
        else:
            raise ServiceAlreadyRegisteredError(
                'Service {0} is already registered'.format(service.name))

    def call(self, method, request, uri, headers):
        logger.debug('StackInABox({0}): Received call to {1} - {2}'
                     .format(self.__id, method, uri))
        service_uri = StackInABox.__get_services_url(uri, self.base_url)
        for k, v in self.services.items():
            matcher, service = v
            logger.debug('StackInABox({0}): Checking if Service {1} handles...'
                         .format(self.__id, service.name))
            logger.debug('StackInABox({0}): ...using regex pattern {1} '
                         'against {2}'
                         .format(self.__id, matcher.pattern, service_uri))
            if matcher.match(service_uri):
                logger.debug('StackInABox({0}): Trying Service {1} handler...'
                             .format(self.__id, service.name))

                try:
                    service_caller_uri = service_uri[(len(service.name) + 1):]
                    return service.request(method,
                                           request,
                                           service_caller_uri,
                                           headers)
                except Exception as ex:
                    return (500,
                            headers,
                            'Service Handler had an error: {0}'.format(ex))
        return (500, headers, 'Unknown service')

local_store = threading.local()
local_store.instance = StackInABox()
