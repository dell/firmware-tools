# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################

from __future__ import generators

import ConfigParser
import glob
import logging
import logging.config
import os
import sys

from firmwaretools.trace_decorator import decorate, traceLog, getLog
import i18n
import errors

# these are replaced by autotools when installed.
__VERSION__="unreleased_version"
SYSCONFDIR=os.path.join(os.path.dirname(os.path.realpath(sys._getframe(0).f_code.co_filename)),"..","etc")
PYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
PKGPYTHONDIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..","firmwaretools")
PKGDATADIR=os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),"..")
CONFDIR=os.path.join(SYSCONFDIR,"firmware")
# end build system subs

API_VERSION="1.0"

# set up logging
logging.basicConfig()
logging.raiseExceptions = 0
moduleVerboseLog = getLog(prefix="verbose.")

from optparse import OptionParser
class FTConfig(OptionParser):
    """Unified cmdline option parsing and config file handling."""
    def __init__(self, *args, **kargs):
        OptionParser.__init__(self, *args, **kargs)

        self.add_option("-c", "--config", help="Override default config file with user-specified config file.", action="append", default=[])
        self.add_option("--extra-plugin-config", help="Add additional plugin config file.", action="append", default=[], dest="extra_plugins")
        self.add_option("-v", "--verbose", action="count", dest="verbosity", default=1, help="Display more verbose output.")
        self.add_option("-q", "--quiet", action="store_const", const=0, dest="verbosity", help="Minimize program output. Only errors and warnings are displayed.")
        self.add_option("--trace", action="store_true", dest="trace", default=False, help="Enable verbose function tracing.")
        self.add_option("--fake-mode", action="store_true", dest="fake_mode", default=False, help="Display fake data for unit-testing.")
        self.add_option("--disableplugin", action="append", dest="disabled_plugins", default=[], help="Disable single named plugin.")
        self.add_option("--listplugins", action="store_const", const="listplugins", dest="mode", default='default', help="list available plugins.")

        self.parseOptionsFirst_novalopts = ['--version','-q', '-v', "--quiet", "--verbose", "--trace"]
        self.parseOptionsFirst_valopts = ['-c', '--config', '--disableplugin', "--extra-plugin-config"]

        defaults = {
            "sysconfdir": SYSCONFDIR,
            "pythondir": PYTHONDIR,
            "pkgpythondir": PKGPYTHONDIR,
            "pkgdatadir": PKGDATADIR,
            "confdir": CONFDIR,
            }
        self.ini = ConfigParser.SafeConfigParser(defaults)

    def parse(self, args=None):
        if args is None: args = []
        # parse enough of the cmdline to know where config is and which plugins to enable
        self.opts = self.firstParse(args)
        if not self.opts.config:
            self.opts.config = [os.path.join(CONFDIR, "firmware.conf"), ]

        # read main config file
        logging.config.fileConfig(self.opts.config[0])
        for i in self.opts.config:
            self.ini.read(i)

        # set up logging
        self.root_log       = logging.getLogger()
        self.ft_log         = logging.getLogger("firmwaretools")
        self.ft_verbose_log = logging.getLogger("verbose")
        self.ft_trace_log   = logging.getLogger("trace")

        self.ft_log.propagate = 0
        self.ft_trace_log.propagate = 0
        self.ft_verbose_log.propagate = 0

        if self.opts.verbosity >= 1:
            self.ft_log.propagate = 1
        if self.opts.verbosity >= 2:
            self.ft_verbose_log.propagate = 1
        if self.opts.verbosity >= 3:
            for hdlr in self.root_log.handlers:
                hdlr.setLevel(logging.DEBUG)
        if self.opts.trace:
            self.ft_trace_log.propagate = 1

        moduleVerboseLog.info("firmware-tools version: %s" % __VERSION__)
        moduleVerboseLog.info("COMMAND: %s" % ' '.join(args))

        # read all addon config files
        plugin_config_dir=os.path.join(self.ini.get("main", "plugin_config_dir"), "*.conf")
        plugin_cfg_files = glob.glob(plugin_config_dir) + self.opts.extra_plugins
        for file in plugin_cfg_files:
            moduleVerboseLog.debug("plugin config: %s" % file)
            self.ini.read(file)

        # load plugins
        self.plugins = self.loadPlugins()

        # parse rest of cmdline
        self.opts, args = self.parse_args(args)

        # if fake mode
        if self.opts.fake_mode:
            moduleVerboseLog.info("Activating fake mode.")
            import repository
            import mockrepository
            # remove all other bootstrap, inventory and repository
            for n, v in self.plugins.items():
                for i in ("InventoryGenerator", "BootstrapGenerator"):
                    if hasattr(v['module'], i):
                        delattr(v['module'], i)

            moduleName = "mockpackage"
            searchPath = ""
            self.plugins[moduleName] = self._loadModule(moduleName, searchPath)
            self.plugins[moduleName]["section"] = 'fake'
            self.plugins[moduleName]["enabled"] = True

        return self.opts, args

    def firstParse(self, args):
        args = _filtercmdline(
            self.parseOptionsFirst_novalopts,
            self.parseOptionsFirst_valopts,
            args)
        return self.parse_args(args=args)[0]

    decorate(traceLog())
    def loadPlugins(self, types="CORE"):
        # scan config for plugins and load them.
        plugins={}
        for sect in self.ini.sections():
            if self.ini.has_option(sect, "plugin_enabled"):
                try:
                    moduleVerboseLog.debug('Checking plugin: "%s"', sect)
                    enabled = parseBool(self.ini.get(sect, "plugin_enabled"))
                    if not enabled:
                        continue
                    if not self.ini.get(sect, "plugin_type") in types:
                        continue

                    moduleName = getOption(self.ini, sect, "plugin_module")
                    searchPath = getOption(self.ini, sect, "plugin_path")

                    plugins[moduleName] = self._loadModule(moduleName, searchPath)
                    plugins[moduleName]["section"] = sect
                    plugins[moduleName]["enabled"] = enabled
                except (ConfigParser.NoOptionError,), e:
                    getLog().warning("misconfigured plugin: %s" % str(e) )
                    pass


        return plugins

    decorate(traceLog())
    def _loadModule(self, moduleName, searchPath):
        # load plugin
        module = __import__(moduleName, globals(),  locals(), [])
        for i in moduleName.split(".")[1:]:
            module = getattr(module, i)

        # Check API version required by the plugin
        if not hasattr(module, 'requires_api_version'):
             raise errors.ConfigError(
                'Plugin "%s" doesn\'t specify required API version' % moduleName
                )

        if not apiverok(API_VERSION, module.requires_api_version):
            raise errors.ConfigError(
                'Plugin "%s" requires API %s. Supported API is %s.' % (
                    moduleName,
                    module.requires_api_version,
                    API_VERSION,
                    ))

        moduleVerboseLog.info('Loading "%s" plugin', moduleName)
        return {'module': module, 'name': moduleName}


