#!/bin/sh
# vim:et:ai:ts=4:sw=4:filetype=sh:tw=0

set -x

cur_dir=$(cd $(dirname $0); pwd)
cd $cur_dir/../

umask 002

[ -n "$LIBSMBIOS_TOPDIR" ] ||
    LIBSMBIOS_TOPDIR=/var/ftp/pub/Applications/libsmbios/

. version.mk
RELEASE_VERSION=${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}
RELEASE_STRING=${RELEASE_NAME}-${RELEASE_VERSION}
DEST=$LIBSMBIOS_TOPDIR/download/${RELEASE_NAME}/$RELEASE_STRING/

set -e

git tag -u libsmbios -m "tag for official release: $RELEASE_STRING" v${RELEASE_VERSION}

make clean tarball srpm

mkdir -p $DEST
for i in dist/*.tar.{gz,bz2} dist/*.zip dist/*.src.rpm; do
    [ -e $i ] || continue
    [ ! -e $DEST/$(basename $i) ] || continue
    cp $i $DEST
done

/var/ftp/pub/yum/dell-repo/software/_tools/upload_rpm.sh dist/${RELEASE_STRING}-${RPM_RELEASE}*.src.rpm

git push --tags origin master:master
