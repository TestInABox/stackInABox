import os
import os.path
import subprocess
import sys

import stackinabox
from tests import base


class TestVersionMatch(base.TestCase):

    def setUp(self):
        super(TestVersionMatch, self).setUp()
        self.local_directory = os.path.dirname(__file__)
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

        # read the data from `pip show <package>` to get the version
        # as seen by the installer
        version_setup = None
        cmd = ["pip", "show", "stackinabox"]
        pip_freeze = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, error = pip_freeze.communicate()
        if error is None:
            output_lines = output.decode('utf-8').split("\n")
            print(f"Read pip freeze data:\n{output_lines}\n")
            for line in output_lines:
                line_data = line.split(':')
                key = line_data[0]
                value = ':'.join(line_data[1:]).strip()
                print(f"\tLine Key: {key} - Value: {value}")
                if key.lower() == "version":
                    version_setup = value
                    break
        else:
            self.fail(f"Unable to retrieve version data - error: {error}")

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
