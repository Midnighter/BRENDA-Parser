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


"""Provide a data model for a protein."""


import logging

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship, validates

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import Base


__all__ = ("Protein",)

LOGGER = logging.getLogger(__name__)


protein_citation_association = Table(
    "protein_citation_association",
    Base.metadata,
    Column("protein_id", Integer, ForeignKey("protein.id")),
    Column("reference_id", Integer, ForeignKey("reference.id")),
)


protein_comment_association = Table(
    "protein_comment_association",
    Base.metadata,
    Column("protein_id", Integer, ForeignKey("protein.id")),
    Column("comment_id", Integer, ForeignKey("comment.id")),
)


class Protein(Base):

    __tablename__ = "protein"

    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey("informationfield.id"))
    field = relationship("InformationField")
    organism_id = Column(Integer, ForeignKey("organism.id"))
    organism = relationship("Organism")
    accession_id = Column(Integer, ForeignKey("accession.id"))
    accession = relationship("Accession")
    citations = relationship(
        "Reference", secondary=protein_citation_association
    )
    comments = relationship("Comment", secondary=protein_comment_association)

    def __init__(self, **kwargs):
        super(Protein, self).__init__(**kwargs)
        self.organism_name = ""
        self.citation_references = list()

    @validates("field")
    def validate_field(self, key, value):
        if value.acronym != "PR":
            raise ValidationError("Wrong field for a protein description!")
        return value
