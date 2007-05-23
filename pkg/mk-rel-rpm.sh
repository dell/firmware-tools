#!/bin/sh
# vim:et:ai:ts=4:sw=4:filetype=sh:

set -e
set -x

PLAGUE_BUILDS="fc5 fc6 fcdev rhel3 rhel4 rhel5 sles9 sles10"
PREFIX=

cur_dir=$(cd $(dirname $0); pwd)
cd $cur_dir/../

[ -n "$LIBSMBIOS_TOPDIR" ] ||
    LIBSMBIOS_TOPDIR=/var/ftp/pub/Applications/libsmbios/

. version.mk
RELEASE_VERSION=${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}
RELEASE_STRING=${RELEASE_NAME}-${RELEASE_VERSION}
DEST=$LIBSMBIOS_TOPDIR/download/${RELEASE_NAME}/$RELEASE_STRING/

make tarball srpm

mkdir -p $DEST
for i in *.tar.{gz,bz2} *.zip *.src.rpm; do
    [ -e $i ] || continue
    [ ! -e $DEST/$(basename $i) ] || continue
    cp $i $DEST
done

for file in ./*.src.rpm
do
	for distro in $PLAGUE_BUILDS
	do
		plague-client build $file ${PREFIX}${distro}
		sleep 5
	done
    rm $file
done
