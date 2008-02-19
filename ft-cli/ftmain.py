#!/usr/bin/python -t
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Copyright 2005 Duke University 

"""
Entrance point for the command line interface.
"""

import sys
import locale
import logging
import signal
import time # test purposes only

from firmwaretools.trace_decorator import decorate, traceLog, getLog
from firmwaretools import errors
from firmwaretools import plugins
import cli

def main(args):
    """This does all the real work"""
    def setDebug():
        import pdb
        pdb.set_trace()

    signal.signal(signal.SIGUSR1,setDebug)

    def exUserCancel():
        logger.critical('Exiting on user cancel')
        sys.exit(1)

    decorate(traceLog())
    def exIOError(e):
        if e.errno == 32:
            logger.critical('Exiting on Broken Pipe')
        else:
            logger.critical(str(e))
        sys.exit(1)

    decorate(traceLog())
    def exPluginExit(e):
        '''Called when a plugin raises PluginExit.

        Log the plugin's exit message if one was supplied.
        '''
        if str(e):
            logger.warn('%s' % e)
        sys.exit(1)

    decorate(traceLog())
    def exFatal(e):
        logger.critical('%s' % e)
        sys.exit(1)


    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error, e:
        # default to C locale if we get a failure.
        print >> sys.stderr, 'Failed to set locale, defaulting to C'
        locale.setlocale(locale.LC_ALL, 'C')
        
    # our core object for the cli
    base = cli.BaseCli()

    logger = getLog()
    verbose_logger = getLog(prefix="verbose.")

    # do our cli parsing and config file setup
    # also sanity check the things being passed on the cli
    try:
        # no logging before this returns.
        base.getOptionsConfig(args)
    except plugins.PluginExit, e:
        exPluginExit(e)
    except errors.BaseError, e:
        exFatal(e)

    lockerr = ""
    while True:
        try:
            base.lock()
        except errors.LockError, e:
            if "%s" %(e.msg,) != lockerr:
                lockerr = "%s" %(e.msg,)
                logger.critical(lockerr)
            logger.critical("Another app is currently holding the lock; waiting for it to exit...")
            time.sleep(2)
        else:
            break

    try:
        result, resultmsgs = base.doCommands()
    except plugins.PluginExit, e:
        exPluginExit(e)
    except errors.BaseError, e:
        result = 1
        resultmsgs = [str(e)]
    except KeyboardInterrupt:
        exUserCancel()
    except IOError, e:
        exIOError(e)

    verbose_logger.info('Complete!')
    base.unlock()
    sys.exit(0)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt, e:
        print >> sys.stderr, "\n\nExiting on user cancel."
        sys.exit(1)
