#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
# render.py:
#
# A class to provide functionality for rendering templates.
#
# ------------------------------------------------------------------------------

import os
import jinja2
import yaml
import glob

# ------------------------------------------------------------------------------
#
# Class Render
#
# ------------------------------------------------------------------------------
class Render():

    # --------------------------------------------------------------------------
    def __init__(self, version="V0.1.1", directory=None):
        """Initialize"""

        if directory is None:
            self.directory = os.path.dirname(__file__)
        else:
            self.directory = directory
        self.version   = version
        self.templates = {}
        self.renderers = {}
        self.dumper    = yaml.dumper.SafeDumper

        # initialize yaml dumper
        self.dumper.ignore_aliases = lambda self, data: True

        # initialize the jinja2 environment
        env = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=[ 'jinja2.ext.loopcontrols' ]
        )

        # load templates
        for template_file in glob.glob( '{}/{}/*.j2'.format( self.directory, self.version ) ):
            template_name = os.path.basename( template_file )[:-3]
            with open( template_file, 'r' ) as stream:
                template = stream.read()
                renderer = env.from_string( template )

                self.templates[template_name] = template
                self.renderers[template_name] = renderer

    # --------------------------------------------------------------------------
    def render(self, data, template_name=None):
        """Render data or dump as yaml"""

        # dump as yaml
        if template_name is None:
            txt = yaml.dump( data, default_flow_style=False, Dumper=noalias_dumper)

        # unknown template
        elif not template_name in self.templates:
            txt = "unknown template"

        # render the data
        else:
            renderer = self.renderers[template_name]
            txt      = renderer.render( data )

        # return the results
        return txt

    # --------------------------------------------------------------------------
    def getDirectory(self):
        """Provide directory"""
        return self.directory

    # --------------------------------------------------------------------------
    def getVersion(self):
        """Provide version"""
        return self.version

    # --------------------------------------------------------------------------
    def getTemplates(self):
        """Provide templates"""
        return self.templates
