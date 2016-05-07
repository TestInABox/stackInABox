.. _quickstart:

Quick Start
===========

Install Stack-In-A-Box per :ref:`install` before continuing.

Building a Service
------------------

Here's a simple example from Stack-In-A-Box:

.. code:: python

	from stackinabox.services.service import StackInABoxService


	class HelloService(StackInABoxService):

		def __init__(self):
			super(HelloService, self).__init__('hello')
			self.register(StackInABoxService.GET, '/', HelloService.handler)

		def handler(self, request, uri, headers):
			return (200, headers, 'Hello')

Running a Test
--------------

We'll borrow the ```requests-mock``` example from the README.rst to show how to use the Stack-In-A-Box
in an actual test:

.. code-block:: python

	import unittest

	import requests

	import stackinabox.util.requests_mock
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
			stackinabox.util.requests_mock.requests_mock_session_registration(
				'localhost', self.session)

			res = self.session.get('http://localhost/hello/')
			self.assertEqual(res.status_code, 200)
			self.assertEqual(res.text, 'Hello')

		def test_context_requests_mock(self):
			with stackinabox.util.requests_mock.activate():
				# Register without the session object
				stackinabox.util.requests_mock.requests_mock_registration(
					'localhost')

				res = requests.get('http://localhost/hello/')
				self.assertEqual(res.status_code, 200)
				self.assertEqual(res.text, 'Hello')
