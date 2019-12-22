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


"""Provide a data model for an information field entry."""


from brenda_parser.models import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship


__all__ = ("FieldEntry",)


fieldentry_protein_association = Table(
    "fieldentry_protein_association",
    Base.metadata,
    Column("fieldentry_id", Integer, ForeignKey("fieldentry.id")),
    Column("protein_id", Integer, ForeignKey("protein.id")),
)


fieldentry_citation_association = Table(
    "fieldentry_citation_association",
    Base.metadata,
    Column("fieldentry_id", Integer, ForeignKey("fieldentry.id")),
    Column("reference_id", Integer, ForeignKey("reference.id")),
)


fieldentry_comment_association = Table(
    "fieldentry_comment_association",
    Base.metadata,
    Column("fieldentry_id", Integer, ForeignKey("fieldentry.id")),
    Column("comment_id", Integer, ForeignKey("comment.id")),
)


class FieldEntry(Base):

    __tablename__ = "fieldentry"

    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey("informationfield.id"))
    field = relationship("InformationField")
    # The `body` might have to be Text.
    body = Column(String(255), nullable=False)
    special = Column(String(255), nullable=True)
    enzyme_id = Column(Integer, ForeignKey("enzyme.id"))
    enzyme = relationship("Enzyme")
    proteins = relationship("Protein", secondary=fieldentry_protein_association)
    citations = relationship("Reference", secondary=fieldentry_citation_association)
    comments = relationship("Comment", secondary=fieldentry_comment_association)

    def __init__(self, **kwargs):
        """
        Instantiate an entry with extra attributes.

        The attributes are used to hold the integer references to proteins
        and citations. These are later replaced with actual relationships.

        """
        super(FieldEntry, self).__init__(**kwargs)
        self.protein_references = list()
        self.citation_references = list()
