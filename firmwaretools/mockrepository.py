# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
repository module
"""

from __future__ import generators

import os

import repository
import mockpackage
import sys
from firmwaretools.trace_decorator import decorate, traceLog, getLog
import firmwaretools.plugins as plugins

plugin_type = (plugins.TYPE_MOCK_INVENTORY, )
requires_api_version = "2.0"

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

#
# DEBUG ONLY
#

# a null function that just eats args. Default callback
def nullFunc(*args, **kargs): pass

def config_hook(conduit, *args, **kargs):
    repository.Repository.iterPackages = iterPackages_DEBUG

decorate(traceLog())
def iterPackages_DEBUG(self, cb=(nullFunc, None)):
    # TODO: put this in a separate function
    yield mockpackage.MockRepositoryPackage(
        displayname="Baseboard Management Controller for Imaginary Server 1234",
        name="debug_system_bmc",
        version="0.9")
    yield mockpackage.MockRepositoryPackage(
        displayname="ReallyFast Network Controller",
        name="debug_pci_firmware_ven_crappy_dev_slow",
        version="1.1")

    # in fake mode, this pkg should never show up.
    from ConfigParser import ConfigParser
    conf = ConfigParser() 
    conf.add_section("package")
    conf.set("package", "limit_system_support", "nonexistent_system")
    yield  mockpackage.MockRepositoryPackage(
        displayname="ReallyFast Network Controller",
        name="debug_pci_firmware_ven_crappy_dev_slow",
        version="1.2",
        conf = conf)

    yield mockpackage.MockRepositoryPackage(
        displayname="Pokey Modem -- Enhanced 1200baud",
        name="debug_pci_firmware_ven_0x0c64_dev_0xrocked",
        version="1.1")
    yield mockpackage.MockRepositoryPackage(
        displayname="Pokey Modem -- Enhanced 1200baud",
        name="debug_pci_firmware_ven_0x0c64_dev_0xrocked",
        version="1.9")
    yield mockpackage.MockRepositoryPackage(
        displayname="SafeData RAID Controller v2i",
        name="debug_pci_firmware_ven_corrupt_dev_yourdata",
        version="1.1")
    yield mockpackage.MockRepositoryPackage(
        displayname="SafeData RAID Controller v2i",
        name="debug_pci_firmware_ven_corrupt_dev_yourdata",
        version="2.9")
    yield mockpackage.MockRepositoryPackage(
        displayname="AdapFirm SloTek AHA-1501",
        name="debug_pci_firmware_ven_violates_dev_scsistandard",
        version="2.1")
    yield mockpackage.MockRepositoryPackage(
        displayname="AdapFirm SloTek AHA-1501",
        name="debug_pci_firmware_ven_violates_dev_scsistandard",
        version="2.5")
    yield mockpackage.MockRepositoryPackage(
        displayname="AdapFirm SloTek AHA-1501",
        name="debug_pci_firmware_ven_violates_dev_scsistandard",
        version="3.0")
    yield mockpackage.MockRepositoryPackage(
        displayname="PixelPusher 2000 Video Adapter",
        name="debug_pci_firmware_ven_draws_dev_polygons",
        version="4.0")
    yield mockpackage.MockRepositoryPackage(
        displayname="PixelPusher 2000 Video Adapter",
        name="debug_pci_firmware_ven_draws_dev_polygons",
        version="4.1")
    yield mockpackage.MockRepositoryPackage(
        displayname="PixelPusher 2000 Video Adapter",
        name="debug_pci_firmware_ven_draws_dev_polygons",
        version="4.1.1")
    yield mockpackage.MockRepositoryPackage(
        displayname="PixelPusher 2000 Video Adapter",
        name="debug_pci_firmware_ven_draws_dev_polygons",
        version="4.1.2")

