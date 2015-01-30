import responses

def responses_callback(request):
    method = request.method
    headers = request.headers
    uri = request.url
    return (200, headers, 'Hello') 

def responses_registration(uri):
    METHODS = [
        responses.DELETE,
        responses.GET,
        responses.HEAD,
        responses.OPTIONS,
        responses.PATCH,
        responses.POST,
        responses.PUT
    ]
    for method in METHODS:
        responses.add_callback(method,
                               uri,
                               callback=responses_callback)
