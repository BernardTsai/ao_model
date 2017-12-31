#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
# action.py:
#
# A class to calculate actions from a delta (difference between models).
#
# ------------------------------------------------------------------------------

# TODO:
# - validate arguments (type, if consistent, ...)
# - proper sequence of adding/removing networks
# - handling dependencies of elements with endpoints
# - adding config data to actions

# ------------------------------------------------------------------------------
#
# Class Action
#
# ------------------------------------------------------------------------------
class Action():

    # --------------------------------------------------------------------------
    def __init__(self, delta):
        """Initialize action"""

        # save references to models and the diff
        self.delta  = delta.model
        self.model1 = delta.model1
        self.model2 = delta.model2
        self.index1 = delta.index1
        self.index2 = delta.index2
        self.model = {
            "context":    delta.model["context"],
            "version1":   delta.model["version1"],
            "version2":   delta.model["version2"],
            "actions":    []
        }

        actions = self.model["actions"]

        # handle internal components
        for vnf in self.delta["vnfs"]:
            for tenant in vnf["tenants"]:

                # remove all obsolete components
                for component in tenant["components"]:
                    if component["action"] == "remove":
                        for node in component["nodes"]:
                            actions.append( node )
                        actions.append( component )

                # change all modified nodes of unmodified components
                for component in tenant["components"]:
                    if component["action"] == "keep":
                        for node in component["nodes"]:
                            if node["action"] != "keep":
                                actions.append( node )

                # change all modified components
                for component in tenant["components"]:
                    if component["action"] == "change":
                        for node in component["nodes"]:
                            if node["action"] != "keep":
                                actions.append( node )
                        actions.append( component )

                # add all new components
                for component in tenant["components"]:
                    if component["action"] == "add":
                        actions.append( component )
                        for node in component["nodes"]:
                            actions.append( node )

        # handle internal networks
        for vnf in self.delta["vnfs"]:
            for tenant in vnf["tenants"]:

                # remove all obsolete components
                for network in tenant["networks"]:
                    if network["action"] == "remove":
                        actions.append( network )

                # change all modified components
                for component in tenant["components"]:
                    if network["action"] == "change":
                        actions.append( network )

                # add all new components
                for component in tenant["components"]:
                    if network["action"] == "add":
                        actions.append( network )

    # --------------------------------------------------------------------------
    def getModel(self):
        """Provide model object"""
        return self.model
