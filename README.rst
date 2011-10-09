This Python module provides classes that encapsulate information provided by the
BRENDA database (http://www.brenda-enzymes.org/) and a parser that generates
relevant content from the text file that can be downloaded for free.

If you want to use this module you will have to add it to your PYTHONPATH
(unix).

Basic usage example::

    >>> import brenda_parser as bp
    >>> with bp.BRENDAParser("brenda_dl_2011.txt") as p:
    ...     content = p.parse()

The method parse returns a dictionary with all enzymes that were parsed. Every
key in the dictionary is a string representing an EC number starting form the 6
general classes down to the individual enzymes. The values in the dictionary are
always lists, as an example:

    >>> len(content["1"])
    1348
    >>> len(content["1.1.1.1"])
    1

There is one additional key "file_encoding" which contains the argument used
for the parser when reading the file.

