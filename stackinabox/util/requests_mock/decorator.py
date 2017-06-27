"""
Stack-In-A-Box: Requests-Mock Support via Decorator
"""
import functools
import logging
import re

import requests

from stackinabox.services.service import StackInABoxService
from stackinabox.stack import StackInABox
from stackinabox.util.requests_mock.core import (
    activate as requests_mock_activate,
    requests_mock_session_registration,
    requests_mock_registration
)
from stackinabox.util.tools import CaseInsensitiveDict


logger = logging.getLogger(__name__)


class stack_activate(object):
    """
    Decorator class to make use of Requests-Mock and Stack-In-A-Box
    extremely simple to do.
    """

    def __init__(self, uri, *args, **kwargs):
        """
        Initialize the decorator instance

        :param uri: URI Stack-In-A-Box will use to recognize the HTTP calls
            f.e 'localhost'.
        :param text_type access_services: name of a keyword parameter in the
            test function to assign access to the services created in the
            arguments to the decorator.
        :param text_type session: name of a keyword parameter in the
            test function to assign a requests.Session instance for use
            in the test function. The requests.Session instance will be
            configured for StackInABox.
        :param args: A tuple containing all the positional arguments. Any
            StackInABoxService arguments are removed before being passed to
            the actual function.
        :param kwargs: A dictionary of keyword args that are passed to the
            actual function.
        """
        self.uri = uri
        self.services = {}
        self.args = []
        self.kwargs = kwargs

        if "access_services" in self.kwargs:
            self.enable_service_access = self.kwargs["access_services"]
            del self.kwargs["access_services"]
        else:
            self.enable_service_access = None

        if "session" in self.kwargs:
            self.session = self.kwargs["session"]
            del self.kwargs["session"]
        else:
            self.session = None

        for arg in args:
            if isinstance(arg, StackInABoxService):
                self.services[arg.name] = arg
            else:
                self.args.append(arg)

    def __call__(self, fn):
        """
        Call to actually wrap the function call.
        """

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            args_copy = list(args)
            for arg in self.args:
                args_copy.append(arg)
            args_finalized = tuple(args_copy)
            kwargs.update(self.kwargs)

            if self.enable_service_access is not None:
                kwargs[self.enable_service_access] = self.services

            with requests_mock_activate():
                if self.session is not None:
                    kwargs[self.session] = requests.Session()

                    StackInABox.reset_services()
                    for service in self.services.values():
                        StackInABox.register_service(service)
                    requests_mock_session_registration(
                        self.uri,
                        kwargs[self.session]
                    )
                    return_value = fn(*args_finalized, **kwargs)
                    StackInABox.reset_services()

                else:
                    StackInABox.reset_services()
                    for service in self.services.values():
                        StackInABox.register_service(service)
                    requests_mock_registration(self.uri)
                    return_value = fn(*args_finalized, **kwargs)
                    StackInABox.reset_services()

            return return_value

        return wrapped