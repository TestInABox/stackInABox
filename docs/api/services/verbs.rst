.. _verbs:

HTTP Verbs Support
==================

The `StackInABoxService` object provides the ability to register arbitrary functions
against an arbitrary set of HTTP Verbs. The object provides definitions of a common
set of verbs, f.e GET, HEAD, POST, PUT. If a desired HTTP Verb is not provided then
it can be simply used by specifying the correct string for the HTTP Verb when
registering the end-point specifications:

.. code-block:: python

    class MoreHttpVerbSupport(StackInABoxService):

        RANDOM = 'RANDOM'

        def __init__(self, *args, **kwargs):
            super(self, MoreHttpVerbSupport).__init__(*args, **kwargs)
            self.register(self.RANDOM, '/random', MoreHttpVerbSupport.random)
            self.register('WHOLESOME', '/wholesome', MoreHttpVerbSupport.wholesome)

        def random(self, request, uri, headers):
            return (200, headers, str(random.randint()))

        def wholesome(self, request, uri, headers):
            return (200, headers, 'wholesome' * 5)

.. note:: There is no validation of the HTTP Methods in the registration functionality.
    Thus any string value can be used for an HTTP Verb; as long as it can be used as a
    valid `dict` key it can be used as an HTTP Verb.
