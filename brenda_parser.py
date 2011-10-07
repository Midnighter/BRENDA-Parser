#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
=============================
BRENDA Enzyme Database Parser
=============================

:Author:
    Moritz Emanuel Beber
:Date:
    2011-01-27
:Copyright:
    Copyright(c) 2011 Jacobs University of Bremen. All rights reserved.
:File:
    errors.py
"""


import re
import errno
import codecs

from StringIO import StringIO
from collections import defaultdict


class ArgumentError(StandardError):
    """
    Error class that is meant to be raised when the arguments provided to a
    function are incorrect.
    """

    def __init__(self, msg, *args, **kw_args):
        """
        Parameters
        ----------
        msg : An unformatted string, i.e., it may contain multiple string
                format markers.

        Returns
        -------
        An ArgumentError instance.

        Notes
        -----
        A variable number of arguments may be passed. They will all be used to
        format msg. So take care that the number and type of additional
        arguments matches the format markers in msg.

        Examples
        --------
        >>> err = errors.ArgumentError("It's too %s outside!", "rainy")
        >>> print(err)
        It's too rainy outside!
        >>> print(err.errno)
        22

        """
        StandardError.__init__(self, *args, **kw_args)
        self.args = (msg,) + args
        self.errno = errno.EINVAL
        self.strerror = msg % args

    def __str__(self):
        """
        Returns
        -------
        strerror : Simply returns the formatted string.
        """
        return self.strerror


class Enzyme(object):
    """
    An object that encompasses all information about a kind of enzyme uniquely
    identified by its EC number.
    """

    def __init__(self, ec_class, *args, **kw_args):
        """
        Initialisation of an Enzyme instance.
        """
        object.__init__(self)
        self.ec_class = ec_class
        self.organisms = dict()
        self.references = dict()
        self.entries = dict()

    def __str__(self):
        return self.ec_class

    def __repr__(self):
        return self.ec_class


class BRENDAEntryComment(object):
    """
    Encapsulates a comment to an entry in a BRENDA information field.
    """

    def __init__(self, message, organisms=None, references=None, *args,\
            **kw_args):
        """
        Initialisation of a BRENDAEntryComment instance.
        """
        object.__init__(self)
        self.msg = message
        self.organisms = organisms
        self.references = references

    def __str__(self):
        return self.msg

    def _repr__(self):
        return self.msg


class BRENDAEntry(BRENDAEntryComment):
    """
    Encapsulates an entry in a BRENDA information field.
    """

    def __init__(self, message, organisms=None, references=None,\
            information=None, comment=None, *args, **kw_args):
        """
        Initialisation of a BRENDAEntryComment instance.
        """
        BRENDAEntryComment.__init__(self, message=message, organisms=organisms,
                references=references, *args, **kw_args)
        self.information = information
        self.comment = comment


class BRENDAOrganism(object):
    """
    Encapsulates an entry in a BRENDA information field.
    """

    _counter = 1
    _memory = dict()

    def __new__(cls, name, identifier, references, information, comment, *args,
            **kw_args):
        """
        Ensures the unique instance policy of all organisms.
        """
        if cls._memory.has_key((cls, name)):
            return cls._memory[(cls, name)]
        else:
            return object.__new__(cls)

    def __init__(self, name, identifier, references, information, comment,
            *args, **kw_args):
        """
        Initialisation of a BRENDAOrganism instance.
        """
        if self.__class__._memory.has_key((self.__class__, name)):
            return
        object.__init__(self)
        self._index = self.__class__._counter
        self.__class__._counter += 1
        self.name = name
        self.identifier = identifier
        self.references = references
        self.information = information
        self.comment = comment
        self.__class__._memory[(self.__class__, self.name)] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s.%s, %d>" % (self.__module__, self.__class__.__name__, self._index)


class BRENDAParser(object):
    """
    Encapsulation of parsing a BRENDA database plain text file.
    """

    _subsections = {
            "ACTIVATING_COMPOUND": "AC",
            "APPLICATION": "AP",
            "COFACTOR": "CF",
            "CLONED": "CL",
            "CRYSTALLIZATION": "CR",
            "CAS_REGISTRY_NUMBER": "CR",
            "ENGINEERING": "EN",
            "GENERAL_STABILITY": "GS",
            "IC50_VALUE": "IC50",
            "INHIBITORS": "IN",
            "KI_VALUE": "KI",
            "KM_VALUE": "KM",
            "LOCALIZATION": "LO",
            "METALS_IONS": "ME",
            "MOLECULAR_WEIGHT": "MW",
            "NATURAL_SUBSTRATE_PRODUCT": "NSP",
            "OXIDATION_STABILITY": "OS",
            "ORGANIC_SOLVENT_STABILITY": "OSS",
            "PH_OPTIMUM": "PHO",
            "PH_RANGE": "PHR",
            "PH_STABILITY": "PHS",
            "PI_VALUE": "PI",
            "POSTTRANSLATIONAL_MODIFICATION": "PM",
            "PROTEIN": "PR",
            "PURIFICATION": "PU",
            "REACTION": "RE",
            "REFERENCE": "RF",
            "RENATURED": "RN",
            "RECOMMENDED_NAME": "RN",
            "REACTION_TYPE": "RT",
            "SPECIFIC_ACTIVITY": "SA",
            "SYSTEMATIC_NAME": "SN",
            "SUBSTRATE_PRODUCT": "SP",
            "STORAGE_STABILITY": "SS",
            "SOURCE_TISSUE": "ST",
            "SUBUNITS": "SU",
            "SYNONYMS": "SY",
            "TURNOVER_NUMBER": "TN",
            "TEMPERATURE_OPTIMUM": "TO",
            "TEMPERATURE_RANGE": "TR",
            "TEMPERATURE_STABILITY": "TS"
            }

    def __init__(self, filename, encoding="iso-8859-1", low_memory=False,
            *args, **kw_args):
        """
        Initialisation of a BRENDAParser instance.
        """
        object.__init__(self)
        self._filename = filename
        self._file_handle = None
        self._low_memory = low_memory
        self._encoding = encoding
        self._organisms_tag = re.compile(r"\#(.+?)\#", re.UNICODE)
        self._comment_tag = re.compile(r" \((.*)\)", re.UNICODE)
        self._reference_tag = re.compile(r"\<(.+?)\>", re.UNICODE)
        self._information_pattern = re.compile(r"\{(.*?)\}", re.UNICODE)
        self._numbers_pattern = re.compile(r"\d+", re.UNICODE)
        self._prot_qualifier = re.compile(r" (\w+) (?=UniProt|Uniprot|"\
                "SwissProt|Swissprot|GenBank|Genbank)", re.UNICODE)
        self._current = None
        self.enzymes = None
        self._line_number = None

    def __enter__(self):
        self._file_handle = codecs.open(self._filename, mode="r",
                encoding=self._encoding)
        if not self._low_memory:
            tmp = StringIO(self._file_handle.read())
            self._file_handle.close()
            self._file_handle = tmp
        self.enzymes = defaultdict(list)
        self._line_number = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the file handle.
        """
        if not self._file_handle.closed:
            self._file_handle.close()

    def parse(self):
        """
        Parse multiple Enzyme sections.
        """
        for line in self._file_handle:
            self._line_number += 1
            line = line.strip("\n")
            if not line:
                continue
            elif line.startswith("*"):
                continue
            elif line.startswith("ID"):
                self._parse_id(line[2:].strip())
            elif line == "PROTEIN":
                self._parse_information_field(line, parser=self._parse_protein)
            elif line == "REFERENCE":
                self._parse_information_field(line, parser=self._parse_reference)
            elif line == "///":
                # end one enzyme entry
                self._current = None
            elif line:
                self._current.entries[line.lower()] =\
                        self._parse_information_field(line)
        # convert to normal dictionary again
        return dict(self.enzymes)

    def _parse_information_field(self, line, parser=None):
        """
        Parse an information field of an enzyme.
        """
        field_identifier = self.__class__._subsections.get(line, False)
        if not field_identifier:
            raise ArgumentError("unrecognised entry: '%s' @ #%d", line,\
                    self._line_number)
        if not parser:
            parser = self._parse_generic_entry
        entries = list()
        record = list()
        for line in self._file_handle:
            self._line_number += 1
            line = line.strip("\n")
            if not line:
                if record:
                    entries.append(parser(" ".join(record)))
                break
            elif line.startswith(field_identifier):
                if record:
                    entries.append(parser(" ".join(record)))
                    record = list()
                record.append(line[len(field_identifier):].strip())
            elif line.startswith("\t"):
                record.append(line.strip())
            elif line.startswith(" ="):
                record.append(line.strip())
            else:
                raise ArgumentError("unrecognised line: '%s' @ #%d", line,\
                        self._line_number)
        return entries

    def _parse_generic_entry(self, text):
        """
        Parse an entry of a specific information field.
        """
        mobj = self._information_pattern.search(text)
        if mobj:
            information = mobj.group(1)
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            information = None
        mobj = self._comment_tag.search(text)
        if mobj:
            comment = self._parse_comment(mobj.group(1))
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            comment = None
        mobj = self._organisms_tag.search(text)
        if mobj:
            organisms = [int(match_num.group(0)) for match_num in\
                    self._numbers_pattern.finditer(mobj.group(1))]
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            organisms = None
        mobj = self._reference_tag.search(text)
        if mobj:
            references = [int(match_num.group(0)) for match_num in\
                    self._numbers_pattern.finditer(mobj.group(1))]
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            references = None
        return BRENDAEntry(text.strip(), organisms, references, information,\
                comment)

    def _parse_comment(self, text):
        """
        Parse an entry of a specific information field.
        """
        mobj = self._organisms_tag.search(text)
        if mobj:
            organisms = [int(match_num.group(0)) for match_num in\
                    self._numbers_pattern.finditer(mobj.group(1))]
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            organisms = None
        mobj = self._reference_tag.search(text)
        if mobj:
            references = [int(match_num.group(0)) for match_num in\
                    self._numbers_pattern.finditer(mobj.group(1))]
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            references = None
        return BRENDAEntryComment(text.strip(), organisms, references)

    def _parse_id(self, text):
        """

        """
        mobj = self._comment_tag.search(text)
        # for now we ignore comments to the id
        if mobj:
            comment = self._parse_comment(mobj.group(1))
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            comment = None
        text = text.strip()
        self._current = Enzyme(text)
        ec_num = text.split(".")
        for i in range(1, len(ec_num) + 1):
            self.enzymes[".".join(ec_num[:i])].append(self._current)

    def _parse_protein(self, text):
        """

        """
        mobj = self._information_pattern.search(text)
        if mobj:
            information = mobj.group(1)
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            information = None
        mobj = self._comment_tag.search(text)
        if mobj:
            comment = self._parse_comment(mobj.group(1))
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            comment = None
        mobj = self._organisms_tag.search(text)
        if mobj:
            organism = int(mobj.group(1))
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            raise ArgumentError("organism reference missing: '%s' @ #%d", text,\
                    self._line_number)
        #TODO: remove databank qualifier somehow capture multiple accessors
        mobj = self._prot_qualifier.search(text)
        if mobj:
            identifier = mobj.group(1)
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            identifier = None
        mobj = self._reference_tag.search(text)
        if mobj:
            references = [int(match_num.group(0)) for match_num in\
                    self._numbers_pattern.finditer(mobj.group(1))]
            text = text[:mobj.start()] + text[mobj.end():]
        else:
            references = None
        self._current.organisms[organism] = BRENDAOrganism(text.strip(),
                identifier, references, information, comment)

    def _parse_reference(self, text):
        """

        """
        pass

