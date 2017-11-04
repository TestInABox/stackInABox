.. _about:

About Stack-In-A-Box
====================

StackInABox started out of trying to reduce code in tests. Initially Mock_
was used. That proved problematic as it was hard to get the the `mock.patch`
applied correctly for third-party tooling (e.g OpenStack Keystone Client) that
didn't break due to changes upstream or even in minor changes in the test. The
tests were then moved to use HTTPretty_ which brought a lot of stability and
all was good until one looked at how much code was being copy/pasted between
tests to use the tool. In centralizing the code and abstracting it in a way
that worked for all the tests Stack-In-A-Box was born. Since then additional
support tools ( RequestsMock_, Response_ ) have been added.


References
==========

.. _Mock: https://docs.python.org/3/library/unittest.mock.html
.. _HTTPretty: http://httpretty.readthedocs.io/en/latest/tutorial.html
.. _RequestsMock: https://requests-mock.readthedocs.io/en/latest/
.. _Response: https://github.com/getsentry/responses
