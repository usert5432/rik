#!/usr/bin/env python

from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name             = 'rik',
    version          = "0.0.1",
    author           = 'Dmitrii Torbunov',
    author_email     = 'torbu001@alumni.umn.edu',
    url              = 'https://github.com/usert5432/rik',
    packages         = find_packages(include = [ 'rik', 'rik.*' ]),
    scripts          = [ 'scripts/rik' ],
    description      = 'Recursive Integrity Keeper',
    license          = 'BSD-2',
    long_description              = readme(),
    long_description_content_type = 'text/markdown',
)

