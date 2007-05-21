#!/bin/sh
# vim:et:ai:ts=4:sw=4:filetype=sh:

# the purpose of this script is to hook into git-autobuilder. It is
# called by autobuild-hook.sh as a host-specific builder. It builds RPMS
# and places them into plague.

set -e
set -x

PLAGUE_BUILDS="fc5 fc6 fcdev rhel3 rhel4 rhel5 sles9 sles10"
PREFIX=testing_

cur_dir=$(cd $(dirname $0); pwd)
cd $cur_dir/..

echo "FOO: $RELEASE_EXTRALEVEL"
make -e tarball srpm

scp -4qr -i ~/.ssh/id_dsa_fwupdate *.src.rpm autobuilder@mock.linuxdev.us.dell.com:~/queue/

for i in *.src.rpm
do
	file=$(basename $i)
	for distro in $PLAGUE_BUILDS
	do
		ssh -4 -i ~/.ssh/id_dsa_fwupdate autobuilder@mock.linuxdev.us.dell.com plague-client build \~/queue/$file ${PREFIX}${distro}
		sleep 5
	done
    ssh -4 -i ~/.ssh/id_dsa_fwupdate autobuilder@mock.linuxdev.us.dell.com rm \~/queue/$file
done
