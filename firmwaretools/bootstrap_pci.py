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
import re
import sys

# my stuff
import package
from trace_decorator import dprint, decorateAllFunctions

# ======
# public API
# ======
def BootstrapGenerator():
    for i in lspciGeneratorFactory():
        yield(makePciDevice(i))

def InventoryGenerator():
    # this module cannot really inventory anything
    # but this function is overridden in fake mode, so leave it here
    # so that we dont get 
    #   "AttributeError: 'module' object has no attribute 'InventoryGenerator'"
    # errors when running in regular mode.

    # return [] so that we dont get an error up the stack (NoneType not iterable)
    return []

# ======
# private stuff from here down
# ======

vendevRe = re.compile(r'^(.*)\[(\w+)\]')
def splitTextFromNumeric(line):
    match = vendevRe.search(line)
    if match:
        text = match.group(1)
        number = match.group(2)
        return (text, number)
    return None

def makePciDevice(oneDevData):
    kargs = {}
    
    kargs["pciVendor_txt"], kargs["pciVendor"] = splitTextFromNumeric(oneDevData["vendor"])
    kargs["pciDevice_txt"], kargs["pciDevice"] = splitTextFromNumeric(oneDevData["device1"])
    name = "pci_firmware(ven_0x%s_dev_0x%s" % (kargs["pciVendor"], kargs["pciDevice"])
    if oneDevData.has_key("svendor"):
        kargs["pciSubVendor_txt"], kargs["pciSubVendor"] = splitTextFromNumeric(oneDevData["svendor"])
        kargs["pciSubDevice_txt"], kargs["pciSubDevice"] = splitTextFromNumeric(oneDevData["sdevice"])
        name = name + "_subven_0x%s_subdev_0x%s" % (kargs["pciSubVendor"], kargs["pciSubDevice"])
    name = name + ")"

    displayname = "%s %s" % (kargs["pciVendor_txt"], kargs["pciDevice_txt"])
    if kargs.has_key("pciSubVendor_txt"):
        if (not kargs["pciSubVendor_txt"].lower().startswith("unknown") and
                not kargs["pciSubDevice_txt"].lower().startswith("unknown")):
            displayname = "%s %s" % (kargs["pciSubVendor_txt"], kargs["pciSubDevice_txt"])

    kargs["pciBDF_Domain"], kargs["pciBDF_Bus"], devfun = oneDevData["device0"].split(":")
    kargs["pciBDF_Domain"] = int(kargs["pciBDF_Domain"],16)
    kargs["pciBDF_Bus"] = int(kargs["pciBDF_Bus"],16)
    kargs["pciBDF_Device"], kargs["pciBDF_Function"] = [int(i,16) for i in devfun.split(".")]
    kargs["pciClass"] = splitTextFromNumeric(oneDevData["class"])[1]
    kargs["pciDbdf"] = (kargs["pciBDF_Domain"], kargs["pciBDF_Bus"], kargs["pciBDF_Device"], kargs["pciBDF_Function"])

    return package.PciDevice(
        name=name,
        version='unknown', 
        displayname=displayname,
        **kargs
        )

# overridden by unit test code.
mockReadLspciWithDomain = os.popen
mockReadLspciWithoutDomain = os.popen

def lspciGenerator():
    for i in ("/sbin/lspci", "/usr/bin/lspci"):
        if os.path.exists(i):
            lspciPath=i
            break

    oneDevData = {}

    fd = mockReadLspciWithDomain("%s -nn -m -v -D 2>/dev/null" % lspciPath, "r")
    deviceNum=0
    for line in fd:
        if not line.strip():
            deviceNum=0
            yield oneDevData
            oneDevData = {}
            continue

        name,value = line.split(":", 1)
        name = name.strip().lower()
        value = value.strip()
        if name == "device":
            name = "device%s" % deviceNum
            deviceNum = deviceNum + 1
        oneDevData[name] = value
    err = fd.close()
    
    if err:
        # if LSPCI doesnt support -D (print PCI Domain) option.
        fd = mockReadLspciWithoutDomain("%s -nn -m -v -D 2>/dev/null" % lspciPath, "r")
        for line in fd:
            if not line.strip():
                yield oneDevData
                oneDevData = {}
    
            name,value = line.split(":")
            if name.strip().lower() == ("device"):
                # fake domain if not present
                if len(value.strip().split(":")) > 2:
                    value = "0000:" + value.strip() 
            oneDevData[name.strip().lower()] = value.strip()
        fd.close()
    


# returns a generator function
def lspciGeneratorFactory():
    return lspciGenerator()

decorateAllFunctions(sys.modules[__name__])

if __name__ == "__main__":
    for pkg in BootstrapGenerator():
        print "%s: %s" % (pkg.name, str(pkg))

