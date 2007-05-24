#!/bin/sh

CURDIR=$(cd $(dirname $0); pwd)
cd $CURDIR/..
umask 002

# order is important here.
. version.mk
# reset RELEASE_EXTRALEVEL before it gets pulled into RELEASE_STRING/etc
[ -z "$BUILD_CYCLE" ] || export RELEASE_EXTRALEVEL=.${BUILD_CYCLE}.autobuild
RELEASE_VERSION=${RELEASE_MAJOR}.${RELEASE_MINOR}.${RELEASE_SUBLEVEL}${RELEASE_EXTRALEVEL}
RELEASE_STRING=${RELEASE_NAME}-${RELEASE_VERSION}
export RELEASE_VERSION  RELEASE_STRING  RELEASE_NAME  RELEASE_MAJOR RELEASE_MINOR  RELEASE_SUBLEVEL  RELEASE_EXTRALEVEL  RPM_RELEASE DEB_RELEASE

set -e

if [ -x $CURDIR/ab-host-$(hostname)-$(id -un).sh ]; then
    $CURDIR/ab-host-$(hostname)-$(id -un).sh
elif [ -x $CURDIR/ab-host-$(hostname).sh ]; then
    $CURDIR/ab-host-$(hostname).sh
elif [ -x $CURDIR/ab-generic.sh ]; then
    $CURDIR/ab-generic.sh
fi
