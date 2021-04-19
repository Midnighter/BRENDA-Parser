# Copyright 2011-2021 Moritz Emanuel Beber
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


"""Define common tokens and patterns shared between sub-parsers."""


import pyparsing as pp


integer = pp.pyparsing_common.integer

content = pp.Regex(r"[^#<>{}()\s]+")

protein_information = (
    "#" + pp.Group(pp.delimitedList(integer)[1, ...])("proteins") + "#"
)
protein_information.setName("protein_information")
protein_information.__doc__ = """
Parse one or more comma-separated integers representing protein identifiers.

Parse a text representation of comma-separated integers enclosed by hashes
``#`` to a list of integers.

"""

reference = "<" + pp.Group(integer)("reference") + ">"
reference.setName("reference")

literature_citation = (
    "<" + pp.Group(pp.delimitedList(integer)[1, ...])("references") + ">"
)
literature_citation.setName("literature_citation")
literature_citation.__doc__ = """
Parse one or more comma-separated integers representing literature citations.

Parse a text representation of comma-separated integers enclosed by angled
brackets ``<>`` to a list of integers.

"""

comment = pp.nestedExpr().setParseAction(
    lambda _, __, tokens: f"({' '.join(tokens[0])})" if len(tokens[0]) > 0 else "()"
)
comment.setName("comment")
comment.__doc__ = """
Parse zero or more comments.

Comments are enclosed by parentheses (``()``) and may contain none, or many
semi-colon (``;``) separated sub-comments.

"""
