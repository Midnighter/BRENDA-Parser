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


"""Define a pattern for parsing protein entries."""


import pyparsing as pp

from .common import comment, integer, literature_citation


protein_id = "#" + integer("id") + "#"
protein_id.setName("id")

organism = pp.Regex(r"[^<>{}()\s]+")

# Accession pattern was taken from:
# https://registry.identifiers.org/registry/uniprot
accession = pp.Regex(
    r"([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2}\b)|"
    r"(([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?\b)|"
    r"(A0A0139XBW5\b)|"
    r"(A0A0D6KU47\b)"
)
accession.setName("accession")
# and extended as required.
extended_accession = pp.Regex(
    r"([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2}\b)|"
    r"(([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?\b)|"
    r"(\d{5})"
)

registry = (
    pp.CaselessKeyword("SwissProt")
    | pp.CaselessKeyword("UniProt")
    | pp.CaselessKeyword("GenBank")
    | pp.CaselessKeyword("TREMBL")
    | pp.CaselessKeyword("EMBL")
    | pp.CaselessKeyword("UniPro")  # This typo exists in the data.
    | pp.CaselessKeyword("?")
)
registry.setName("registry")

protein_identifier = pp.Group(
    pp.Group(
        accession
        + pp.ZeroOrMore(pp.Suppress(pp.CaselessKeyword("and")) + extended_accession)
    )("accessions")
    + pp.Optional(registry("registry"))
)
protein_identifier.setName("identifier")

protein_entry = pp.Group(
    pp.LineStart()
    + pp.Keyword("PR")("key")
    + protein_id
    + pp.Group(pp.ZeroOrMore(organism, stopOn=accession))("organism")
    + pp.Optional(
        protein_identifier("identifier")
        | pp.Literal("(nomen rejiciendum)")("postfix")
        | pp.Literal("(Schum ex Fr) Karsten")("postfix")
        | (
            pp.originalTextFor("(in:" + organism + ")")("postfix")
            + pp.Optional(protein_identifier("identifier"))
        )
    )
    + pp.Optional(comment("comment"))
    + pp.Optional(protein_identifier("identifier"))
    + literature_citation
)
protein_entry.setName("protein_entry")

protein_section = pp.Optional("PROTEIN" + pp.Group(protein_entry[1, ...])("proteins"))
