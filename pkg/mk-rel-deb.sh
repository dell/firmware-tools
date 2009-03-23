#!/bin/sh
# vim:et:ai:ts=4:sw=4:filetype=sh:

set -x

cur_dir=$(cd $(dirname $0); pwd)
cd $cur_dir/../

umask 002

[ -n "$APT_REPO" ] || 
    APT_REPO=/var/ftp/pub/yum/dell-repo/software/debian/incoming

set -e

chmod -R +w _builddir ||:
rm -rf _builddir

./autogen.sh

mkdir _builddir
pushd _builddir
../configure

eval "$(make get-version)"
make deb


# need to port the following to pbuilder
mkdir -p ${APT_REPO}/etch-i386/${PACKAGE_NAME}/${PACKAGE_VERSION}-${DEB_RELEASE}/

DEST=${APT_REPO}/etch-i386/${PACKAGE_NAME}/${PACKAGE_VERSION}-${DEB_RELEASE}/
for file in build/*.deb build/*.dsc build/*.diff.gz build/*.tar.gz
do
    [ -e $DEST/$(basename $file) ] || cp $file $DEST/
done

