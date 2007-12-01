# vim:noexpandtab:autoindent:tabstop=8:shiftwidth=8:filetype=make:nocindent:tw=0:

AUTOMAKE_OPTIONS = subdir-objects
SUBDIRS = 

# dont move these 5 lines, as this is how we override the autoconf version and package name
RELEASE_NAME=@RELEASE_NAME@
RELEASE_MAJOR=@RELEASE_MAJOR@
RELEASE_MINOR=@RELEASE_MINOR@
RELEASE_SUBLEVEL=@RELEASE_SUBLEVEL@
RELEASE_EXTRALEVEL=@RELEASE_EXTRALEVEL@

RELEASE_VERSION = $(RELEASE_MAJOR).$(RELEASE_MINOR).$(RELEASE_SUBLEVEL)$(RELEASE_EXTRALEVEL)
RELEASE_STRING = $(RELEASE_NAME)-$(RELEASE_VERSION)
VERSION = $(RELEASE_VERSION)
PACKAGE = $(RELEASE_NAME)

CLEANFILES=$(RELEASE_NAME)-*.tar.gz $(RELEASE_NAME)-*.tar.bz2 $(RELEASE_NAME)-*.rpm _buildtemp version
DISTCLEANFILES=*~

EXTRA_DIST =
bin_PROGRAMS=
EXTRA_PROGRAMS=

CLEANFILES += $(EXTRA_PROGRAMS)

pkgetcdir = $(sysconfdir)/firmware/
nodist_pkgetc_DATA = etc/firmware/firmware.conf

EXTRA_DIST += etc doc glade pkg/debian test yum-plugin COPYING-GPL COPYING-OSL COPYING.LIB

dist_sbin_SCRIPTS = \
	bin/bootstrap_firmware  \
	bin/inventory_firmware  \
	bin/inventory_firmware_gui  \
	bin/update_firmware

nodist_pkgdata_DATA = glade/inventory_firmware_gui.glade

pkgpython_PYTHON = \
	firmwaretools/__init__.py       \
	firmwaretools/bootstrap_pci.py  \
	firmwaretools/clifuncs.py       \
	firmwaretools/decorator.py      \
	firmwaretools/dep_parser.py     \
	firmwaretools/guihelpers.py     \
	firmwaretools/mockpackage.py    \
	firmwaretools/mockrepository.py \
	firmwaretools/package.py   	\
	firmwaretools/ply_lex.py   	\
	firmwaretools/ply_yacc.py	\
	firmwaretools/pycompat.py	\
	firmwaretools/repository.py	\
	firmwaretools/trace_decorator.py


REPLACE_VARS_ON_INSTALL= 		   \
	$(sbindir)/bootstrap_firmware  	   \
	$(sbindir)/inventory_firmware  	   \
	$(sbindir)/inventory_firmware_gui  \
	$(sbindir)/update_firmware
install-exec-hook:
	for i in $(REPLACE_VARS_ON_INSTALL); do      \
                file=$(DESTDIR)/$$i                     ;\
                perl -p -i -e 's|^__VERSION__=.*|__VERSION__="$(RELEASE_VERSION)"|' $$file ;\
                perl -p -i -e 's|^SYSCONFDIR=.*|SYSCONFDIR="$(sysconfdir)"|' $$file        ;\
                perl -p -i -e 's|^PYTHONDIR=.*|PYTHONDIR="$(pythondir)"|' $$file           ;\
                perl -p -i -e 's|^PKGPYTHONDIR=.*|PKGPYTHONDIR="$(pkgpythondir)"|' $$file  ;\
                perl -p -i -e 's|^PKGDATADIR=.*|PKGDATADIR="$(pkgdatadir)"|' $$file        ;\
        done

rpm: dist
	rm -rf _build
	mkdir -p _build/{SOURCES,BUILD,RPMS,SRPMS,SPECS}
	cp pkg/$(PACKAGE_NAME).spec _build/SPECS
	cp $(PACKAGE_NAME)*.tar.gz  _build/SOURCES
	rpmbuild --define "_topdir $$PWD/_build" -ba --nodeps _build/SPECS/$(PACKAGE_NAME).spec
	find _build/{RPMS,SRPMS} -name \*.rpm -exec mv {} . \;
	rm -rf _build

srpm: dist
	rm -rf _build
	mkdir -p _build/{SOURCES,BUILD,RPMS,SRPMS,SPECS}
	cp pkg/$(PACKAGE_NAME).spec _build/SPECS
	cp $(PACKAGE_NAME)*.tar.gz  _build/SOURCES
	rpmbuild --define "_topdir $$PWD/_build" -bs --nodeps _build/SPECS/$(PACKAGE_NAME).spec
	find _build/{RPMS,SRPMS} -name \*.rpm -exec mv {} . \;
	rm -rf _build


