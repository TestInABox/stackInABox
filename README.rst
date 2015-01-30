**************
Stack-In-A-Box
**************

Testing framework for OpenStack/Rackspace Service Suites

========
Overview
========

Stack-In-A-Box is an OpenStack/Rackspace Services Testing Framework for unit testing applications against the OpenStack/Rackspace services.

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
On the other hand, pretenders (https://github.com/pretenders) has a nice framework too, but it doesn't actually generate a socket usage.

================
What's Provided?
================

It's a work in progress. BuHTTPrettyt here's the list of current targets in-order:

- Keystone v2
- Keystone v3
- Swift

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


    @httpretty.activate
    class TestHttpretty(unittest.TestCase):

        def setUp(self):
            super(TestHttpretty, self).setUp()

        def tearDown(self):
            super(TestHttpretty, self).tearDown()

        def test_basic(self):
            stackinabox.httpretty.httpretty_registration('http://localhost:8000/hello')

            res = requests.get('http://localhost:8000/hello')
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


    @responses.activate
    def test_basic_responses():
        stackinabox.responses.responses_registration('http://localhost:8000/hello')

        res = requests.get('http://localhost:8000/hello')
        assert res.status_code == 200
        assert res.text == 'Hello'
