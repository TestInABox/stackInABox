"""
Stack-In-A-Box: Responses Support via decorator
"""
import functools
import logging
import re

import responses
import six

from stackinabox.services.service import StackInABoxService
from stackinabox.stack import StackInABox
from stackinabox.util.responses.core import (
    responses_registration
)
from stackinabox.util.tools import CaseInsensitiveDict


logger = logging.getLogger(__name__)


class stack_activate(object):
    """
    Decorator class to make use of Responses and Stack-In-A-Box
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

            return_value = None

            def run():
                responses.mock.start()

                StackInABox.reset_services()
                for service in self.services.values():
                    StackInABox.register_service(service)
                responses_registration(self.uri)
                return_value = fn(*args_finalized, **kwargs)
                StackInABox.reset_services()

                responses.mock.stop()
                responses.mock.reset()

            with responses.RequestsMock():
                run()

            return return_value

        return wrapped
