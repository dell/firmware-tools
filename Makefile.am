# vim:noexpandtab:autoindent:tabstop=8:shiftwidth=8:filetype=make:nocindent:tw=0:

include Makefile-std

pkgetcdir = $(sysconfdir)/firmware/
nodist_pkgetc_DATA = etc/firmware/firmware.conf

EXTRA_DIST += etc doc glade pkg/debian test yum-plugin COPYING-GPL COPYING-OSL COPYING.LIB

TESTS = test/testAll.py
nodist_check_SCRIPTS = test/testAll.py

dist_sbin_SCRIPTS = \
	bin/firmwaretool  \
	bin/inventory_firmware_gui

nodist_pkgdata_DATA = glade/inventory_firmware_gui.glade

pkgpython_PYTHON = \
	firmwaretools/__init__.py       \
	firmwaretools/bootstrap_pci.py  \
	firmwaretools/dep_parser.py     \
	firmwaretools/errors.py     \
	firmwaretools/i18n.py     \
	firmwaretools/mockpackage.py    \
	firmwaretools/mockrepository.py \
	firmwaretools/package.py   	\
	firmwaretools/plugins.py   	\
	firmwaretools/ply_lex.py   	\
	firmwaretools/ply_yacc.py	\
	firmwaretools/pycompat.py	\
	firmwaretools/repository.py	\
	firmwaretools/trace_decorator.py

clidir = $(datadir)/$(PACKAGE)
cli_PYTHON = \
	ft-cli/cli.py	\
	ft-cli/ftcommands.py	\
	ft-cli/ftmain.py	\
	ft-cli/guihelpers.py

plugindir = $(clidir)/plugins
plugin_PYTHON = \
	ft-cli/plugins/bootstrap.py	\
	ft-cli/plugins/inventory.py	\
	ft-cli/plugins/listplugins.py	\
	ft-cli/plugins/update.py

REPLACE_VARS_ON_INSTALL= 		   \
	$(sbindir)/firmwaretool  	   \
	$(sbindir)/inventory_firmware_gui  \
	$(pkgpythondir)/__init__.py
