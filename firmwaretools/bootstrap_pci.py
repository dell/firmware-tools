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
import os
import subprocess

# my stuff
import firmwaretools.package as package
from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

plugin_type = (plugins.TYPE_INVENTORY,)
requires_api_version = "2.0"

# ======
# public API
# ======

def config_hook(conduit, *args, **kargs):
    conduit.getBase().registerInventoryFunction( "bootstrap_pci", PciInventory )

sysfs_pcidevdir="/sys/bus/pci/devices"

decorate(traceLog())
def PciInventory(base=None, cb=None, inventory=None, devdir=sysfs_pcidevdir, *args, **kargs):
    for d in os.listdir(devdir):
        d = makePciDevice(os.path.join(devdir, d))
        if inventory.getDevice(d.uniqueInstance) is None:
            inventory.addDevice(d)

decorate(traceLog())
def getFile(f):
    fd = open(f,"r")
    ret = fd.read()
    fd.close()
    if ret[-1:] == '\n': ret = ret[:-1]
    return ret

decorate(traceLog())
def chomp(s):
    if s.endswith("\n"):
        return s[:-1]
    return s

LSPCI = None
for i in ("/sbin/lspci", "/usr/bin/lspci"):
    if os.path.exists(i):
        LSPCI=i
        break


decorate(traceLog())
def makePciDevice(devDir):
    kargs = {}
    kargs["pciVendor"] = int(getFile(os.path.join(devDir, "vendor")),16)
    kargs["pciDevice"] = int(getFile(os.path.join(devDir, "device")),16)
    kargs["pciSubVendor"] = int(getFile(os.path.join(devDir, "subsystem_vendor")),16)
    kargs["pciSubDevice"] = int(getFile(os.path.join(devDir, "subsystem_device")),16)
    kargs["pciClass"] = int(getFile(os.path.join(devDir, "class")),16)

    name = "pci_firmware(ven_0x%04x_dev_0x%04x" % (kargs["pciVendor"], kargs["pciDevice"])
    if kargs["pciSubVendor"] and kargs["pciSubDevice"]:
        name = name + "_subven_0x%04x_subdev_0x%04x" % (kargs["pciSubVendor"], kargs["pciSubDevice"])
    name = name + ")"

    dirname = os.path.basename(devDir)
    dets = dirname.split(":")
    kargs["pciBDF_Domain"] = int(dets[0],16)
    kargs["pciBDF_Bus"] = int(dets[1],16)
    kargs["pciBDF_Device"] = int(dets[2].split(".")[0],16)
    kargs["pciBDF_Function"] = int(dets[2].split(".")[1],16)

    kargs["pciDbdf"] = (kargs["pciBDF_Domain"], kargs["pciBDF_Bus"], kargs["pciBDF_Device"], kargs["pciBDF_Function"])

    null = open("/dev/null", "w")
    p = subprocess.Popen([LSPCI, "-s", "%02x:%02x:%02x.%x" % kargs["pciDbdf"]], stdout=subprocess.PIPE, stderr=null, stdin=null)
    lspciname = chomp(p.communicate()[0])
    null.close()

    if lspciname is not None and len(lspciname) > 0:
        displayname = lspciname
    else:
        displayname = "unknown device"

    return package.PciDevice(
        name=name,
        version='unknown',
        displayname=displayname,
        lspciname=lspciname,
        **kargs
        )

if __name__ == "__main__":
    for p in getPciDevs():
        print "%s" % p.name

