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
from pyparsing import Optional, ParseException

from brenda_parser.parser.pyparsing_enzyme_parser import PyParsingEnzymeParser


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("##", None, marks=pytest.mark.raises(exception=ParseException)),
        ("#1#", [1]),
        ("#1,2,3#", [1, 2, 3]),
        ("#1,2,3,\n\t4,5,6#", [1, 2, 3, 4, 5, 6]),
        ("#1,2,3\n\t4,5,6#", [1, 2, 3, 4, 5, 6]),
    ],
)
def test_protein_information(text, expected):
    result = PyParsingEnzymeParser.protein_information.parseString(text, parseAll=True)
    assert list(result.proteins) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("<>", None, marks=pytest.mark.raises(exception=ParseException)),
        ("<1>", [1]),
        ("<1,2,3>", [1, 2, 3]),
        ("<1,2,3,\n\t4,5,6>", [1, 2, 3, 4, 5, 6]),
        ("<1,2,3\n\t4,5,6>", [1, 2, 3, 4, 5, 6]),
    ],
)
def test_literature_citation(text, expected):
    result = PyParsingEnzymeParser.literature_citation.parseString(text, parseAll=True)
    assert list(result.references) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("fööbär", "fööbär"),
        pytest.param(
            "fööbär#", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär<", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär>", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär;", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär(", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär)", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär{", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param(
            "fööbär}", None, marks=pytest.mark.raises(exception=ParseException)
        ),
        pytest.param("fööbär ", "fööbär"),
        pytest.param("fööbär\t", "fööbär"),
        pytest.param("fööbär\n", "fööbär"),
        pytest.param("fööbär\r", "fööbär"),
        pytest.param("fööbär\r\n", "fööbär"),
    ],
)
def test_content(text, expected):
    result = PyParsingEnzymeParser.content.parseString(text, parseAll=True)
    assert result[0] == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("föö", ["föö"]),
        ("föö bär", "föö bär".split()),
        ("föö 24 bär", "föö 24 bär".split()),
        ("at (pH 4.5), 30°C", "at ( pH 4.5 ) , 30°C".split()),
        ("at (pH), 30°C", "at ( pH ) , 30°C".split()),
    ],
)
def test_value(text, expected):
    result = PyParsingEnzymeParser.inside.parseString(text, parseAll=True)
    assert list(result.value) == expected


@pytest.mark.parametrize(
    "text, proteins, content, citations",
    [
        ("föö", [], ["föö"], []),
        ("föö bär", [], "föö bär".split(), []),
        ("föö 24 bär", [], "föö 24 bär".split(), []),
        ("#11# at pH 4.5, 30°C <100>", [11], "at pH 4.5, 30°C".split(), [100]),
        (
            "#11# at pH 4.5 (5 mL), 30°C <100>",
            [11],
            "at pH 4.5 ( 5 mL ) , 30°C".split(),
            [100],
        ),
    ],
)
def test_inside(text, proteins, content, citations):
    result = PyParsingEnzymeParser.inside.parseString(text, parseAll=True)
    assert list(result.proteins) == proteins
    assert list(result.value) == content
    assert list(result.references) == citations


@pytest.mark.parametrize(
    "text, expected",
    [
        ("()", [([], [], [])]),
        ("(at pH 4.5, 30°C)", [([], "at pH 4.5, 30°C".split(), []),]),
        ("(#11# at pH 4.5, 30°C <100>)", [([11], "at pH 4.5, 30°C".split(), [100]),]),
        (
            "(#11# at pH 4.5, 30°C <100>; #11# at pH 5.5, 30°C\n\t<100>)",
            [
                ([11], "at pH 4.5, 30°C".split(), [100]),
                ([11], "at pH 5.5, 30°C".split(), [100]),
            ],
        ),
    ],
)
def test_comment(text, expected):
    comnt = Optional(PyParsingEnzymeParser.comment)("comments")
    result = comnt.parseString(text, parseAll=True)
    for comment, outcome in zip_longest(result.comments, expected):
        assert list(comment.proteins) == outcome[0]
        assert list(comment.value) == outcome[1]
        assert list(comment.references) == outcome[2]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("1", "1"),
        ("1.1", "1.1"),
        ("1.1.1", "1.1.1"),
        ("1.1.1.1", "1.1.1.1"),
        ("1.1.1.n1", "1.1.1.n1"),
    ],
)
def test_ec_number(text, expected):
    result = PyParsingEnzymeParser.ec_number.parseString(text, parseAll=True)
    assert result[0] == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("ID\t1.1.1.1", ("1.1.1.1", [])),
        (
            "ID\t1.1.1.109 (transferred to EC 1.3.1.28)",
            ("1.1.1.109", [([], "transferred to EC 1.3.1.28".split(), [])]),
        ),
    ],
)
def test_enzyme_begin(text, expected):
    result = PyParsingEnzymeParser.enzyme_begin.parseString(text, parseAll=True)
    assert result.ec_number == expected[0]
    for comment, outcome in zip_longest(result.comments, expected[1]):
        assert list(comment.proteins) == outcome[0]
        assert list(comment.value) == outcome[1]
        assert list(comment.references) == outcome[2]


@pytest.mark.parametrize(
    "text, expected", [("KI\t#12# 0.0000001 {korormicin} <13>", ""),]
)
def test_ki_value(text, expected):
    result = PyParsingEnzymeParser.ki_value.parseString(text, parseAll=True)
    assert result.key == expected.key
    assert list(result.protein) == expected.protein
    assert list(result.value) == expected.value
    assert list(result.inhibitor) == expected.inhibitor
    assert list(result.comments) == expected.comments
    assert list(result.citations) == expected.citations


@pytest.mark.parametrize(
    "text, expected",
    [
        ("RN\tlactate aldolase", ""),
        ("SN\t(S)-lactate acetaldehyde-lyase (formate-forming)", ""),
        ("RE\t(S)-lactate = formate + acetaldehyde", ""),
        ("NSP\t#1# formate + acetaldehyde = lactate <1>", ""),
        ("PU\t#1# <1>", ""),
        ("SN\t", ""),
        (
            "TN\t#105# 13.1 {benzaldehyde}  (#105# mutant enzyme W95L/N249Y in 0.1 M\n"
            "glycine-NaOH buffer (pH 10.5), at 65°C <207>) <207>",
            "",
        ),
    ],
)
def test_field_entry(text, expected):
    result = PyParsingEnzymeParser.field_entry.parseString(text, parseAll=True)
    assert result.key == expected.key
    assert list(result.proteins) == expected.proteins
    assert list(result.entry) == expected.entry
    assert list(result.comments) == expected.comments
    assert list(result.citations) == expected.citations


@pytest.mark.parametrize(
    "text, expected",
    [
        ("///\n", "///"),
        ("///\r\n", "///"),
        pytest.param(
            "\t///\n", None, marks=pytest.mark.raises(exception=ParseException)
        ),
    ],
)
def test_enzyme_end(text, expected):
    result = PyParsingEnzymeParser.enzyme_end.parseString(text, parseAll=True)
    assert result[0] == expected
