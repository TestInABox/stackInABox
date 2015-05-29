import sys
from setuptools import setup, find_packages

REQUIRES = ['six']

setup(
    name='stackinabox',
    version='0.10',
    description='RESTful API Testing Suite',
    license='Apache License 2.0',
    url='https://github.com/BenjamenMeyer/stackInABox',
    author='Benjamen R. Meyer',
    author_email='ben.meyer@rackspace.com',
    install_requires=REQUIRES,
    test_suite='stackinabox',
    packages=find_packages(exclude=['tests*', 'stackinabox/tests']),
    zip_safe=True,
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Topic :: Software Development :: Testing"],
)
