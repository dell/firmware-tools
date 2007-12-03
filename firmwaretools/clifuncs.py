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

from trace_decorator import  traceLog, decorate

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=os.path.join(os.path.dirname(os.path.realpath(sys._getframe(0).f_code.co_filename)),"..","etc")
CONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

# set up logging
moduleLog = logging.getLogger("ft.trace." + __name__)

decorate(traceLog(moduleLog))
def runInventory(cfg):
    # returns a list of devices on the system
    return runSomething(cfg, "InventoryGenerator")

decorate(traceLog(moduleLog))
def runBootstrapInventory(cfg):
    return runSomething(cfg, "BootstrapGenerator")

# gets a list of modules and runs a generator function from each module
decorate(traceLog(moduleLog))
def runSomething(cfg, function):
    for n,det in cfg.plugins.items():
        try:
            for thing in getattr(det['module'],function)():
                yield thing
        except AttributeError, e:
            moduleLog.error("AttributeError usually means the module is missing the specified function.\n\tModule: %s\n\tFunction: %s\n" % (module, function))
            moduleLog.error(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        except:   # don't let module messups propogate up
            moduleLog.error(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))

