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

"""Provide a command line interface for the parser."""


import logging
from multiprocessing import cpu_count
from warnings import warn

import click
import click_log

import brenda_parser.api as api
from brenda_parser import __version__


LOGGER = logging.getLogger(__name__.split(".", 1)[0])
click_log.basic_config(LOGGER)

try:
    PROCESSES = cpu_count()
except NotImplementedError:
    warn("Could not detect the number of CPUs - assuming 1.", UserWarning)
    PROCESSES = 1


@click.group()
@click.help_option("--help", "-h")
@click.version_option(__version__, "--version", "-V")
@click_log.simple_verbosity_option(
    LOGGER,
    default="INFO",
    show_default=True,
    type=click.Choice(["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)
def cli():
    """Parse the BRENDA Enzyme flat file distribution to a local database."""
    pass


@cli.command()
@click.help_option("--help", "-h")
@click.option(
    "--filename",
    type=click.Path(exists=False, writable=True),
    default="brenda.db",
    show_default=True,
    help="Path to where the SQLite3 database is stored.",
)
@click.option(
    "--connection",
    default=None,
    show_default=True,
    metavar="URL",
    help="An rfc1738 compatible database URL. Overrides the "
    "filename option.",
)
@click.option(
    "--processes",
    type=int,
    default=PROCESSES,
    show_default=True,
    help="The number of parallel processes to use during parsing.",
)
@click.argument(
    "flat_file", type=click.Path(exists=True, dir_okay=False), envvar="FILENAME"
)
def parse(flat_file, filename, connection, processes):
    if connection is None:
        connection = "sqlite:///{}".format(filename)
    with open(flat_file) as file_handle:
        lines = file_handle.readlines()
    api.parse(lines, connection, processes=processes)
