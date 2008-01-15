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
requires_api_version = "1.0"

moduleLog = getLog()

def config_hook(conduit, *args, **kargs):
    conduit.getOptParser().addEarlyParse("--update")
    conduit.getOptParser().add_option(
        "--update", help="Update the system's firmware.",
        action="store_const", const="update", dest="mode")
    conduit.getBase().registerCommand(UpdateCommand())

class UpdateCommand(ftcommands.YumCommand):
    decorate(traceLog())
    def getModes(self):
        return ['update']

    decorate(traceLog())
    def addSubOptions(self, base, mode, cmdline, processedArgs):
        base.optparser.add_option("--rpm", action="store_true", dest="rpmMode", default=False, help="Used when running as part of an rpm \%post script.")
        base.optparser.add_option("--yes", "-y", action="store_const", const=0, dest="interactive", default=1, help="Default all answers to 'yes'.")
        base.optparser.add_option("--test", "-t", action="store_const", const=2, dest="interactive", help="Perform test but do not actually update.")

    decorate(traceLog())
    def doCommand(self, base, mode, cmdline, processedArgs):
        if base.opts.rpmMode:
            if base.conf.rpmMode != 'auto':
                print "Config does not specify automatic install during package install."
                print "Please run update_firmware manually to install updates."
                return [0, "Done"]

        base.updateFirmware()
        return [0, "Done"]

