#!/usr/bin/python2
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
"""

from __future__ import generators

import sys
import os
import unittest

class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def testExcCommandNoTimeout(self):
        import pycompat
        pycompat.executeCommand("sleep 0", timeout=0)

    def testExcCommandTimeout(self):
        import pycompat
        self.assertRaises(pycompat.commandTimeoutExpired, pycompat.executeCommand, "sleep 3", timeout=1)

    def testExcCommandAlarmNoTimeout(self):
        # test that executeCommand() doesn't interfere with existing alarm calls
        # given a command that itself doesnt timeout
        import pycompat, signal, time
        class alarmExc(Exception): pass
        def alarmhandler(signum,stackframe):
            raise alarmExc("timeout expired")

        oldhandler=signal.signal(signal.SIGALRM,alarmhandler)
        prevTimeout = signal.alarm(2)
        pycompat.executeCommand("sleep 0", timeout=1)
        self.assertRaises(alarmExc, time.sleep, 5)

    def testExcCommandAlarmTimeout(self):
        # test that executeCommand() doesn't interfere with existing alarm calls
        # given a command that itself times out
        import pycompat, signal, time
        class alarmExc(Exception): pass
        def alarmhandler(signum,stackframe):
            raise alarmExc("timeout expired")

        oldhandler=signal.signal(signal.SIGALRM,alarmhandler)
        prevTimeout = signal.alarm(2)
        self.assertRaises(pycompat.commandTimeoutExpired, pycompat.executeCommand,"sleep 2", timeout=1)
        self.assertRaises(alarmExc, time.sleep, 10)



if __name__ == "__main__":
    import test.TestLib
    sys.exit(not test.TestLib.runTests( [TestCase] ))
