#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
package module
"""

class InternalError(Exception): pass
class InstallError(Exception): pass

def defaultCompareStrategy(ver1, ver2):
    if ver1 == ver2:
        return 0
    if ver1 > ver2:
        return -1
    return 1

def defaultInstallStrategy(self):
    raise InternalError("Attempt to install a package with no install function. Name: %s, Version: %s" % (self.name, self.version))

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

class RepositoryPackage(Package):
    def __init__(self, *args, **kargs):
        self.installFunction = defaultInstallStrategy
        self.conf = None
        self.path = None
        super(RepositoryPackage, self).__init__(*args, **kargs)
        
    def install(self):
        return self.installFunction(self)

