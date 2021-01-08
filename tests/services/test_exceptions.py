import re

import ddt

from stackinabox.services import exceptions

from tests.services import base


class TestExceptions(base.TestCase):

    def test_parentage(self):
        self.assertIsInstance(exceptions.StackInABoxServiceErrors(), Exception)

        exception_objs = []
        for obj in dir(exceptions):
            if not obj.startswith('__') and obj != 'StackInABoxServiceErrors':
                exception_objs.append(obj)

        for exception_obj in exception_objs:
            self.assertIsInstance(
                getattr(exceptions, exception_obj)(),
                exceptions.StackInABoxServiceErrors
            )
