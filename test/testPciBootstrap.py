#!/usr/bin/python2
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def testBootstrapInventory(self):
        module = __import__("bootstrap_pci", globals(),  locals(), [])
        module.unit_test_mode=1
        index = 0
        for package in module.BootstrapGenerator():
            self.assertEqual( module.mockExpectedOutput.split("\n")[index], str(package) )
            index = index + 1
 

if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
