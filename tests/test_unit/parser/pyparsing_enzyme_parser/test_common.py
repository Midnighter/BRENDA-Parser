# Copyright 2011-2021 Moritz Emanuel Beber
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


"""Test the common tokens and patterns."""


from typing import List

import pytest
from pyparsing import ParseException

from brenda_parser.parser.pyparsing_enzyme_parser import common


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
def test_protein_information(text: str, expected: List[int]):
    result = common.protein_information.parseString(text, parseAll=True)
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
def test_literature_citation(text: str, expected: List[int]):
    result = common.literature_citation.parseString(text, parseAll=True)
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
        pytest.param("fööbär;", "fööbär;"),
        pytest.param("fööbär ", "fööbär"),
        pytest.param("fööbär\t", "fööbär"),
        pytest.param("fööbär\n", "fööbär"),
        pytest.param("fööbär\r", "fööbär"),
        pytest.param("fööbär\r\n", "fööbär"),
    ],
)
def test_content(text: str, expected: str):
    result = common.content.parseString(text, parseAll=True)
    assert result[0] == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("()", "()"),
        ("(at pH 4.5, 30°C)", "(at pH 4.5, 30°C)"),
        ("(#11# at pH 4.5, 30°C <100>)", "(#11# at pH 4.5, 30°C <100>)"),
        (
            "(#11# at pH 4.5, 30°C <100>; #11# at pH 5.5, 30°C\n\t<100>)",
            "(#11# at pH 4.5, 30°C <100>; #11# at pH 5.5, 30°C <100>)",
        ),
    ],
)
def test_comment(text: str, expected: str):
    result = common.comment.parseString(text, parseAll=True)
    assert result[0] == expected
