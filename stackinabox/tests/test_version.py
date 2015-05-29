import os
import unittest

import stackinabox


class TestVersionMatch(unittest.TestCase):

    def setUp(self):
        super(TestVersionMatch, self).setUp()

    def tearDown(self):
        super(TestVersionMatch, self).tearDown()

    def test_version_match(self):
        version_source = '{0}.{1}'.format(stackinabox.version[0],
                                          stackinabox.version[1])

        version_setup = None
        with open('../setup.py', 'rt') as input_data:
            for line in input_data:
                ln = line.strip()
                if ln.startswith('version='):
                    l = ln.replace("'", '', 2).replace(',', '')
                    version_setup = l.split('=')[1]
                    break

        self.assertEqual(version_source, version_setup)
