import sys
from setuptools import setup

REQUIRES = []

setup(
    name='stackinabox',
    version='0.1',
    description='OpenStack/Rackspace Service Testing Suite',
    license='Apache License 2.0',
    url='https://github.com/BenjamenMeyer/stackInABox',
    author='Benjamen R. Meyer',
    author_email='ben.meyer@rackspace.com',
    install_requires=REQUIRES,
    test_suite='stackinabox',
)
