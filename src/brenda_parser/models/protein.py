# -*- coding: utf-8 -*-

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

from __future__ import absolute_import

import logging
import re

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import validates, relationship

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import Base

__all__ = ("Protein",)

LOGGER = logging.getLogger(__name__)


class Protein(Base):

    __tablename__ = "protein"

    # Taken from identifiers.org
    UNIPROT_PATTERN = re.compile(
        r"([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9]"
        r"[A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?")

    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey("informationfield.id"))
    field = relationship("InformationField")
    organism_id = Column(Integer, ForeignKey("organism.id"))
    organism = relationship("Organism")
    accession = Column(String(255), nullable=True, unique=True)
    database = Column(String(255), nullable=True)
    # citations = relationship("Reference")

    def __init__(self, **kwargs):
        super(Protein, self).__init__(**kwargs)
        self.organism_name = ""
        self.citation_references = list()

    @validates("accession")
    def validate_accession(self, key, value):
        if value is None:
            return value
        if self.UNIPROT_PATTERN.match(value) is None:
            raise ValidationError(
                "'{}' does not match the required pattern '{}'."
                "".format(value, self.UNIPROT_PATTERN))
        return value

    @validates("field")
    def validate_field(self, key, value):
        if value.acronym != "PR":
            raise ValidationError("Wrong field for a protein description!")
        return value
