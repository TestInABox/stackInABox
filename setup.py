import sys
from setuptools import setup, find_packages

REQUIRES = ['six', 'sphinx']

setup(
    name='stackinabox',
    version='0.10',
    description='RESTful API Testing Suite',
    license='Apache License 2.0',
    url='https://github.com/TestInABox/stackInABox',
    author='Benjamen R. Meyer',
    author_email='bm_witness@yahoo.com',
    install_requires=REQUIRES,
    test_suite='stackinabox',
    packages=find_packages(exclude=['tests*', 'stackinabox/tests']),
    zip_safe=True,
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Topic :: Software Development :: Testing"],
)
