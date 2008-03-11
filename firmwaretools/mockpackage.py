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

plugin_type = (plugins.TYPE_MOCK_INVENTORY,)
requires_api_version = "2.0"

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================
decorate(traceLog())
def inventory_hook(conduit, inventory=None, *args, **kargs):
    base = conduit.getBase()
    cb = base.cb

    import firmwaretools as ft
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd")
    inventory.addDevice( package.Device(
            name = "debug_system_bios",
            displayname = "System BIOS for Imaginary Server 1234",
            version = "A02"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 2")
    inventory.addDevice( package.Device(
            name = "debug_system_bmc",
            displayname = "Baseboard Management Controller for Imaginary Server 1234",
            version = "1.0"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 3")
    inventory.addDevice( package.Device(
            name = "debug_pci_firmware_ven_crappy_dev_slow",
            displayname = "ReallyFast Network Controller",
            version = "1.0"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 4")
    inventory.addDevice( package.Device(
            name = "debug_pci_firmware_ven_0x0c64_dev_0xrocked",
            displayname = "Pokey Modem -- Enhanced 1200baud",
            version = "2.0"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 5")
    inventory.addDevice( package.Device(
            name = "debug_pci_firmware_ven_corrupt_dev_yourdata",
            displayname = "SafeData RAID Controller v2i",
            version = "2.0"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 6")
    inventory.addDevice( package.Device(
            name = "debug_pci_firmware_ven_violates_dev_scsistandard",
            displayname = "AdapFirm SloTek AHA-1501",
            version = "3.0"))
    ft.callCB(cb, who="mock_inventory", what="running_inventory", details="fake cmd 7")
    inventory.addDevice( package.Device(
            name = "debug_pci_firmware_ven_draws_dev_polygons",
            displayname = "PixelPusher 2000 Video Adapter",
            version = "4.0"))


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
        self.uniqueInstance = self.name

    decorate(traceLog())
    def install(self):
        self.status = "in_progress"
        for i in xrange(100):
            self.progressPct = i/100.0
            time.sleep(0.01)
        #print "MockRepositoryPackage -> Install pkg(%s)  version(%s)" % (str(self), self.version)
        self.progressPct = 1
        self.status = "success"







#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

mockExpectedOutput = """debug_pci_firmware_ven_0x0c64_dev_0xrocked
debug_pci_firmware_ven_crappy_dev_slow
debug_system_bmc
debug_pci_firmware_ven_corrupt_dev_yourdata
debug_system_bios
debug_pci_firmware_ven_draws_dev_polygons
debug_pci_firmware_ven_violates_dev_scsistandard"""


# re-use mock data from low-level getSystemId mock function
mockExpectedOutput_inventory = [("mock_package(ven_0x1028_dev_0x1234)", "a05"), ]

#==============================================================
# mock classes for unit tests
#   plus expected data returns
#==============================================================

# re-use mock data from low-level getSystemId mock function
mockExpectedOutput_bootstrap = """mock_package(ven_0x1028_dev_0x1234)"""

