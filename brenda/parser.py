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
    Copyright |c| 2011, Jacobs University Bremen gGmbH, all rights reserved.
:File:
    parser.py

.. |c| unicode:: U+A9
"""


__all__ = ["BRENDAParser"]


import sys
import re
import errno
import codecs

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

    def __init__(self, ec_number, *args, **kw_args):
        """
        Initialisation of an Enzyme instance.
        """
        object.__init__(self)
        self.ec_number = ec_number
        self.organisms = dict()
        self.references = dict()
        self.entries = dict()

    def __str__(self):
        return self.ec_number

    def __unicode__(self):
        return unicode(self.ec_number)

    def __repr__(self):
        return self.ec_number


class EntryComment(object):
    """
    Encapsulates a comment to an entry in a BRENDA information field.
    """

    def __init__(self, message, organisms=None, references=None, *args,\
            **kw_args):
        """
        Initialisation of a EntryComment instance.
        """
        object.__init__(self)
        self.msg = message
        self.organisms = organisms
        self.references = references

    def __str__(self):
        return self.msg

    def _repr__(self):
        return self.msg


class Entry(EntryComment):
    """
    Encapsulates an entry in a BRENDA information field.
    """

    def __init__(self, message, organisms=None, references=None,\
            information=None, comment=None, *args, **kw_args):
        """
        Initialisation of a EntryComment instance.
        """
        EntryComment.__init__(self, message=message, organisms=organisms,
                references=references, *args, **kw_args)
        self.information = information
        self.comment = comment


class Organism(object):
    """
    Encapsulates an entry in a BRENDA information field.
    """

    _counter = 1

    def __init__(self, name, identifier, references, information, comment,
            *args, **kw_args):
        """
        Initialisation of an Organism instance.
        """
        object.__init__(self)
        self._index = self.__class__._counter
        self.__class__._counter += 1
        self.name = name
        self.identifier = identifier
        self.references = references
        self.information = information
        self.comment = comment

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<%s.%s, %d>" % (self.__module__, self.__class__.__name__,
                id(self))


class ProgressMeter(object):

    def __init__(self, end=None, **kw_args):
        super(ProgressMeter, self).__init__(**kw_args)
        if end:
            self.end = float(end)
            self.update = self._progress

    def update(self, current):
        pass

    def _progress(self, current):
        sys.stdout.write("\r{0:.1%}".format(current / self.end))
        sys.stdout.flush()

    def close(self):
        sys.stdout.write("\r{0:.1%}\n".format(1.0))
        sys.stdout.flush()


class BRENDAParser(object):
    """
    Encapsulation of parsing a BRENDA database plain text file.
    """

    _sections = [
            "ACTIVATING_COMPOUND",
            "APPLICATION",
            "COFACTOR",
            "CLONED",
            "CRYSTALLIZATION",
            "CAS_REGISTRY_NUMBER",
            "ENGINEERING",
            "GENERAL_STABILITY",
            "IC50_VALUE",
            "INHIBITORS",
            "KI_VALUE",
            "KM_VALUE",
            "LOCALIZATION",
            "METALS_IONS",
            "MOLECULAR_WEIGHT",
            "NATURAL_SUBSTRATE_PRODUCT",
            "OXIDATION_STABILITY",
            "ORGANIC_SOLVENT_STABILITY",
            "PH_OPTIMUM",
            "PH_RANGE",
            "PH_STABILITY",
            "PI_VALUE",
            "POSTTRANSLATIONAL_MODIFICATION",
            "PROTEIN",
            "PURIFICATION",
            "REACTION",
            "REFERENCE",
            "RENATURED",
            "RECOMMENDED_NAME",
            "REACTION_TYPE",
            "SPECIFIC_ACTIVITY",
            "SYSTEMATIC_NAME",
            "SUBSTRATE_PRODUCT",
            "STORAGE_STABILITY",
            "SOURCE_TISSUE",
            "SUBUNITS",
            "SYNONYMS",
            "TURNOVER_NUMBER",
            "TEMPERATURE_OPTIMUM",
            "TEMPERATURE_RANGE",
            "TEMPERATURE_STABILITY"
            ]
    _section_entries = [
            "AC",
            "AP",
            "CF",
            "CL",
            "CR",
            "CR",
            "EN",
            "GS",
            "IC50",
            "IN",
            "KI",
            "KM",
            "LO",
            "ME",
            "MW",
            "NSP",
            "OS",
            "OSS",
            "PHO",
            "PHR",
            "PHS",
            "PI",
            "PM",
            "PR",
            "PU",
            "RE",
            "RF",
            "RN",
            "RN",
            "RT",
            "SA",
            "SN",
            "SP",
            "SS",
            "ST",
            "SU",
            "SY",
            "TN",
            "TO",
            "TR",
            "TS"
            ]

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
        self._progress = None
        self._organisms_tag = re.compile(r"\#(.+?)\#", re.UNICODE)
        self._comment_tag = re.compile(r" \((.*)\)", re.UNICODE)
        self._reference_tag = re.compile(r"\<(.+?)\>", re.UNICODE)
        self._information_pattern = re.compile(r"\{(.*?)\}", re.UNICODE)
        self._numbers_pattern = re.compile(r"\d+", re.UNICODE)
        self._prot_qualifier = re.compile(r" (\w+) (?=UniProt|Uniprot|"\
                "SwissProt|Swissprot|GenBank|Genbank)", re.UNICODE)
        self._section_names = set(self.__class__._sections)
        self._entry_names = dict(zip(self.__class__._sections,
            self.__class__._section_entries))
        self._current = None
        self.enzymes = None
        self._line_number = None

    def __enter__(self):
        self._file_handle = codecs.open(self._filename, mode="rb",
                encoding=self._encoding)
        if not self._low_memory:
            tmp = self._file_handle.readlines()
            self._file_handle.close()
            self._file_handle = tmp
            self._progress = ProgressMeter(end=len(tmp))
        else:
            self._progress = ProgressMeter()
        self.enzymes = defaultdict(list)
        self._line_number = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Close the file handle.
        """
        if not isinstance(self._file_handle, list):
            self._file_handle.close()
        return False

    def parse(self):
        """
        Parse multiple Enzyme sections.
        """
        section_id = ""
        section = list()
        entry_id = ""
        entry = list()
        parser = self._parse_generic_entry
        for line in self._file_handle:
            if self._line_number % 1000 == 0:
                self._progress.update(self._line_number)
            self._line_number += 1
            line = line.rstrip()
            if not line:
                continue
            if line.startswith("*"):
                continue
            content = line.split(None, 1)
            if content[0] == "ID":
                self._parse_id(content[1])
            elif content[0] in self._section_names:
                # two cases to handle: (1) continued entry not starting with tab
                # (2) continued entry starting with section name
                if content[1:]:
                    entry.append(line.lstrip())
                    continue
                # first handle old content, then start new
                if entry:
                    section.append(parser(" ".join(entry)))
                if section:
                    self._current.entries[section_id] = section
                section_id = content[0]
                section = list()
                entry_id = self._entry_names.get(section_id, False)
                if not entry_id:
                    raise ArgumentError("unrecognised entry: '%s' @ #%d", line,\
                            self._line_number)
                entry = list()
                if section_id == "PROTEIN":
                    parser = self._parse_protein
                elif section_id == "REFERENCE":
                    parser = self._parse_reference
                else:
                    parser = self._parse_generic_entry
            elif content[0] == entry_id:
                if entry:
                    section.append(parser(" ".join(entry)))
                entry = content[1:]
            elif content[0] == "///":
                # end one enzyme entry
                if entry:
                    section.append(parser(" ".join(entry)))
                if section:
                    self._current.entries[section_id] = section
                self._current = None
            else:
                entry.append(line.lstrip())
        # convert to normal dictionary again
        res =  dict(self.enzymes)
        res["file_encoding"] = self._encoding
        self._progress.close()
        return res

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
        return Entry(text.strip(), organisms, references, information,\
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
        return EntryComment(text.strip(), organisms, references)

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
        self._current.organisms[organism] = Organism(text.strip(),
                identifier, references, information, comment)

    def _parse_reference(self, text):
        """

        """
        pass

