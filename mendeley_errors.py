# -*- coding: utf-8 -*-
"""
Contains all custom errors called within the mendeley_python package.
"""

class OptionalLibraryError(Exception):
    pass

class DOINotFoundError(KeyError):
    pass