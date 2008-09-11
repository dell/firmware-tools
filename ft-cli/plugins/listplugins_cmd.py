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

from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

import ftcommands

plugin_type = (plugins.TYPE_CLI,)
requires_api_version = "2.0"

moduleLog = getLog()

def config_hook(conduit, *args, **kargs):
    conduit.getOptParser().addEarlyParse("--listplugins")
    conduit.getOptParser().add_option(
        "--listplugins", action="store_const", const="listplugins", 
        dest="mode", help="list available plugins.")
    conduit.getBase().registerCommand(ListPluginsCommand())

class ListPluginsCommand(ftcommands.YumCommand):
    decorate(traceLog())
    def getModes(self):
        return ['listplugins']

    decorate(traceLog())
    def doCommand(self, base, mode, cmdline, processedArgs):
        print("Available Plugins:")
        for p in base.listPluginsFromIni():
            print("\t%s" % p)

        print("Loaded Plugins:")
        for p in base.plugins.listLoaded():
            print("\t%s" % p)

        return [0, "Done"]


