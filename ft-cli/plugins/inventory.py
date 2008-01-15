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

from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

import ftcommands

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
    def doCommand(self, base, mode, cmdline, processedArgs):
        for pkg in base.yieldInventory():
            moduleLog.info("%s = %s" % (str(pkg), pkg.version))

        return [0, "Done"]

