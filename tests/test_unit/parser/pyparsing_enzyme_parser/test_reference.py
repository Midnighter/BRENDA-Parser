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


"""Test the reference tokens and patterns."""


from pathlib import Path

import pytest
import toml
from pyparsing import ParseException

from brenda_parser.parser.pyparsing_enzyme_parser import reference


with (Path(__file__).parent / "data" / "reference_entries.toml").open() as handle:
    entry_cases = toml.load(handle)


@pytest.mark.parametrize(
    "text, expected",
    [
        pytest.param("<>", None, marks=pytest.mark.raises(exception=ParseException)),
        ("<1>", 1),
        pytest.param("<1,2>", None, marks=pytest.mark.raises(exception=ParseException)),
    ],
)
def test_id(text: str, expected: str):
    result = reference.id.parseString(text, parseAll=True)
    assert result.id == expected


@pytest.mark.parametrize("case", entry_cases["cases"])
def test_reference_entry(case: dict):
    result = reference.entry.parseString(case.pop("text"), parseAll=True)[0]
    for attribute, expected in case.items():
        if isinstance(expected, list):
            assert list(getattr(result, attribute)) == expected
        elif isinstance(expected, dict):
            assert getattr(result, attribute).asDict() == expected
        else:
            assert getattr(result, attribute) == expected
