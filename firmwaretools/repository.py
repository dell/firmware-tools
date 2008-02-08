# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
repository module
"""

from __future__ import generators

import os
import ConfigParser

import package
import pycompat
import dep_parser
import sys
import traceback
from firmwaretools.trace_decorator import decorate, traceLog, getLog

import logging
moduleLog = getLog()
moduleVerboseLog = getLog(prefix="verbose.")

class CircularDependencyError(Exception): pass

# TODO:
#  -- conf item should NEVER be used outside of constructor (makePackage)

decorate(traceLog())
def makePackage(configFile):
    conf = ConfigParser.ConfigParser()
    conf.read(configFile)

    # make a standard package
    if conf.has_option("package", "displayname"):
        displayname = conf.has_option("package", "displayname")
    else:
        displayname = "unknown"

    p = package.RepositoryPackage(
        displayname = displayname,
        name=conf.get("package", "name"),
        version=conf.get("package", "version"),
        conf=conf,
        path=os.path.dirname(configFile),
        )

    try:
        pymod = conf.get("package","module")
        moduleLog.debug("pymod: %s" % pymod)
        module = __import__(pymod, globals(),  locals(), [])
        for i in pymod.split(".")[1:]:
            module = getattr(module, i)

        packageTypeClass = conf.get("package", "type")
        type = getattr(module, packageTypeClass)
        if issubclass(type, package.Package):
            moduleLog.debug("direct instantiate")
            # direct instantiate class (new style)
            p = type(
                displayname=displayname,
                name=conf.get("package", "name"),
                version=conf.get("package", "version"),
                conf=conf,
                path=os.path.dirname(configFile),
            )
        else:
            # just wrap it (old style)
            moduleLog.debug("wrap")
            type(p)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError, ImportError, AttributeError):
        moduleLog.debug(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
        pass

    return p

# a null function that just eats args. Default callback
def nullFunc(*args, **kargs): pass

class SystemInventory(object):
    decorate(traceLog())
    def __init__(self, *args, **kargs):
        self.deviceList = {}
        self.allowDowngrade=False
        self.allowReflash=False

    decorate(traceLog())
    def addDevice(self, device):
        self.deviceList[device.name] = { "device": device, "update": None, "available_updates": []}

    decorate(traceLog())
    def addAvailablePackage(self, package):
        if self.deviceList.has_key(package.name):
            available_updates = self.deviceList[package.name]["available_updates"]
            available_updates.append(package)
            self.deviceList[package.name]["available_updates"] = available_updates
            package.attachToDevice(self.deviceList[package.name]['device'])

    decorate(traceLog())
    def hasDevice(self, device):
        return self.deviceList.has_key(device.name)

    decorate(traceLog())
    def iterDevices(self):
        for device, details in self.deviceList.items():
            yield details["device"]

    decorate(traceLog())
    def iterAvailableUpdates(self, device):
        for pkg in self.deviceList[device.name]["available_updates"]:
            yield pkg

    decorate(traceLog())
    def getSuggestedUpdatePackageForDevice(self, device):
        ret = None
        if self.deviceList.has_key(device.name):
            ret = self.deviceList[device.name]["update"]
        return ret

    decorate(traceLog())
    def getUpdatePackageForDevice(self, device):
        ret = None
        if self.deviceList.has_key(device.name):
            if self.deviceList[device.name].has_key("pinned_update"):
                ret = self.deviceList[device.name]["pinned_update"]
            else:
                ret = self.deviceList[device.name]["update"]
        return ret

    decorate(traceLog())
    def pinUpdatePackage(self, device, pkg):
        #TODO: ensure that pkg is in 'available_pkgs'
        hasOldPin = False
        if self.deviceList[device.name].has_key("pinned_update"):
            hasOldPin = True
            oldPin = self.deviceList[device.name]["pinned_update"]

        self.deviceList[device.name]["pinned_update"] = pkg

        # just check the rules... not actually installing
        try:
            for i in self.generateInstallationOrder(): pass
        except CircularDependencyError, e:
            # roll back
            if hasOldPin:
                self.deviceList[device.name]["pinned_update"] = oldPin
            else:
                del(self.deviceList[device.name]["pinned_update"])
            raise


    decorate(traceLog())
    def unPinDevice(self, device):
        if self.deviceList[device.name].has_key("pinned_update"):
            del(self.deviceList[device.name]["pinned_update"])

    decorate(traceLog())
    def reset(self):
        for device in self.iterDevices():
            self.unPinDevice(device)

    decorate(traceLog())
    def getMemento(self, deviceHint=None):
        memento = {}
        memento['savePin'] = {}
        for deviceName, details in self.deviceList.items():
            if deviceHint:
                if deviceHint.name != deviceName:
                    continue
            if details.has_key("pinned_update"):
                memento['savePin'][deviceName] = { 'device': details["device"], 'hasPin': 1, 'oldPin': details["pinned_update"] }
            else:
                memento['savePin'][deviceName] = { 'device': details["device"], 'hasPin': 0, 'oldPin': None }

        memento["internal.allowReflash"] = self.allowReflash
        memento["internal.allowDowngrade"] = self.allowDowngrade
        return memento

    decorate(traceLog())
    def setMemento(self, memento):
        self.allowReflash = memento["internal.allowReflash"]
        self.allowDowngrade = memento["internal.allowDowngrade"]
        for deviceName, details in memento['savePin'].items():
            if details['hasPin']:
                self.pinUpdatePackage(details["device"], details["oldPin"])
            else:
                self.unPinDevice(details["device"])

    decorate(traceLog())
    def setAllowDowngrade(self, val):
        self.allowDowngrade = val

    decorate(traceLog())
    def getAllowDowngrade(self):
        return self.allowDowngrade

    decorate(traceLog())
    def setAllowReflash(self, val):
        self.allowReflash = val

    decorate(traceLog())
    def getAllowReflash(self):
        return self.allowReflash

    decorate(traceLog())
    def checkRules(self, candidate, unionInventory, cb=(nullFunc, None)):
        # check if candidate update even applies to this system
        if not self.deviceList.get(candidate.name):
            cb[0]( who="checkRules", what="package_not_present_on_system", package=candidate, cb=cb)
            return 0

        # is candidate newer than what is either installed or scheduled for install
        if not self.allowDowngrade and unionInventory[candidate.name].compareVersion(candidate) > 0:
            cb[0]( who="checkRules", what="package_not_newer", package=candidate, systemPackage=unionInventory[candidate.name], cb=cb)
            return 0

        # is candidate newer than what is either installed or scheduled for install
        if not self.allowReflash and unionInventory[candidate.name].compareVersion(candidate) == 0:
            cb[0]( who="checkRules", what="package_same_version", package=candidate, systemPackage=unionInventory[candidate.name], cb=cb)
            return 0

        #check to see if this package has specific system requirements
        # for now, check if we are on a specific system by checking for
        # a BIOS package w/ matching id. In future, may have specific
        # system package.
        if hasattr(candidate,"conf") and candidate.conf.has_option("package", "limit_system_support"):
            systemVenDev = candidate.conf.get("package", "limit_system_support")
            if not unionInventory.get( "system_bios(%s)" % systemVenDev ):
                cb[0]( who="checkRules", what="fail_limit_system_check", package=candidate, cb=cb )
                return 0

        #check generic dependencies
        if hasattr(candidate,"conf") and candidate.conf.has_option("package", "requires"):
            requires = candidate.conf.get("package", "requires")
            if len(requires):
                d = dep_parser.DepParser(requires, unionInventory, self.deviceList)
                if not d.depPass:
                    cb[0]( who="checkRules", what="fail_dependency_check", package=candidate, reason=d.reason, cb=cb )
                    return 0
        return 1


    decorate(traceLog())
    def calculateUpgradeList(self, cb=(nullFunc, None)):
        unionInventory = {}
        for deviceName, details in self.deviceList.items():
            unionInventory[deviceName] = details["device"]

        # for every device, look at the available updates to see if one can be applied.
        # if we do any work, start over so that dependencies work themselves out over multiple iterations.
        workToDo = 1
        while workToDo:
            workToDo = 0
            for pkgName, details in self.deviceList.items():
                for candidate in details["available_updates"]:
                    if self.checkRules(candidate, unionInventory, cb=cb):
                        self.deviceList[candidate.name]["update"] = candidate
                        # update union inventory
                        unionInventory[candidate.name] = candidate
                        # need another run-through in case this fixes deps for another package
                        workToDo = 1

    decorate(traceLog())
    def generateInstallationOrder(self, returnDeviceToo=0, cb=(nullFunc, None)):
        unionInventory = {}
        for deviceName, details in self.deviceList.items():
            unionInventory[deviceName] = details["device"]

        # generate initial union inventory
        # we will start with no update packages and add them in one at a time
        # as we install them
        updateDeviceList = [] # [ pkg, pkg, pkg ]
        for pkgName, details in self.deviceList.items():
            update = self.getUpdatePackageForDevice(details["device"])
            if update:
                updateDeviceList.append( (details["device"], update) )

        workToDo = 1
        while workToDo:
            workToDo = 0
            for device, candidate in updateDeviceList:
                if self.checkRules(candidate, unionInventory, cb=cb):
                    candidate.setCurrentInstallDevice(device)
                    if returnDeviceToo:
                        yield (device, candidate)
                    else:
                        yield candidate

                    # move pkg from to-install list to inventory list
                    updateDeviceList.remove((device,candidate))
                    unionInventory[candidate.name] = candidate

                    # need another run-through in case this fixes deps for another package
                    workToDo = 1

        if len(updateDeviceList):
            raise CircularDependencyError("packages have circular dependency, or are otherwise uninstallable.")



class Repository(object):
    decorate(traceLog())
    def __init__(self, *args):
        self.dirList = []
        for i in args:
            self.dirList.append(i)

    decorate(traceLog())
    def iterPackages(self, cb=(nullFunc, None)):
        for dir in self.dirList:
            try:
                for (path, dirs, files) in pycompat.walkPath(dir):
                    if "package.ini" in files:
                        cb[0]( who="iterPackages", what="found_package_ini", path=os.path.join(path, "package.ini" ), cb=cb)
                        try:
                            p = makePackage( os.path.join(path, "package.ini" ))
                            cb[0]( who="iterPackages", what="made_package", package=p, cb=cb)
                            yield p
                        except:
                            moduleLog.debug(''.join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
                            pass
            except OSError:   # directory doesnt exist, so no repo packages. :-)
                pass

    decorate(traceLog())
    def iterLatestPackages(self, cb=(nullFunc, None)):
        latest = {}
        for candidate in self.iterPackages(cb=cb):
            pkgName = candidate.name
            if candidate.conf.has_option("package", "limit_system_support"):
                pkgName = pkgName + "_" + candidate.conf.get("package", "limit_system_support")

            p = latest.get(pkgName)
            if not p:
                latest[pkgName] = candidate
            elif p.compareVersion(candidate) < 0:
                latest[pkgName] = candidate

        cb[0]( who="iterLatestPackages", what="done_generating_list", cb=cb)
        keys = latest.keys()
        keys.sort()
        for package in keys:
            cb[0]( who="iterLatestPackages", what="made_package", package=latest[package], cb=cb)
            yield latest[package]


