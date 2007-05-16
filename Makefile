#!/usr/bin/make 
# vim:noet:ai:ts=8:sw=8:filetype=make:nocindent:textwidth=0:
#
# Copyright (C) 2005 fwupdate.com
#  by Admin <admin@fwupdate.com>
# Licensed under the Open Software License version 2.1 
# 
# Alternatively, you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 2 of the License, 
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# Note that all 'module.mk' files are "include"-ed in this file and
# fall under the same license.
# 
# This is a standard non-recursive make system.
#

  include version.mk
  RELEASE_VERSION := $(RELEASE_MAJOR).$(RELEASE_MINOR).$(RELEASE_SUBLEVEL)$(RELEASE_EXTRALEVEL)
  RELEASE_STRING := $(RELEASE_NAME)-$(RELEASE_VERSION)

  BUILD_DATE := $(shell date "+%Y-%m-%d %H:%M:%S")

#--------------------------------------------
# Generic Makefile stuff is below. You
#  should not have to modify any of the stuff
#  below.
#--------------------------------------------

  MODULES :=
  default: all

#Included makefiles will add their deps for each stage in these vars:
  CLEAN_LIST :=
  CLEAN_DEPS :=

  DISTCLEAN_LIST :=
  DISTCLEAN_DEPS :=

  ALL_DEPS :=

#Define the top-level build directory
  BUILDDIR := $(shell pwd)

