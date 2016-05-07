"""
Stack-In-A-Box: Hello
"""
from stackinabox.services.service import StackInABoxService


class HelloService(StackInABoxService):
    """Example Hello World Stack-In-A-Box Service application
    """

    def __init__(self):
        """Initialize and register the single end-point
        """
        super(HelloService, self).__init__('hello')
        self.register(StackInABoxService.GET, '/', HelloService.handler)

    def handler(self, request, uri, headers):
        """Single End-Point that simply returns 'hello'
        """
        return (200, headers, 'Hello')
