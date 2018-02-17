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

import pytest

from brenda_parser.parsing.lexer import BRENDALexer


@pytest.fixture(scope="module")
def lexer():
    return BRENDALexer()


@pytest.fixture(scope="function")
def tokenizer(lexer, request):
    lexer.input(request.param)
    return lexer


@pytest.mark.parametrize("tokenizer, expected", [
    ("KM\tRF\tKI\t", ["INITIAL", "INITIAL", "INITIAL"]),
    ("KM\tPR\tKI\t", ["INITIAL", "protentry", "INITIAL"]),
    ("KM\tPR\tPR\tKI\t", ["INITIAL", "protentry", "protentry", "INITIAL"]),
    ("KM\tPR\tRF\t", ["INITIAL", "protentry", "INITIAL"])
], indirect=["tokenizer"])
def test_inclusive_entry_states(tokenizer, expected):
    states = [t.lexer.current_state() for t in tokenizer]
    assert states == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("<13>", ["citation", "citation", "INITIAL"]),
    ("#13#", ["protein", "protein", "INITIAL"]),
    ("#13##", ["protein", "protein", "INITIAL", "protein"]),
    ("{13}", ["special", "special", "INITIAL"]),
    ("(13)", ["comment", "comment", "INITIAL"]),
], indirect=["tokenizer"])
def test_exclusive_states(tokenizer, expected):
    states = [t.lexer.current_state() for t in tokenizer]
    assert states == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("# ,,#", ["POUND", "POUND"]),
    ("#12#", ["POUND", "PROTEIN", "POUND"]),
    ("# 12,423,23#", ["POUND", "PROTEIN", "PROTEIN", "PROTEIN", "POUND"]),
    ("# # 13 #", ["POUND", "POUND", "CONTENT", "POUND"]),
], indirect=["tokenizer"])
def test_protein_tokens(tokenizer, expected):
    tokens = [t.type for t in tokenizer]
    assert tokens == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("< ,,>", ["LANGLE", "RANGLE"]),
    ("<12>", ["LANGLE", "CITATION", "RANGLE"]),
    ("< 12,423,23>", ["LANGLE", "CITATION", "CITATION", "CITATION", "RANGLE"]),
    ("<12> 13 <", ["LANGLE", "CITATION", "RANGLE", "CONTENT", "LANGLE"]),
], indirect=["tokenizer"])
def test_citation_tokens(tokenizer, expected):
    tokens = [t.type for t in tokenizer]
    assert tokens == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("{ }", ["LCURLY", "RCURLY"]),
    ("{12}", ["LCURLY", "SPECIAL", "RCURLY"]),
    ("{ 12,423,23}", ["LCURLY", "SPECIAL", "RCURLY"]),
    ("{12} 13 {", ["LCURLY", "SPECIAL", "RCURLY", "CONTENT", "LCURLY"]),
], indirect=["tokenizer"])
def test_special_tokens(tokenizer, expected):
    tokens = [t.type for t in tokenizer]
    assert tokens == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("( )", ["LPARENS", "RPARENS"]),
    ("(12)", ["LPARENS", "COMMENT", "RPARENS"]),
    ("( 12,423,23)", ["LPARENS", "COMMENT", "RPARENS"]),
    ("(12) 13 (", ["LPARENS", "COMMENT", "RPARENS", "CONTENT", "LPARENS"]),
], indirect=["tokenizer"])
def test_comment_tokens(tokenizer, expected):
    tokens = [t.type for t in tokenizer]
    assert tokens == expected


@pytest.mark.parametrize("tokenizer, expected", [
    ("KM\t#13# Q4AE87 SwissProt\n",
     ["ENTRY", "POUND", "PROTEIN", "POUND", "CONTENT", "CONTENT"]),
    ("PR\t#41# Pseudomonas sp. Q4AE87 SwissProt\nPI\t",
     ["PROTEIN_ENTRY", "POUND", "PROTEIN", "POUND", "CONTENT", "CONTENT",
      "ACCESSION", "CONTENT", "ENTRY"]),
], indirect=["tokenizer"])
def test_protein_entry_state(tokenizer, expected):
    tokens = [t.type for t in tokenizer]
    assert tokens == expected
