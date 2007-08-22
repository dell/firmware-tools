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
import os
import re
import sys
from trace_decorator import dprint, decorateAllFunctions

import package

# new standard entry point. 
def BootstrapGenerator(): 
    for i in lspciGeneratorFactory():
        # TODO: parse lspci output to get device name for displayname
        # TODO: add pciDbdf
        yield package.PciDevice(name=process_pci_dev(i), version='unknown', displayname='Unknown PCI Device', pciDbdf="foo")

# a regular expression to parse 'lspci -n -m' output
#                       "Class NNNN" "NNNN" "NNNN" -rXX... "NNNN" "NNNN"
pciRe = re.compile(r'^.*?"[\w ]+"\s"(\w+)"\s"(\w+)"\s.*?"(\w*)"\s"(\w*)"')

def splodeLine(line):
    ven = dev = subven = subdev = None
    res = pciRe.search(line)
    if res:
        ven = res.group(1)
        dev = res.group(2)
        subven = res.group(3)
        subdev = res.group(4)
        
    return [ven, dev, subven, subdev]

def process_pci_dev(line):
    ven, dev, subven, subdev = splodeLine(line)
    item = "pci_firmware(ven_0x%s_dev_0x%s" % (ven, dev)
    if subven and subdev:
        item = item + "_subven_0x%s_subdev_0x%s" % (subven, subdev)
    item = item + ")"
    return item

def lspciGenerator():
    for i in ("/sbin/lspci", "/usr/bin/lspci"):
        if os.path.exists(i):
            lspciPath=i
            break

    fd = os.popen("%s -n -m 2>/dev/null" % lspciPath, "r")
    for line in fd:
        yield line
    fd.close()

# returns a generator function
unit_test_mode = 0
def lspciGeneratorFactory():
    global unit_test_mode
    if not unit_test_mode:
        return lspciGenerator()
    else:
        return mockLspciGenerator()


decorateAllFunctions(sys.modules[__name__])


