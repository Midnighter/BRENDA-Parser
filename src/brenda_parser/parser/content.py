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


"""Provide functions for the actual content parsing."""


from typing import Iterable, List


__all__ = ("enzyme_section_iter",)


ENZYME_BEGIN = "ID"
ENZYME_END = "///"
COMMENT = "*"


def enzyme_section_iter(lines: Iterable[str]):
    """
    Yield individual enzyme sections from linewise text content.

    Parameters
    ----------
    lines : iterable of str
        The entire content as individual lines that is to be broken up.

    Returns
    -------
    list
        Yields lists of all the lines representing one enzyme section.

    """
    buffer: List[str] = []
    balance = 0
    collect = False
    # We skip comment lines but keep empty lines since they are important
    # markers for the end of a sub-section.
    for index, line in (
        (i, l) for i, l in enumerate(lines, start=1)
        if not l.startswith(COMMENT)
    ):
        if line.startswith(ENZYME_BEGIN):
            assert balance == 0
            balance += 1
            collect = True
            buffer = [line]
        elif line.startswith(ENZYME_END):
            balance -= 1
            collect = False
            buffer.append(line)
            assert balance == 0
            yield buffer
        elif collect:
            buffer.append(line)



