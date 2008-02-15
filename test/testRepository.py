#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
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

def generateUpdateSet(repo, inv):
    import firmwaretools.repository as repository
    _systemInventory = repository.SystemInventory()
    for dev in inv:
        _systemInventory.addDevice(dev)

    for candidate in repo.iterPackages():
        _systemInventory.addAvailablePackage(candidate)

    _systemInventory.calculateUpgradeList()
    return _systemInventory


class TestCase(unittest.TestCase):
    def setUp(self):
        if globals().get('firmwaretools'): del(firmwaretools)
        for k in sys.modules.keys():
            if k.startswith("firmwaretools"):
                del(sys.modules[k])

    def tearDown(self):
        if globals().get('firmwaretools'): del(firmwaretools)
        for k in sys.modules.keys():
            if k.startswith("firmwaretools"):
                del(sys.modules[k])

    def testRepositoryInventory(self):
        import firmwaretools.repository as repository
        r = repository.Repository(datafiles)
        for pkg in r.iterPackages():
            pass

    def testIterLatest(self):
        import firmwaretools.repository as repository
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
            elif pkg.name == "testpack_newpkgstrat":
                self.assertEqual( pkg.version, "a08" )
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
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack",
            version = "a04",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "testpack" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a06" )

    def testGenerateUpdateSet2(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack_different",
            version = "a04",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "testpack_different" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a07" )

    def testGenerateUpdateSet3(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack",
            version = "a08",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.failUnless( updateSet.getUpdatePackageForDevice(p) is None )

    def testGenerateUpdateSet4_andInstall(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack_newpkgstrat",
            version = "a04",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "testpack_newpkgstrat" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a08")
        res = updateSet.getUpdatePackageForDevice(p).install()
        self.assertEqual( res, "SUCCESS" )

    def testGenerateUpdateSetMultiple(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "testpack",
            version = "a04",
            displayname = "fake"
            )

        q = package.Device(
            name = "testpack_different",
            version = "a04",
            displayname = "fake"
            )

        r = package.Device(
            name = "testpack_another",
            version = "a05",
            displayname = "fake"
            )

        systemInventory = [p,q,r]
        repo = repository.Repository(datafiles)
        updateSet = generateUpdateSet(repo, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "testpack" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a06" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(q).name, "testpack_different" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(q).version, "a07" )
        self.failUnless( updateSet.getUpdatePackageForDevice(r) is None )

    def testGenerateUpdateSetInstallDefault(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack",
            version = "a04",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)
        self.assertRaises(package.NoInstaller, updateSet.getUpdatePackageForDevice(p).install)

    def testGenerateUpdateSetInstall(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "testpack_different",
            version = "a04",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)
        res = updateSet.getUpdatePackageForDevice(p).install()
        self.assertEqual( res, "SUCCESS" )


    def testGenerateUpdateSet_SystemSpecific1(self):
        # test the case where system specific update available that doesn't
        # apply to current system
        import firmwaretools.repository as repository
        import firmwaretools.package as package
        p = package.Device(
            name = "system_specific",
            version = "a01",
            displayname = "fake"
            )
        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.failUnless( updateSet.getUpdatePackageForDevice(p) is None )

    def testGenerateUpdateSet_SystemSpecific2(self):
        # test the case where system specific update available that does
        # apply to current system
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "system_specific",
            version = "a01",
            displayname = "fake"
            )

        q = package.Device(
            name = "system_bios(ven_0x5555_dev_0x1234)",
            version = "a00",
            displayname = "fake"
            )

        systemInventory = [p,q]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "system_specific" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a04" )

    def testGenerateUpdateSet_SystemSpecific3(self):
        # test the case where system specific update available that does
        # apply to current system
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "system_specific",
            version = "a01",
            displayname = "fake"
            )

        q = package.Device(
            name = "system_bios(ven_0x5555_dev_0x4321)",
            version = "a00",
            displayname = "fake"
            )

        systemInventory = [p,q]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "system_specific" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a09" )


    def testGenerateUpdateSet_testRequires1(self):
        # test the case where system specific update available that doesn't
        # apply to current system
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "test_requires",
            version = "a01",
            displayname = "fake"
            )

        systemInventory = [p,]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.failUnless( updateSet.getUpdatePackageForDevice(p) is None )

    def testGenerateUpdateSet_testRequires2(self):
        # test the case where system specific update available that does
        # apply to current system
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "test_requires",
            version = "a01",
            displayname = "fake"
            )

        q = package.Device(
            name = "otherpackage",
            version = "a00",
            displayname = "fake"
            )

        r = package.Device(
            name = "foo",
            version = "43",
            displayname = "fake"
            )

        systemInventory = [p,q,r]
        r = repository.Repository(datafiles)
        updateSet = generateUpdateSet(r, systemInventory)

        self.assertEqual( updateSet.getUpdatePackageForDevice(p).name, "test_requires" )
        self.assertEqual( updateSet.getUpdatePackageForDevice(p).version, "a09" )

    def testInstallationOrder1(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "testorder1",
            version = "a01",
            displayname = "fake"
            )

        q = package.Device(
            name = "testorder2",
            version = "a01",
            displayname = "fake"
            )

        r = package.Device(
            name = "testorder3",
            version = "a01",
            displayname = "fake"
            )

        systemInventory = [r,p,q]
        r = repository.Repository(datafiles)

        installationOrder = ["testorder1", "testorder2", "testorder3" ]
        updateSet = generateUpdateSet(r, systemInventory)
        for pkg in updateSet.generateInstallationOrder():
            n = installationOrder[0]
            if len(installationOrder) > 1:
                installationOrder = installationOrder[1:]

            self.assertEqual( n, pkg.name )

    def testInstallationOrder2(self):
        import firmwaretools.repository as repository
        import firmwaretools.package as package

        p = package.Device(
            name = "testorder1",
            version = "a01",
            displayname = "fake"
            )

        q = package.Device(
            name = "testorder2",
            version = "a08",
            displayname = "fake"
            )

        r = package.Device(
            name = "testorder3",
            version = "a01",
            displayname = "fake"
            )

        systemInventory = [r,p,q]
        r = repository.Repository(datafiles)

        installationOrder = ["testorder1", "testorder3" ]
        updateSet = generateUpdateSet(r, systemInventory)
        for pkg in updateSet.generateInstallationOrder():
            n = installationOrder[0]
            if len(installationOrder) > 1:
                installationOrder = installationOrder[1:]

            self.assertEqual( n, pkg.name )


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
