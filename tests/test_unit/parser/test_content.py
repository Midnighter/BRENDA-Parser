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


import pytest

from brenda_parser.parser import content


@pytest.mark.parametrize(
    "lines, lengths",
    [
        (["ID\n", "///\n",], [2]),
        (["ID\n", "\n", "///\n",], [3]),
        (["ID\n", "///\n", "ID\n", "///\n",], [2, 2]),
        pytest.param(
            ["ID\n", "ID\n", "///\n",],
            [None],
            marks=pytest.mark.raises(exception=AssertionError),
        ),
        pytest.param(
            ["ID\n", "///\n", "///\n",],
            [None],
            marks=pytest.mark.raises(exception=AssertionError),
        ),
    ],
)
def test_enzyme_section_iter(lines, lengths):
    for section, length in zip(content.enzyme_section_iter(lines), lengths):
        assert len(section) == length
