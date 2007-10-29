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
import commands
import getopt
import glob
import os
import sys
import ConfigParser
import math
import zipfile
import re
import shutil
import signal
import time
import threading

from trace_decorator import dprint, decorateAllFunctions

def clearLine():
    return "\033[2K\033[0G"

def spinner(cycle=['/', '-', '\\', '|']):
    step = cycle[0]
    del cycle[0]
    cycle.append(step)
    # ESC codes for clear line and position cursor at horizontal pos 0
    return step

def spinPrint( strn ):
    print clearLine(),
    print "%s\t%s" % (spinner(), strn),
    sys.stdout.flush()

def timedSpinPrint( strn, start ):
    now = time.time()
    # ESC codes for position cursor at horizontal pos 65
    spinPrint( strn + "\033[65G time: %2.2f" % (now - start) )


# helper class & functions for executeCommand()
# User should handle this if they specify a timeout
class commandTimeoutExpired(Exception): pass

# the problem with os.system() is that the command that is run gets any 
# keyboard input and/or signals. This means that <CTRL>-C interrupts the 
# sub-program instead of the python program. This helper function fixes that.
# It also allows us to set up a maximum timeout before all children are killed
def executeCommand(cmd, timeout=0):
    class alarmExc(Exception): pass
    def alarmhandler(signum,stackframe):
        raise alarmExc("timeout expired")
    
    pid = os.fork()
    if pid:
        #parent
        rpid = ret = 0
        oldhandler=signal.signal(signal.SIGALRM,alarmhandler)
        starttime = time.time()
        prevTimeout = signal.alarm(timeout)
        try:
            (rpid, ret) = os.waitpid(pid, 0)
            signal.alarm(0)
            signal.signal(signal.SIGALRM,oldhandler)
            if prevTimeout:
                passed = time.time() - starttime
                signal.alarm(int(math.ceil(prevTimeout - passed)))
        except alarmExc:
            try:
                os.kill(-pid, signal.SIGTERM)
                time.sleep(1)
                os.kill(-pid, signal.SIGKILL)
            except OSError: # errno=3  == no such process
                pass
            (rpid, ret) = os.waitpid(pid, 0)
            signal.signal(signal.SIGALRM,oldhandler)
            if prevTimeout:
                passed = time.time() - starttime
                signal.alarm(max(math.ceil(prevTimeout - passed), 1))
            raise commandTimeoutExpired( "Specified timeout of %s seconds expired before command finished. Command was: %s"
                    % (timeout, cmd)
                    )
        except KeyboardInterrupt:
            signal.signal(signal.SIGALRM,oldhandler)
            try:
                os.kill(-pid, signal.SIGTERM)
                time.sleep(1)
                os.kill(-pid, signal.SIGKILL)
            except OSError: # errno=3  == no such process
                pass
            (rpid, ret) = os.waitpid(pid, 0)
            raise

        # mask and return just return value
        return (ret & 0xFF00) >> 8
    else:
        #child
        os.setpgrp()  # become process group leader so that we can kill all our children
        signal.signal(signal.SIGINT, signal.SIG_IGN) #ignore <CTRL>-C so parent gets it
        ret = os.system(cmd)
        os._exit( (ret & 0xFF00) >> 8 )

def copyFile( source, dest, ignoreException=0 ):
    try:
        shutil.copyfile(source, dest)
    except IOError:
        if not ignoreException:
            raise

# python 2.3 has a better version, but we have to run on python 2.2. :-(
def mktempdir( prefix="/tmp" ):
    status, output = commands.getstatusoutput("mktemp -d %s/tempdir-$$-$RANDOM-XXXXXX" % prefix)
    if status != 0:
        raise Exception("could not create secure temporary directory: %s" % output)
    return output

# generator function -- emulates the os.walk() generator in python 2.3 (mostly)
# ret = (path, dirs, files) foreach dir
def walkPath(topdir, direction=0):
    rawFiles = os.listdir(topdir)
    
    files=[f for f in rawFiles if os.path.isfile(os.path.join(topdir,f))]
    dirs =[f for f in rawFiles if os.path.isdir (os.path.join(topdir,f))]

    if direction == 0:
        yield (topdir, dirs, files)

    for d in dirs:
        if not os.path.islink(os.path.join(topdir,d)):
            for (newtopdir, newdirs, newfiles) in walkPath(os.path.join(topdir,d)):
                yield (newtopdir, newdirs, newfiles)

    if direction == 1:
        yield (topdir, dirs, files)


def runLongProcess(function, args=None, kargs=None, waitLoopFunction=None):
    # runs a function in a separate thread. Runs waitLoopFunction() while it
    # waits for the function to finish. Good for updating GUI, or other stuff
    thread = BackgroundWorker(function, args, kargs)
    while thread.running:
        if waitLoopFunction is not None:
            waitLoopFunction()

    # run waitLoopFunction one last time before exit.
    # gives status opportunity to update to 100% 
    if waitLoopFunction is not None:
        waitLoopFunction()

    if thread.exception:
        raise thread.exception
    return thread.returnCode

class BackgroundWorker(threading.Thread):
    def __init__ (self, function, args=None, kargs=None):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args
        self.kargs = kargs

        self.exception = None
        self.returnCode = None
        self.running=1

        if self.args is None: self.args = []
        if self.kargs is None: self.kargs = {}

        self.start()

    def run(self):
        try:
            self.returnCode = self.function(*self.args, **self.kargs)
        except (Exception,), e:
            self.exception = e

        self.running=0

decorateAllFunctions(sys.modules[__name__])
