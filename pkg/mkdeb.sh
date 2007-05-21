#!/bin/sh
# vim:et:ai:ts=4:sw=4:filetype=sh:

set -e
set -x

# dont run this from radon.

cur_dir=$(cd $(dirname $0); pwd)
cd $cur_dir/../

[ -n "$LIBSMBIOS_TOPDIR" ] ||
    LIBSMBIOS_TOPDIR=/var/ftp/pub/Applications/libsmbios/

[ -n "$APT_REPO" ] || 
    APT_REPO=/var/ftp/pub/yum/dell-repo/software/debian/

. version.mk
RELEASE_VERSION=${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}
RELEASE_STRING=${RELEASE_NAME}-${RELEASE_VERSION}
DEST=$LIBSMBIOS_TOPDIR/download/${RELEASE_NAME}/$RELEASE_STRING/

make distclean
make deb

# need to port the following to pbuilder
mkdir -p ${APT_REPO}/etch-i386/${RELEASE_NAME}/${RELEASE_VERSION}-${DEB_RELEASE}/
cp build/* ${APT_REPO}/etch-i386/${RELEASE_NAME}/${RELEASE_VERSION}-${DEB_RELEASE}/


