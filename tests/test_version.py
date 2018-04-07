import os
import os.path
import sys
import unittest

import stackinabox


class TestVersionMatch(unittest.TestCase):

    def setUp(self):
        super(TestVersionMatch, self).setUp()

    def tearDown(self):
        super(TestVersionMatch, self).tearDown()

    @staticmethod
    def make_version_source():
        return '{0}.{1}'.format(
            stackinabox.version[0],
            stackinabox.version[1]
        )

    def test_version_match(self):
        version_source = self.make_version_source()

        version_setup = None
        with open('../setup.py', 'rt') as input_data:
            for line in input_data:
                ln = line.strip()
                if ln.startswith('version='):
                    ln_parts = ln.replace("'", '', 2).replace(',', '')
                    version_setup = ln_parts.split('=')[1]
                    break

        self.assertEqual(version_source, version_setup)

    def test_sphinx_version_match(self):
        sphinx_conf_path = os.path.abspath(
            os.getcwd() + '../../docs/conf.py'
        )

        sys.path.insert(0, sphinx_conf_path)
        import docs.conf

        version_source = self.make_version_source()
        self.assertEqual(
            docs.conf.version,
            version_source
        )
        self.assertEqual(
            docs.conf.release,
            version_source
        )
