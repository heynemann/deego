#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from deego.version import __version__

setup(
    name = 'deego',
    version = __version__,
    description = "deego is a vm manager that is dead simple",
    long_description = """
    deego is a vm manager for dummies (like me);
    deego is for those that feel threatened every time they need a VM;
    deego is for those that want virtualization to be easy (as it should);
    deego is all it can be and more (ok pushed a little here).

    For more info visit http://github.com/heynemann/deego.
""",
    keywords = 'virtualization vm lxc vmware virtualbox',
    author = 'Bernardo Heynemann',
    author_email = 'heynemann@gmail.com',
    url = 'http://heynemann.github.com/deego/',
    license = 'MIT',
    classifiers = ['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(),

    include_package_data = True,
    package_data = {
        '': ['*.xml'],
    },

    install_requires=[
        'colorama>=0.2.4',
        'sh>=1.0.5'
    ]
)

