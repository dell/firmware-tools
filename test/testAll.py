#! /usr/bin/env python2
# VIM declarations
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

#alphabetical
import sys
import glob

import test.TestLib

# runs all modules TestCase() classes in files that match test*.py

if __name__ == "__main__":
    tests = []
    for moduleName in glob.glob("test/test*.py"):
        if moduleName.startswith("test/testAll.py"): continue
        moduleName = moduleName[:-3]
        module = __import__(moduleName, globals(), locals(), [])
        tests.append(module.TestCase)

    retval = test.TestLib.runTests( tests )

    sys.exit( not retval )
