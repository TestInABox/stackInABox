.. _latest:

ChangeLog for Stack-In-A-Box (latest)
=====================================

New
---

Breaking Changes
----------------
- Refactored the Utility APIs to have a consistent interface so one can
  switch just by changing the imports. Previously the utility being supported
  had its name in the methods, thus requiring more significant code changes
  if one decided to change utilities.

Fixed
-----
- Fixed the project setup to detect when optional dependencies are installed
  and advertise itself appropriately.