#Include the docs in the build
#  doc_FILES += COPYING INSTALL README

  all:  $(ALL_DEPS) 

  clean: clean_list $(CLEAN_DEPS) 
  clean_list:
	rm -rf $(CLEAN_LIST)

  distclean: clean distclean_list $(DISTCLEAN_DEPS) 
  distclean_list:
	rm -rf $(DISTCLEAN_LIST)

  CLEAN_LIST += dist rpm build MANIFEST*
  CLEAN_LIST += $(RELEASE_NAME)*.rpm $(RELEASE_NAME)*.tar.gz  $(RELEASE_NAME)*.zip
  CLEAN_LIST += $(shell find . -name .\#\* )
  CLEAN_LIST += $(shell find . -name core )
  CLEAN_LIST += $(shell find . -name .\*.swp )
  CLEAN_LIST += $(shell find . -name \*.pyc )

  .PHONY: all clean clean_list distclean distclean_list \
  		rpm unit_test tarball

SPEC=pkg/$(RELEASE_NAME).spec
# check that firmware-tools.spec has correct version info. force build if not.
G_RELEASE_MAJOR=$(shell grep "^%define major" $(SPEC) | awk '{print $$3}')
G_RELEASE_MINOR=$(shell grep "^%define minor" $(SPEC) | awk '{print $$3}')
G_RELEASE_SUBLEVEL=$(shell grep "^%define sub" $(SPEC) | awk '{print $$3}')
G_RELEASE_EXTRALEVEL=$(shell grep "^%define extralevel" $(SPEC) | awk '{print $$3}')
ifneq ($(G_RELEASE_MAJOR),$(RELEASE_MAJOR))
 .PHONY: $(SPEC) setup.py
endif
ifneq ($(G_RELEASE_MINOR),$(RELEASE_MINOR))
 .PHONY: $(SPEC) setup.py
endif
ifneq ($(G_RELEASE_SUBLEVEL),$(RELEASE_SUBLEVEL))
 .PHONY: $(SPEC) setup.py
endif
# convoluted. sorry.
ifneq ($(G_RELEASE_EXTRALEVEL),$(RELEASE_EXTRALEVEL))
 ifeq ($(G_RELEASE_EXTRALEVEL),%{nil})
  ifneq ($(RELEASE_EXTRALEVEL),)
  .PHONY: $(SPEC) setup.py
  endif
 else
  .PHONY: $(SPEC) setup.py
 endif
endif


$(SPEC): version.mk
	@echo Updating $@
	@cp -f $@ $@.new
	@perl -p -i -e 's/^%define major .*/%define major $(RELEASE_MAJOR)/' $@.new
	@perl -p -i -e 's/^%define minor .*/%define minor $(RELEASE_MINOR)/' $@.new
	@perl -p -i -e 's/^%define sub .*/%define sub $(RELEASE_SUBLEVEL)/' $@.new
	@perl -p -i -e 's/^%define rpm_release .*/%define sub $(RPM_RELEASE)/' $@.new
	@: # extralevel can be empty, so make rpm happy with conditional substitution
	@[ -z "$(RELEASE_EXTRALEVEL)" ] || perl -p -i -e 's/^%define extralevel .*/%define extralevel $(RELEASE_EXTRALEVEL)/' $@.new
	@[ -n "$(RELEASE_EXTRALEVEL)" ] || perl -p -i -e 's/^%define extralevel .*/%define extralevel %{nil}/' $@.new
	@diff -q $@ $@.new >/dev/null 2>&1 || mv -f $@.new $@
	@rm -f $@.new


setup.py: version.mk
	@echo Updating $@
	@cp $@ $@.new
	@perl -p -i -e 's/^RELEASE_MAJOR=.*/RELEASE_MAJOR="$(RELEASE_MAJOR)"/' $@.new
	@perl -p -i -e 's/^RELEASE_MINOR=.*/RELEASE_MINOR="$(RELEASE_MINOR)"/' $@.new
	@perl -p -i -e 's/^RELEASE_SUBLEVEL=.*/RELEASE_SUBLEVEL="$(RELEASE_SUBLEVEL)"/' $@.new
	@perl -p -i -e 's/^RELEASE_EXTRALEVEL=.*/RELEASE_EXTRALEVEL="$(RELEASE_EXTRALEVEL)"/' $@.new
	@diff -q $@ $@.new >/dev/null 2>&1 || mv -f $@.new $@
	@rm -f $@.new

PY_VER_UPDATES=bin/up2date_repo_autoconf yum-plugin/dellsysidplugin.py
$(PY_VER_UPDATES): version.mk
	@echo Updating $@
	@cp -f $@ $@.new
	@perl -p -i -e 's/^version=.*/version="$(RELEASE_VERSION)"/' $@.new
	@diff -q $@ $@.new >/dev/null 2>&1 || mv -f $@.new $@
	@rm -f $@.new

TARBALL=$(shell ls $(PWD)/$(RELEASE_STRING).tar.gz)

# to specify key if package is to be signed: make deb debsign=-k<keyname>
ifndef debsign
debsign=-uc -us
endif

DEBFILES= \
  build/$(RELEASE_NAME)_$(RELEASE_VERSION)-$(DEB_RELEASE)_$(DEBARCH).deb      \
  build/$(RELEASE_NAME)_$(RELEASE_VERSION)-$(DEB_RELEASE)_i386.changes      \
  build/$(RELEASE_NAME)_$(RELEASE_VERSION).dsc

# use debopts to do things like override maintainer email, etc.
deb: $(DEBFILES)
$(DEBFILES): $(RELEASE_STRING).tar.gz
	rm -rf build
	mkdir -p build
	tar zxvf $(TARBALL) -C build
	cp $(TARBALL) build/$(RELEASE_NAME)_$(RELEASE_VERSION).orig.tar.gz
	cp -a pkg/debian build/$(RELEASE_STRING)/
	chmod +x build/$(RELEASE_STRING)/debian/rules
	cd build/$(RELEASE_STRING)/ && debuild -rfakeroot $(debsign) $(debopts)

rpm: $(RELEASE_STRING)-$(RPM_RELEASE).$(RPM_TYPE).rpm
$(RELEASE_STRING)-$(RPM_RELEASE).$(RPM_TYPE).rpm: $(RELEASE_STRING).tar.gz
	mkdir -p build/{RPMS,SRPMS,SPECS,SOURCES,BUILD}
	rpmbuild --define "_topdir $(PWD)/build/" -ta $(TARBALL)
	mv build/RPMS/*/*.rpm $(BUILDDIR)
	mv build/SRPMS/*.rpm $(BUILDDIR)
	-rm -rf build/ dist/ MANIFEST*

srpm: $(RELEASE_STRING)-$(RPM_RELEASE).src.rpm
$(RELEASE_STRING)-$(RPM_RELEASE).src.rpm: $(RELEASE_STRING).tar.gz
	mkdir -p build/{RPMS,SRPMS,SPECS,SOURCES,BUILD}
	rpmbuild --define "_topdir $(PWD)/build/" -ts $(TARBALL)
	mv build/SRPMS/*.rpm $(BUILDDIR)
	-rm -rf build/ dist/ MANIFEST*

tarball: $(RELEASE_STRING).tar.gz
$(RELEASE_STRING).tar.gz: $(SPEC) setup.py $(PY_VER_UPDATES)
	-rm -rf MANIFEST*
	python ./setup.py sdist --dist-dir=$$(pwd)
	-rm -rf MANIFEST*

unit_test:
	@#do the following so that we don't end up running "build_libs" multiple times
	@# the first invocation will end up compiling everything, and subsequent 
	@# invocations will do nothing because everything is up to date.
	@echo "-------------------------"
	@echo " Running python tests..."
	@echo "-------------------------"
	@if [ -z "$(py_test)" ]; then 	\
		py_test=All		;\
	fi				;\
	if [ -e ./test/test$${py_test}.py ]; then \
		PYTHONPATH=$$PYTHONPATH:$$(pwd):$$(pwd)/pymod ./test/test$${py_test}.py		;\
	fi
