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


"""Define the parsing expression grammar (PEG) for a BRENDA parser."""


import pyparsing as pp

from . import result
from .abstract_enzyme_parser import AbstractEnzymeParser


class PyParsingEnzymeParser(AbstractEnzymeParser):
    """
    Implement an enzyme parser using the pyparsing package.

    Notes
    -----
    We use ``setName`` on each pattern in order to enable more convenient
    pattern matching debugging.

    """

    integer = pp.pyparsing_common.integer

    identifier = pp.Regex(r"[A-Z50]{2,4}")
    identifier.setName("identifier")

    protein = "#" + pp.Group(integer)("protein") + "#"
    protein.setName("protein")

    protein_information = "#" + pp.Group(pp.delimitedList(integer))("proteins") + "#"
    protein_information.setName("protein_information")
    protein_information.__doc__ = """
    Parse one or more comma-separated integers representing protein identifiers.

    Parse a text representation of comma-separated integers enclosed by hashes
    ``#`` to a list of integers.

    """

    reference = "<" + pp.Group(integer)("reference") + ">"
    reference.setName("reference")

    literature_citation = "<" + pp.Group(pp.delimitedList(integer)[1, ...])("references") + ">"
    literature_citation.setName("literature_citation")
    literature_citation.__doc__ = """
    Parse one or more comma-separated integers representing literature citations.

    Parse a text representation of comma-separated integers enclosed by angled
    brackets ``<>`` to a list of integers.

    """

    content = pp.Regex(r"[^#<>;(){}\s]+")
    value = pp.Group(pp.OneOrMore("(" | content | ")"))("value")
    value.setName("value")
    content.__doc__ = """
    Parse any unicode string that is not whitespace or of special meaning to BRENDA.

    This is meant to parse content of comments. Within the special context of
    comments in the BRENDA format the following special symbols do not occur:
    ``#<>;(){}``. Everything else that is not whitespace is considered valid
    content.

    """

    comment = pp.Forward()
    comment.__doc__ = """
    Define the expected format of a single (sub-)comment entry.

    """

    inside = (
        pp.Optional(protein_information)
        + pp.Optional(value)
        + pp.Optional(literature_citation)
    )
    inside.setName("inside")

    comment.__doc__ = """
    Parse zero or more comments.

    Comments are enclosed by parentheses (``()``) and may contain none, or many
    semi-colon (``;``) separated sub-comments.

    """
    comment <<= pp.Group(
        pp.Suppress("(")
        + pp.Optional(pp.delimitedList(inside, delim=";"))
        + pp.Suppress(")")
    )
    comment.setName("comment")

    ec_number = pp.Combine(
        pp.Word(pp.nums)
        + ("." + pp.Word(pp.nums)) * (0, 2)
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
        + pp.Optional(comment)("comments")
    )
    enzyme_begin.setName("enzyme_begin")
    enzyme_begin.__doc__ = """
    Parse the beginning of an enzyme defining section.
    """

    field_entry = (
        pp.LineStart()
        + identifier("key")
        + pp.Optional(protein_information)
        + pp.Optional(value)
        + pp.Optional(comment)("comments")
        + pp.Optional(literature_citation)
    )
    field_entry.setName("field_entry")

    ki_value = (
        pp.LineStart()
        + pp.Keyword("KI")("key")
        + protein
        + pp.Optional(value)
        + "{"
        + pp.Group(pp.OneOrMore(content))("inhibitor")
        + "}"
        + pp.Optional(comment)("comments")
        + pp.Optional(literature_citation)
    )
    ki_value.setName("ki_value")

    km_value = (
        pp.LineStart()
        + pp.Keyword("KM")("key")
        + protein
        + pp.Optional(value)
        + "{"
        + pp.Group(pp.OneOrMore(content))("substrate")
        + "}"
        + pp.Optional(comment)("comments")
        + pp.Optional(literature_citation)
    )
    km_value.setName("km_value")

    natural_substrate_product = (
        pp.LineStart()
        + pp.Keyword("NSP")("key")
        + pp.Optional(protein_information)
        + pp.Optional(value)
        + pp.Optional(comment)("comments")
        + "{"
        + pp.Group(pp.OneOrMore(content))("reversibility")
        + "}"
        + pp.Optional(literature_citation)
    )
    natural_substrate_product.setName("natural_substrate_product")

    substrate_product = (
        pp.LineStart()
        + pp.Keyword("SP")("key")
        + pp.Optional(protein_information)
        + pp.Optional(value)
        + pp.Optional(comment)("comments")
        + "{"
        + pp.Group(pp.OneOrMore(content))("reversibility")
        + "}"
        + pp.Optional(literature_citation)
    )
    substrate_product.setName("substrate_product")

    turnover_number = (
        pp.LineStart()
        + pp.Keyword("TN")("key")
        + protein
        + pp.Optional(value)
        + "{"
        + pp.Group(pp.OneOrMore(content))("substrate")
        + "}"
        + pp.Optional(comment)("comments")
        + pp.Optional(literature_citation)
    )
    turnover_number.setName("turnover_number")

    # Accession pattern was taken from:
    # https://registry.identifiers.org/registry/uniprot
    accession = pp.Regex(
        r"^([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|"
        r"([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?$"
    )
    accession.setName("accession")

    registry = pp.CaselessKeyword("swissprot") | pp.CaselessKeyword("uniprot")
    registry.setName("registry")

    protein_entry = (
        pp.LineStart()
        + pp.Keyword("PR")("key")
        + protein
        + pp.Group(content[2, ...])("organism")
        + pp.Optional(accession)("accession")
        + pp.Optional(registry)("registry")
        + pp.Optional(comment)("comments")
        + pp.Optional(literature_citation)
    )
    protein_entry.setName("protein_entry")

    reference_entry = (
        pp.LineStart()
        + pp.Keyword("RF")("key")
        + reference
        + pp.Group(value)("entry")
        + pp.Optional("{" + pp.Group(pp.ZeroOrMore(content))("pubmed") + "}")
        + pp.Optional("(" + pp.Group(pp.ZeroOrMore(content))("type") + ")")
    )
    reference_entry.setName("reference_entry")

    enzyme_end = pp.LineStart() + pp.Keyword("///")
    enzyme_end.__doc__ = """
    Parse the symbol defining the end of an enzyme section.
    """

    def parse_id(self, text: str) -> result.AbstractIDParsingResult:
        return self.enzyme_begin.parseString(text, parseAll=True)

    def parse_field_entry(self, text: str) -> result.AbstractEntryParsingResult:
        return self.field_entry.parseString(text, parseAll=True)

    def parse_ki_value(self, text: str) -> result.AbstractKiValueParsingResult:
        pass

    def parse_km_value(self, text: str) -> result.AbstractKmValueParsingResult:
        pass

    def parse_natural_substrate_product(
        self, text: str
    ) -> result.AbstractNaturalSubstrateProductParsingResult:
        pass

    def parse_substrate_product(
        self, text: str
    ) -> result.AbstractSubstrateProductParsingResult:
        pass

    def parse_turnover_number(
        self, text: str
    ) -> result.AbstractTurnoverNumberParsingResult:
        pass

    def parse_protein(self, text: str) -> result.AbstractProteinParsingResult:
        return self.protein_entry.parseString(text, parseAll=True)

    def parse_reference(self, text: str) -> result.AbstractReferenceParsingResult:
        return self.reference_entry.parseString(text, parseAll=True)
