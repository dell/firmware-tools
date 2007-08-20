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
from trace_decorator import dprint, decorateAllFunctions

import package

# new standard entry point. 
def BootstrapGenerator(): 
    for i in lspciGeneratorFactory():
        # TODO: parse lspci output to get device name for displayname
        # TODO: add pciDbdf
        yield package.PciDevice(name=process_pci_dev(i), version='unknown', displayname='Unknown PCI Device', pciDbdf="foo")

# a regular expression to parse 'lspci -n -m' output
#                       "Class NNNN" "NNNN" "NNNN" -rXX... "NNNN" "NNNN"
pciRe = re.compile(r'^.*?"[\w ]+"\s"(\w+)"\s"(\w+)"\s.*?"(\w*)"\s"(\w*)"')

def splodeLine(line):
    ven = dev = subven = subdev = None
    res = pciRe.search(line)
    if res:
        ven = res.group(1)
        dev = res.group(2)
        subven = res.group(3)
        subdev = res.group(4)
        
    return [ven, dev, subven, subdev]

def process_pci_dev(line):
    ven, dev, subven, subdev = splodeLine(line)
    item = "pci_firmware(ven_0x%s_dev_0x%s" % (ven, dev)
    if subven and subdev:
        item = item + "_subven_0x%s_subdev_0x%s" % (subven, subdev)
    item = item + ")"
    return item

def lspciGenerator():
    for i in ("/sbin/lspci", "/usr/bin/lspci"):
        if os.path.exists(i):
            lspciPath=i
            break

    fd = os.popen("%s -n -m 2>/dev/null" % lspciPath, "r")
    for line in fd:
        yield line
    fd.close()

# returns a generator function
unit_test_mode = 0
def lspciGeneratorFactory():
    global unit_test_mode
    if not unit_test_mode:
        return lspciGenerator()
    else:
        return mockLspciGenerator()


decorateAllFunctions(sys.modules[__name__])

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

# this is a TEST generator. It only is active if you set the environment
# variable DEBUG_INVENTORY=1
def InventoryGenerator():
    if os.environ.get("DEBUG_INVENTORY", None) == "1":
        yield package.Device( 
                name = "test_device_0",
                displayname = "DEBUG Test Device 0",
                version = "0.0")
        yield package.Device( 
                name = "test_device_1a",
                displayname = "DEBUG Test Device 1a",
                version = "1.0")
        yield package.Device( 
                name = "test_device_1b",
                displayname = "DEBUG Test Device 1b",
                version = "1.0")
        yield package.Device( 
                name = "test_device_2a",
                displayname = "DEBUG Test Device 2a",
                version = "2.0")
        yield package.Device( 
                name = "test_device_2b",
                displayname = "DEBUG Test Device 2b",
                version = "2.0")
        yield package.Device( 
                name = "test_device_3a",
                displayname = "DEBUG Test Device 3a",
                version = "3.0")
        yield package.Device( 
                name = "test_device_3b",
                displayname = "DEBUG Test Device 3b",
                version = "3.0")

def mockLspciGenerator():
    mockInput = """00:00.0 "Class 0600" "1166" "0012" -r13 "" ""
00:00.1 "Class 0600" "1166" "0012" "" ""
00:00.2 "Class 0600" "1166" "0000" "" ""
00:04.0 "Class ff00" "1028" "000c" "000c" "000c"
00:04.1 "Class ff00" "1028" "0008" "0008" "0008"
00:04.2 "Class ff00" "1028" "000d" "000d" "000d"
00:0e.0 "Class 0300" "1002" "4752" -r27 "4752" "0121"
00:0f.0 "Class 0600" "1166" "0201" -r93 "0201" "0201"
00:0f.1 "Class 0101" "1166" "0212" -r93 -p82 "0212" "0212"
00:0f.2 "Class 0c03" "1166" "0220" -r05 -p10 "0220" "0220"
00:0f.3 "Class 0601" "1166" "0225" "0225" "0230"
00:10.0 "Class 0600" "1166" "0101" -r03 "" ""
00:10.2 "Class 0600" "1166" "0101" -r03 "" ""
00:11.0 "Class 0600" "1166" "0101" -r03 "" ""
00:11.2 "Class 0600" "1166" "0101" -r03 "" ""
02:06.0 "Class 0100" "9005" "00c0" -r01 "00c0" "f620"
02:06.1 "Class 0100" "9005" "00c0" -r01 "00c0" "f620"
03:06.0 "Class 0200" "14e4" "1645" -r15 "1645" "0121"
03:08.0 "Class 0200" "14e4" "1645" -r15 "1645" "0121"
04:08.0 "Class 0604" "8086" "0309" -r01 "" ""
05:06.0 "Class 0100" "9005" "00cf" -r01 "00cf" "0121"
05:06.1 "Class 0100" "9005" "00cf" -r01 "00cf" "0121\""""

    for line in mockInput.split("\n"):
        yield(line)


mockExpectedOutput = """pci_firmware(ven_0x1166_dev_0x0012)
pci_firmware(ven_0x1166_dev_0x0012)
pci_firmware(ven_0x1166_dev_0x0000)
pci_firmware(ven_0x1028_dev_0x000c_subven_0x000c_subdev_0x000c)
pci_firmware(ven_0x1028_dev_0x0008_subven_0x0008_subdev_0x0008)
pci_firmware(ven_0x1028_dev_0x000d_subven_0x000d_subdev_0x000d)
pci_firmware(ven_0x1002_dev_0x4752_subven_0x4752_subdev_0x0121)
pci_firmware(ven_0x1166_dev_0x0201_subven_0x0201_subdev_0x0201)
pci_firmware(ven_0x1166_dev_0x0212_subven_0x0212_subdev_0x0212)
pci_firmware(ven_0x1166_dev_0x0220_subven_0x0220_subdev_0x0220)
pci_firmware(ven_0x1166_dev_0x0225_subven_0x0225_subdev_0x0230)
pci_firmware(ven_0x1166_dev_0x0101)
pci_firmware(ven_0x1166_dev_0x0101)
pci_firmware(ven_0x1166_dev_0x0101)
pci_firmware(ven_0x1166_dev_0x0101)
pci_firmware(ven_0x9005_dev_0x00c0_subven_0x00c0_subdev_0xf620)
pci_firmware(ven_0x9005_dev_0x00c0_subven_0x00c0_subdev_0xf620)
pci_firmware(ven_0x14e4_dev_0x1645_subven_0x1645_subdev_0x0121)
pci_firmware(ven_0x14e4_dev_0x1645_subven_0x1645_subdev_0x0121)
pci_firmware(ven_0x8086_dev_0x0309)
pci_firmware(ven_0x9005_dev_0x00cf_subven_0x00cf_subdev_0x0121)
pci_firmware(ven_0x9005_dev_0x00cf_subven_0x00cf_subdev_0x0121)"""

