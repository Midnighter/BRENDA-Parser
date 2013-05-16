=============
BRENDA Parser
=============

This Python module provides classes that encapsulate information provided by the
`BRENDA database`__ and a parser that generates relevant content from the text
file that can be downloaded for free.

.. __: http://www.brenda-enzymes.org/

Copyright
---------

:Author:
    Moritz Emanuel Beber
:License:
    Please see the LICENSE.rst file distributed with this module.

Recent Changes
--------------

* Parser no longer hick-ups on empty lines, continued lines not starting with a
  tab, and other format breaking content.
* Parser now prints progress to stdout.
* Soon, support for the SOAP interface will be added.
* If desired, a setup script could be added.

Usage
-----

If you want to use this module outside its directory, you will have to add it to your
PYTHONPATH environment variable (unix).

.. code:: python

    >>> from brenda import BRENDAParser
    >>> with BRENDAParser("brenda_download.txt") as bp:
    ...     content = bp.parse()

The method parse returns a dictionary with all enzymes that were parsed. Every
key in the dictionary is a string representing an EC number starting form the 6
general classes down to the individual enzymes. The values in the dictionary are
always lists, as an example:

.. code:: python

    >>> len(content["1"])
    1348
    >>> len(content["1.1.1.1"])
    1

Warning
-------

The API changed slightly.

Notes
-----

There is one additional key "file_encoding" which contains the argument used
for the parser when reading the file.

