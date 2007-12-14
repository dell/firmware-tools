# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################

from __future__ import generators

import logging
import logging.config
import os
import sys
import traceback

from firmwaretools.trace_decorator import decorate, traceLog, getLog

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=os.path.join(os.path.dirname(os.path.realpath(sys._getframe(0).f_code.co_filename)),"..","etc")
CONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

# set up logging
moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

decorate(traceLog())
def runInventory(cfg):
    # returns a list of devices on the system
    return runSomething(cfg, "InventoryGenerator")

decorate(traceLog())
def runBootstrapInventory(cfg):
    return runSomething(cfg, "BootstrapGenerator")

# gets a list of modules and runs a generator function from each module
decorate(traceLog())
def runSomething(cfg, functionName):
    for n,det in cfg.plugins.items():
        moduleVerboseLog.info("Try module: %s" % n)
        try:
            try:
                func = getattr(det['module'], functionName)
                moduleVerboseLog.info("  Got function: %s" % functionName)
            except AttributeError:
                continue

            moduleVerboseLog.info("  Running function.")
            gen = func()
            for thing in gen:
                yield thing

        except Exception, e:
            moduleLog.error(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))

