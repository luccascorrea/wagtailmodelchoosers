#!/usr/bin/env python

from __future__ import absolute_import, unicode_literals

from codecs import open

from wagtailmodelchoosers import __version__

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup


install_requires = [
    'wagtail>=2.0,<6.0',  # Depends on Wagtail's Django and Django RestFramework dependencies
    'django-filter>=1.1.0,<25.0',
]

# Testing dependencies
testing_extras = [
    # Required for running the tests
    'tox>=2.3.1',

    # For coverage and PEP8 linting
    'coverage>=4.1.0',
    'flake8>=3.2.0',
    'flake8-colors>=0.1.6',
    'isort>=4.2.5',
]


# Documentation dependencies
documentation_extras = [

]

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name='wagtailmodelchoosers',
    version=__version__,
    description='A Wagtail app to pick generic models (rather than snippets or pages)',
    author='Springload',
    author_email='hello@springload.co.nz',
    url='https://github.com/springload/wagtailmodelchoosers',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
        'Framework :: Wagtail :: 3',
        'Framework :: Wagtail :: 4',
        'Framework :: Wagtail :: 5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Editors :: Word Processors',
    ],
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        'docs': documentation_extras,
    },
    zip_safe=False,
)
