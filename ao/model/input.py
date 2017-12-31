#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
# input.py:
#
# A class to provide functionality for reading data.
#
# ------------------------------------------------------------------------------

import yaml
import os
import sys

# ------------------------------------------------------------------------------
#
# Class Input
#
# ------------------------------------------------------------------------------
class Input():

    # --------------------------------------------------------------------------
    def __init__(self, directory=None):
        """Initialize"""

        self.directory = directory
        self.filename  = None
        self.data      = None
        self.object    = None

    # --------------------------------------------------------------------------
    def read(self, filename=None):
        """Read data from STDIN or a file"""

        self.filename = filename
        self.data     = ''

        try:
            # read from STDIN
            if filename is None:
                for line in sys.stdin:
                    self.data += line
            # read from file
            else:
                if self.directory:
                    self.filename = os.path.join( self.directory, filename )

                with open( self.filename, 'r' ) as stream:
                    self.data = stream.read()

            self.object = yaml.safe_load(self.data)
        except Exception as e:
            self.object = None

        # return object
        return self.object

    # --------------------------------------------------------------------------
    def getDirectory(self):
        """Provide directory"""
        return self.directory

    # --------------------------------------------------------------------------
    def getFilename(self):
        """Provide filename"""
        return self.filename

    # --------------------------------------------------------------------------
    def getData(self):
        """Provide raw data"""
        return self.data

    # --------------------------------------------------------------------------
    def getObject(self):
        """Provide object derived from raw yaml data"""
        return self.object
