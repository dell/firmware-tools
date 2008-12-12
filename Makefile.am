# vim:noexpandtab:autoindent:tabstop=8:shiftwidth=8:filetype=make:nocindent:tw=0:

include Makefile-std

pkgconfdir = $(sysconfdir)/firmware/
nodist_pkgconf_DATA = etc/firmware/firmware.conf

EXTRA_DIST += etc doc glade test yum-plugin COPYING-GPL COPYING-OSL COPYING.LIB

TESTS = test/testAll.py
nodist_check_SCRIPTS = test/testAll.py

dist_sbin_SCRIPTS = \
	bin/firmwaretool  \
	bin/inventory_firmware_gui

nodist_pkgdata_DATA = glade/inventory_firmware_gui.glade

pkgpython_PYTHON = \
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
	firmwaretools/trace_decorator.py \
	firmwaretools/peak_util_decorators.py	\
	firmwaretools/compat_subprocess.py	\
	firmwaretools/generated/__init__.py

clidir = $(datadir)/$(PACKAGE)
cli_PYTHON = \
	ft-cli/cli.py	\
	ft-cli/ftcommands.py	\
	ft-cli/ftmain.py	\
	ft-cli/guihelpers.py

plugindir = $(clidir)/plugins
plugin_PYTHON = \
	ft-cli/plugins/bootstrap_cmd.py	\
	ft-cli/plugins/inventory_cmd.py	\
	ft-cli/plugins/listplugins_cmd.py	\
	ft-cli/plugins/update_cmd.py

__VERSION__=$(VERSION)
PYTHONDIR=$(pythondir)
PKGDATADIR=$(pkgdatadir)
PKGGLADEDIR=$(pkgdatadir)
SYSCONFDIR=$(sysconfdir)
PKGPYTHONDIR=$(pkgpythondir)
DATADIR=$(datadir)
PKGCONFDIR=$(pkgconfdir)
REPLACE_VARS+= __VERSION__ PYTHONDIR PKGDATADIR PKGGLADEDIR SYSCONFDIR PKGPYTHONDIR DATADIR PKGCONFDIR
DATA_HOOK_REPLACE += 		   \
	$(sbindir)/firmwaretool  	   \
	$(sbindir)/inventory_firmware_gui

EXTRA_DIST += firmwaretools/__init__.py
DISTCLEANFILES +=   firmwaretools/generated/__init__.py
firmwaretools/generated/__init__.py: firmwaretools/__init__.py configure Makefile config.status
	mkdir -p $$(dirname $@) ||:
	cp $< $@
	for var in $(REPLACE_VARS)	;\
	do	\
		perl -p -i -e "s|^$$var\s*=.*|$$var=\"$${!var}\"|"  $@;\
	done
