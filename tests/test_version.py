import os
import os.path
import sys

import stackinabox
from tests import base


class TestVersionMatch(base.TestCase):

    def setUp(self):
        super(TestVersionMatch, self).setUp()
        self.local_directory = os.path.dirname(__file__)
        self.setup_py = '{0}/../setup.py'.format(self.local_directory)
        self.doc_conf = '{0}/../../docs/conf.py'.format(self.local_directory)

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
        with open(self.setup_py, 'rt') as input_data:
            for line in input_data:
                ln = line.strip()
                if ln.startswith('version='):
                    ln_parts = ln.replace("'", '', 2).replace(',', '')
                    version_setup = ln_parts.split('=')[1]
                    break

        self.assertEqual(version_source, version_setup)

    def test_sphinx_version_match(self):
        sphinx_conf_path = self.doc_conf

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
