#!/usr/bin/env python


import versioneer
from setuptools import setup


# All other arguments are defined in `setup.cfg`.
setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
