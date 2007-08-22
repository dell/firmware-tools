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

import os

# import arranged alphabetically
import package

# old style
class MockPackageWrapper(object):
    def __init__(self, package):
        package.installFunction = self.installFunction
        package.type = self

    def installFunction(self, package):
        #print "MOCK INSTALL OF: %s = %s" % (package, package.version)
        return "SUCCESS"


#new style
class MockPackage2(package.RepositoryPackage):
    def __init__(self, *args, **kargs):
        super(MockPackage2, self).__init__(*args, **kargs)

    def install(self):
        #print "MOCK INSTALL OF: %s = %s" % (self.name, self.version)
        return "SUCCESS"


# standard entry point -- Bootstrap
def BootstrapGenerator(): 
    for i in [ "mock_package(ven_0x1028_dev_0x1234)", "testpack_different" ]:
        yield package.Device( name=i )

# standard entry point -- Inventory
#  -- this is a generator function, but system can only have one system bios,
#     so, only one yield, no loop
def InventoryGenerator(): 
    p = package.Device( name="mock_package(ven_0x1028_dev_0x1234)", version="a05")
    yield p
    p = package.Device( name="testpack_different", version="a04")
    yield p

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

# re-use mock data from low-level getSystemId mock function
mockExpectedOutput_inventory = [("mock_package(ven_0x1028_dev_0x1234)", "a05"), ]

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

# re-use mock data from low-level getSystemId mock function
mockExpectedOutput_bootstrap = """mock_package(ven_0x1028_dev_0x1234)"""

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

# this is a TEST generator. It only is active if you set the environment
# variable DEBUG_INVENTORY=1
def mockBootstrapPci_InventoryGenerator():
    yield package.Device( 
            name = "debug_system_bios",
            displayname = "System BIOS for Imaginary Server 1234",
            version = "0.0")
    yield package.Device( 
            name = "debug_system_bmc",
            displayname = "Baseboard Management Controller for Imaginary Server 1234",
            version = "1.0")
    yield package.Device( 
            name = "debug_pci_firmware_ven_crappy_dev_slow",
            displayname = "ReallyFast Network Controller",
            version = "1.0")
    yield package.Device( 
            name = "debug_pci_firmware_ven_0x0c64_dev_0xrocked",
            displayname = "Pokey Modem -- Enhanced 1200baud",
            version = "2.0")
    yield package.Device( 
            name = "debug_pci_firmware_ven_corrupt_dev_yourdata",
            displayname = "SafeData RAID Controller v2i",
            version = "2.0")
    yield package.Device( 
            name = "debug_pci_firmware_ven_violates_dev_scsistandard",
            displayname = "AdapFirm SloTek AHA-1501",
            version = "3.0")
    yield package.Device( 
            name = "debug_pci_firmware_ven_draws_dev_polygons",
            displayname = "PixelPusher 2000 Video Adapter",
            version = "3.0")

import bootstrap_pci
if os.environ.get("DEBUG_INVENTORY", None) == "1":
    bootstrap_pci.InventoryGenerator = mockBootstrapPci_InventoryGenerator

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

bootstrap_pci.mockLspciGenerator = mockLspciGenerator


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


bootstrap_pci.mockExpectedOutput = mockExpectedOutput
