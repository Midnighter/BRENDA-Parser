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

from __future__ import absolute_import

from builtins import open
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
def proteins_parser():
    return BRENDAParser(start="proteins")


@pytest.mark.parametrize("text, expected", [
    (" #, #", None),
    (" #13, 334,23 #", [13, 334, 23]),
])
def test_proteins(proteins_parser, text, expected):
    assert proteins_parser.parse(text, None) == expected


@pytest.fixture(scope="module")
def citations_parser():
    return BRENDAParser(start="citations")


@pytest.mark.parametrize("text, expected", [
    (" <, >", None),
    (" <13, 334,23 >", [13, 334, 23]),
])
def test_citations(citations_parser, text, expected):
    assert citations_parser.parse(text, None) == expected


@pytest.fixture(scope="module")
def special_parser():
    return BRENDAParser(start="special")


@pytest.mark.parametrize("text, expected", [
    (" { }", None),
    (" { I am important content. }", "I am important content.")
])
def test_special(special_parser, text, expected):
    assert special_parser.parse(text, None) == expected


@pytest.fixture(scope="module")
def comment_parser():
    return BRENDAParser(start="comment")


@pytest.mark.parametrize("text, expected", [
    pytest.param(" ( )", None,
                 marks=pytest.mark.raises(exception=AttributeError,
                                          message="NoneType")),
    (" ( I am important content. )", "I am important content.")
])
def test_comment(comment_parser, text, expected):
    assert comment_parser.parse(text, None).body == expected


@pytest.fixture(scope="module")
def protein_entry_parser():
    return BRENDAParser(start="protein_entry")


@pytest.mark.parametrize("text, expected", [
    ("PR\t#2#", "PR"),
    ("PR\t#2# alpha omega", "PR"),
    ("PR\t#2# <12, 14>", "PR"),
    ("PR\t#2# Q4AE87 SwissProt", "PR"),
])
def test_protein_entry(session, protein_entry_parser, text, expected):
    protein = protein_entry_parser.parse(text, session)
    assert protein.field.acronym == expected
    assert protein_entry_parser.proteins[2] is protein


@pytest.fixture(scope="module")
def reference_entry_parser():
    return BRENDAParser(start="reference_entry")


@pytest.mark.parametrize("text, expected", [
    ("RF\t<2>", "RF"),
    ("RF\t<2> Dogbert & Co", "RF"),
    ("RF\t<2> Dogbert & Co (1748) Cool", "RF"),
    ("RF\t<2> Dogbert & Co {Pubmed:1234567}", "RF"),
])
def test_reference_entry(session, reference_entry_parser, text, expected):
    reference = reference_entry_parser.parse(text, session)
    assert reference.field.acronym == expected
    assert reference_entry_parser.citations[2] is reference


@pytest.fixture(scope="module")
def entry_parser():
    return BRENDAParser(start="entry")


@pytest.mark.parametrize("text, expected", [
    ("PI\thigh point", "PI"),
    ("KI\t(high point)", "KI"),
    ("KM\thigh point (this is a comment)", "KM"),
])
def test_entry(session, entry_parser, text, expected):
    entry = entry_parser.parse(text, session)
    assert entry.field.acronym == expected


@pytest.fixture(scope="module")
def enzyme_parser():
    return BRENDAParser(start="enzyme")


@pytest.mark.parametrize("text, expected", [
    ("ID\t1.1.1.1", "1.1.1.1"),
    ("ID\t1.1.2.1\n///\n", "1.1.2.1"),
    ("ID\t1.1.2.3 (mighty comment)\n///\n", "1.1.2.3"),
])
def test_enzyme(session, enzyme_parser, text, expected):
    enzyme = enzyme_parser.parse(text, session)
    assert enzyme.ec_number == expected


def test_section(session):
    parser = BRENDAParser()
    with open(join(
            dirname(__file__), "data", "small_section.txt")) as file_handle:
        enzyme = parser.parse(file_handle.read(), session)
    print(enzyme.__dict__)
