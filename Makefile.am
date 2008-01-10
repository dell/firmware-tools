# vim:noexpandtab:autoindent:tabstop=8:shiftwidth=8:filetype=make:nocindent:tw=0:

include Makefile-std

pkgetcdir = $(sysconfdir)/firmware/
nodist_pkgetc_DATA = etc/firmware/firmware.conf

EXTRA_DIST += etc doc glade pkg/debian test yum-plugin COPYING-GPL COPYING-OSL COPYING.LIB

TESTS = test/testAll.py
nodist_check_SCRIPTS = test/testAll.py

dist_sbin_SCRIPTS = \
	bin/bootstrap_firmware  \
	bin/inventory_firmware  \
	bin/inventory_firmware_gui  \
	bin/update_firmware

nodist_pkgdata_DATA = glade/inventory_firmware_gui.glade

pkgpython_PYTHON = \
	firmwaretools/__init__.py       \
	firmwaretools/bootstrap_pci.py  \
	firmwaretools/config.py       \
	firmwaretools/clifuncs.py       \
	firmwaretools/dep_parser.py     \
	firmwaretools/errors.py     \
	firmwaretools/guihelpers.py     \
	firmwaretools/i18n.py     \
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
	$(sbindir)/update_firmware	   \
	$(pkgpythondir)/clifuncs.py	   \
	$(pkgpythondir)/config.py	   \
	$(pkgpythondir)/__init__.py


