# vim:ai:ts=4:sw=4:et:filetype=python:

#future imports always first
from __future__ import generators

# std python stuff
import logging
import gtk

from firmwaretools.pycompat import runLongProcess
from firmwaretools.trace_decorator import decorate, traceLog, getLog

moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")


decorate(traceLog())
def getSelectionPaths(treeview):
    def func(model, path, iterator, data):
        model = None
        iterator = None
        data.append(path)

    paths = []
    treeselection = treeview.get_selection()
    treeselection.selected_foreach(func, paths)
    return paths

decorate(traceLog())
def gtkYield():
    # process gui events during long-running loops
    # so that we are more responsive
    while gtk.events_pending():
        gtk.main_iteration(False)


decorate(traceLog())
def runLongProcessGtk(function, args=None, kargs=None, waitLoopFunction=None):
    decorate(traceLog())
    def myFunc():
        # can access outer function variables
        if waitLoopFunction is not None:
            waitLoopFunction()
        gtkYield() # make sure current GUI is fully displayed

    return runLongProcess(function, args, kargs, waitLoopFunction=myFunc)
