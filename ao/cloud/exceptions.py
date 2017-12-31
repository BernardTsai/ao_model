#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class SchemaError(AttributeError):
    pass

class ParameterError(AttributeError):
    pass

class ConnectionError(IOError):
    pass

class UnknownEntityError(Exception):
    pass

class ModuleError(Exception):
    pass

class TimeoutError(Exception):
    pass

class UnknownError(Exception):
    pass
