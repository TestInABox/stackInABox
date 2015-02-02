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

Stack-In-A-Box is a RESTful API Testing Framework for unit testing applications against the other services with support for OpenStack/Rackspace APIs.

==========
Installing
==========

Installation is simple:


.. code-block:: bash 

   pip install stackinabox

=====
Goals
=====

- Enable Python modules to be unit tested against externals services and the OpenStack/Rackspace services (f.e Keystone) in particular in an environment entirely controlled by the unittest.
- The service should be started/stopped and configured from the setup/teardown methods of the unittest
- Support both Postive and Negative testing
- Testing should be easy to do:
  - you shouldn't need to know the ins and outs of each service
  - you should be able to register what you need (f.e keystone, swift) and have it just work
- should be useable on systems like Travis (https://travis-ci.org/)
- should be light on requirements
  - we don't want to bloat your testing to fit our needs
  - if we have many requirements they could interfere with your requirements:w
- The code being unit-tested should not be able to tell the difference of whether it is working with Stack-In-A-Box or the real thing
  - the should be nothing special about setting up the test
  - if you don't turn on Stack-In-A-Box then the code should be able to call the real thing

========================
Why not use framework X?
========================

I considered a couple frameworks and tools, but they didn't quite meet the goal.

For instance, mimic (https://github.com/rackerlabs/mimic) is a great tool for testing multiple things. However, you have to start/stop it separately from your tests.
On the other hand, pretenders (https://github.com/pretenders) has a nice framework too, but it doesn't actually use sockets.

================
What's Provided?
================

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
Out-of-the-box it supports two frameworks:

- HTTPretty (https://github.com/gabrielfalcao/HTTPretty)
- Responses (https://github.com/dropbox/responses)

You can use either one, and you must pull them in via your own test requirements.

Both of these are extremely easy to use as shown in the following examples:

---------
HTTPretty
---------

.. code-block:: python

    import unittest

    import httpretty
    import requests

    import stackinabox.httpretty
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
            stackinabox.httpretty.httpretty_registration('localhost')

            res = requests.get('http://localhost/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'Hello')
            assert False

---------
Responses
---------

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
        stackinabox.responses.responses_registration('localhost')

        res = requests.get('http://localhost/hello/')
        assert res.status_code == 200
        assert res.text == 'Hello'