decorate(traceLog())
def parseBool(opt):
    if opt.lower() in ("true", "1", "enabled", "on"):
        return True
    return False

decorate(traceLog())
def getOption(ini, section, option, default=None):
    if ini.has_option(section, option):
        return ini.get(section, option)
    return default

# filched from yum cli.py
def _filtercmdline(novalopts, valopts, args):
    '''Keep only specific options from the command line argument list

    This function allows us to peek at specific command line options when using
    the optparse module. This is useful when some options affect what other
    options should be available.

    @param novalopts: A sequence of options to keep that don't take an argument.
    @param valopts: A sequence of options to keep that take a single argument.
    @param args: The command line arguments to parse (as per sys.argv[:1]
    @return: A list of strings containing the filtered version of args.

    Will raise ValueError if there was a problem parsing the command line.
    '''
    out = []
    args = list(args)       # Make a copy because this func is destructive

    while len(args) > 0:
        a = args.pop(0)
        if '=' in a:
            opt, _ = a.split('=', 1)
            if opt in valopts:
                out.append(a)

        elif a in novalopts:
            out.append(a)

        elif a in valopts:
            if len(args) < 1:
                raise ValueError
            next = args.pop(0)
            if next[0] == '-':
                raise ValueError

            out.extend([a, next])

        else:
            # Check for single letter options that take a value, where the
            # value is right up against the option
            for opt in valopts:
                if len(opt) == 2 and a.startswith(opt):
                    out.append(a)

    return out

decorate(traceLog())
def parsever(apiver):
    maj, min = apiver.split('.')
    return int(maj), int(min)

decorate(traceLog())
def apiverok(a, b):
    '''Return true if API version "a" supports API version "b"
    '''
    a = parsever(a)
    b = parsever(b)

    if a[0] != b[0]:
        return 0

    if a[1] >= b[1]:
        return 1

    return 0
# end filch
