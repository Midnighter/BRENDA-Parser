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


"""Define a pattern for parsing substrate/product entries."""


import pyparsing as pp

from .common import literature_citation, protein_information, reversibility


metabolite = pp.Word(
    initChars=pp.alphanums + "?()[]->'ß/",
    bodyChars=pp.printables + "ß",
    excludeChars="=#",
)
operator = pp.Literal("+") | pp.Literal("*")
side = (
    pp.Optional("+")
    + pp.OneOrMore(metabolite, stopOn="(#")
    + (operator + pp.Optional("+") + pp.OneOrMore(metabolite, stopOn="(#"))[...]
)
equation = (side + pp.Optional("+") + "=" + pp.Optional(side)).setParseAction(" ".join)

entry = pp.Group(
    pp.LineStart()
    + pp.Keyword("SP")("key")
    + protein_information
    + equation("equation")
    + ...
    + (reversibility + literature_citation + pp.LineEnd())
)
entry.setName("substrate_product_entry")

protein_section = pp.Optional(
    "SUBSTRATE_PRODUCT" + pp.Group(entry[1, ...])("substrates_products")
)
