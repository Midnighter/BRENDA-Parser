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


"""Provide a data model for a protein database cross reference."""


import logging
import re

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, validates

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import Base


__all__ = ("Accession",)

LOGGER = logging.getLogger(__name__)


class Accession(Base):

    __tablename__ = "accession"

    # http://identifiers.org/uniprot/
    UNIPROT_PATTERN = re.compile(
        r"([A-NR-Z][0-9]([A-Z][A-Z0-9][A-Z0-9][0-9]){1,2})|"
        r"([OPQ][0-9][A-Z0-9][A-Z0-9][A-Z0-9][0-9])(\.\d+)?"
    )

    id = Column(Integer, primary_key=True)
    accession = Column(String(255), nullable=False, unique=True, index=True)
    database = Column(String(255), nullable=True)
    proteins = relationship("Protein")

    @validates("accession")
    def validate_accession(self, key, value):
        if value is None:
            return value
        if self.UNIPROT_PATTERN.match(value) is None:
            raise ValidationError(
                "'{}' does not match the required pattern '{}'."
                "".format(value, self.UNIPROT_PATTERN)
            )
        return value
