.. _errors:

StackInABoxService Errors
=========================

StackInABox has several specific HTTP Status Codes it returns to help in
diagnosing issues.

+---------+------------------------------------------------------------------+
| Status  | Reason                                                           |
+---------+------------------------------------------------------------------+
| 595     | The specified route is not handled. This typically means that a  |
|         | service route was specified for a service that was not           |
|         | registered, as opposed to a method on an end-point in a service  |
|         | not being supported.                                             |
+---------+------------------------------------------------------------------+
| 596     | An unhandled exception occurred in the StackInABoxService        |
|         | instance that supports the specified route. See logs for details.|
+---------+------------------------------------------------------------------+
| 597     | URI is for a service that is unknown.                            |
+---------+------------------------------------------------------------------+
