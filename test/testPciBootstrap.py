#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import unittest
import ConfigParser

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

    def testBootstrapInventory(self):
        import firmwaretools
        import firmwaretools.plugins as plugins

        # manually setup fake config file
        f = firmwaretools.FtBase()
        pluginTypes = [
            plugins.TYPE_CORE,
            plugins.TYPE_MOCK_CORE, plugins.TYPE_MOCK_INVENTORY, plugins.TYPE_MOCK_BOOTSTRAP,
            ] 
        f._getConfig(None, pluginTypes, None, [])

        # import functions for bootstrap/compare

        # run bootstrap and compare.
        index = 0
        for pkg in f.yieldBootstrap():
            self.assertEqual( firmwaretools.mockpackage.mockExpectedOutput.split("\n")[index], pkg.name )
            index = index + 1

        # ensure it actually ran.
        self.assertEqual(index, len(firmwaretools.mockpackage.mockExpectedOutput.split("\n")))


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
