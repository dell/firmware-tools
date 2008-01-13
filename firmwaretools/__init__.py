#!/usr/bin/python -tt
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
Firmware-tools: update infrastructure for firmware
"""

import ConfigParser
import logging
import os
import sys

from trace_decorator import decorate, traceLog, getLog
import errors
import constants

#import config
import plugins

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..","etc")
PYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
PKGPYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..","firmwaretools")
PKGDATADIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
DATADIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..","ft-cli")
CONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

class FtBase(object):
    """This is a primary structure and base class. It houses the objects and
       methods needed to perform most things . It is almost an abstract
       class in that you will need to add your own class above it for most
       real use."""
    
    def __init__(self):
        self.logger = getLog()
        self.verbose_logger = getLog(prefix="verbose.")

        self._conf = None
        self._repo = None

        # Start with plugins disabled
        self.disablePlugins()


    def _getConfig(self, cfgFiles=None, pluginTypes=(plugins.TYPE_CORE,), optparser=None, disabledPlugins=None):
        if self._conf is not None:
            return self._conf

        if cfgFiles is None:
            cfgFiles = [os.path.join(CONFDIR, "firmware.conf"),]

        if disabledPlugins is None:
            disabledPlugins = []

        class foo: pass
        self.conf = foo()

        self.setupLogging()

        self.setConfFromIni(cfgFiles)

        self.conf.uid = os.geteuid()

        self.doPluginSetup(optparser, pluginTypes, disabledPlugins)


    def setupLogging(self):
        # set up logging
        logging.config.fileConfig(self.opts.configFiles[0])
        root_log       = logging.getLogger()
        ft_log         = logging.getLogger("firmwaretools")
        ft_verbose_log = logging.getLogger("verbose")
        ft_trace_log   = logging.getLogger("trace")

        ft_log.propagate = 0
        ft_trace_log.propagate = 0
        ft_verbose_log.propagate = 0

        if self.opts.verbosity >= 1:
            ft_log.propagate = 1
        if self.opts.verbosity >= 2:
            ft_verbose_log.propagate = 1
        if self.opts.verbosity >= 3:
            for hdlr in root_log.handlers:
                hdlr.setLevel(logging.DEBUG)
        if self.opts.trace:
            ft_trace_log.propagate = 1

    decorate(traceLog())
    def setConfFromIni(self, cfgFiles):
        defaults = { 
            "sysconfdir": SYSCONFDIR, 
            "pythondir": PYTHONDIR, 
            "pkgpythondir": PKGPYTHONDIR, 
            "pkgdatadir": PKGDATADIR, 
            "confdir": CONFDIR, 
        } 
        self._ini = ConfigParser.SafeConfigParser(defaults) 
        for i in cfgFiles:
            self._ini.read(i)

        mapping = {
            # conf.WHAT    : (iniSection, iniOption, default)
            "storageTopdir": ('main', 'storage_topdir', PKGDATADIR),
            "pluginConfDir": ('main', 'plugin_config_dir', os.path.join(CONFDIR, "firmware.d")),
            "rpmMode": ('main', 'rpm_mode', "manual"),
        }
        for key, val in mapping.items():
            if self._ini.has_option( val[0], val[1] ):
                setattr(self.conf, key, self._ini.get(val[0], val[1]))
            else:
                setattr(self.conf, key, val[2])

    decorate(traceLog())
    def listPluginsFromIni(self):
        return [x[len("plugin:"):] for x in self._ini.sections() if x.startswith("plugin:")]

    decorate(traceLog())
    def getPluginConfFromIni(self, plugin):
        section = "plugin:%s" % plugin
        class foo(object): pass
        conf = foo()

        for i in self._ini.options(section):
            setattr(conf, i, self._ini.get(section, i))

        #required ("enabled", "module"):
        if getattr(conf, "module", None) is None:
            conf.module = None
            conf.enabled = False

        if getattr(conf, "enabled", None) is None:
            conf.enabled = False

        return conf

    def disablePlugins(self):
        '''Disable plugins
        '''
        self.plugins = plugins.DummyPlugins()
    
    decorate(traceLog())
    def doPluginSetup(self, optparser=None, pluginTypes=None, disabledPlugins=None):
        if isinstance(self.plugins, plugins.Plugins):
            raise RuntimeError("plugins already initialised")

        self.plugins = plugins.Plugins(self, optparser, pluginTypes, disabledPlugins)

    # properties so they auto-create themselves with defaults
    repo = property(fget=lambda self: self._getRepos(),
                     fset=lambda self, value: setattr(self, "_repos", value),
                     fdel=lambda self: self._delRepos())
    conf = property(fget=lambda self: self._getConfig(),
                    fset=lambda self, value: setattr(self, "_conf", value),
                    fdel=lambda self: setattr(self, "_conf", None))
    
    decorate(traceLog())
    def lock(self):
        if self.conf.uid == 0:
            self.runLock = open(constants.PID_FILE, "a+")
            try:
                fcntl.lockf(self.runLock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError, e:
                raise errors.LockError, "unable to obtain exclusive lock."
            
    decorate(traceLog())
    def unlock(self):
        if self.conf.uid == 0:
            fcntl.lockf(self.runLock.fileno(), fcntl.LOCK_UN)
            os.unlink(PID_FILE)


