import logging

from stackinabox.services import exceptions


logger = logging.getLogger(__name__)


class StackInABoxServiceRouter(object):
    """Stack-In-A-Box Service Router object.

    Advanced URI routing to support Service-within-Service routing
    """

    def __init__(self, name, uri, obj, parent_obj):
        """Initialize router.

        :param name: service name for the route
        :param uri: URI to match for the route
        :param obj: optional object for sub-service routing
        :param parent_obj: parent for sub-service routing

        :raises: CircularReferenceError if a circular route is detected
        """
        self.service_name = name
        self.uri = uri
        self.obj = obj
        self.parent_obj = parent_obj
        self.methods = {}

        # Ensure we do not have any circular references
        if None not in (self.obj, self.parent_obj):
            if self.obj == self.parent_obj:
                raise exceptions.CircularReferenceError

    @property
    def is_subservice(self):
        """Is the object managing a sub-service."""
        if self.obj is not None:
            return True

        return False

    def set_subservice(self, obj):
        """Add a sub-service object.

        :param obj: stackinabox.services.StackInABoxService instance
        :raises: RouteAlreadyRegisteredError if the route is already registered
        :raises: CircularReferenceError if a circular route is detected
        :returns: n/a
        """
        # ensure there is not already a sub-service
        if self.obj is not None:
            raise exceptions.RouteAlreadyRegisteredError(
                'Service Router ({0} - {1}): Route {2} already has a '
                'sub-service handler'
                .format(id(self), self.service_name, self.uri))

        # warn if any methods are already registered
        if len(self.methods):
            logger.debug(
                'WARNING: Service Router ({0} - {1}): Methods detected '
                'on Route {2}. Sub-Service {3} may be hidden.'
                .format(id(self), self.service_name, self.uri, obj.name))

        # Ensure we do not have any circular references
        if obj == self.parent_obj:
            raise exceptions.CircularReferenceError

        # if no errors, save the object and update the URI
        self.obj = obj
        self.obj.base_url = '{0}/{1}'.format(self.uri, self.service_name)

    def update_uris(self, new_uri):
        """Update all URIS.

        :param new_uri: URI to switch to and update the matching
        :returns: n/a

        .. note:: This overwrites any existing URI
        """
        self.uri = new_uri

        # if there is a sub-service, update it too
        if self.obj:
            self.obj.base_url = '{0}/{1}'.format(self.uri, self.service_name)

    def register_method(self, method, fn):
        """Register an HTTP method and handler function.

        :param method: string, HTTP verb
        :param fn: python function handling the request
        :raises: RouteAlreadyRegisteredError if the route is already registered
        :returns: n/a
        """

        # ensure the HTTP verb is not already registered
        if method not in self.methods.keys():
            logger.debug(
                'Service Router ({0} - {1}): Adding method {2} on route {3}'
                .format(
                    id(self),
                    self.service_name,
                    method,
                    self.uri
                )
            )
            self.methods[method] = fn

        else:
            raise exceptions.RouteAlreadyRegisteredError(
                'Service Router ({0} - {1}): Method {2} already registered '
                'on Route {3}'
                .format(
                    id(self),
                    self.service_name,
                    method,
                    self.uri
                )
            )

    def __call__(self, method, request, uri, headers):
        """Python callable interface.

        :param method: HTTP verb
        :param request: Request object
        :param uri: URI of the request
        :param headers: response headers for the request

        :returns: tuple - (int, dict, string) containing:
                          int - the http response status code
                          dict - the headers for the http response
                          string - http string response
        """

        # Check the registered methods, preferring a function to sub-service
        if method in self.methods:
            logger.debug(
                'Service Router ({0} - {1}): Located Method {2} on Route '
                '{3}. Calling...'.format(
                    id(self),
                    self.service_name,
                    method,
                    self.uri
                )
            )

            return self.methods[method](
                self.parent_obj,
                request,
                uri,
                headers
            )

        # If no method, is there a sub-service that handles it?
        elif self.obj is not None:
            logger.debug(
                'Service Router ({0} - {1}): Located Subservice {2} on Route '
                '{3}. Calling...'.format(
                    id(self),
                    self.service_name,
                    self.obj.name,
                    self.uri
                )
            )

            return self.obj.sub_request(
                method,
                request,
                uri,
                headers
            )

        # otherwise, return an HTTP 405 error
        else:
            logger.debug(
                'Service Router ({0} - {1}): No Method handler for service'
                .format(
                    id(self),
                    self.service_name
                )
            )

            return (
                405,
                headers,
                '{0} not supported. Supported Methods are {1}'.format(
                    method, self.methods
                )
            )
