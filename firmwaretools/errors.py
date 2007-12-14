# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

import exceptions

class FTBaseError(exceptions.Exception): pass

class ConfigError(FTBaseError): pass
