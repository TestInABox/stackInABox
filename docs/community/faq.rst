.. _faq:

Frequently Asked Questions
==========================

Why not use framework X?
------------------------

Stack-In-A-Box is designed to enable building full REST API service mocks that
are fully integrated into unit tests. This enables reliable tests with minimal
to no changes of the actual code, and without deep knowledge of the code
itself; further the unit tests can essentially be integration tests as a
result. Stack-In-A-Box utilizes existing testing frameworks such as
```httpretty```, ```responses```, and ```requests-mock``` to be able to
perform its function; it's focus is on enabling the use of the frameworks to
do the testing.

What Frameworks are supported?
------------------------------

Stack-In-A-Box provides built-in support for the following frameworks:

* `HTTPretty <http://httpretty.readthedocs.io/>`_
* `Responses <https://github.com/getsentry/responses>`_
* `Requests-Mock <https://requests-mock.readthedocs.io/>`_

Support for any framework that can provide the requisite functionality will be
accepted.

Why not just `mock.patch` all things?
-------------------------------------

`mock.patch` is good for some things where it's clear where to use it.
However, once you start integrating other libraries then the line of where
to use it can easily become muddy and may even change as those tools get updated
and new releases come out.

The advantage of using StackInABox is that you can update your code so it
continues to work, but you don't have to update all the tests because the
underlying network wire contract is the same even though the third party tool
changed.

I'd rather use something I can Google or look up StackOverflow; why should I use Stack-In-A-Box?
------------------------------------------------------------------------------------------------

First, you're free to use whatever tool fits the task at hand. Stack-In-A-Box is
just one tool in many. Don't feel like you should use it for all things b/c that
is not it's intent or purpose.

Second, Stack-In-A-Box is a tool to help with testing, and utilizes other tools
that are standard tools in the Python world (e.g HTTPretty, Requests-Mock) which
are searchable via Google and StackOverflow, as is the code you're writing or
third party libraries you are using to write your project.

Stack-In-A-Box just makes some of the test framework highly re-usable. As adoption
increases it's ability to be found via Google and StackOverflow will also increase.

As always - use the best tool for the job. Stack-In-A-Box may or may not be that
tool. So use your best judgement; try it out and see what you think.

Why not use Mimic_?
-------------------

Mimic is a great tool for what it does. However, it still introduces external
dependencies and potential errors that have nothing to do with your testing as
it is a server that runs outside your testing framework over the network - locally
or otherwise.

Local, unit testing should use a tool like StackInABox; while more formal integration
testing where multiple systems may be interacting together and all need to have
a common mocked backend fit better with Mimic_; though work is underway to
create a means of using existing Stack-In-A-Box services to provide a similar
role as Mimic_ via StackInAWSGI_.

References
----------

.. _Mimic: https://pypi.python.org/pypi/mimic/
.. _StackInAWSGI: https://github.com/TestInABox/stackInAWSGI
