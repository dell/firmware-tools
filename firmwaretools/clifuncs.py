# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################

from __future__ import generators

import getopt
import glob
import os
import sys
import ConfigParser
import traceback
from trace_decorator import dprint,  decorateAllFunctions

configLocations = [
    "/etc/firmware/firmware.conf",
    "/etc/firmware/firmware.d/*.conf",
    "~/.firmware.conf",
    ]


def getConfig(ini, fileList):
    for i in fileList:
        for j in glob.glob(i):
            if os.path.exists(j):
                ini.read(j)

def getBootstrapConfig(ini, prefix):
    # scan config for 
    #   -- prefix + inventory_ext_plugin
    #   -- prefix + inventory_py_plugin
    pluginConfigNames=( "inventory_plugin", "inventory_plugin_dir" )
    plugins={}
    for sect in ini.sections():
        for opt in pluginConfigNames:
            if ini.has_option(sect, prefix + opt):
                # read/modify/write
                if not ini.get(sect, prefix + opt):
                    continue
                i = plugins.get(prefix + opt, [])
                i.append( ini.get(sect, prefix + opt) )
                plugins[prefix + opt] = i

    # set up python path for plugins
    for path in plugins.get("inventory_plugin_dir", []):
        sys.path.append(path)

    return plugins


def runInventory(ini):
    # returns a list of devices on the system
    return runSomething(ini, "", "inventory_plugin", "InventoryGenerator")

def runBootstrapInventory(ini):
    return runSomething(ini, "bootstrap_", "bootstrap_inventory_plugin", "BootstrapGenerator")

# gets a list of modules and runs a generator function from each module
def runSomething(ini, prefix, pluginName, function):
    plugins = getBootstrapConfig(ini, prefix)

    for pymod in plugins.get(pluginName, []):
        try:
            module = __import__(pymod, globals(),  locals(), [])
            for i in pymod.split(".")[1:]:
                module = getattr(module, i)

            for thing in getattr(module,function)():
                yield thing

        except ImportError, e:
            dprint("module is missing.\n\tModule: %s\n\tFunction: %s\n" % (module, function))
            dprint(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        except AttributeError, e:
            dprint("AttributeError usually means the module is missing the specified function.\n\tModule: %s\n\tFunction: %s\n" % (module, function))
            dprint(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        except:   # don't let module messups propogate up
            dprint(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))


decorateAllFunctions(sys.modules[__name__])
