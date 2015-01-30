from httpretty import register_uri
from httpretty.http import HttpBaseClass


def httpretty_callback(request, uri, headers):
    method = request.method
    return (200, headers, 'Hello')

def httpretty_registration(uri):
    for method in HttpBaseClass.METHODS:
        register_uri(method, uri, body=httpretty_callback)
