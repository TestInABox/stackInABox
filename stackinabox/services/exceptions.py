"""
Stack-In-A-Box Service and Routing Exceptions
"""


class StackInABoxServiceErrors(Exception):
    """Stack-In-A-Box Service Exception object.

    All Stack-In-A-Box Service specific exceptions are
    base on StackInABoxServiceErrors
    """


class CircularReferenceError(StackInABoxServiceErrors):
    """Exception: Route would result in a circular reference"""


class RouteAlreadyRegisteredError(StackInABoxServiceErrors):
    """Exception: Route is already registered."""


class InvalidRouteRegexError(StackInABoxServiceErrors):
    """Exception: Regex for URI is invalid."""
