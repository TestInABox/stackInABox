**************
Stack-In-A-Box
**************

Testing framework for RESTful APIs

.. image:: https://travis-ci.org/BenjamenMeyer/stackInABox.svg?branch=master
   :target: https://travis-ci.org/BenjamenMeyer/stackInABox
   :alt: Travis-CI Status

.. image:: https://coveralls.io/repos/BenjamenMeyer/stackInABox/badge.svg
   :target: https://coveralls.io/r/BenjamenMeyer/stackInABox
   :alt: Coverage Status

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

This project initially setup to provide mock-ups of the OpenStack Keystone and Swift APIs. In doing so other frameworks, such as ``mimic`` (https://github.com/rackerlabs/mimic) were considered.
However, they did not meet the goals set out above. This framework was then built and initially provided the Keystone module that is now part of ``OpenStack-In-A-Box`` (https://github.com/BenjamenMeyer/openstackinabox).
This framework now makes it easy to build services that can be integrated with one of many unit testing frameworks, f.e httpretty, to provide a consistent, reliable unit testing framework that essentially merges the API/Integration-level tests into
the more specific unit tests. It does not, however, replace a proper Integration Test as the responses (in terms of time and integration) will likely be different; but it does allow the unit tests to be sufficient to catch the coding errors early on
so that you can focus on the real integration problems with the Integration-level tests.

This framework is specifically targetted at running the unit tests, as part of the unit tests, and fully controlled by the unit tests. Projects such as ``mimic`` (https://github.com/rackerlabs/mimic) provide a good next-layer of testing if mocked integration level testing is desired; otherwise full integration tests could be utilized.

================
What's Provided?
================

Here's what is currently provided:

- An easy to build Service object and end-point registration that is plug-in-play with StackInABox
- A plug-in-play utility set for several testing frameworks so you the developer can choose which fits your needs best
- An example HelloWorld Service to show the basics

Note: The ``OpenStack-In-A-Box`` (https://github.com/BenjamenMeyer/openstackinabox) provides a more advanced example of building a Stack-In-A-Box Service.

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
