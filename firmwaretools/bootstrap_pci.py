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
import firmwaretools.trace_decorator
from firmwaretools.trace_decorator import decorateAllFunctions

# set up logging
moduleLog = logging.getLogger("firmwaretools.addon")

# ======
# public API
# ======
def BootstrapGenerator():
    for i in lspciGenerator():
        yield(makePciDevice(i))

def InventoryGenerator():
    # this module cannot really inventory anything
    # but this function is overridden in fake mode, so leave it here
    # so that we dont get 
    #   "AttributeError: 'module' object has no attribute 'InventoryGenerator'"
    # errors when running in regular mode.

    # This needs to return something that is iterable, so return an empty array
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

lspciPath=None
for i in ("/sbin/lspci", "/usr/bin/lspci"):
    if os.path.exists(i):
        lspciPath=i
        break

def lspciGenerator():
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
        # Do it the hard way

        fd = mockReadLspciWithoutDomain("%s -nn -m -v 2>/dev/null" % lspciPath, "r")
        deviceNum=0
        for line in fd:
            if not line.strip():
                deviceNum=0
                yield supplementOldLspciFormat(oneDevData)
                oneDevData = {}
                continue
    
            name,value = line.split(":", 1)
            name = name.strip().lower()
            value = value.strip()
            if name == ("device"):
                name = "device%s" % deviceNum
                deviceNum = deviceNum + 1
                # fake domain if not present
            if name == ("device0"):
                if len(value.split(":")) < 3:
                    value = "0000:" + value.strip() 
            oneDevData[name] = value
        fd.close()
    
def supplementOldLspciFormat(oneDevData):
    #oneDevData["device0"]
    #oneDevData["vendor"] = "old-lspci-format-fixme [%s]" % oneDevData["vendor"]
    #oneDevData["device1"] = "old-lspci-format-fixme [%s]" % oneDevData["device1"]
    #if oneDevData.has_key("svendor"): oneDevData["svendor"] = "old-lspci-format-fixme [%s]" % oneDevData["svendor"]
    #if oneDevData.has_key("sdevice"): oneDevData["sdevice"] = "old-lspci-format-fixme [%s]" % oneDevData["sdevice"]

    fd = os.popen("%s -m -v -s %s 2>/dev/null" % (lspciPath, oneDevData["device0"]), "r")
    deviceNum=0
    for line in fd:
        if not line.strip(): continue
        name,value = line.split(":", 1)
        name = name.strip().lower()
        value = value.strip()
        if name == ("device"):
            name = "device%s" % deviceNum
            deviceNum = deviceNum + 1

        if name == ("device0"):
            # fake domain if not present
            if len(value.split(":")) < 3:
                value = "0000:" + value.strip() 

        if name == "class":
            oneDevData["class"] = "%s [%s]" % (value, oneDevData["class"].split()[-1])

        if name == "vendor":
            oneDevData["vendor"] = "%s [%s]" % (value, oneDevData["vendor"])
        if name == "svendor":
            oneDevData["svendor"] = "%s [%s]" % (value, oneDevData["svendor"])
        if name == "device1":
            oneDevData["device1"] = "%s [%s]" % (value, oneDevData["device1"])
        if name == "sdevice":
            oneDevData["sdevice"] = "%s [%s]" % (value, oneDevData["sdevice"])

    fd.close()
    
    return oneDevData

decorateAllFunctions(sys.modules[__name__], moduleLog)

if __name__ == "__main__":
    for pkg in BootstrapGenerator():
        print "%s: %s" % (pkg.name, str(pkg))

