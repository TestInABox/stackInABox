.. _faq:

Frequently Asked Questions
==========================

Why not use framework X?
------------------------

Stack-In-A-Box is designed to enable building full REST API service mocks that are fully integrated into unit tests.
This enables reliable tests with minimal to no changes of the actual code, and without deep knowledge of the code itself;
further the unit tests can essentially be integration tests as a result. Stack-In-A-Box utilizes existing testing frameworks
such as ```httpretty```, ```responses```, and ```requests-mock``` to be able to perform its function; it's focus is on enabling
the use of the frameworks to do the testing.

What Frameworks are supported?
------------------------------

Stack-In-A-Box provides built-in support for the following frameworks:

* `HTTPretty <https://github.com/gabrielfalcao/HTTPretty>`_
* `Responses <https://github.com/dropbox/responses>`_
* `Requests-Mock <https://git.openstack.org/cgit/stackforge/requests-mock>`_

Support for any framework that can provide the requisite functionality will be accepted.
