"""
Stack-In-A-Box: Hello
"""
from stackinabox.services.service import StackInABoxService


class HelloService(StackInABoxService):

    def __init__(self):
        super(HelloService, self).__init__('hello')
        self.register(StackInABoxService.GET, '/', HelloService.handler)

    def handler(self, request, uri, headers):
        return (200, headers, 'Hello')
