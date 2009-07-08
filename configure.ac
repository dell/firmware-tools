#                                               -*- Autoconf -*-
# vim:tw=0:et:ts=4:sw=4
# Process this file with autoconf to produce a configure script.

##############################################################################
#  RELEASE VARIABLES
##############################################################################
#
# The following variables define the libsmbios release version.
#   This is the "marketing" version, or overall version of the project.
#   This doesnt have anything in relation to the ABI versions of individual
#   libraries, which are defined further below.
#
m4_define([release_major_version], [2])
m4_define([release_minor_version], [1])
m4_define([release_micro_version], [8])
# if you define any "extra" version info, include a leading dot (".")
m4_define([release_extra_version], [])

AC_INIT([firmware-tools],
          [release_major_version().release_minor_version().release_micro_version()release_extra_version()])

####################################

AC_PREREQ(2.61)
AC_CONFIG_AUX_DIR([pkg])
AM_INIT_AUTOMAKE([1.9 subdir-objects tar-ustar dist-bzip2 dist-lzma no-define foreign])
AM_MAINTAINER_MODE

# Checks for programs.
AC_PROG_INSTALL

# automake macros
AM_PATH_PYTHON

# versioning
AC_SUBST([RELEASE_MAJOR], [release_major_version()])
AC_SUBST([RELEASE_MINOR], [release_minor_version()])
AC_SUBST([RELEASE_MICRO], [release_micro_version()])
AC_SUBST([RELEASE_EXTRA], [release_extra_version()])
AC_SUBST([RELEASE_RPM_EXTRA], [%{nil}])
if test -n "$RELEASE_EXTRA"; then
    RELEASE_RPM_EXTRA=$RELEASE_EXTRA
fi

# firmware-tools oddity: package name cannot contain '-', so we have to fix it
pkgpythondir=\${pythondir}/firmwaretools
pkgpyexecdir=\${pyexecdir}/firmwaretools

# generate files and exit
AC_CONFIG_FILES([Makefile])
AC_CONFIG_FILES([pkg/${PACKAGE_NAME}.spec], [], [PACKAGE_NAME='$PACKAGE_NAME'])
AC_OUTPUT

