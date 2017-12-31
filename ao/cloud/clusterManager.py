#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions  import ParameterError, SchemaError, ConnectionError, UnknownEntityError, UnknownError
from .api         import API
from .baseManager import BaseManager
from jsonschema   import validate
from ipaddress    import IPv4Network, IPv6Network, IPv4Address, IPv6Address

from .securitygroups import SecurityGroups

class ClusterManager(BaseManager):
    """Manage lifecycle of security groups"""

    # schema for attributes
    schema = {
        "$schema":    "http://json-schema.org/schema#",
        "type":       "object",
        "properties": {
            "project":       {"type": "string"},
            "cluster":       {"type": "string"},
            "communication": {
                "type": "array",
                "items": [{
                    "type":       "object",
                    "properties": {
                        "network": {"type": "string"},
                        "rules":  {
                            "type": "array",
                            "items": [{
                                "type":       "object",
                                "properties": {
                                    "direction": {"type": "string", "enum": ["ingress", "egress"] },
                                    "protocol":  {"type": "string", "enum": ["tcp", "udp", "icmp"] },
                                    "min":       {"type": "number", "minimum": 1, "maximum": 65535 },
                                    "max":       {"type": "number", "minimum": 1, "maximum": 65535 },
                                    "target":    {"type": "string" }
                                },
                                "required": ["direction","protocol","min","max","target"]
                            }]
                        }
                    },
                    "required": ["network","rules"]
                }]
            },
            "state":      {"type": ["string","null"], "enum": ["inactive", "active"] },
            "loglevel":   {"type": ["string","null"], "enum": ["debug", "error"] }
        },
        "required":["project","cluster","communication","state"]
    }

    # attributes
    attributes = ["project", "cluster", "communication"]

    def __init__(self, params, check_mode=False):
        """Initialize"""
        BaseManager.__init__(self)

        # initialize attributes
        self.params     = params
        self.check_mode = check_mode
        self.current    = {}
        self.target     = {}
        self.result     = {}
        self.api        = None        # admin API connection
        self.action     = "none"      # default action
        self.changed    = False       # default status
        self.network    = None        # current network setup

        # process request
        try:
            self.validate_parameters()        # validate based on schema
            self.initialize()                 # connect to the contrail API
            self.get_current_configuration()  # get current state
            self.get_target_configuration()   # get target state
            self.update_configuration()       # update configuration
            self.get_result()                 # retrieve the results
        except Exception as exc:
            raise UnknownError(str(exc))

    # @log("Schema validation")
    def validate_parameters(self):
        """Validate schema of parameters"""
        # check schema
        try:
            validate(self.params, ClusterManager.schema)
        except:
            raise SchemaError("Schema error")

    # @log("Schema validation")
    def initialize(self):
        """Initialize connections"""
        try:
            self.api = API(
                openstack_url = self.params["auth_url"],
                project       = self.params["project"],
                username      = self.params["username"],
                password      = self.params["password"])

            self.api.connect()
        except Exception:
            raise ConnectionError( "Unable to connect to API")

    # @log("Determination of current state")
    def get_current_configuration(self):
        """Determine current configuration"""
        # determine cluster
        self.current["project"] = self.params["project"]
        self.current["cluster"] = self.params["cluster"]

        # read cluster information
        try:
            self.current["groups"] = self.api.securitygroups().list(
                tenant_name  = self.params["project"],
                cluster_name = self.params["cluster"])
        except UnknownEntityError:
            self.current["groups"] = []

    # @log("Determination of target state")
    def get_target_configuration(self):
        """Determine target configuration"""

        # validate parameters
        params = self.params

        # construct target configurations
        try:
            self.target["project"] = self.params["project"]
            self.target["cluster"] = self.params["cluster"]
            self.target["groups"]  = []

            for entry in params["communication"]:
                # check port range
                for rule in entry["rules"]:
                    port_min = int(rule["min"])
                    port_max = int(rule["min"])
                    if port_min > port_max:
                        raise ParameterError("Invalid port range")

                # add new group to target groups
                self.target["groups"].append(
                    self.api.securitygroups().new(
                        tenant_name  = self.params["project"],
                        cluster_name = self.params["cluster"],
                        network_name = entry["network"],
                        rules        = entry["rules"] )
                )
        except Exception as exc:
            raise ParameterError(str(exc))

    # @log("Update configuration")
    def update_configuration(self):
        """Update communication rules"""
        current  = self.current["groups"]
        target   = self.target["groups"]
        delete   = []
        maintain = []
        update   = []
        create   = []

        # do we need to create/update or delete a cluster?
        if self.params["state"] == "inactive":
            for current_group in current:
                delete.append(current_group)
        else:
            # determine groups to be removed, kept or updated
            for current_group in current:
                # try to find corresponding group in target
                found = False
                for target_group in target:
                    if current_group.name == target_group.name:
                        found = True
                        if current_group != target_group:
                            update.append(target_group)
                        else:
                            maintain.append(current_group)
                        break

                if not found:
                    delete.append(current_group)

            # determine groups to be added
            for target_group in target:
                # try to find corresponding group in target
                found = False
                for current_group in current:
                    if current_group.name == target_group.name:
                        found = True
                        break
                if not found:
                    create.append(target_group)

        # add new groups
        for group in create:
            self.create_group(group)

        # update groups which have changed
        for group in update:
            self.update_group(group)

        # remove deprecated groups
        for group in delete:
            self.delete_group(group)

        # change/update network to desired state
        if len(create) > 0 and len(delete) == 0 and len(update) == 0 and len(maintain) == 0:
            self.action = "create"
        elif len(delete) > 0 and len(create) == 0 and len(update) == 0 and len(maintain) == 0:
            self.action = "delete"
        elif len(create) == 0 and len(delete) == 0 and len(update) == 0:
            self.action = "none"
        else:
            self.action = "update"

    # @log("Security group deletion")
    def delete_group(self, group):
        """Delete an existing security group"""
        if self.check_mode:
            return

        self.changed = True

        group.delete()

    # @log("Security group creation")
    def create_group(self, group):
        """Create a new security group"""
        if self.check_mode:
            return

        self.changed = True

        # create network
        group.save()

    # @log("Security group update")
    def update_group(self, group):
        """Update an existing security group"""
        if self.check_mode:
            return

        self.changed = True

        group.save()

    # @log("Cluster information")
    def get_result(self):
        """Retrieve the results of the action"""
        self.result = {
            "project":       self.params["project"],
            "cluster":       self.params["cluster"],
            "communication": self.params["communication"],
            "state":         self.params["state"],
            "changed":       self.changed,
            "action":        self.action,
            "log":           self.msgs
        }

        return self.result
