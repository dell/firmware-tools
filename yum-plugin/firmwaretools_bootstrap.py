# vim:tw=0:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
Yum plugin to automatically bootstrap packages.
"""

from yum.plugins import TYPE_CORE
import yum.Errors

version="1.5.6"
requires_api_version = '2.1'
plugin_type = TYPE_CORE

import ConfigParser
import os
import sys

global firmwaretools
import firmwaretools.clifuncs
import firmwaretools.trace_decorator as trace_decorator

if os.environ.get('DEBUG_BOOTSTRAP') == "1":
    import firmwaretools.mockpackage

if os.environ.get('DEBUG'):
    trace_decorator.debug["__main__"] = 9

def exclude_hook(conduit):
    ini = ConfigParser.ConfigParser()
    firmwaretools.clifuncs.getConfig(ini, firmwaretools.clifuncs.configLocations)
    for pkg in firmwaretools.clifuncs.runBootstrapInventory(ini):
        # see if it is a normal package name
        try:
            conduit._base.install(name=pkg.name)
            continue
        except yum.Errors.InstallError, e:
            pass

        # isnt a straight name, need to see if it is a dep
        try:
            mypkgs = conduit._base.returnPackagesByDep(pkg.name)
            mybestpkgs = conduit._base.bestPackagesFromList(mypkgs)
            for mypkg in mybestpkgs:
                if conduit._base._installable(mypkg, True):
                    conduit._base.install(mypkg)
        except yum.Errors.YumBaseError, e:
            pass

trace_decorator.decorateAllFunctions(sys.modules[__name__])
