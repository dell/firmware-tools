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
import time
import logging

# import arranged alphabetically
import package
from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

plugin_type = (plugins.TYPE_MOCK_INVENTORY, plugins.TYPE_MOCK_BOOTSTRAP)
requires_api_version = "1.0"

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")


def config_hook(conduit, *args, **kargs):
    conduit.getBase().registerBootstrapFunction( "mockpackage", BootstrapGenerator )
    conduit.getBase().registerInventoryFunction( "mockpackage", InventoryGenerator )


# old style
class MockPackageWrapper(object):
    decorate(traceLog())
    def __init__(self, package):
        package.installFunction = self.installFunction
        package.type = self

    decorate(traceLog())
    def installFunction(self, package):
        self.status = "in_progress"
        self.status = "success"
        return "SUCCESS"


#new style -- used by unit tests.
class MockPackage2(package.RepositoryPackage):
    decorate(traceLog())
    def __init__(self, *args, **kargs):
        super(MockPackage2, self).__init__(*args, **kargs)

    decorate(traceLog())
    def install(self):
        self.status = "in_progress"
        self.status = "success"
        return "SUCCESS"

# used when we switch to 'fake' data
class MockRepositoryPackage(package.RepositoryPackage):
    decorate(traceLog())
    def __init__(self, *args, **kargs):
        super(MockRepositoryPackage, self).__init__(*args, **kargs)
        self.capabilities['can_downgrade'] = True
        self.capabilities['can_reflash'] = True
        self.capabilities['accurate_update_percentage'] = True

    decorate(traceLog())
    def install(self):
        self.status = "in_progress"
        for i in xrange(100):
            self.progressPct = i/100.0
            time.sleep(0.01)
        #print "MockRepositoryPackage -> Install pkg(%s)  version(%s)" % (str(self), self.version)
        self.progressPct = 1
        self.status = "success"

# standard entry point -- Bootstrap
decorate(traceLog())
def BootstrapGenerator():
    import bootstrap_pci
    bootstrap_pci.mockReadLspciWithDomain = mockReadLspciWithDomain
    for i in bootstrap_pci.lspciGenerator():
        yield(bootstrap_pci.makePciDevice(i))

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
decorate(traceLog())
def InventoryGenerator():
    yield package.Device(
            name = "debug_system_bios",
            displayname = "System BIOS for Imaginary Server 1234",
            version = "A02")
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
            version = "4.0")

