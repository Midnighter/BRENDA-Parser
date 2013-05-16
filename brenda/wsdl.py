# -*- coding: utf-8 -*-


"""
=====================
Querying WSDL Servers
=====================

:Authors:
    Moritz Emanuel Beber
:Date:
    2012-06-02
:Copyright:
    Copyright(c) 2012 Jacobs University of Bremen. All rights reserved.
:File:
    wsdl.py
"""


__all__ = ["ThreadedWSDLFetcher"]


import logging
import threading

from .. import miscellaneous as misc

#TODO: make a rewrite using ZSI

SOAPpy = misc.load_module("SOAPpy", url="http://pywebsvcs.sourceforge.net/")


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(misc.NullHandler())


class ThreadedWSDLFetcher(threading.Thread):
    """
    A Thread class that fetches instructions from the queue passed to the
    constructor and queries the given WSDL server attaching the result to a
    given list.

    Notes
    -----
    Requires SOAPpy and an active internet connection.
    """
    def __init__(self, queue, wsdl, group=None, target=None, name=None, *args,
            **kw_args):
        """
        Parameters
        ----------
        queue: Queue.Queue
            Task queue that contains triples of a string with the function name
            to be queried on the WSDL server, the query string, and the
            container (list) to attach results to.
        wsdl: str
            URL of the WSDL server.
        The remaining parameters are the same as for the threading.Thread class.
        """
        threading.Thread.__init__(self, group=group, target=target, name=name,
                args=args, kwargs=kw_args)
        # establish connection to DBGET server
        self._srvr = SOAPpy.WSDL.Proxy(wsdl)
        self._queue = queue
        self._lock = threading.Lock()

    def run(self):
        """
        Extracts tasks from a given queue that contains triples of a string
        with the function name to be queried on the WSDL server, the query
        string, and the container (list) to attach results to.
        """
        while True:
            (function, item, output) = self._queue.get()
            try:
                info = eval("self._srvr.%s(item)" % function)
            except StandardError:
                LOGGER.debug("psssst:", exc_info=True)
            else:
                if info:
                    self._lock.acquire()
                    output.append((item, info))
                    self._lock.release()
                else:
                    LOGGER.warn("No information for '%s'.", item)
            finally:
                self._queue.task_done()

