Second Step: Hooking up a test
------------------------------

Testing with StackInABox is actually really easy as you don't have to hook up
complicated mockings. For this example we'll use the ```requests-mock```; however,
```httpretty``` and ```responses``` are also natively supported.

To start, we need to setup the test structure as follows:

.. code:: python

	import unittest

	import requests

	import stackinabox.util.requests_mock
	from stackinabox.stack import StackInABox

	from tests.service.lookupService import LookupService


	class TestLookupService(unittest.TestCase):

		def setUp(self):
			super(TestLookupService, self).setUp()
			# Register LookupService for use in the test
			StackInABox.register_service(LookupService())
			# Access the requests session for use in the test
			self.session = requests.Session()

		def tearDown(self):
			super(TestLookupSerice, self).tearDown()
			# Reset StackInABox for the next test
			StackInABox.reset_services()
			# Reset Requests for the next request
			self.session.close()

The above setups each test and ensure each one is completely separate so
they don't interfere with each other. Now we'll add a simple test to it:

.. code:: python

	def test_basic(self):
		stackinabox.util.requests_mock.request_mock_session_registration(
			'localhost', self.session)
		res = self.session.head('http://localhost/lookup/')
		self.assertEqual(res.status_code, 204)
		self.assertIn(res.headers, 'X-Key-Value-Count')
		self.assertEqual(res.headers['X-Key-Value-Count'], '0')

StackInABox provides some utility functions to work with the support testing
frameworks. In this instance, we're going to use the one for ```requests-mock```
and it's registration for using the ```requests``` session object, though you
also do the registration without the session object and just use ```requests```
itself too.

The utility function performs the rest of the setup to use StackInABox,
which will be registered under the ```http://``` and ```https://`` protocols.
The first parameter to the utility function is the base of the URI name for any
StackInABox calls. Under this location will be each service based on the name
in it's initialization, f.e lookup. Thus several different services can all
be registered at the same time as long as their names do not collide. If a
StackInABoxService with the same name is already registered then the
registration will throw an exception.

The rest of the test runs just as it would in normal usage for an application;
the only difference is that you have to specify the URL for the StackInABox.
If you services rely on external systems like the OpenStack Keystone Service
that provides a catalog of related-services, then you may need to implement
the required services and related-service lookup functionality for all your
code to work properly.

