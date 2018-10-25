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


"""Provide a data model for a reference."""

from __future__ import absolute_import

import logging
import re

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, validates

from brenda_parser.exceptions import ValidationError
from brenda_parser.models import Base


__all__ = ("Reference",)

LOGGER = logging.getLogger(__name__)


class Reference(Base):

    __tablename__ = "reference"

    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey("informationfield.id"))
    field = relationship("InformationField")
    pubmed = Column(String(14), nullable=True, unique=True, index=True)
    # The `body` might have to be Text.
    body = Column(String(255), nullable=False)

    PUBMED_PATTERN = re.compile(r"^Pubmed:\d{7}$")

    @validates("pubmed")
    def validate_pubmed(self, key, value):
        if value is None:
            return value
        if self.PUBMED_PATTERN.match(value) is None:
            raise ValidationError(
                "'{}' does not match the required pattern '{}'."
                "".format(value, self.PUBMED_PATTERN))
        return value
