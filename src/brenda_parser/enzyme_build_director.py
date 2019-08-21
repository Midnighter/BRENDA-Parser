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


"""Provide the enzyme build director."""


from .abstract_enzyme_section_visitor import AbstractEnzymeSectionVisitor
from .parser import AbstractEnzymeParser
from .builder import AbstractEnzymeBuilder


class EnzymeSectionBuildDirector(AbstractEnzymeSectionVisitor):
    """
    Implement an enzyme section visitor that builds an enzyme object.

    An implementation of the visitor[1]_ and builder[2]_ design patterns[3]_.
    Each section of an enzyme text definition is visited and the
    corresponding content parsed by using the respective format. Parsing
    results are then passed to an enzyme builder implementation that
    constructs the desired instances.

    Attributes
    ----------
    parser : AbstractEnzymeParser
        The concrete parser implementation.
    builder : AbstractEnzymeBuilder
        The concrete builder implementation.

    See Also
    --------
    parser.PyParser : A parser implemented using the pyparsing package.
    builder.ORMEnzymeBuilder : A builder implementation constructing SQLAlchemy
    model instances.
    builder.DataModelEnzymeBuilder : A builder implementation constructing
        pydantic data model instances.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Visitor_pattern
    .. [2] https://en.wikipedia.org/wiki/Builder_pattern
    .. [3] https://en.wikipedia.org/wiki/Software_design_pattern

    """

    def __init__(
        self, parser: AbstractEnzymeParser, builder: AbstractEnzymeBuilder
    ):
        self.parser = parser
        self.builder = builder
        self._dispatch = {
            "KI_VALUE": self._visit_ki_value,
            "KM_VALUE": self._visit_km_value,
            "NATURAL_SUBSTRATE_PRODUCT": self._visit_natural_substrate_product,
            "SUBSTRATE_PRODUCT": self._visit_substrate_product,
            "TURNOVER_NUMBER": self._visit_turnover_number,
            "PROTEIN": self._visit_protein,
            "REFERENCE": self._visit_reference,
        }

    def visit_id(self, text: str):
        self.builder.build_enzyme(self.parser.parse_id(text))

    def visit(self, heading: str, section: str):
        self._dispatch.get(heading, self._visit_field_entry)(section)

    def _visit_field_entry(self, text: str):
        self.builder.build_field_entry(self.parser.parse_field_entry(text))

    def _visit_ki_value(self, text: str):
        self.builder.build_ki_value(self.parser.parse_ki_value(text))

    def _visit_km_value(self, text: str):
        self.builder.build_km_value(self.parser.parse_km_value(text))

    def _visit_natural_substrate_product(self, text: str):
        self.builder.build_natural_substrate_product(
            self.parser.parse_natural_substrate_product(text))

    def _visit_substrate_product(self, text: str):
        self.builder.build_substrate_product(
            self.parser.parse_substrate_product(text))

    def _visit_turnover_number(self, text: str):
        self.builder.build_turnover_number(self.parser.parse_turnover_number(text))

    def _visit_protein(self, text: str):
        self.builder.build_protein(self.parser.parse_protein(text))

    def _visit_reference(self, text: str):
        self.builder.build_reference(self.parser.parse_reference(text))
