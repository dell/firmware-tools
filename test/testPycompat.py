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
        if globals().get('firmwaretools'): del(firmwaretools)
        for k in sys.modules.keys():
            if k.startswith("firmwaretools"):
                del(sys.modules[k])

    def tearDown(self):
        if globals().get('firmwaretools'): del(firmwaretools)
        for k in sys.modules.keys():
            if k.startswith("firmwaretools"):
                del(sys.modules[k])

    def testExcCommandNoTimeout(self):
        import firmwaretools.pycompat as pycompat
        pycompat.executeCommand("sleep 0", timeout=0)

    def testExcCommandTimeout(self):
        import firmwaretools.pycompat as pycompat
        self.assertRaises(pycompat.commandTimeoutExpired, pycompat.executeCommand, "sleep 3", timeout=1)

    def testExcCommandAlarmNoTimeout(self):
        # test that executeCommand() doesn't interfere with existing alarm calls
        # given a command that itself doesnt timeout
        import signal, time
        import firmwaretools.pycompat as pycompat
        class alarmExc(Exception): pass
        def alarmhandler(signum,stackframe):
            raise alarmExc("timeout expired")

        oldhandler=signal.signal(signal.SIGALRM,alarmhandler)
        prevTimeout = signal.alarm(1)
        pycompat.executeCommand("sleep 0", timeout=1)
        self.assertRaises(alarmExc, time.sleep, 5)

    def testExcCommandAlarmTimeout(self):
        # test that executeCommand() doesn't interfere with existing alarm calls
        # given a command that itself times out
        import signal, time
        import firmwaretools.pycompat as pycompat
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
