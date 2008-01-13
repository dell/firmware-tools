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
# Written by Seth Vidal

"""
Command line interface class and related.
"""

import os
import re
import sys
import time
import random
import logging

from optparse import OptionParser

import firmwaretools
import firmwaretools.plugins as plugins
from firmwaretools.trace_decorator import decorate, traceLog, getLog

from firmwaretools.i18n import _
import signal
import ftcommands
from firmwaretools import errors

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=os.path.join(os.path.dirname(os.path.realpath(sys._getframe(0).f_code.co_filename)),"..","etc")
PYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
PKGPYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..","firmwaretools")
PKGDATADIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
CONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

def sigquit(signum, frame):
    """ SIGQUIT handler for the cli. """
    print >> sys.stderr, "Quit signal sent - exiting immediately"
    sys.exit(1)

class CliError(errors.BaseError): pass

class BaseCli(firmwaretools.FtBase):
    """This is the base class for cli.
       Inherits from FtBase """
       
    def __init__(self):
        # handle sigquit early on
        signal.signal(signal.SIGQUIT, sigquit)
        firmwaretools.FtBase.__init__(self)
        logging.basicConfig()

        self.logger = getLog()
        self.verbose_logger = getLog(prefix="verbose.")

        self.cli_commands = {}
        self.registerCommand(ftcommands.UpdateCommand())
        self.registerCommand(ftcommands.InventoryCommand())
        self.registerCommand(ftcommands.BootstrapCommand())
        self.registerCommand(ftcommands.ListPluginsCommand())

    def registerCommand(self, command):
        for name in command.getModes():
            if self.cli_commands.has_key(name):
                raise errors.ConfigError('Command "%s" already defined' % name)
            self.cli_commands[name] = command
            
    def getOptionsConfig(self, args):
        """parses command line arguments, takes cli args:
        sets up self.conf and self.cmds as well as logger objects 
        in base instance"""
        

        self.optparser = FtOptionParser(
            usage='yum [options] < %s >' % (', '.join(self.cli_commands)))

        
        # Parse only command line options that affect basic yum setup
        self.opts = self.optparser.firstParse(args)

        # Read up configuration options and initialise plugins
        try:
            self._getConfig(self.opts.configFiles, 
                    pluginTypes=(plugins.TYPE_CORE, plugins.TYPE_INTERACTIVE),
                    optparser=self.optparser,
                    disabledPlugins=self.opts.disabled_plugins)
                    
        except errors.ConfigError, e:
            self.logger.critical(_('Config Error: %s'), e)
            sys.exit(1)
        except ValueError, e:
            self.logger.critical(_('Options Error: %s'), e)
            sys.exit(1)

        # update usage in case plugins have added commands
        self.optparser.set_usage('ft [options] < %s >''' % (
            ', '.join(self.cli_commands)))

        self.opts, self.args = self.optparser.parse_args(args)

        # Now parse the command line for real and 
        # apply some of the options to self.conf
        #(self.opts, self.args) = self.optparser.setupYumConfig()

        self.parseCommands()

        
    def parseCommands(self):
        """reads self.cmds and parses them out to make sure that the requested 
        base command + argument makes any sense at all""" 

        
        if not self.cli_commands.has_key(self.opts.mode):
            self.usage()
            raise CliError, "mode not specified."
    
        self.cli_commands[self.opts.mode].doCheck(self, self.opts.mode, self.args)

    def doShell(self):
        """do a shell-like interface for commands"""
        pass

    def doCommands(self):
        """
        Calls the base command passes the extended commands/args out to be
        parsed (most notably package globs).
        
        Returns a numeric result code and an optional string
           - 0 = we're done, exit
           - 1 = we've errored, exit with error string
           - 2 = we've got work yet to do, onto the next stage
        """
        
        return self.cli_commands[self.opts.mode].doCommand(self, self.opts.mode, self.args)
    

    def usage(self):
        ''' Print out command line usage '''
        self.optparser.print_help()

    def shellUsage(self):
        ''' Print out the shell usage '''
        self.optparser.print_usage()
    

from optparse import OptionParser
class FtOptionParser(OptionParser):
    """Unified cmdline option parsing and config file handling."""
    def __init__(self, *args, **kargs):
        OptionParser.__init__(self, *args, **kargs)
        
        self.add_option("--inventory", help="", action="store_const", const="inventory", dest="mode", default=None)
        self.add_option("--update", help="", action="store_const", const="update", dest="mode")
        self.add_option("--bootstrap", help="", action="store_const", const="bootstrap", dest="mode")
        self.add_option("--listplugins", action="store_const", const="listplugins", dest="mode", help="list available plugins.")


        self.add_option("-c", "--config", help="Override default config file with user-specified config file.", dest="configFiles", action="append", default=[])
        self.add_option("--extra-plugin-config", help="Add additional plugin config file.", action="append", default=[], dest="extraConfigs")
        self.add_option("-v", "--verbose", action="count", dest="verbosity", default=1, help="Display more verbose output.")
        self.add_option("-q", "--quiet", action="store_const", const=0, dest="verbosity", help="Minimize program output. Only errors and warnings are displayed.")
        self.add_option("--trace", action="store_true", dest="trace", default=False, help="Enable verbose function tracing.")
        self.add_option("--fake-mode", action="store_true", dest="fake_mode", default=False, help="Display fake data for unit-testing.")
        self.add_option("--disableplugin", action="append", dest="disabled_plugins", default=[], help="Disable single named plugin.")

        self.parseOptionsFirst_novalopts = ['--version','-q', '-v', "--quiet", "--verbose", "--trace"]
        self.parseOptionsFirst_valopts = ['-c', '--config', '--disableplugin', "--extra-plugin-config"]

    def firstParse(self, args):
        args = _filtercmdline(
            self.parseOptionsFirst_novalopts,
            self.parseOptionsFirst_valopts,
            args)
        opts, args = self.parse_args(args=args)

        if not opts.configFiles:
            opts.configFiles = [os.path.join(CONFDIR, "firmware.conf"), ]

        opts.configFiles = opts.configFiles + opts.extraConfigs

        return opts

def _filtercmdline(novalopts, valopts, args):
    '''Keep only specific options from the command line argument list

    This function allows us to peek at specific command line options when using
    the optparse module. This is useful when some options affect what other
    options should be available.

    @param novalopts: A sequence of options to keep that don't take an argument.
    @param valopts: A sequence of options to keep that take a single argument.
    @param args: The command line arguments to parse (as per sys.argv[:1]
    @return: A list of strings containing the filtered version of args.

    Will raise ValueError if there was a problem parsing the command line.
    '''
    out = []
    args = list(args)       # Make a copy because this func is destructive

    while len(args) > 0:
        a = args.pop(0)
        if '=' in a:
            opt, _ = a.split('=', 1)
            if opt in valopts:
                out.append(a)

        elif a in novalopts:
            out.append(a)

        elif a in valopts:
            if len(args) < 1:
                raise ValueError
            next = args.pop(0)
            if next[0] == '-':
                raise ValueError

            out.extend([a, next])

        else:
            # Check for single letter options that take a value, where the
            # value is right up against the option
            for opt in valopts:
                if len(opt) == 2 and a.startswith(opt):
                    out.append(a)

    return out
