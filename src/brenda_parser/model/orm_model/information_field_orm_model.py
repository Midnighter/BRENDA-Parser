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


"""Provide a data model for an information field."""


import csv
import logging
import re
from importlib.resources import open_text

from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import validates

from ... import data
from ..abstract_model import AbstractInformationFieldModel
from . import Base


__all__ = ("InformationFieldORMModel",)


logger = logging.getLogger(__name__)


class InformationFieldORMModel(Base):

    __tablename__ = "informationfield"

    id = Column(Integer, primary_key=True)
    acronym = Column(String(4), nullable=False, unique=True, index=True)
    description = Column(String(100), nullable=True)
    heading = Column(String(100), nullable=True)

    acronym_pattern = re.compile(r"^[A-Z50]{2,4}$")

    @validates("acronym")
    def validate_acronym(self, _, value):
        if self.acronym_pattern.match(value) is None:
            raise AssertionError(
                f"'{value}' does not match the required pattern "
                f"'{self.acronym_pattern}'."
            )
        return value

    @classmethod
    def preload(cls, session):
        """
        Pre-load information fields from the packaged table.

        Parameters
        ----------
        session : sqlalchemy.Session
            A valid SQLAlchemy database session.

        """
        with open_text(data, "information_fields.csv") as handle:
            rows = list(csv.DictReader(handle))
        table = cls.__table__
        try:
            session.execute(table.insert().values(rows))
            logger.debug("Successfully loaded information fields.")
        except IntegrityError:
            session.rollback()
            for row in rows:
                # This query will ignore or fail on non-existent
                # `row["acronym"]`.
                session.query(InformationFieldORMModel).filter_by(
                    acronym=row["acronym"]
                ).update(row)
                logger.debug("Updated field '%s'.", row["acronym"])
        session.commit()


AbstractInformationFieldModel.register(InformationFieldORMModel)
