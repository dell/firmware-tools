#!/usr/bin/python2
# VIM declarations
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

  #############################################################################
  #
  # Copyright (c) 2003 Dell Computer Corporation
  #
  #############################################################################
"""
"""
import distutils.core 
import glob
import os

###################################################################
#
# WARNING
#
# These are all automatically replaced by the release script.
# START = Do not edit manually
RELEASE_MAJOR="1"
RELEASE_MINOR="2"
RELEASE_SUBLEVEL="1"
RELEASE_EXTRALEVEL=""
#
# END = Do not edit manually
#
###################################################################

# override from makefile environment vars, if necessary
for i in ("RELEASE_MAJOR", "RELEASE_MINOR", "RELEASE_SUBLEVEL", "RELEASE_EXTRALEVEL",):
    if os.environ.get(i):
        globals()[i] = os.environ.get(i)

gen_scripts = [
    "bin/inventory_firmware", "bin/bootstrap_firmware", "bin/update_firmware", "bin/apply_updates"
    ]

doc_files = [ "COPYING-GPL", "COPYING-OSL", "README", ]

MANIFEST = open( "MANIFEST.in", "w+" )
MANIFEST.write( "#BEGIN AUTOGEN\n" )
# include binaries
for i in gen_scripts:
    MANIFEST.write("include " + i + "\n" )
for i in doc_files:
    MANIFEST.write("include " + i + "\n" )

MANIFEST.write("include doc/firmware.conf\n" )
MANIFEST.write("include version.mk\n" )
MANIFEST.write("include firmware-tools.spec\n" )
MANIFEST.write( "#END AUTOGEN\n" )
MANIFEST.close()

dataFileList = []
dataFileList.append(  ("/usr/bin/", gen_scripts ) )
dataFileList.append(  ("/etc/firmware/", ["doc/firmware.conf",] ) )

distutils.core.setup (
        name = 'firmware-tools',
        version = '%s.%s.%s%s' % (RELEASE_MAJOR, RELEASE_MINOR, RELEASE_SUBLEVEL, RELEASE_EXTRALEVEL,),

        description = 'Scripts and tools to manage firmware and BIOS updates.',
        author="Libsmbios team",
        author_email="libsmbios-devel@lists.us.dell.com",
        url="http://linux.dell.com/libsmbios/main/",

        package_dir={'': 'pymod'},
        packages=[''],

        ext_modules = [ ],
        data_files=dataFileList,
        scripts=[],
)


