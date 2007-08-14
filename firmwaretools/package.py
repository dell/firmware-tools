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

class InternalError(Exception): pass
class InstallError(Exception): pass
class NoInstaller(Exception): pass

def defaultCompareStrategy(ver1, ver2):
    return rpm.labelCompare( ("0", str(ver1), "0"), ("0", str(ver2), "0"))

class Package(object):
    def __init__(self, *args, **kargs):
        self.name = None
        self.version = None
        self.compareStrategy = defaultCompareStrategy
        for key, value in kargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name

    def compareVersion(self, otherPackage):
        return self.compareStrategy(self.version, otherPackage.version)

class InstalledPackage(Package):
    pass

#
class Device(InstalledPackage):
    pass

# required: pci bus, device, function, pci ven/dev
class PciDevice(Device):
    pass

class RepositoryPackage(Package):
    mainIni = None
    def __init__(self, *args, **kargs):
        self.installFunction = None
        self.conf = None
        self.path = None
        super(RepositoryPackage, self).__init__(*args, **kargs)
        
    def install(self):
        if self.installFunction is not None:
            return self.installFunction(self)

        raise NoInstaller("Attempt to install a package with no install function. Name: %s, Version: %s" % (self.name, self.version))
