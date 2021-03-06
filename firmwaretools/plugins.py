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

import atexit
import gettext
import sys

from trace_decorator import decorate, traceLog, getLog
import errors

API_VERSION = '2.0'

# plugin can raise this to disable plugin during load
class DisablePlugin(ImportError): pass

NEXT_AVAIL_TYPE_NUM = 0
def registerPluginType(name):
    global NEXT_AVAIL_TYPE_NUM
    globals()[name] = NEXT_AVAIL_TYPE_NUM
    NEXT_AVAIL_TYPE_NUM = NEXT_AVAIL_TYPE_NUM + 1

# Plugin types
registerPluginType("TYPE_CORE")
registerPluginType("TYPE_INVENTORY")

registerPluginType("TYPE_CLI")

# testing types
registerPluginType("TYPE_MOCK_CORE")
registerPluginType("TYPE_MOCK_INVENTORY")

# all the 'normal' types
ALL_TYPES = (TYPE_CORE, TYPE_INVENTORY)

SLOT_TO_CONDUIT = {}
def registerSlotToConduit(slot, conduit):
    global SLOT_TO_CONDUIT
    SLOT_TO_CONDUIT[slot] = conduit

registerSlotToConduit('config', 'PluginConduit')
registerSlotToConduit('preinventory', 'PluginConduit')
registerSlotToConduit('inventory', 'PluginConduit')
registerSlotToConduit('postinventory', 'PluginConduit')
registerSlotToConduit('close', 'PluginConduit')

moduleLog = getLog()
moduleLogVerbose = getLog(prefix="verbose.")

class PluginExit(Exception):
    '''Used by plugins to signal to stop
    '''
    def __init__(self, value="", translation_domain=""):
        self.value = value
        self.translation_domain = translation_domain
    def __str__(self):
        if self.translation_domain:
            return gettext.dgettext(self.translation_domain, self.value)
        else:
            return self.value

class Plugins:
    '''
    Manager class for plugins.
    '''

    def __init__(self, base, optparser=None, types=None, disabled=None):
        '''Initialise the instance.
        '''
        self.base = base
        self.optparser = optparser
        self.cmdline = (None, None)

        self.verbose_logger = getLog(prefix="verbose.")

        self.disabledPlugins = disabled
        if types is None:
            types = ALL_TYPES
        if not isinstance(types, (list, tuple)):
            types = (types,)

        # TODO: load plugins here
        self._plugins = {}
        for i in self.base.listPluginsFromIni():
            conf = self.base.getPluginConfFromIni(i)
            moduleLogVerbose.info( "Checking Plugin (%s)" % i )
            if conf.enabled:
                self._loadModule(i, conf, types)

        # Call close handlers when yum exit's
        #atexit.register(self.run, 'close')

        # Let plugins register custom config file options
        self.run('config')

    decorate(traceLog())
    def _loadModule(self, pluginName, conf, types):
        # load plugin
        try:
            savePath = sys.path
            sys.path.insert(0,self.base.conf.pluginSearchPath)
            if conf.search is not None:
                sys.path.insert(0, conf.search)
            module = __import__(conf.module, globals(),  locals(), [])
            sys.path = savePath
        except DisablePlugin:
            moduleLogVerbose.info("\tPlugin raised DisablePlugin exception. skipping.")
            return
        except ImportError, e:
            sys.path = savePath
            raise errors.ConfigError(
                'Plugin "%s" cannot be loaded: %s' % (conf.module, e))

        for i in conf.module.split(".")[1:]:
            module = getattr(module, i)

        # Check API version required by the plugin
        if not hasattr(module, 'requires_api_version'):
            raise errors.ConfigError(
                'Plugin "%s" doesn\'t specify required API version' % conf.module
                )

        if not apiverok(API_VERSION, module.requires_api_version):
            raise errors.ConfigError(
                'Plugin "%s" requires API %s. Supported API is %s.' % (
                    conf.module,
                    module.requires_api_version,
                    API_VERSION,
                    ))

        # Check plugin type against filter
        plugintypes = getattr(module, 'plugin_type', None)
        if plugintypes is None:
             raise errors.ConfigError(
                'Plugin "%s" doesn\'t specify plugin type' % pluginName
                )
        if not isinstance(plugintypes, (list, tuple)):
            plugintypes = (plugintypes,)
        for plugintype in plugintypes:
            if plugintype not in types:
                moduleLogVerbose.info("\tPlugin %s not loaded: doesnt match load type (%s)" % (pluginName, plugintypes))
                return
        # Check if this plugin has been temporary disabled
        if self.disabledPlugins:
            if pluginName in self.disabledPlugins:
                moduleLogVerbose.info("\tPlugin %s not loaded: disabled" % pluginName)
                return

        moduleLogVerbose.info("\tLoaded %s plugin" % pluginName)
        self._plugins[pluginName] = {"conf": conf, "module": module}

    decorate(traceLog())
    def listLoaded(self):
        return self._plugins.keys()

    decorate(traceLog())
    def run(self, slotname, *args, **kargs):
        '''Run all plugin functions for the given slot.
        '''
        # Determine handler class to use
        conduitcls = SLOT_TO_CONDUIT.get(slotname, None)
        if conduitcls is None:
            raise ValueError('unknown slot name "%s"' % slotname)
        conduitcls = eval(conduitcls)       # Convert name to class object

        for pluginName, dets in self._plugins.items():
            module = dets['module']
            conf = dets['conf']
            hook = "%s_hook" % slotname
            if hasattr(module, hook):
                getattr(module, hook)(conduitcls(self, self.base, conf), *args, **kargs)


class DummyPlugins:
    '''
    This class provides basic emulation of the YumPlugins class. It exists so
    that calls to plugins.run() don't fail if plugins aren't in use.
    '''
    decorate(traceLog())
    def run(self, *args, **kwargs):
        pass

    decorate(traceLog())
    def setCmdLine(self, *args, **kwargs):
        pass

class PluginConduit(object):
    decorate(traceLog())
    def __init__(self, parent, base, conf):
        self._parent = parent
        self._base = base
        self._conf = conf

        self.logger = getLog()
        self.verbose_logger = getLog(prefix="verbose.")

    decorate(traceLog())
    def info(self, msg):
        self.verbose_logger.info(msg)

    decorate(traceLog())
    def error(self, msg):
        self.logger.error(msg)

    decorate(traceLog())
    def getVersion(self):
        import firmwaretools
        return firmwaretools.__version__

    decorate(traceLog())
    def getOptParser(self):
        '''Return the optparse.OptionParser instance for this execution of Yum

        In the "config" slot a plugin may add extra options to this
        instance to extend the command line options that Yum exposes.

        In all other slots a plugin may only read the OptionParser instance.
        Any modification of the instance at this point will have no effect.

        @return: the global optparse.OptionParser instance used by Yum. May be
            None if an OptionParser isn't in use.
        '''
        return self._parent.optparser

    decorate(traceLog())
    def getBase(self):
        return self._base

    decorate(traceLog())
    def getConf(self):
        return self._conf

decorate(traceLog())
def parsever(apiver):
    maj, min = apiver.split('.')
    return int(maj), int(min)

decorate(traceLog())
def apiverok(a, b):
    '''Return true if API version "a" supports API version "b"
    '''
    a = parsever(a)
    b = parsever(b)

    if a[0] != b[0]:
        return 0

    if a[1] >= b[1]:
        return 1

    return 0
