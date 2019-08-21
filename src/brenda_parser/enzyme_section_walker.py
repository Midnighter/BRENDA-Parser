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


"""Provide an enzyme section walker."""


from os import linesep
from typing import List, Tuple

from .abstract_enzyme_section_visitor import AbstractEnzymeSectionVisitor
from .parser import ENZYME_END


class EnzymeSectionWalker:
    """
    Walk through sub-sections of an enzyme definition and visit each one.

    The visitor can be used to construct an enzyme object or otherwise handle
    each visited section.

    Attributes
    ----------
    visitor : AbstractEnzymeSectionVisitor
        A visitor for each enzyme section.

    See Also
    --------
    enzyme_build_director.EnzymeBuildDirector

    """

    def __init__(
        self, visitor: AbstractEnzymeSectionVisitor
    ):
        self.visitor = visitor

    def __call__(self, lines: List[str]):
        """
        Walk through and visit each enzyme description section.

        Parameters
        ----------
        lines : list of str
            Lines of text describing an enzyme. The first line **must** start with
            ``ID`` and the last line with ``///``.

        Returns
        -------
        AbstractEnzyme
            A concrete enzyme instance depending on the chosen visitor.

        """
        index = 0
        advance, section = self.concatenate_section(lines[index:])
        index += advance
        self.visitor.visit_id(section)

        while index < len(lines):
            advance, heading = self.skip_to_heading(lines[index:])
            if heading == ENZYME_END:
                break
            index += advance
            advance, section = self.concatenate_section(lines[index:])
            index += advance
            self.visitor.visit(heading, section)

    @staticmethod
    def skip_to_heading(lines: List[str]) -> Tuple[int, str]:
        """Increment an index until finding a non-empty line."""
        try:
            index, line = next(
                (pair for pair in enumerate((l.strip() for l in lines)) if pair[1])
            )
        except StopIteration:
            raise RuntimeError("No more content found.")
        # We add one to the index because we don't want to inspect the same
        # line again.
        return index + 1, line

    @staticmethod
    def concatenate_section(lines: List[str]) -> Tuple[int, str]:
        """Concatenate a section until the first empty line."""
        index = 0
        for index, line in enumerate((l.strip() for l in lines)):
            if not line:
                break
        # We add one to the index because we don't want to inspect the empty
        # line again.
        return index + 1, linesep.join(lines[:index])
