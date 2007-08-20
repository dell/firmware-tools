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
        
    def install(self):
        if self.installFunction is not None:
            return self.installFunction(self)

        raise NoInstaller("Attempt to install a package with no install function. Name: %s, Version: %s" % (self.name, self.version))


# Base class for all devices on a system
class Device(Package):
    def __init__(self, *args, **kargs):
        super(Device, self).__init__(*args, **kargs)
        self.uniqueKey = self.name

# required: 
#   displayname
#   name
#   version
#   pciDbdf
# optional:
#   compareStrategy
class PciDevice(Device):
    def __init__(self, *args, **kargs):
        super(Device, self).__init__(*args, **kargs)
        assert(hasattr(self, "pciDbdf"))
        self.uniqueInstance = "%s_%s" % (self.name, self.pciDbdf)


#
# TESTING/DEBUG stuff below here
#

class MockRepositoryPackage(RepositoryPackage):
    def install(self):
        print "MockRepositoryPackage -> Install pkg(%s)  version(%s)" % (str(self), self.version)
