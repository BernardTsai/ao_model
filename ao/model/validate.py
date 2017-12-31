#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
# validate.py:
#
# A class to provide functionality for validating data.
#
# ------------------------------------------------------------------------------

import yaml
import glob
import os
import jsonschema

# ------------------------------------------------------------------------------
#
# Class Validate
#
# ------------------------------------------------------------------------------
class Validate():

    # --------------------------------------------------------------------------
    def __init__(self, version="V0.1.1", directory=None):
        """Initialize"""

        if directory is None:
            self.directory = os.path.dirname(__file__)
        else:
            self.directory = directory
        self.version    = version
        self.schemas    = {}
        self.validators = {}

        # load schemas
        for schema_file in glob.glob( '{}/{}/*.yaml'.format( self.directory, self.version ) ):
            schema_name = os.path.basename( schema_file )[:-5]
            with open( schema_file, 'r' ) as stream:
                schema    = yaml.safe_load( stream )
                validator = jsonschema.Draft4Validator( schema )

                self.schemas[schema_name]    = schema
                self.validators[schema_name] = validator

    # --------------------------------------------------------------------------
    def validate(self, data):
        """Validate data against a schema"""
        missing_type     = "/topology_template/node_templates/{}: 'type' is a required property"
        unknown_type     = "/topology_template/node_templates/{}: unknown type: {}"
        missing_property = "/topology_template/node_templates/{}: 'properties' is a required property"
        other_error      = "/topology_template/node_templates/'{}'/properties{}: {}"
        messages = []

        # validate TOSCA header
        validator = self.validators[ "Tosca" ]

        for error in validator.iter_errors(data):
            path = ""
            for entry in error.absolute_path:
                if isinstance( entry, int ):
                    path = path + "[" + str(entry) + "]"
                else:
                    path = path + "/" + str(entry)
            if path == "":
                path="/"

            messages.append( path  + ": " + error.message)

        # check if template has any nodes
        templates = data["topology_template"]["node_templates"]
        if not templates:
            return messages

        # validate nodes of the TOSCA template
        for uuid, node in templates.items():

            # check if type has been defined
            if not "type" in node:
                messages.append( missing_type.format(uuid) )
                continue

            # check validity of type
            type = node["type"].rsplit(".", 1)[-1]
            if not type in self.schemas:
                messages.append( unknown_type.format(uuid,type) )
                continue

            # check if properties has been defined
            if not "properties" in node:
                messages.append( missing_property.format(uuid) )
                continue

            # validate properties against schema
            properties = node["properties"]

            # get schema
            validator = self.validators[ type ]

            # validate properties
            for error in validator.iter_errors(properties):
                path = ""
                for entry in error.absolute_path:
                    if isinstance( entry, int ):
                        path = path + "[" + str(entry) + "]"
                    else:
                        path = path + "/" + str(entry)
                if path == "":
                    path="/"

                messages.append( other_error.format(uuid,path,error.message) )

        return messages

    # --------------------------------------------------------------------------
    def getDirectory(self):
        """Provide directory"""
        return self.directory

    # --------------------------------------------------------------------------
    def getVersion(self):
        """Provide version"""
        return self.version

    # --------------------------------------------------------------------------
    def getSchemas(self):
        """Provide schemas"""
        return self.schemas
