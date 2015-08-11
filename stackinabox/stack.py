"""
Stack-In-A-Box: Stack Management
"""
import logging
import re
import threading
import uuid

import six


logger = logging.getLogger(__name__)


class ServiceAlreadyRegisteredError(Exception):
    pass


class StackInABox(object):
	"""Stack-In-A-Box Testing Service

	StackInABox provides a testing framework for RESTful APIs

	The framework provides a thread-local instance holding the
	StackInABoxService objects that are representing the
	RESTful APIs.

	The StackInABox object provides a means of accessing it
	from anywhere in a thread; however, it is not necessarily
	thread-safe at this time. If one is careful o setup StackInABox
	and write StackInABoxService's that are thread-safe
	themselves, then there is no reason it could not be used in a
	multi-threaded or multi-processed test.
	"""

    @classmethod
    def reset_services(cls):
		"""Reset the thread's StackInABox instance
		"""
        logger.debug('Resetting services')
        return local_store.instance.reset()

    @classmethod
    def register_service(cls, service):
		"""Add a service to the thread's StackInABox instance

		:parameter: service - StackInABoxService instance to add to the test
		
		For return value and errors see StackInABox.register()
		"""
        logger.debug('Registering service {0}'.format(service.name))
        return local_store.instance.register(service)

    @classmethod
    def call_into(cls, method, request, uri, headers):
		"""Make a call into the thread's StackInABox instance

		:parameter: method - HTTP Method (e.g GET, POST)
		:parameter: request - a Request object containing the request data
		:parameter: uri - the URI of the request submitted with the method
		:parameter: headers - the return headers in a Case-Insensitive dict

		For return value and errors see StackInABox.call()
		"""
        logger.debug('Request: {0} - {1}'.format(method, uri))
        return local_store.instance.call(method,
                                         request,
                                         uri,
                                         headers)

    @classmethod
    def hold_onto(cls, name, obj):
		"""Add data into the a storage area provided by the framework

		Note: The data is stored with the thread local instance.

		:parameter: name - name of the data to be stored
		:parameter: obj - data to be stored

		For return value and errors see StackInABox.into_hold()
		"""
        logger.debug('Holding on {0} of type {1} with id {2}'
                     .format(name, type(obj), id(obj)))
        local_store.instance.into_hold(name, obj)

    @classmethod
    def hold_out(cls, name):
		"""Get data from the storage area provided by the framework

		Note: The data is retrieved from the thread local instance.

		:parameter: name - name of the data to be retrieved

		:returns: The data associated with the specified name.

		For errors see StackInABox.from_hold()
		"""
        logger.debug('Retreiving {0} from hold'
                     .format(name))
        obj = local_store.instance.from_hold(name)
        logger.debug('Retrieved {0} of type {1} with id {2} from hold'
                     .format(name, type(obj), id(obj)))
        return obj

    @classmethod
    def update_uri(cls, uri):
		"""Set the URI of the StackInABox framework

		:parameter: uri - the base URI used to match the service.
		"""
        logger.debug('Request: Update URI to {0}'.format(uri))
        local_store.instance.base_url = uri

    def __init__(self):
		"""Initialize the StackInABox instance.

		Default Base URI is '/'.

		There are no services registered, and the storage hold
		is a basic dictionary object used as a key-value store.
		"""
        self.__id = uuid.uuid4()
        self.__base_url = '/'
        self.services = {
        }
        self.holds = {
        }

    @staticmethod
    def __get_service_url(base_url, service_name):
		"""Get the URI for a given StackInABoxService

		Note: this is an internal function

		:parameter: base_url - base URL to use
		:parameter: service_name - name of the service the URI is for
		"""
        return '{0}/{1}'.format(base_url, service_name)

    @staticmethod
    def get_services_url(url, base_url):
		"""Get the URI from a given URL.

		:returns: URI within the URL
		"""
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
		"""Base URL property
		"""
        return self.__base_url

    @base_url.setter
    def base_url(self, value):
		"""Set the Base URL property, updating all associated services
		"""
        logger.debug('StackInABox({0}): Updating URL from {1} to {2}'
                     .format(self.__id, self.__base_url, value))
        self.__base_url = value
        for k, v in six.iteritems(self.services):
            matcher, service = v
            service.base_url = StackInABox.__get_service_url(value,
                                                             service.name)
            logger.debug('StackInABox({0}): Service {1} has url {2}'
                         .format(self.__id, service.name, service.base_url))

    def reset(self):
		"""Reset StackInABox to a like-new state
		"""
        logger.debug('StackInABox({0}): Resetting...'
                     .format(self.__id))
        for k, v in six.iteritems(self.services):
            matcher, service = v
            logger.debug('StackInABox({0}): Resetting Service {1}'
                         .format(self.__id, service.name))
            service.reset()

        self.services = {}
        self.holds = {}

        logger.debug('StackInABox({0}): Reset Complete'
                     .format(self.__id))

    def register(self, service):
		"""Add a service to the thread's StackInABox instance

		:parameter: service - StackInABoxService instance to add to the test
		
		:returns: None
		:raises: ServiceAlreadyRegisteredError if the service already exists
		"""
        if service.name not in self.services.keys():
            logger.debug('StackInABox({0}): Registering Service {1}'
                         .format(self.__id, service.name))
            regex = '^/{0}/'.format(service.name)
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
		"""Make a call into the thread's StackInABox instance

		:parameter: method - HTTP Method (e.g GET, POST)
		:parameter: request - a Request object containing the request data
		:parameter: uri - the URI of the request submitted with the method
		:parameter: headers - the return headers in a Case-Insensitive dict

		:returns: A tuple containing - (i) the Status Code, (ii) the response
		          headers, and (iii) the response body data

		This function should not emit any Exceptions
		"""
        logger.debug('StackInABox({0}): Received call to {1} - {2}'
                     .format(self.__id, method, uri))
        service_uri = StackInABox.get_services_url(uri, self.base_url)

        for k, v in six.iteritems(self.services):
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
                    logger.exception('StackInABox({0}): Service {1} - '
                                     'Internal Failure'
                                     .format(self.__id, service.name))
                    return (596,
                            headers,
                            'Service Handler had an error: {0}'.format(ex))
        return (597, headers, 'Unknown service - {0}'.format(service_uri))

    def into_hold(self, name, obj):
		"""Add data into the a storage area provided by the framework

		Note: The data is stored with the thread local instance.

		:parameter: name - name of the data to be stored
		:parameter: obj - data to be stored

		:returns: N/A
		:raises: N/A
		"""
        logger.debug('StackInABox({0}): Holding onto {1} of type {2} '
                     'with id {3}'
                     .format(self.__id, name, type(obj), id(obj)))
        self.holds[name] = obj

    def from_hold(self, name):
		"""Get data from the storage area provided by the framework

		Note: The data is retrieved from the thread local instance.

		:parameter: name - name of the data to be retrieved

		:returns: The data associated with the specified name.
		:raises: Lookup/KeyError error if the name does not match
		         a value in the storage
		"""
        logger.debug('StackInABox({0}): Retreiving {1} from the hold'
                     .format(self.__id, name))
        obj = self.holds[name]
        logger.debug('StackInABox({0}): Retrieved {1} of type {2} with id {3}'
                     .format(self.__id, name, type(obj), id(obj)))

        return obj

# Thread local instance of StackInABox
local_store = threading.local()
local_store.instance = StackInABox()
