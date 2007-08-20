# vim:tw=0:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
package module
"""

import rpm
from gettext import gettext as _

class InternalError(Exception): pass
class InstallError(Exception): pass
class NoInstaller(Exception): pass

def defaultCompareStrategy(ver1, ver2):
    return rpm.labelCompare( ("0", str(ver1), "0"), ("0", str(ver2), "0"))

packageStatusEnum = {
    "unknown": _("The package status is not known."),
    "not_installed": _("The device has not been updated to this version."),
    "in_progress":   _("The device is being updated now"),
    "failed":        _("Device update failed."),
    "success":       _("Device update was successful."),
    "disabled":       _("Device update is disabled for this device."),
    }

# Package public API:
#   pkg.name
#   pkg.version
#   str(pkg) == display name
#   pkg.compareVersion(otherPkg)
class Package(object):
    def __init__(self, *args, **kargs):
        self.name = None
        self.version = None
        self.compareStrategy = defaultCompareStrategy
        for key, value in kargs.items():
            setattr(self, key, value)

        assert(hasattr(self, "name"))
        assert(hasattr(self, "version"))
        assert(hasattr(self, "displayname"))

        status = "unknown"

    def __str__(self):
        if hasattr(self, "displayname"):
            return self.displayname
        return self.name

    def compareVersion(self, otherPackage):
        return self.compareStrategy(self.version, otherPackage.version)

class RepositoryPackage(Package):
    mainIni = None
    def __init__(self, *args, **kargs):
        self.installFunction = None
        self.path = None
        super(RepositoryPackage, self).__init__(*args, **kargs)

        self.capabilities = {
            'can_downgrade': False,
            'can_reflash': False,
            }

        self.status = "not_installed"
        self.deviceList = []
        
    def install(self):
        self.status = "in_progress"
        if self.installFunction is not None:
            return self.installFunction(self)

        self.status = "failed"
        raise NoInstaller(_("Attempt to install a package with no install function. Name: %s, Version: %s") % (self.name, self.version))

    def getCapability(self, capability):
        return self.capabilities.get(capability, None)

    def attachToDevice(self, device):
        self.deviceList.append(device)

    def getDeviceList(self):
        return self.deviceList


# Base class for all devices on a system
# required: 
#   displayname
#   name
#   version
# optional:
#   compareStrategy
class Device(Package):
    def __init__(self, *args, **kargs):
        self.name = None
        self.version = None
        self.compareStrategy = defaultCompareStrategy
        for key, value in kargs.items():
            setattr(self, key, value)

        if not hasattr(self, "uniqueInstance"):
            self.uniqueInstance = self.name

        assert(hasattr(self, "name"))
        assert(hasattr(self, "version"))
        assert(hasattr(self, "displayname"))

        status = "unknown"

    def __str__(self):
        if hasattr(self, "displayname"):
            return self.displayname
        return self.name

    def compareVersion(self, otherPackage):
        return self.compareStrategy(self.version, otherPackage.version)


# required:  (in addition to base class)
#   pciDbdf
class PciDevice(Device):
    def __init__(self, *args, **kargs):
        super(Device, self).__init__(*args, **kargs)
        assert(hasattr(self, "pciDbdf"))
        self.uniqueInstance = "%s_%s" % (self.name, self.pciDbdf)


#
# TESTING/DEBUG stuff below here
#

class MockRepositoryPackage(RepositoryPackage):
    def __init__(self, *args, **kargs):
        super(MockRepositoryPackage, self).__init__(*args, **kargs)
        self.capabilities['can_downgrade'] = True
        self.capabilities['can_reflash'] = True

    def install(self):
        self.status = "in_progress"
        print "MockRepositoryPackage -> Install pkg(%s)  version(%s)" % (str(self), self.version)
        self.status = "success"
