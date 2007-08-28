# vim:tw=0:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:
"""
Yum plugin to automatically bootstrap packages.

The purpose of this plugin is to automatically always add firmware-tools
bootstrap to the yum transaction. Before this was done by an explicit added
step. The instructions used to say:

# yum install $(bootstrap_firmware)

Normal bootstrap_firmware output looks like this:

# bootstrap_firmware 
pci_firmware(ven_0x10de_dev_0x00e1)
pci_firmware(ven_0x10de_dev_0x00e0_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e4_subven_0x10de_subdev_0x0c11)
pci_firmware(ven_0x10de_dev_0x00e7_subven_0x10de_subdev_0x0c11)
... cut ...

The yum install command would effectively look up each pci_firmware(...) line
and look for RPM packages that had "Provides:" tags for the corresponding
firmware.

The purpose of this plugin is to remove that additional step. Now anytime the
user says "yum upgrade", they will automatically get the latest bootstrap
packages installed on their system.
"""

from yum.plugins import TYPE_CORE
import yum.Errors

version="1.5.7"
requires_api_version = '2.1'
plugin_type = TYPE_CORE

import ConfigParser
import os
import sys

global firmwaretools
import firmwaretools.clifuncs
import firmwaretools.trace_decorator as trace_decorator

if os.environ.get('DEBUG_BOOTSTRAP') == "1":
    # provide a made-up set of bootstrap packages rather than real one.
    # useful for testing.
    import firmwaretools.mockpackage

if os.environ.get('DEBUG'):
    # activate function tracing
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
            mypkg = conduit._base.returnPackageByDep(pkg.name)
            conduit._base.install(mypkg)
        except yum.Errors.YumBaseError, e:
            pass

# this decorates all functions in this module to provide tracing if it is enabled.
trace_decorator.decorateAllFunctions(sys.modules[__name__])
