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
from trace_decorator import decorateAllFunctions

#
# DEBUG ONLY
#

# a null function that just eats args. Default callback
def nullFunc(*args, **kargs): pass

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

if os.environ.get("DEBUG_REPOSITORY", None) == "1":
    repository.Repository.iterPackages = iterPackages_DEBUG

decorateAllFunctions(sys.modules[__name__])
