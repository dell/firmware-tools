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


"""
Firmware-tools: update infrastructure for firmware
"""

import ConfigParser
import fcntl
import glob
import logging
import logging.config
import os
import sys

from trace_decorator import decorate, traceLog, getLog
import errors
import repository

#import config
import plugins

def mkselfrelpath(*args):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), *args))

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=mkselfrelpath("..", "etc")
PYTHONDIR=mkselfrelpath("..")
PKGPYTHONDIR=mkselfrelpath("..", "firmwaretools")
PKGDATADIR=mkselfrelpath("..", "ft-cli")
DATADIR=mkselfrelpath("..", "ft-cli")
PKGCONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

PID_FILE = '/var/run/ft.pid'

class confObj(object):
    def __getattribute__(self, name):
        return object.__getattribute__(self, name.lower())
    def __setattr__(self, name, value):
        object.__setattr__(self, name.lower(), value)

decorate(traceLog())
def callCB(cb, *args, **kargs):
    if cb is None: return
    try:
        return cb(*args, **kargs)
    except TypeError:
        pass

class Callback(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kargs):
        func = getattr(self, kargs.get("what", "UNKNOWN"), None)
        if func is not None:
            return func(*args, **kargs)

class FtBase(object):
    """This is a primary structure and base class. It houses the objects and
       methods needed to perform most things . It is almost an abstract
       class in that you will need to add your own class above it for most
       real use."""

    def __init__(self):
        self.logger = getLog()
        self.verbose_logger = getLog(prefix="verbose.")

        self.cmdargs = []
        self.cb = None

        self._conf = None
        self._repo = None
        self._systemInventory = None

        self.verbosity = 0
        self.trace = 0
        self.loggingConfig = os.path.join(PKGCONFDIR, "firmware.conf")

        self._bootstrapFuncs = {}
        self._inventoryFuncs = {}

        # Start with plugins disabled
        self.disablePlugins()

    def _getConfig(self, cfgFiles=None, pluginTypes=(plugins.TYPE_CORE, plugins.TYPE_INVENTORY, plugins.TYPE_BOOTSTRAP), optparser=None, disabledPlugins=None):
        if self._conf is not None:
            return self._conf

        if cfgFiles is None:
            cfgFiles = [os.path.join(PKGCONFDIR, "firmware.conf"),]

        if disabledPlugins is None:
            disabledPlugins = []

        self.conf = confObj()

        self.setupLogging(self.loggingConfig, self.verbosity, self.trace)

        self.setConfFromIni(cfgFiles)

        self.conf.uid = os.geteuid()

        self.doPluginSetup(optparser, pluginTypes, disabledPlugins)

        return self._conf


    def setupLogging(self, configFile, verbosity=1, trace=0):
        # set up logging
        logging.config.fileConfig(configFile)
        root_log       = logging.getLogger()
        ft_log         = logging.getLogger("firmwaretools")
        ft_verbose_log = logging.getLogger("verbose")
        ft_trace_log   = logging.getLogger("trace")

        ft_log.propagate = 0
        ft_trace_log.propagate = 0
        ft_verbose_log.propagate = 0

        if verbosity >= 1:
            ft_log.propagate = 1
        if verbosity >= 2:
            ft_verbose_log.propagate = 1
        if verbosity >= 3:
            for hdlr in root_log.handlers:
                hdlr.setLevel(logging.DEBUG)
        if trace:
            ft_trace_log.propagate = 1

    decorate(traceLog())
    def setConfFromIni(self, cfgFiles):
        defaults = {
            "sysconfdir": SYSCONFDIR,
            "pythondir": PYTHONDIR,
            "datadir": DATADIR,
            "pkgpythondir": PKGPYTHONDIR,
            "pkgdatadir": PKGDATADIR,
            "pkgconfdir": PKGCONFDIR,
        }
        self._ini = ConfigParser.SafeConfigParser(defaults)
        for i in cfgFiles:
            self._ini.read(i)

        mapping = {
            # conf.WHAT    : (iniSection, iniOption, default)
            "storageTopdir": ('main', 'storage_topdir', "%s/firmware" % DATADIR),
            "pluginSearchPath": ('main', 'plugin_search_path', os.path.join(PKGDATADIR, "plugins")),
            "pluginConfDir": ('main', 'plugin_config_dir', os.path.join(PKGCONFDIR, "firmware.d")),
            "rpmMode": ('main', 'rpm_mode', "manual"),
        }
        for key, val in mapping.items():
            if self._ini.has_option( val[0], val[1] ):
                setattr(self.conf, key, self._ini.get(val[0], val[1]))
            else:
                setattr(self.conf, key, val[2])

        # read plugin configs
        for i in glob.glob( "%s/*.conf" % self.conf.pluginConfDir ):
            self._ini.read(i)

    decorate(traceLog())
    def listPluginsFromIni(self):
        return [x[len("plugin:"):] for x in self._ini.sections() if x.startswith("plugin:")]

    decorate(traceLog())
    def getPluginConfFromIni(self, plugin):
        section = "plugin:%s" % plugin
        conf = confObj()

        conf.module = None
        conf.enabled = False
        conf.search = None

        for i in self._ini.options(section):
            setattr(conf, i, self._ini.get(section, i))

        #required ("enabled", "module"):
        if getattr(conf, "module", None) is None:
            conf.enabled = False

        return conf

    # called early so no tracing.
    def disablePlugins(self):
        '''Disable plugins
        '''
        self.plugins = plugins.DummyPlugins()

    decorate(traceLog())
    def doPluginSetup(self, optparser=None, pluginTypes=None, disabledPlugins=None):
        if isinstance(self.plugins, plugins.Plugins):
            raise RuntimeError("plugins already initialised")

        self.plugins = plugins.Plugins(self, optparser, pluginTypes, disabledPlugins)

    decorate(traceLog())
    def _getRepo(self):
        if self._repo is not None:
            return self._repo

        self._repo = repository.Repository( self.conf.storageTopdir )
        return self._repo

    decorate(traceLog())
    def _getInventory(self):
        if self._systemInventory is not None:
            return self._systemInventory

        self._systemInventory = repository.SystemInventory()
        self.plugins.run("preinventory")
        for name, func in self._inventoryFuncs.items():
            self.verbose_logger.info("running inventory for module: %s" % name)
            callCB(self.cb, who="populateInventory", what="call_func", func=func)
            for dev in func(self, cb=self.cb):
                callCB(self.cb, who="populateInventory", what="got_device", device=dev)
                self._systemInventory.addDevice(dev)

        return self._systemInventory

    decorate(traceLog())
    def calculateUpgradeList(self, cb=None):
        saveCb = self.cb
        self.cb = cb
        try:
            for candidate in self.repo.iterPackages(cb=cb):
                self.systemInventory.addAvailablePackage(candidate)

            self.systemInventory.calculateUpgradeList(cb)
        finally:
            self.cb = saveCb

        return self.systemInventory

    # properties so they auto-create themselves with defaults
    repo = property(fget=lambda self: self._getRepo(),
                     fset=lambda self, value: setattr(self, "_repo", value))
    conf = property(fget=lambda self: self._getConfig(),
                    fset=lambda self, value: setattr(self, "_conf", value),
                    fdel=lambda self: setattr(self, "_conf", None))
    systemInventory = property(
                    fget=lambda self: self._getInventory(),
                     fset=lambda self, value: setattr(self, "_systemInventory", value),
                    fdel=lambda self: setattr(self, "_systemInventory", None))

    decorate(traceLog())
    def lock(self):
        if self.conf.uid == 0:
            self.runLock = open(PID_FILE, "a+")
            try:
                fcntl.lockf(self.runLock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError, e:
                raise errors.LockError, "unable to obtain exclusive lock."

    decorate(traceLog())
    def unlock(self):
        if self.conf.uid == 0:
            fcntl.lockf(self.runLock.fileno(), fcntl.LOCK_UN)
            os.unlink(PID_FILE)


    decorate(traceLog())
    def registerBootstrapFunction(self, name, function):
        self._bootstrapFuncs[name] = function

    decorate(traceLog())
    def yieldBootstrap(self):
        self.plugins.run("prebootstrap")
        for name, func in self._bootstrapFuncs.items():
            self.verbose_logger.info("running bootstrap for module: %s" % name)
            for i in func():
                yield i

    decorate(traceLog())
    def registerInventoryFunction(self, name, function):
        self._inventoryFuncs[name] = function

    decorate(traceLog())
    def yieldInventory(self, cb=None):
        saveCb = self.cb
        try:
            self.cb = cb
            for dev in self.systemInventory.iterDevices():
                yield dev
        except:
            self.cb = saveCb
            raise


