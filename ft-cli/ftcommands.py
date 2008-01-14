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
# Copyright 2006 Duke University 
# Written by Seth Vidal

"""
Classes for subcommands of the yum command line interface.
"""

import os
import firmwaretools.errors
from firmwaretools.i18n import _
from firmwaretools.trace_decorator import decorate, traceLog, getLog

moduleLog = getLog()

class YumCommand(object):
        
    def getModes(self):
        return []

    def getUsage(self):
        return ''
    
    def doCheck(self, base, mode, args):
        pass

    def doCommand(self, base, mode, args):
        """
        @return: (exit_code, [ errors ]) where exit_code is:
           0 = we're done, exit
           1 = we've errored, exit with error string
        """
        return 0, ['Nothing to do']
    

class UpdateCommand(YumCommand):
    def getModes(self):
        return ['update']

    def doCheck(self, base, mode, args):
        pass

    def doCommand(self, base, mode, args):
        return [0, "Hello World"]

class InventoryCommand(YumCommand):
    def getModes(self):
        return ['inventory']

    def doCheck(self, base, mode, args):
        pass

    def doCommand(self, base, mode, args):
        for pkg in base.yieldInventory():
            moduleLog.info("%s = %s" % (str(pkg), pkg.version))

        return [0, "Done"]

class BootstrapCommand(YumCommand):
    def getModes(self):
        return ['bootstrap']

    def doCheck(self, base, mode, args):
        # need to add bootstrap-specific options to optparser
        base.optparser.add_option("-u", "--up2date_mode", action="store_true", dest="comma_separated", default=False, help="Comma-separate values for use with up2date.")
        base.optparser.add_option("-a", "--apt_mode", action="store_true", dest="apt_mode", default=False, help="fixup names so that they are compatible with apt")

    def doCommand(self, base, mode, args):
        parse=str
        if base.opts.apt_mode:
            parse = debianCleanName

        out = ""
        for pkg in base.yieldBootstrap():
            if base.opts.comma_separated:
                out = out + ",%s" % parse(pkg.name)
            else:
                moduleLog.info("%s" % parse(pkg.name))
        
        # strip leading comma:
        out = out[1:]
        if out:
            moduleLog.info(out) 

        return [0, "Done"]

class ListPluginsCommand(YumCommand):
    def getModes(self):
        return ['listplugins']

    def doCheck(self, base, mode, args):
        pass

    def doCommand(self, base, mode, args):
        moduleLog.info("Available Plugins:")
        for p in base.listPluginsFromIni():
            moduleLog.info("\t%s" % p)

        moduleLog.info("Loaded Plugins:")
        for p in base.plugins.listLoaded():
            moduleLog.info("\t%s" % p)

        return [0, "Hello World"]


# used by bootstrap
def debianCleanName(s):
    s = s.replace('_', '-')
    s = s.replace('(', '-')
    s = s.replace(')', '')
    s = s.lower()
    return s

