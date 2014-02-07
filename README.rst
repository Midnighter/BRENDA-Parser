========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/BRENDA-Parser/badge/?style=flat
    :target: https://readthedocs.org/projects/BRENDA-Parser
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/Midnighter/BRENDA-Parser.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Midnighter/BRENDA-Parser

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Midnighter/BRENDA-Parser?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/Midnighter/BRENDA-Parser

.. |codecov| image:: https://codecov.io/github/Midnighter/BRENDA-Parser/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Midnighter/BRENDA-Parser

.. |version| image:: https://img.shields.io/pypi/v/brenda-parser.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/brenda-parser

.. |commits-since| image:: https://img.shields.io/github/commits-since/Midnighter/BRENDA-Parser/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/Midnighter/BRENDA-Parser/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/brenda-parser.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/brenda-parser

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/brenda-parser.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/brenda-parser

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/brenda-parser.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/brenda-parser


.. end-badges

A parser for the BRENDA flat file distribution.

* Free software: Apache Software License 2.0

Installation
============

::

    pip install brenda-parser

Documentation
=============

https://BRENDA-Parser.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
