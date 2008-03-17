#                                               -*- Autoconf -*-
# vim:tw=0:et:ts=4:sw=4
# Process this file with autoconf to produce a configure script.

####################################
# change version here.
AC_INIT([firmware-tools],[2.1.0])

temp_RELEASE_NAME=firmware-tools
temp_RELEASE_MAJOR=2
temp_RELEASE_MINOR=1
temp_RELEASE_SUBLEVEL=0
temp_RELEASE_EXTRALEVEL=
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

# update 'real' variables from the temp variable names.
# do this at the end of the file so that they A) are not overwitten by other
# autoconf stuff, and B) so that user can override on cmdline
for i in RELEASE_NAME RELEASE_MAJOR RELEASE_MINOR RELEASE_SUBLEVEL RELEASE_EXTRALEVEL
do
    varname=temp_$i
    if test -z "${!i}"; then
        eval $i=${!varname}; export $i
    fi
done

if test -z "$RELEASE_RPM_EXTRALEVEL"; then
    if test -z "$RELEASE_EXTRALEVEL"; then
        RELEASE_RPM_EXTRALEVEL=%{nil}
    else
        RELEASE_RPM_EXTRALEVEL=$RELEASE_EXTRALEVEL
    fi
fi

PACKAGE=$RELEASE_NAME
PACKAGE_VERSION=[`echo ${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}`]
PACKAGE_STRING=[`echo ${RELEASE_NAME} ${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}`]
VERSION=$PACKAGE_VERSION

cat confdefs.h |
    grep -v 'define PACKAGE_VERSION ' |
    grep -v 'define PACKAGE_STRING '  > confdefs.new
mv confdefs.new confdefs.h
cat >>confdefs.h <<_ACEOF 
#define PACKAGE_VERSION "$PACKAGE_VERSION"
#define PACKAGE_STRING "$PACKAGE_STRING"
_ACEOF

AC_SUBST([RELEASE_NAME RELEASE_MAJOR RELEASE_MINOR RELEASE_SUBLEVEL RELEASE_EXTRALEVEL RELEASE_RPM_EXTRALEVEL])

# this is used by the autobuilder hook to determine the version we built
echo "PACKAGE_NAME='$PACKAGE_NAME'" > version
echo "PACKAGE_VERSION='$PACKAGE_VERSION'" >> version
echo "PACKAGE_STRING='$PACKAGE_STRING'" >> version

# firmware-tools oddity: package name cannot contain '-', so we have to fix it
pkgpythondir=\${pythondir}/firmwaretools
pkgpyexecdir=\${pyexecdir}/firmwaretools

# generate files and exit
AC_CONFIG_FILES([ Makefile pkg/${PACKAGE_NAME}.spec ])
AC_OUTPUT

