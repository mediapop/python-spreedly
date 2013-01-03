#!/usr/bin/env python
"""
=============================================================================
pyspreedly
=============================================================================

pyspreedly is an python api wrapper to the spreedly web api.
"""

from setuptools import setup, find_packages

setup(
    name='pyspreedly',
    version='2.0.1',
    author='MediaPop',
    author_email='dev@mediapop.co',
    url='http://github.org/mediapop/python-spreedly',
    description='API for spreedly',
    long_description=__doc__,
    packages=find_packages(exclude=("tests",)),
    zip_safe=False,
    install_requires=[
        'requests>=0.14.0',
        'pytz>=2012f',
    ],
    test_requires=[
        'nose>=1.2.1',
        ],
    #test_suite='python_spreedly.test.runtests.get_tests',
    include_package_data=True,
    entry_points={},
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
