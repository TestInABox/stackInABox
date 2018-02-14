import sys
from setuptools import setup, find_packages

REQUIRES = ['six']
EXTRA_REQUIRES = {
    'httpretty': ['httpretty==0.8.6'],
    'requests-mock': ['requests-mock'],
    'responses': ['responses>=0.4.0']
}

setup(
    name='stackinabox',
    version='0.13',
    description='RESTful API Testing Suite',
    license='Apache License 2.0',
    url='https://github.com/TestInABox/stackInABox',
    author='Benjamen R. Meyer',
    author_email='bm_witness@yahoo.com',
    install_requires=REQUIRES,
    extras_require=EXTRA_REQUIRES,
    test_suite='stackinabox',
    packages=find_packages(exclude=['tests*', 'stackinabox/tests']),
    zip_safe=True,
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: MIT License",
                 "Topic :: Software Development :: Testing"],
)
