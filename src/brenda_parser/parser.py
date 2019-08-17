# Copyright 2011-2019 Moritz Emanuel Beber
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""Define the parsing expression grammar (PEG) for BRENDA."""


import pyparsing as pp


integer = pp.pyparsing_common.integer

protein_information = "#" + pp.Group(pp.delimitedList(integer))("proteins") + "#"
protein_information.__doc__ = """
Parse one or more comma-separated integers representing protein identifiers.

Parse a text representation of comma-separated integers enclosed by hashes 
``#`` to a list of integers.

"""

literature_citation = "<" + pp.Group(pp.delimitedList(integer))("citations") + ">"
literature_citation.__doc__ = """
Parse one or more comma-separated integers representing literature citations.

Parse a text representation of comma-separated integers enclosed by angled 
brackets ``<>`` to a list of integers.

"""

content = pp.Regex(r"[^#<>;(){}\s]+")
content.__doc__ = """
Parse any unicode string that is not whitespace or of special meaning to BRENDA.

This is meant to parse content of comments. Within the special context of 
comments in the BRENDA format the following special symbols do not occur:
``#<>;(){}``. Everything else that is not whitespace is considered valid 
content.

"""

comment = (
    pp.Optional(protein_information) +
    pp.Group(pp.ZeroOrMore(content))("content") +
    pp.Optional(literature_citation)
)
comment.__doc__ = """
Define the expected format of a single (sub-)comment entry.

"""

comments = (
    "(" +
    pp.Optional(pp.delimitedList(
        pp.Group(comment)("comments*"),
        delim=";"
    )) +
    ")"
)
comments.__doc__ = """
Parse zero or more comments.

Comments are enclosed by parentheses (``()``) and may contain none, or many 
semi-colon (``;``) separated sub-comments.

"""

ec_number = pp.Combine(
    pp.Word(pp.nums) +
    ("." + pp.Word(pp.nums)) * (0, 2) +
    pp.Optional("." + pp.Word("n" + pp.nums, pp.nums))
)
ec_number.__doc__ = """
Parse a full or partial EC number.

An EC number is a hierarchical number format that consists of up to four 
parts. Any of the parts following the first may be omitted to mean broader 
categories. Preliminary EC numbers prefix the last number with an ``n``. Read
more at https://en.wikipedia.org/wiki/Enzyme_Commission_number.

"""

enzyme_begin = pp.LineStart() + pp.Keyword("ID") + ec_number("ec_number") + \
               pp.Optional(comments)
enzyme_begin.__doc__ = """
Parse the beginning of an enzyme defining section.
"""

enzyme_end = pp.LineStart() + pp.Keyword("///")
enzyme_end.__doc__ = """
Parse the symbol defining the end of an enzyme section.
"""