decorate(traceLog())
def mockReadLspciWithDomain(*args, **kargs):
    mockInput = """Device:	0000:00:00.0
Class:	Host bridge [0600]
Vendor:	nVidia Corporation [10de]
Device:	nForce3 250Gb Host Bridge [00e1]
Rev:	a1

Device:	0000:00:01.0
Class:	ISA bridge [0601]
Vendor:	nVidia Corporation [10de]
Device:	nForce3 250Gb LPC Bridge [00e0]
SVendor:	nVidia Corporation [10de]
SDevice:	Winfast NF3250K8AA [0c11]
Rev:	a2

Device:	0000:00:01.1
Class:	SMBus [0c05]
Vendor:	nVidia Corporation [10de]
Device:	nForce 250Gb PCI System Management [00e4]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a1

Device:	0000:00:02.0
Class:	USB Controller [0c03]
Vendor:	nVidia Corporation [10de]
Device:	CK8S USB Controller [00e7]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a1
ProgIf:	10

Device:	0000:00:02.1
Class:	USB Controller [0c03]
Vendor:	nVidia Corporation [10de]
Device:	CK8S USB Controller [00e7]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a1
ProgIf:	10

Device:	0000:00:02.2
Class:	USB Controller [0c03]
Vendor:	nVidia Corporation [10de]
Device:	nForce3 EHCI USB 2.0 Controller [00e8]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a2
ProgIf:	20

Device:	0000:00:05.0
Class:	Bridge [0680]
Vendor:	nVidia Corporation [10de]
Device:	CK8S Ethernet Controller [00df]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a2

Device:	0000:00:08.0
Class:	IDE interface [0101]
Vendor:	nVidia Corporation [10de]
Device:	CK8S Parallel ATA Controller (v2.5) [00e5]
SVendor:	Unknown vendor [f0de]
SDevice:	Unknown device [0c11]
Rev:	a2
ProgIf:	8a

Device:	0000:00:0a.0
Class:	IDE interface [0101]
Vendor:	nVidia Corporation [10de]
Device:	CK8S Serial ATA Controller (v2.5) [00e3]
SVendor:	nVidia Corporation [10de]
SDevice:	Unknown device [0c11]
Rev:	a2
ProgIf:	85

Device:	0000:00:0b.0
Class:	PCI bridge [0604]
Vendor:	nVidia Corporation [10de]
Device:	nForce3 250Gb AGP Host to PCI Bridge [00e2]
Rev:	a2

Device:	0000:00:0e.0
Class:	PCI bridge [0604]
Vendor:	nVidia Corporation [10de]
Device:	nForce3 250Gb PCI-to-PCI Bridge [00ed]
Rev:	a2

Device:	0000:00:18.0
Class:	Host bridge [0600]
Vendor:	Advanced Micro Devices [AMD] [1022]
Device:	K8 [Athlon64/Opteron] HyperTransport Technology Configuration [1100]

Device:	0000:00:18.1
Class:	Host bridge [0600]
Vendor:	Advanced Micro Devices [AMD] [1022]
Device:	K8 [Athlon64/Opteron] Address Map [1101]

Device:	0000:00:18.2
Class:	Host bridge [0600]
Vendor:	Advanced Micro Devices [AMD] [1022]
Device:	K8 [Athlon64/Opteron] DRAM Controller [1102]

Device:	0000:00:18.3
Class:	Host bridge [0600]
Vendor:	Advanced Micro Devices [AMD] [1022]
Device:	K8 [Athlon64/Opteron] Miscellaneous Control [1103]

Device:	0000:01:00.0
Class:	VGA compatible controller [0300]
Vendor:	ATI Technologies Inc [1002]
Device:	Radeon R300 NG [FireGL X1] [4e47]
SVendor:	ATI Technologies Inc [1002]
SDevice:	Unknown device [0172]
Rev:	80

Device:	0000:01:00.1
Class:	Display controller [0380]
Vendor:	ATI Technologies Inc [1002]
Device:	Radeon R300 [FireGL X1] (Secondary) [4e67]
SVendor:	ATI Technologies Inc [1002]
SDevice:	Unknown device [0173]
Rev:	80

Device:	0000:02:07.0
Class:	FireWire (IEEE 1394) [0c00]
Vendor:	VIA Technologies, Inc. [1106]
Device:	IEEE 1394 Host Controller [3044]
SVendor:	VIA Technologies, Inc. [1106]
SDevice:	IEEE 1394 Host Controller [3044]
Rev:	80
ProgIf:	10

Device:	0000:02:08.0
Class:	Multimedia audio controller [0401]
Vendor:	C-Media Electronics Inc [13f6]
Device:	CM8738 [0111]
SVendor:	C-Media Electronics Inc [13f6]
SDevice:	CMI8738/C3DX PCI Audio Device [0111]
Rev:	10
"""
    for line in mockInput.split("\n"):
        yield(line)

mockExpectedOutput = """pci_firmware(ven_0x10de_dev_0x00e1)
pci_firmware(ven_0x10de_dev_0x00e0_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e4_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e7_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e7_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e8_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00df_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e5_subven_0xf0de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e3_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e2)
pci_firmware(ven_0x10de_dev_0x00ed)
pci_firmware(ven_0x1022_dev_0x1100)
pci_firmware(ven_0x1022_dev_0x1101)
pci_firmware(ven_0x1022_dev_0x1102)
pci_firmware(ven_0x1022_dev_0x1103)
pci_firmware(ven_0x1002_dev_0x4e47_subven_0x1002_subdev_0x0172)
pci_firmware(ven_0x1002_dev_0x4e67_subven_0x1002_subdev_0x0173)
pci_firmware(ven_0x1106_dev_0x3044_subven_0x1106_subdev_0x3044)
pci_firmware(ven_0x13f6_dev_0x0111_subven_0x13f6_subdev_0x0111)"""





