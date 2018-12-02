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


from os.path import dirname, join

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from brenda_parser.models import Base, InformationField
from brenda_parser.parsing.parser import BRENDAParser


Session = sessionmaker()


@pytest.fixture(scope="module")
def connection():
    """
    Use a connection such transactions can be used.

    Notes
    -----
    Follows a transaction pattern described in the following:
    http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#session-begin-nested
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    InformationField.preload(session)
    session.close()
    del session
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope="function")
def session(connection):
    """
    Create a transaction and session per test unit.

    Rolling back a transaction removes even committed rows
    (``session.commit``) from the database.
    """
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()


@pytest.fixture(scope="module")
def parser():
    return BRENDAParser()


def test_long_comment(session, parser):
    with open(
        join(dirname(__file__), "data", "long_comments.txt")
    ) as file_handle:
        enzyme = parser.parse(file_handle.read(), session)
    assert len(enzyme.entries) == 1
    entry = enzyme.entries[0]
    assert entry.field.acronym == "IN"
    assert len(entry.protein_references) == 8
    assert len(entry.citation_references) == 40
    assert len(entry.comments) == 44
