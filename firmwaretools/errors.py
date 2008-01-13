# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0

import exceptions

class BaseError(exceptions.Exception): pass

class ConfigError(BaseError): pass
class LockError(BaseError): pass
