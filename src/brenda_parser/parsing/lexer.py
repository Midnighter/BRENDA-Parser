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

"""Tokenize the BRENDA flat file."""

from __future__ import absolute_import

import logging

from ply.lex import lex


__all__ = ("BRENDALexer",)

LOGGER = logging.getLogger(__name__)


class BRENDALexer(object):
    """

    We use functions for most tokens in order to fully control pattern
    matching order. Tokens (methods) defined first are matched first.
    """

    states = (
        ("citation", "exclusive"),
        ("protein", "exclusive"),
        ("special", "exclusive"),
        ("comment", "exclusive"),
        ("enzyme", "exclusive"),
        ("protentry", "inclusive"),
    )
    # List of token names. This is always required.
    tokens = (
        "ENZYME_ENTRY",
        "PROTEIN",
        "CITATION",
        "ENTRY",
        "PROTEIN_ENTRY",
        "REFERENCE_ENTRY",
        "POUND",
        "LPARENS",
        "RPARENS",
        "LANGLE",
        "RANGLE",
        "LCURLY",
        "RCURLY",
        "EC_NUMBER",
        "END",
        "CONTENT",
        "SPECIAL",
        "COMMENT",
        "AND",
        "ACCESSION"
    )

    # A string containing ignored characters interpreted literally not as regex.
    t_ignore = " \t\r\f\v"  # all whitespace minus newlines
    t_citation_protein_ignore = " ,\t"
    t_special_comment_enzyme_ignore = " \t\r\f\v"
    # Regular expression rules for simple tokens are parsed after all patterns
    # defined in methods.
    t_CONTENT = "[^\{\}\(\)\<\>\# \t\r\f\v\n]+"

    def __init__(self, **kwargs):
        """
        Instantiate a BRENDA flat file specific lexer.

        An instance can then be used to tokenize a string by using
        >>> lexer = BRENDALexer()
        >>> lexer.input("What will happen?")
        >>> [token.type for token in lexer]
        ['CONTENT', 'CONTENT', 'CONTENT']

        Parameters
        ----------
        kw_args :
            Keyword arguments are passed to the ply.lex.lex call.
        """
        super(BRENDALexer, self).__init__()
        self.lexer = lex(module=self, errorlog=LOGGER, **kwargs)
        self.parens_level = 0
        self.last_lparens = 0
        self.last_rparens = 0

    def __getattr__(self, attr):
        return getattr(self.lexer, attr)

    def __iter__(self):
        return (tok for tok in iter(self.lexer.token, None))

    def input(self, data):
        """
        Add a new string to the lexer.

        This is the setup step necessary before you can iterate over the tokens.

        Parameters
        ----------
        data : str
            Any string.
        """
        self.lexer.push_state("INITIAL")
        self.parens_level = 0
        self.lexer.input(data)

    def t_ANY_error(self, t):
        LOGGER.error("Invalid token '%s' at line %d.", t.value[0], t.lineno)
        t.lexer.skip(1)

    def t_ANY_newline(self, t):
        r'\n+'
        LOGGER.debug("lineno %d +%d", t.lineno, len(t.value))
        t.lexer.lineno += len(t.value)

    def t_brenda_comment(self, t):
        r"\*.+\n"
        LOGGER.debug("lineno %d: Skipping comment line.", t.lineno)
        t.lexer.lineno += 1

    def t_POUND(self, t):
        r"[#]"
        self.lexer.push_state("protein")
        return t

    def t_protein_PROTEIN(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_protein_POUND(self, t):
        r"[#]"
        self.lexer.pop_state()
        return t

    def t_LANGLE(self, t):
        r"<"
        t.lexer.push_state("citation")
        return t

    def t_citation_CITATION(self, t):
        r"\d+"
        t.value = int(t.value)
        return t

    def t_citation_RANGLE(self, t):
        r">"
        t.lexer.pop_state()
        return t

    def t_LCURLY(self, t):
        r"{"
        t.lexer.push_state("special")
        return t

    def t_special_SPECIAL(self, t):
        r"[^\{\}\s]+"
        return t

    def t_special_RCURLY(self, t):
        r"}"
        t.lexer.pop_state()
        return t

    def t_LPARENS(self, t):
        r"\("
        t.lexer.push_state("comment")
        self.parens_level += 1
        return t

    def t_comment_COMMENT(self, t):
        r"[^\(\)\s]+"
        # TODO: In future properly parse proteins and citations inside comments.
        # r"[^\s\{\}\(\)\<\>\#]+"
        return t

    def t_comment_LPARENS(self, t):
        r"\("
        self.parens_level += 1
        t.type = "COMMENT"
        return t

    def t_comment_RPARENS(self, t):
        r"\)"
        self.parens_level -= 1
        if self.parens_level == 0:
            t.lexer.pop_state()
        else:
            t.type = "COMMENT"
        return t

    def t_END(self, t):
        r"[/]{3}\s"
        t.lexer.push_state("INITIAL")
        t.value = t.value.strip()
        return t

    def t_ENZYME_ENTRY(self, t):
        r"ID\t"
        t.lexer.push_state("enzyme")
        t.value = t.value.strip()
        return t

    def t_enzyme_EC_NUMBER(self, t):
        r"(\d+)\.(\d+)\.(\d+)\.(\d+)"
        t.lexer.pop_state()
        return t

    def t_protentry_PROTEIN_ENTRY(self, t):
        r"PR\t"
        t.value = t.value.strip()
        return t

    def t_protentry_ENTRY(self, t):
        r"[A-Z0-9]{2,4}\t"
        t.value = t.value.strip()
        if t.value != "PR":
            t.lexer.pop_state()
        return t

    def t_PROTEIN_ENTRY(self, t):
        r"PR\t"
        t.value = t.value.strip()
        if t.lexer.current_state() != "protentry":
            t.lexer.push_state("protentry")
        return t

    def t_REFERENCE_ENTRY(self, t):
        r"RF\t"
        t.value = t.value.strip()
        return t

    def t_ENTRY(self, t):
        r"[A-Z0-9]{2,4}\t"
        t.value = t.value.strip()
        return t

    def t_brenda_header(self, t):
        r"[A-Z0-9_]{4,}\n"
        LOGGER.debug("lineno %d: Section header '%s'.", t.lineno,
                     t.value.strip())
        t.lexer.lineno += 1

    def t_protentry_AND(self, t):
        r"AND"
        return t

    def t_protentry_ACCESSION(self, t):
        r"([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?"
        # Regular expression from identifiers.org for UniProt.
        return t
