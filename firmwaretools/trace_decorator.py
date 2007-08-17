# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:

import inspect
import sys
import traceback
import types
from decorator import decorator

# levels:
#   0: Nothing
#   1: Basic
#   3: Detailed
#   9: ENTER/LEAVE

debug = {}

# TODO: convert this to use a logging object
def dprint(message, msgLevel=1, outLevel=None):
    if outLevel is None:
        e = traceback.extract_stack(limit=2)
        function = str(e[0][2])
        # get function object pointer for whatever called us
        global debug
        outLevel=debug.get("__main__", 0)
        outLevel=debug.get(function, outLevel)
        try:
            f = inspect.currentframe().f_back.f_globals[function]
            outLevel=debug.get(f.func_dict.get("module", function), outLevel)
        except KeyError:
            pass

    if outLevel >= msgLevel:
        sys.stderr.write(message)

#@decorator
def trace(f, *args, **kw):
    # search path for outLevel
    #   - debug[module]
    #   - debug[f.func_name]
    #   - debug['__main__']
    #   - 0
    global debug
    outLevel=debug.get("__main__", 0)
    outLevel=debug.get(f.func_name, outLevel)
    outLevel=debug.get(f.func_dict.get("module", f.func_name), outLevel)

    msgLevel=9
    dprint("ENTER: %s(%s, %s)\n" % (f.func_name, args, kw), msgLevel=msgLevel, outLevel=outLevel)
    try:
        result = "Bad exception raised: Exception was not a derived class of 'Exception'"
        try:
            result = f(*args, **kw)
        except Exception, e:
            result = "EXCEPTION RAISED"
            dprint( "EXCEPTION: %s\n" % e, msgLevel=msgLevel, outLevel=outLevel)
            raise
    finally:
        dprint( "LEAVE %s --> %s\n\n" % (f.func_name, result), msgLevel=msgLevel, outLevel=outLevel)

    return result

# helper function so we can use back-compat format but not be ugly
def decorateAllFunctions(module):
    methods = [ method for method in dir(module)
            if isinstance(getattr(module, method), types.FunctionType)
            ]
    for i in methods:
        setattr(module, i, trace(getattr(module,i)))

# backwards compat
trace = decorator(trace)

def setModule(module):
    def newFunc(func):
        func.func_dict['module'] = module
        return func
    return newFunc

