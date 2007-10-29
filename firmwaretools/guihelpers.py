# vim:ai:ts=4:sw=4:et:filetype=python:

#future imports always first
from __future__ import generators

# std python stuff
import gtk

from firmwaretools.pycompat import runLongProcess

def getSelectionPaths(treeview):
    def func(model, path, iterator, data):
        model = None
        iterator = None
        data.append(path)

    paths = []
    treeselection = treeview.get_selection()
    treeselection.selected_foreach(func, paths)
    return paths

def gtkYield():
    # process gui events during long-running loops
    # so that we are more responsive
    while gtk.events_pending():                        
        gtk.main_iteration(False)


def runLongProcessGtk(function, args=None, kargs=None, waitLoopFunction=None):
    def myFunc():
        # can access outer function variables
        if waitLoopFunction is not None:
            waitLoopFunction()
        gtkYield() # make sure current GUI is fully displayed

    return runLongProcess(function, args, kargs, waitLoopFunction=myFunc)
