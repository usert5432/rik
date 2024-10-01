#!/usr/bin/env python

from setuptools import setup, find_packages

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
)

