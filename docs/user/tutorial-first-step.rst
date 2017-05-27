First Step
----------

Before continuing be sure to :ref:`install <install>` StackInABox
in your test environment. In your test module, add a directory to
hold your StackInABoxService and cd into it:

.. code:: bash

    $ cd tests
    $ mkdir service

Next we'll create a new file that will host the test StackInABoxService:

.. code:: bash

    $ touch lookupService.py

Open the file using your favorite text editor and add the following:

.. code:: python

    from stackinabox.services.service import StackInABoxService

    class LookupService(StackInABoxService):

        def __init__(self):
            super(LookupService, self).__init__('lookup')
            # We'll store values in self.storage
            self.storage = dict()

This is the basic structure of the service. Everything from here is
adding HTTP Resources to the test service. For the key-value store
we'll add a POST, GET, and DELETE. We'll also add a HEAD to get a count
of how many items are in the key-value store.

First, let's add check to see how many items there are. Add the following
method to the LookupService class:

.. code:: python

    def get_key_value_count(self, request, uri, headers):
        headers['X-Key-Value-Count'] = len(self.storage)
        return (204, headers, '')

This implements the logic that the RESTful API end-point for the HEAD
operation. The operation will be generic the whole service; so we can use the
very simple registration operation. To do so, update the ```__init__(self)```
to the following:

.. code:: python

    def __init__(self):
        super(LookupService, self).__init__('lookup')
        # We'll store values in self.storage
        self.storage = dict()
        self.register(StackInABoxService.GET,
                      '/',
                      LookupService.get_key_value_count)

Please note that the parameter to the ```__init__()``` is extremely important
as this is what identifies the service within StackInABox. We'll discuss this
more later when we hookup the test.

This version of the LookupService can will work in a test now. However, we want
to make more useful tests. The key will be used in the URI, and the value will
be in the body. So let's add the other end-points:

.. code:: python

    def set_key_value(self, request, uri, headers):
        # some test times the body is a string type
        # other times it's a byte type
        key_value = request.body.decode('utf-8') if hasattr(
            request.body, 'decode') else request.body
        key_name = uri[1:]

        self.storage[key_name] = key_value

        return (204, headers, '')

    def get_key(self, request, uri, headers):
        key_name = uri[1:]
        if key_name in self.storage:
            key_value = self.storage[key_name]
            return (200, headers, key_value)
        else:
            return (404, headers, 'Not Found')

    def delete_key(self, request, uri, headers):
        key_name = uri[1:]
        if key_name in self.storage:
            del self.storage[key_value]
            return (204, headers, '')
        else:
            return (404, headers, 'Not Found')

The above relies on being able to match the URI using a regex pattern such as
the following:

..

    ^/[0-9a-zA-Z]?$

Fortunately, StackInABox provides the ability to match a handler function via
either a static string like we did with the HEAD operation or with a regex
like in the following to register the three handler functions above:

.. code:: python

    import regex

    class LookupService(StackInABoxService):

        LookupServiceKeyRegEx = re.compile('^/[0-9a-zA-Z]?$')

        def __init__(self):
            super(LookupService, self).__init__('lookup')
            # We'll store values in self.storage
            self.storage = dict()
            # registration via a static string:
            self.register(StackInABoxService.HEAD,
                          '/',
                          LookupService.get_key_value_count)
            # registration via regexi:
            self.register(StackInABoxService.DELETE,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.delete_key)
            self.register(StackInABoxService.GET,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.get_key)
            self.register(StackInABoxService.POST,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.set_key_value)

So the final class will look like:

.. code:: python

    import regex

    from stackinabox.services.service import StackInABoxService

    class LookupService(StackInABoxService):

        LookupServiceKeyRegEx = re.compile('^/[0-9a-zA-Z]?$')

        def __init__(self):
            super(LookupService, self).__init__('lookup')
            # We'll store values in self.storage
            self.storage = dict()
            # registration via a static string:
            self.register(StackInABoxService.HEAD,
                          '/',
                          LookupService.get_key_value_count)
            # registration via regexi:
            self.register(StackInABoxService.DELETE,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.delete_key)
            self.register(StackInABoxService.GET,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.get_key)
            self.register(StackInABoxService.POST,
                          LookupService.LookupServiceKeyRegEx,
                          LookupService.set_key_value)

        def get_key_value_count(self, request, uri, headers):
            headers['X-Key-Value-Count'] = len(self.storage)
            return (204, headers, '')

        def set_key_value(self, request, uri, headers):
            # some test times the body is a string type
            # other times it's a byte type
            key_value = request.body.decode('utf-8') if hasattr(
                request.body, 'decode') else request.body
            key_name = uri[1:]

            self.storage[key_name] = key_value

            return (204, headers, '')

        def get_key(self, request, uri, headers):
            key_name = uri[1:]
            if key_name in self.storage:
                key_value = self.storage[key_name]
                return (200, headers, key_value)
            else:
                return (404, headers, 'Not Found')

        def delete_key(self, request, uri, headers):
            key_name = uri[1:]
            if key_name in self.storage:
                del self.storage[key_value]
                return (204, headers, '')
            else:
                return (404, headers, 'Not Found')

