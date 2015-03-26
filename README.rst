**************
Stack-In-A-Box
**************

Testing framework for RESTful APIs such as the OpenStack/Rackspace APIs

.. image:: https://travis-ci.org/BenjamenMeyer/stackInABox.svg?branch=master
   :target: https://travis-ci.org/BenjamenMeyer/stackInABox
   :alt: Travis-CI Status

========
Overview
========

Stack-In-A-Box is a RESTful API Testing Framework for unit testing applications against the other services

==========
Installing
==========

Installation is simple:

.. code-block:: bash 

   pip install stackinabox

=====
Goals
=====

- Enable Python modules to be unit tested against externals services in particular in an environment entirely controlled by the unittest.
- The service should be started/stopped and configured from the setup/teardown methods of the unittest
- Support both Postive and Negative testing
- Testing should be easy to do:

  - you should not necessarily need to know the ins and outs of each service
  - you should be able to register what you need (f.e authentication, storage) and have it just work
  
- should be useable on systems like Travis (https://travis-ci.org/)
- should be light on requirements

  - we do not want to bloat your testing to fit our needs
  - if we have many requirements they could interfere with your requirements
  
- The code being unit-tested should not be able to tell the difference of whether it is working with Stack-In-A-Box or the real thing

  - there should be nothing special about setting up the test
  - if you don't turn on Stack-In-A-Box then the code should be able to call the real thing
  - caveat: the utility tools (f.e httpretty, requests-mock) will determine the URL for the Stack-In-A-Box Service which will start differently from the URL of the real thing. For example: if the Hello World service was normally run at 'www.helloworld.com/v1', it's Stack-In-A-Box version was registered with Stack-In-A-Box as 'hello/v1', and Stack-In-A-Box was registered using 'localhost', then it's Stack-In-A-Box URL would be 'http://localhost/hello/v1'. The remainder of the URL and any query-string parameters should be the same.

========================
Why not use framework X?
========================

A couple of frameworks and tools were considered, but they did not quite meet the goals above.

For instance, mimic (https://github.com/rackerlabs/mimic) is a great tool for testing multiple things. However, you have to start/stop it separately from your tests, and each test is configured through a series of HTTP calls to Mimic itself.

On the other hand, pretenders (https://github.com/pretenders) has a nice framework too, but it does not provide a way to emulate an integrated application that requires a series of dependent calls that modify each other.

================
What's Provided?
================

Here's what is currently provided:

- An easy to build Service object and end-point registration that is plug-in-play with StackInABox
- A plug-in-play utility set for several testing frameworks so you the developer can choose which fits your needs best
- An example HelloWorld Service to show the basics
- The start of support StackInABox services for testing against OpenStack/Rackspace APIs

It's a work in progress. Here's the list of current targets in-order:

- Keystone v2
- Keystone v3
- Swift

Thus far Keystone v2 provides end-points for:

- Listing tenants
- Listing users

It also has support in the backend for:

- tenant (add/remove/enable/disable)
- users (add/remove/enable/disable, apikey, password)
- tokens (add/remove, revoke, validate, admin tokens)
- roles (add, assign)

=======================
Working with Frameworks
=======================

Stack-In-A-Box does not itself provide a socket interception framework.
Out-of-the-box it supports the following frameworks:

- HTTPretty (https://github.com/gabrielfalcao/HTTPretty)
- Responses (https://github.com/dropbox/responses)
- Requests-Mock(https://git.openstack.org/cgit/stackforge/requests-mock)

You can use any of them, and you must pull them in via your own test requirements.

Both of these are extremely easy to use as shown in the following examples:

---------
HTTPretty
---------

``httypretty`` works well with class-based tests.

.. code-block:: python

    import unittest

    import httpretty
    import requests

    import stackinabox.util_httpretty
    from stackinabox.stack import StackInABox
    from stackinabox.services.hello import HelloService


    @httpretty.activate
    class TestHttpretty(unittest.TestCase):

        def setUp(self):
            super(TestHttpretty, self).setUp()
	    StackInABox.register_service(HelloService())

        def tearDown(self):
            super(TestHttpretty, self).tearDown()
	    StackInABox.reset_services()

        def test_basic(self):
            stackinabox.util_httpretty.httpretty_registration('localhost')

            res = requests.get('http://localhost/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')
            assert False

---------
Responses
---------

``responses`` works well with function-based tests; however, it does require you use the Python ``requests`` library.

.. code-block:: python

    import unittest

    import responses
    import requests

    import stackinabox.responses
    from stackinabox.stack import StackInABox
    from stackinabox.services.hello import HelloService


    @responses.activate
    def test_basic_responses():
	StackInABox.reset_services()
	StackInABox.register_service(HelloService())
        stackinabox.util_responses.responses_registration('localhost')

        res = requests.get('http://localhost/hello/')
        assert res.status_code == 200
        assert res.text == 'Hello'


-------------
Requests Mock
-------------

``requests-mock`` works well with class-based tests, however, it does require that you use the Python ``requests`` API. If you use ``requests-mock`` directly than you also have to configure ``requests.session.Session`` objects and setup your code to use them. However, Stack-In-A-Box makes that unnecessary by providing thread-based session objects that are automatically registered and patching ``requests`` to return them automatically. Thus you can either use a Session object directly or just use the nice calls that ``requests`` provides and your tests will still just work.

.. code-block:: python

	import unittest

	import requests

	import stackinabox.util_requests_mock
	from stackinabox.stack import StackInABox
	from stackinabox.services.hello import HelloService

	class TestRequestsMock(unittest.TestCase):

		def setUp(self):
			super(TestRequestsMock, self).setUp()
			StackInABox.register_service(HelloService())
			self.session = requests.Session()

		def tearDown(self):
			super(TestRequestsMock, self).tearDown()
			StackInABox.reset_services()
			self.session.close()

		def test_basic_requests_mock(self):
		    # Register with existing session object
			stackinabox.util_requests_mock.requests_mock_session_registration(
				'localhost', self.session)

			res = self.session.get('http://localhost/hello/')
			self.assertEqual(res.status_code, 200)
			self.assertEqual(res.text, 'Hello')

		def test_context_requests_mock(self):
			with stackinabox.util_requests_mock.activate():
                # Register without the session object
				stackinabox.util_requests_mock.requests_mock_registration(
					'localhost')

				res = requests.get('http://localhost/hello/')
				self.assertEqual(res.status_code, 200)
				self.assertEqual(res.text, 'Hello')
