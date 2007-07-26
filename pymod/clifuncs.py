# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

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
    plugins = getBootstrapConfig(ini, "")
    for pymod in plugins.get("inventory_plugin", []):
        try:
            module = __import__(pymod, globals(),  locals(), [])
            for package in module.InventoryGenerator():
                yield package

        except (ImportError):
            pass
        except:   # don't let module messups propogate up
            #import traceback
            #traceback.print_exc()
            pass


def runBootstrapInventory(ini):
    plugins = getBootstrapConfig(ini, "bootstrap_")

    for pymod in plugins.get("bootstrap_inventory_plugin", []):
        try:
            module = __import__(pymod, globals(),  locals(), [])
            for pkg in module.BootstrapGenerator():
                yield pkg

        except (ImportError):
            pass
        except:   # don't let module messups propogate up
            #import traceback
            #traceback.print_exc()
            pass


def generateFullSystemInventory(ini):
    plugins = getBootstrapConfig(ini, "")

    for pymod in plugins.get("inventory_plugin", []):
        try:
            module = __import__(pymod, globals(),  locals(), [])
            for pkg in module.InventoryGenerator():
                yield pkg

        except (ImportError):
            pass
        except:   # don't let module messups propogate up
            #traceback.print_exc()
            pass


