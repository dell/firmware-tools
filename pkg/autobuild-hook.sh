#!/bin/sh

CURDIR=$(cd $(dirname $0); pwd)

[ -z "$BUILD_CYCLE" ] || export RELEASE_EXTRALEVEL=.${BUILD_CYCLE}.autobuild
if [ -x $CURDIR/ab-host-$(hostname).sh ]; then
    $CURDIR/ab-host-$(hostname).sh
fi
