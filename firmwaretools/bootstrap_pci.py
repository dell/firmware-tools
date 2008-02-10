# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""module

some docs here eventually.
"""

from __future__ import generators

# import arranged alphabetically
import logging
import os
import re
import sys

# my stuff
import firmwaretools.package as package
from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

plugin_type = (plugins.TYPE_BOOTSTRAP, plugins.TYPE_INVENTORY)
requires_api_version = "2.0"

# ======
# public API
# ======

def config_hook(conduit, *args, **kargs):
    conduit.getBase().registerBootstrapFunction( "bootstrap_pci", getPciDevs )


sysfs_pcidevdir="/sys/bus/pci/devices"

decorate(traceLog())
def getPciDevs(devdir=sysfs_pcidevdir, *args, **kargs):
    for d in os.listdir(devdir):
        yield makePciDevice(os.path.join(devdir, d))

decorate(traceLog())
def getFile(f):
    fd = open(f,"r")
    ret = fd.read()
    fd.close()
    if ret[-1:] == '\n': ret = ret[:-1]
    return ret

decorate(traceLog())
def makePciDevice(devDir):
    kargs = {}
    kargs["pciVendor"] = int(getFile(os.path.join(devDir, "vendor")),16)
    kargs["pciDevice"] = int(getFile(os.path.join(devDir, "device")),16)
    kargs["pciSubVendor"] = int(getFile(os.path.join(devDir, "subsystem_vendor")),16)
    kargs["pciSubDevice"] = int(getFile(os.path.join(devDir, "subsystem_device")),16)
    kargs["pciClass"] = int(getFile(os.path.join(devDir, "class")),16)

    name = "pci_firmware(ven_0x%x_dev_0x%x" % (kargs["pciVendor"], kargs["pciDevice"])
    if kargs["pciSubVendor"] and kargs["pciSubDevice"]:
        name = name + "_subven_0x%x_subdev_0x%x" % (kargs["pciSubVendor"], kargs["pciSubDevice"])
    name = name + ")"

    dirname = os.path.basename(devDir)
    dets = dirname.split(":")
    kargs["pciBDF_Domain"] = int(dets[0],16)
    kargs["pciBDF_Bus"] = int(dets[1],16)
    kargs["pciBDF_Device"] = int(dets[2].split(".")[0],16)
    kargs["pciBDF_Function"] = int(dets[2].split(".")[1],16)

    kargs["pciDbdf"] = (kargs["pciBDF_Domain"], kargs["pciBDF_Bus"], kargs["pciBDF_Device"], kargs["pciBDF_Function"])

    kargs["pciVendor_txt"] = "unknown vendor"
    kargs["pciDevice_txt"] = "unknown device"
    kargs["pciSubVendor_txt"] = ""
    kargs["pciSubDevice_txt"] = ""
    displayname = "%s %s" % (kargs["pciVendor_txt"], kargs["pciDevice_txt"])

    return package.PciDevice(
        name=name,
        version='unknown',
        displayname=displayname,
        **kargs
        )

if __name__ == "__main__":
    for p in getPciDevs():
        print "%s" % p.name

