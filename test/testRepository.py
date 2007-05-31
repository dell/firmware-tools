#!/usr/bin/python2
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import os
import unittest

try:
    test_path = os.path.dirname( os.path.realpath( globals()["__file__"] ) )
except KeyError:
    test_path = os.path.realpath( sys.path[0] )

datafiles = os.path.join( test_path, "datafiles" )


class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def testRepositoryInventory(self):
        import repository
        r = repository.Repository(datafiles)
        for pkg in r.iterPackages():
            pass
 
    def testIterLatest(self):
        import repository
        r = repository.Repository(datafiles)
        list = []

        # list of versions for system_specific
        li = ["a04", "a09"]

        for pkg in r.iterLatestPackages():
            if pkg.name == "testpack":
                self.assertEqual( pkg.version, "a06" )
            elif pkg.name == "testpack_another":
                self.assertEqual( pkg.version, "a04" )
            elif pkg.name == "testpack_different":
                self.assertEqual( pkg.version, "a07" )
            elif pkg.name == "system_specific":
                self.failUnless( pkg.version in li )
                li.remove(pkg.version)
            elif pkg.name == "test_requires":
                self.assertEqual( pkg.version, "a09" )
            elif pkg.name == "testorder1":
                self.assertEqual( pkg.version, "a04" )
            elif pkg.name == "testorder2":
                self.assertEqual( pkg.version, "a05" )
            elif pkg.name == "testorder3":
                self.assertEqual( pkg.version, "a06" )
            elif pkg.name == "circtest1":
                self.assertEqual( pkg.version, "a04" )
            elif pkg.name == "circtest2":
                self.assertEqual( pkg.version, "a04" )
            else:
                self.fail("Unknown package. %s version %s" % (pkg.name, pkg.version))

        self.assertEqual( len(li), 0 )

    def testGenerateUpdateSet1(self):
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "testpack"
        p.version = "a04"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["testpack"]["update"].name, "testpack" )
        self.assertEqual( packagesToUpdate["testpack"]["update"].version, "a06" )

    def testGenerateUpdateSet2(self):
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "testpack_different"
        p.version = "a04"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["testpack_different"]["update"].name, "testpack_different" )
        self.assertEqual( packagesToUpdate["testpack_different"]["update"].version, "a07" )

    def testGenerateUpdateSet3(self):
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "testpack"
        p.version = "a08"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.failUnless( packagesToUpdate["testpack"]["update"] is None )

    def testGenerateUpdateSetMultiple(self):
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "testpack"
        p.version = "a04"

        q = package.InstalledPackage()
        q.name = "testpack_different"
        q.version = "a04"

        r = package.InstalledPackage()
        r.name = "testpack_another"
        r.version = "a05"

        systemInventory = [p,q,r]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["testpack"]["update"].name, "testpack" )
        self.assertEqual( packagesToUpdate["testpack"]["update"].version, "a06" )
        self.assertEqual( packagesToUpdate["testpack_different"]["update"].name, "testpack_different" )
        self.assertEqual( packagesToUpdate["testpack_different"]["update"].version, "a07" )
        self.failUnless( packagesToUpdate["testpack_another"]["update"] is None )

    def testGenerateUpdateSetInstallDefault(self):
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "testpack"
        p.version = "a04"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)
        self.assertRaises(package.InternalError, packagesToUpdate["testpack"]["update"].install)

    def testGenerateUpdateSetInstall(self):
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "testpack_different"
        p.version = "a04"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)
        res = packagesToUpdate["testpack_different"]["update"].install()
        self.assertEqual( res, "SUCCESS" )


    def testGenerateUpdateSet_SystemSpecific1(self):
        # test the case where system specific update available that doesn't 
        # apply to current system
        import repository
        import package
        p = package.InstalledPackage()
        p.name = "system_specific"
        p.version = "a01"
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.failUnless( packagesToUpdate["system_specific"]["update"] is None )

    def testGenerateUpdateSet_SystemSpecific2(self):
        # test the case where system specific update available that does
        # apply to current system
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "system_specific"
        p.version = "a01"

        q = package.InstalledPackage()
        q.name = "system_bios(ven_0x5555_dev_0x1234)"
        q.version = "a00"

        systemInventory = [p,q]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["system_specific"]["update"].name, "system_specific" )
        self.assertEqual( packagesToUpdate["system_specific"]["update"].version, "a04" )

    def testGenerateUpdateSet_SystemSpecific3(self):
        # test the case where system specific update available that does
        # apply to current system
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "system_specific"
        p.version = "a01"

        q = package.InstalledPackage()
        q.name = "system_bios(ven_0x5555_dev_0x4321)"
        q.version = "a00"

        systemInventory = [p,q]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["system_specific"]["update"].name, "system_specific" )
        self.assertEqual( packagesToUpdate["system_specific"]["update"].version, "a09" )


    def testGenerateUpdateSet_testRequires1(self):
        # test the case where system specific update available that doesn't 
        # apply to current system
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "test_requires"
        p.version = "a01"

        systemInventory = [p,]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.failUnless( packagesToUpdate["test_requires"]["update"] is None )

    def testGenerateUpdateSet_testRequires2(self):
        # test the case where system specific update available that does
        # apply to current system
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "test_requires"
        p.version = "a01"

        q = package.InstalledPackage()
        q.name = "otherpackage"
        q.version = "a00"

        r = package.InstalledPackage()
        r.name = "foo"
        r.version = "43"

        systemInventory = [p,q,r]
        r = repository.Repository(datafiles)
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)

        self.assertEqual( packagesToUpdate["test_requires"]["update"].name, "test_requires" )
        self.assertEqual( packagesToUpdate["test_requires"]["update"].version, "a09" )

    def testInstallationOrder1(self):
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "testorder1"
        p.version = "a01"

        q = package.InstalledPackage()
        q.name = "testorder2"
        q.version = "a01"

        r = package.InstalledPackage()
        r.name = "testorder3"
        r.version = "a01"

        systemInventory = [r,p,q]
        r = repository.Repository(datafiles)

        installationOrder = ["testorder1", "testorder2", "testorder3" ]
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)
        for pkg in repository.generateInstallationOrder(packagesToUpdate):
            n = installationOrder[0]
            if len(installationOrder) > 1:
                installationOrder = installationOrder[1:]

            self.assertEqual( n, pkg.name )

    def testInstallationOrder2(self):
        import repository
        import package

        p = package.InstalledPackage()
        p.name = "testorder1"
        p.version = "a01"

        q = package.InstalledPackage()
        q.name = "testorder2"
        q.version = "a08"

        r = package.InstalledPackage()
        r.name = "testorder3"
        r.version = "a01"

        systemInventory = [r,p,q]
        r = repository.Repository(datafiles)

        installationOrder = ["testorder1", "testorder3" ]
        packagesToUpdate = repository.generateUpdateSet(r, systemInventory)
        for pkg in repository.generateInstallationOrder(packagesToUpdate):
            n = installationOrder[0]
            if len(installationOrder) > 1:
                installationOrder = installationOrder[1:]

            self.assertEqual( n, pkg.name )


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
