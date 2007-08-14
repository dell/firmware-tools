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
        yield package.InstalledPackage( name=i )

# standard entry point -- Inventory
#  -- this is a generator function, but system can only have one system bios,
#     so, only one yield, no loop
def InventoryGenerator(): 
    p = package.InstalledPackage( name="mock_package(ven_0x1028_dev_0x1234)", version="a05")
    yield p
    p = package.InstalledPackage( name="testpack_different", version="a04")
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

