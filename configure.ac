#                                               -*- Autoconf -*-
# vim:tw=0:et:ts=4:sw=4
# Process this file with autoconf to produce a configure script.

####################################
# change version here.
AC_INIT([firmware-tools],[unconfigured-version])

test -n "$RELEASE_MAJOR"      || RELEASE_MAJOR=2
test -n "$RELEASE_MINOR"      || RELEASE_MINOR=1
test -n "$RELEASE_MICRO"      || RELEASE_MICRO=5
test -n "$RELEASE_EXTRA"      || RELEASE_EXTRA=
####################################

AC_PREREQ(2.61)
AC_CONFIG_AUX_DIR([pkg])
AM_INIT_AUTOMAKE(1.9 tar-ustar no-define)
AM_MAINTAINER_MODE

# Checks for programs.
AC_PROG_INSTALL

# automake macros
AM_PATH_PYTHON

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

if test -z "$RELEASE_RPM_EXTRA"; then
    if test -z "$RELEASE_EXTRA"; then
        RELEASE_RPM_EXTRA=%{nil}
    else
        RELEASE_RPM_EXTRA=$RELEASE_EXTRA
    fi
fi

AC_SUBST([RELEASE_MAJOR])
AC_SUBST([RELEASE_MINOR])
AC_SUBST([RELEASE_MICRO])
AC_SUBST([RELEASE_EXTRA])
AC_SUBST([RELEASE_RPM_EXTRA])

# firmware-tools oddity: package name cannot contain '-', so we have to fix it
pkgpythondir=\${pythondir}/firmwaretools
pkgpyexecdir=\${pyexecdir}/firmwaretools

# generate files and exit
AC_CONFIG_FILES([ Makefile pkg/${PACKAGE_NAME}.spec ])
AC_OUTPUT

