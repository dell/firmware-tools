#!/bin/sh
set -e

# run this script to create all the autotools fluff

DIR=$(cd $(dirname $0); pwd)
pushd $DIR

aclocal
automake --force --foreign --add-missing -c
autoconf --force

popd

$DIR/configure
