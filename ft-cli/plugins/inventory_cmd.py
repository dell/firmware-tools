# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

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
#
# Copyright (C) 2008 Dell Inc.
#  by Michael Brown <Michael_E_Brown@dell.com>

"""
Classes for subcommands of the yum command line interface.
"""

import sys

import firmwaretools.pycompat
from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

import ftcommands
import cli

plugin_type = (plugins.TYPE_CLI,)
requires_api_version = "2.0"

moduleLog = getLog()

def config_hook(conduit, *args, **kargs):
    conduit.getOptParser().addEarlyParse("--inventory")
    conduit.getOptParser().add_option(
            "--inventory", help="List system inventory", 
            action="store_const", const="inventory", 
            dest="mode", default=None)
    conduit.getBase().registerCommand(InventoryCommand())

class InventoryCommand(ftcommands.YumCommand):
    decorate(traceLog())
    def getModes(self):
        return ['inventory']

    decorate(traceLog())
    def addSubOptions(self, base, mode, cmdline, processedArgs):
        base.optparser.add_option(
            "--show-unknown", help="Show unknown devices.", 
            action="store_true", dest="show_unknown", default=False)

    decorate(traceLog())
    def doCommand(self, base, mode, cmdline, processedArgs):
        sys.stderr.write("Wait while we inventory system:\n")

        headerWasPrinted=False
        for pkg in base.yieldInventory(cb=cli.mycb({})):
            if not headerWasPrinted:
                sys.stderr.write(firmwaretools.pycompat.clearLine())
                sys.stderr.write("System inventory:\n")
                sys.stderr.flush()
                headerWasPrinted = True

            if pkg.version == "unknown" and not base.opts.show_unknown :
                continue

            print("\t%s = %s" % (str(pkg), pkg.version))

        return [0, "Done"]

