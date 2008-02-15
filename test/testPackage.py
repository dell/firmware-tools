#!/usr/bin/python
# vim:tw=0:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import os
import unittest

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

    def testCompareVersions(self):
        import firmwaretools.package as package
        self.assertEqual(-1, package.defaultCompareStrategy( "1.0", "2.0"))
        self.assertEqual( 0, package.defaultCompareStrategy( "1.0", "1.0"))
        self.assertEqual( 1, package.defaultCompareStrategy( "2.0", "1.0"))


if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
