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

"""Provide an API to the BRENDA parser."""

from __future__ import absolute_import, division

import logging
import multiprocessing
import re
from warnings import warn

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

import brenda_parser.models as models
from brenda_parser.parsing import BRENDAParser, BRENDALexer

__all__ = ("initialize", "parse")

LOGGER = logging.getLogger(__name__)
EC_PATTERN = re.compile(r"ID\t((\d+)\.(\d+)\.(\d+)\.(\d+))")

Session = sessionmaker()


def init_worker(engine):
    global lexer
    global parser
    global session
    lexer = BRENDALexer(optimize=1)
    parser = BRENDAParser(lexer=lexer, optimize=1)
    session = Session(bind=engine)


def worker(section):
    global parser
    global session
    enzyme = parser.parse(section, session)
    if enzyme is None:
        match = EC_PATTERN.match(section)
        return False, match.group(1)
    else:
        return True, enzyme


def initialize(connection="sqlite:///:memory:"):
    engine = create_engine(connection)
    session = Session(bind=engine)
    models.Base.metadata.create_all(engine, checkfirst=True)
    models.InformationField.preload(session)
    return engine, session


def parse(lines, connection="sqlite:///:memory:", processes=1):
    """
    Parse each section of the BRENDA flat file into an enzyme model.

    Parameters
    ----------
    lines : list
        The BRENDA flat file download as a list of strings.
    connection : str, optional
        An rfc1738 compatible database connection string.
    processes : int, optional
        The number of processes to use.

    Returns
    -------
    Session
        A database session that can be queried using the various data models.

    """
    engine, session = initialize(connection)
    start = 1
    sections = list()
    for i in range(len(lines)):
        if lines[i].startswith("ID"):
            start = i
            continue
        if lines[i].startswith("///"):
            sections.append("".join(lines[start:i + 1]))
    processes = min(processes, len(sections))
    if processes > 1:
        multi_parse(sections, engine, processes=processes)
    else:
        init_worker(engine)
        single_parse(sections)
    return session


def single_parse(sections):
    """

    Parameters
    ----------
    sections

    Returns
    -------

    """
    global parser
    global session
    for section in tqdm(sections):
        enzyme = parser.parse(section, session)
        if enzyme is None:
            match = EC_PATTERN.match(section)
            LOGGER.error("Problem with enzyme '%s'.", match.group(1))
            LOGGER.debug("%s", section)
        else:
            session.add(enzyme)
            session.commit()


def multi_parse(sections, engine, processes=2):
    pool = multiprocessing.Pool(
        processes=processes, initializer=init_worker, initargs=(engine,))
    result_iter = pool.imap_unordered(
        worker, sections, chunksize=len(sections) // processes)
    with tqdm(total=len(sections)) as pbar:
        for success, enzyme in result_iter:
            if success:
                session.add(enzyme)
                session.commit()
            else:
                LOGGER.error("Problem with enzyme '%s'.", enzyme)
            pbar.update()
    pool.close()
    pool.join()
