"""
Stack-In-A-Box: HTTPretty Support
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
        :param args: A tuple containing all the positional arguments. Any
            StackInABoxService arguments are removed before being passed to
            the actual function.
        :param kwargs: A dictionary of keyword args that are passed to the
            actual function.
        """
        self.uri = uri
        self.services = []
        self.args = []
        self.kwargs = kwargs

        for arg in args:
            if isinstance(arg, StackInABoxService):
                self.services.append(arg)
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

            return_value = None

            def run():
                responses.mock.start()

                StackInABox.reset_services()
                for service in self.services:
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
