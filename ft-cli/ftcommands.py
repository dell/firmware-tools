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
#
# Copyright (C) 2008 Dell Inc.
#  by Michael Brown <Michael_E_Brown@dell.com>
#
# Based in part on design and code in Yum 3.2:
# Copyright 2006 Duke University 
# Written by Seth Vidal

"""
Classes for subcommands of the yum command line interface.
"""

from firmwaretools.trace_decorator import decorate, traceLog, getLog

moduleLog = getLog()

class YumCommand(object):
        
    def getModes(self):
        return []

    def doCheck(self, base, mode, cmdline, processedArgs):
        pass

    def addSubOptions(self, base, mode, cmdline, processedArgs):
        pass

    def doCommand(self, base, mode, cmdline, processedArgs):
        """
        @return: (exit_code, [ errors ]) where exit_code is:
           0 = we're done, exit
           1 = we've errored, exit with error string
        """
        return 0, ['Nothing to do']
    

