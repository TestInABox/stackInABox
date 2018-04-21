from tests import base

from tests.utils import services
from tests.utils import hello


class TestCase(base.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

    def tearDown(self):
        super(TestCase, self).tearDown()


class UtilTestCase(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.hello_service = hello.HelloService()
        self.advanced_service = services.AdvancedService()

    def tearDown(self):
        super(TestCase, self).tearDown()
