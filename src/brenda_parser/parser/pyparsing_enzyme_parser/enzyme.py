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


"""Define the parsing expression grammar (PEG) for a BRENDA parser."""


import pyparsing as pp

from .common import comment
from .recommended_name import section as recommended_name_section
from .systematic_name import section as systematic_name_section


ec_number = pp.Combine(
    pp.Word(pp.nums)
    + ("." + pp.Word(pp.nums))[0, 2]
    + pp.Optional("." + pp.Word("n" + pp.nums, pp.nums))
)
ec_number.__doc__ = """
Parse a full or partial EC number.

An EC number is a hierarchical number format that consists of up to four
parts. Any of the parts following the first may be omitted to mean broader
categories. Preliminary EC numbers prefix the last number with an ``n``. Read
more at https://en.wikipedia.org/wiki/Enzyme_Commission_number.

"""

enzyme_begin = (
    pp.LineStart()
    + pp.Keyword("ID")("key")
    + ec_number("ec_number")
    + pp.Optional(comment)("comment")
)
enzyme_begin.setName("enzyme_begin")
enzyme_begin.__doc__ = """
Parse the beginning of an enzyme defining section.
"""

enzyme_end = pp.LineStart() + pp.Keyword("///")
enzyme_end.__doc__ = """
Parse the symbol defining the end of an enzyme section.
"""

enzyme = pp.Group(
    enzyme_begin
    + pp.Optional(recommended_name_section)
    + pp.Optional(systematic_name_section)
    + enzyme_end
)
banner_comment = pp.LineStart() + "*" + pp.restOfLine
enzyme.ignore(banner_comment)
