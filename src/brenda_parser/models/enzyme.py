# Copyright (c) 2018 Moritz E. Beber
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


"""Provide a data model for an information field entry."""


import logging

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from brenda_parser.models import Base


__all__ = ("Enzyme",)

LOGGER = logging.getLogger(__name__)


enzyme_entry_association = Table(
    "enzyme_entry_association",
    Base.metadata,
    Column("enzyme_id", Integer, ForeignKey("enzyme.id")),
    Column("fieldentry_id", Integer, ForeignKey("fieldentry.id")),
)


enzyme_comment_association = Table(
    "enzyme_comment_association",
    Base.metadata,
    Column("enzyme_id", Integer, ForeignKey("enzyme.id")),
    Column("comment_id", Integer, ForeignKey("comment.id")),
)


class Enzyme(Base):
    """Represent a complete enzyme classification (EC) number section."""

    __tablename__ = "enzyme"

    id = Column(Integer, primary_key=True)
    ec_number = Column(String(19), nullable=False)
    entries = relationship("FieldEntry", secondary=enzyme_entry_association)
    comments = relationship("Comment", secondary=enzyme_comment_association)
    # proteins = relationship("PR")
    # # TODO: The following relationships should be established by joins on
    # # 'field' selecting specific acronyms.
    # recommended_names = relationship(
    #     "FieldEntry",
    #     secondary=enzyme_entry_association,
    #     secondaryjoin="FieldEntry.field.acronym == 'RN'"
    # )
    # systematic_names = relationship("SN")
    # synonyms = relationship("SY")
    # reactions = relationship("RE")
    # reaction_types = relationship("RT")
    # source_tissues = relationship("ST")
    # localization = relationship("LO")
    # natural_substrates_products = relationship("NSP")
    # substrates_products = relationship("SP")
    # turnover_numbers = relationship("TN")
    # km_values = relationship("KM")
    # ph_optima = relationship("PHO")
    # ph_ranges = relationship("PHR")
    # specific_activities = relationship("SA")
    # temperature_optima = relationship("TO")
    # temperature_ranges = relationship("TR")
    # cofactors = relationship("CF")
    # activating_compounds = relationship("AC")
    # inhibitors = relationship("IN")
    # ki_values = relationship("KI")
    # metals_ions = relationship("ME")
    # molecular_weights = relationship("MW")
    # posttranslational_modifications = relationship("PM")
    # subunits = relationship("SU")
    # pi_values = relationship("PI")
    # applications = relationship("AP")
    # engineering = relationship("EN")
    # clones = relationship("CL")
    # crystallizations = relationship("CR")
    # purifications = relationship("PU")
    # renatured = relationship("REN")
    # general_stabilities = relationship("GS")
    # organic_solvent_stabilities = relationship("OSS")
    # oxidation_stabilities = relationship("OS")
    # ph_stabilities = relationship("PHS")
    # storage_stabilities = relationship("SS")
    # temperature_stabilities = relationship("TS")
    # references = relationship("RF")
    # ic50_values = relationship("IC50")

    def __init__(self, **kwargs):
        super(Enzyme, self).__init__(**kwargs)
        self.protein_references = list()
        self.citation_references = list()
