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


"""Provide an abstract data model for a protein database cross-reference."""


from itertools import zip_longest

import pytest
from pyparsing import ParseException

from brenda_parser import parser


@pytest.mark.parametrize("text, expected", [
    ("#1#", [1]),
    ("#1,2,3#", [1, 2, 3]),
    pytest.param("##", None, marks=pytest.mark.raises(exception=ParseException)),
])
def test_protein_information(text, expected):
    result = parser.protein_information.parseString(text, parseAll=True)
    assert list(result.proteins) == expected


@pytest.mark.parametrize("text, expected", [
    ("<1>", [1]),
    ("<1,2,3>", [1, 2, 3]),
    pytest.param("<>", None, marks=pytest.mark.raises(exception=ParseException)),
])
def test_literature_citation(text, expected):
    result = parser.literature_citation.parseString(text, parseAll=True)
    assert list(result.citations) == expected


@pytest.mark.parametrize("text, proteins, content, citations", [
    ("föö", [], ["föö"], []),
    ("föö bär", [], "föö bär".split(), []),
    ("föö 24 bär", [], "föö 24 bär".split(), []),
    ("#11# at pH 4.5, 30°C <100>", [11], "at pH 4.5, 30°C".split(), [100]),
])
def test_comment(text, proteins, content, citations):
    result = parser.comment.parseString(text, parseAll=True)
    assert list(result.proteins) == proteins
    assert list(result.content) == content
    assert list(result.citations) == citations


@pytest.mark.parametrize("text, expected", [
    ("()", [([], [], [])]),
    ("(at pH 4.5, 30°C)", [
        ([], "at pH 4.5, 30°C".split(), []),
    ]),
    ("(#11# at pH 4.5, 30°C <100>)", [
        ([11], "at pH 4.5, 30°C".split(), [100]),
    ]),
    (r"(#11# at pH 4.5, 30°C <100>; #11# at pH 5.5, 30°C\n\t<100>)", [
        ([11], "at pH 4.5, 30°C".split(), [100]),
        ([11], r"at pH 5.5, 30°C\n\t".split(), [100]),
    ]),
])
def test_comments(text, expected):
    result = parser.comments.parseString(text, parseAll=True)
    for comment, outcome in zip_longest(result.comments, expected):
        assert list(comment.proteins) == outcome[0]
        assert list(comment.content) == outcome[1]
        assert list(comment.citations) == outcome[2]


@pytest.mark.parametrize("text, expected", [
    ("1", "1"),
    ("1.1", "1.1"),
    ("1.1.1", "1.1.1"),
    ("1.1.1.1", "1.1.1.1"),
    ("1.1.1.n1", "1.1.1.n1"),
])
def test_ec_number(text, expected):
    result = parser.ec_number.parseString(text, parseAll=True)
    assert result[0] == expected


@pytest.mark.parametrize("text, expected", [
    ("ID\t1.1.1.1", ("1.1.1.1", [])),
    ("ID\t1.1.1.109 (transferred to EC 1.3.1.28)",
        ("1.1.1.109", [([], "transferred to EC 1.3.1.28".split(), [])])
    ),
])
def test_enzyme_begin(text, expected):
    result = parser.enzyme_begin.parseString(text, parseAll=True)
    assert result.ec_number == expected[0]
    for comment, outcome in zip_longest(result.comments, expected[1]):
        assert list(comment.proteins) == outcome[0]
        assert list(comment.content) == outcome[1]
        assert list(comment.citations) == outcome[2]


@pytest.mark.parametrize("text, expected", [
    ("///\n", "///"),
    ("///\t\n", "///"),
    pytest.param("\t///\n", None, marks=pytest.mark.raises(
        exception=ParseException)),
])
def test_enzyme_end(text, expected):
    result = parser.enzyme_end.parseString(text, parseAll=True)
    assert result[0] == expected
