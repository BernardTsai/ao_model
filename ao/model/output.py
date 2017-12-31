#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
# output.py:
#
# A class to provide functionality for writing data.
#
# ------------------------------------------------------------------------------

import os
import sys
import re
import codecs

# ------------------------------------------------------------------------------
#
# Class Output
#
# ------------------------------------------------------------------------------
class Output():

    # --------------------------------------------------------------------------
    def __init__(self, directory=None):
        """Initialize"""

        self.directory = directory
        self.data      = None
        self.filenames = []
        self.blocks    = []

    # --------------------------------------------------------------------------
    def write(self, data):
        """Write blocks of data to STDOUT or a file"""

        self.data      = data
        self.filenames = []
        self.blocks    = []

        # check if the data contains special output statement lines:
        # ">> [path] [comments]\n" which advise to output the following
        # data to a file location indicated by the [path] argument

        block    = ""
        filename = ""
        for line in self.data.splitlines():
            # determine new filename: ">> [filename] [comments]"
            match = re.match(">> ([^ ]*)(.*)", line)
            if match:
                # write the existing block
                if block != "":
                    self.write2(filename, block)

                    # reset block and file name
                    block = ""

                # set new file name
                filename = match.group(1)
            else:
                if block == "":
                    block = line
                else:
                    block += "\n" + line

        # write last block
        self.write2(filename, block)

    # --------------------------------------------------------------------------
    def write2(self, filename, block):
        """Write block to STDOUT or a file"""

        self.blocks.append( block )

        # write to stdout if no filename has been provided
        if filename == "" or filename is None:
            self.filenames.append( "STDOUT" )

            print( block )

        # write to file
        else:
            if self.directory:
                filepath = os.path.join( self.directory, filename )
            else:
                filepath = filename

            self.filenames.append( filepath )

            # write block as text file
            with codecs.open(filepath, "w", "utf-8") as stream:
                stream.write(block)

    # --------------------------------------------------------------------------
    def getDirectory(self):
        """Provide directory"""
        return self.directory

    # --------------------------------------------------------------------------
    def getData(self):
        """Provide raw data"""
        return self.data

    # --------------------------------------------------------------------------
    def getFilenames(self):
        """Provide filenames"""
        return self.filenames

    # --------------------------------------------------------------------------
    def getBlocks(self):
        """Provide blocks"""
        return self.blocks
