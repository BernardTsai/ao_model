#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions  import ParameterError, SchemaError, ConnectionError, UnknownEntityError, UnknownError
from .api         import API
from .baseManager import BaseManager
from jsonschema   import validate
from ipaddress    import IPv4Network, IPv6Network, IPv4Address, IPv6Address

class NodeManager(BaseManager):
    """Manage lifecycle of nodes (servers/volumes/interfaces)"""

    # schema for attributes
    schema = {
            "$schema":    "http://json-schema.org/schema#",
            "type":       "object",
            "properties": {
                "project":    {"type": "string"},
                "cluster":    {"type": "string"},
                "node":       {"type": "string"},
                "placement":  {"type": "string", "enum": ["INT", "EXT", "MGMT"]},
                "flavor":     {"type": "string"},
                "image":      {"type": "string"},
                "volumes":    {"type": "array"},
                "interfaces": {"type": "array"},
                "state":      {"type": "string", "enum": ["inactive", "active"] }
            },
            "required":["project","cluster","node","placement","flavor","image","state"]
        }

    volume_schema = {
        "$schema":    "http://json-schema.org/schema#",
        "type":       "object",
        "properties": {
            "volume": {"type": "string"},
            "type":   {"type": "string"},
            "size":   {"type": "number", "minimum": 0}
        },
        "required":["volume","type","size"]
    }

    interface_schema = {
        "$schema":    "http://json-schema.org/schema#",
        "type":       "object",
        "properties": {
            "network": {"type": "string"},
            "allowed": {
                "type": "array",
                "items": {
                    "anyOf": [
                        { "format": "ipv4" },
                        { "format": "ipv6" }
                    ]
                }
            }
        },
        "required":["network","allowed"]
    }

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
            # validate server
            validate(self.params, NodeManager.schema)

            # validate volumes
            if "volumes" in self.params:
                for volume in self.params["volumes"]:
                    validate(volume, NodeManager.volume_schema)

            # validate interfaces
            if "interfaces" in self.params:
                for interface in self.params["interfaces"]:
                    validate(interface, NodeManager.interface_schema)
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
        # determine node
        self.current["project"] = self.params["project"]
        self.current["cluster"] = self.params["cluster"]
        self.current["node"]    = self.params["node"]

        # read server information
        try:
            self.current["server"] = self.api.servers().get(
                tenant_name  = self.params["project"],
                cluster_name = self.params["cluster"],
                node_name    = self.params["node"])
        except:
            self.current["server"] = None

        # read volume information
        try:
            self.current["volumes"] = self.api.volumes().list(
                tenant_name  = self.params["project"],
                cluster_name = self.params["cluster"],
                node_name    = self.params["node"])
        except:
            self.current["volumes"] = []

        # read port information
        try:
            self.current["ports"] = self.api.ports().list(
                tenant_name  = self.params["project"],
                cluster_name = self.params["cluster"],
                node_name    = self.params["node"])
        except:
            self.current["ports"] = []

    # @log("Determination of target state")
    def get_target_configuration(self):
        """Determine target configuration"""

        # validate parameters
        params = self.params

        # construct target configurations
        try:
            self.target["project"] = self.params["project"]
            self.target["cluster"] = self.params["cluster"]
            self.target["node"]    = self.params["node"]
            self.target["state"]   = self.params["state"]

            # target server
            self.target["server"] = self.api.servers().new(
                tenant_name  = self.params["project"],
                cluster_name = self.params["cluster"],
                node_name    = self.params["node"],
                placement    = self.params["placement"],
                flavor_name  = self.params["flavor"],
                image_name   = self.params["image"],
                network_name = self.params["interfaces"][0]["network"]
            )

            # target volumes
            self.target["volumes"] = []
            for params in self.params["volumes"]:
                volume = self.api.volumes().new(
                    tenant_name  = self.params["project"],
                    cluster_name = self.params["cluster"],
                    node_name    = self.params["node"],
                    volume_name  = params["volume"],
                    volume_size  = params["size"],
                    volume_type  = params["type"]
                )

                self.target["volumes"].append( volume )

            # target ports
            self.target["ports"] = []
            for params in self.params["interfaces"]:
                port = self.api.ports().new(
                    tenant_name  = self.params["project"],
                    cluster_name = self.params["cluster"],
                    node_name    = self.params["node"],
                    network_name = params["network"],
                    allowed      = params["allowed"]
                )

                self.target["ports"].append( port )

        except Exception as exc:
            raise ParameterError(str(exc))

    # @log("Update configuration")
    def update_configuration(self):
        """Update node"""

        # do we need to delete a node?
        if self.params["state"] == "inactive":

            self.action = "none"

            for port in self.current["ports"]:
                self.delete_port(port)
                self.action  = "delete"

            for volume in self.current["volumes"]:
                self.delete_volumet(port)
                self.action  = "delete"

            if self.current["server"]:
                self.delete_server(self.current["server"])
                self.action  = "delete"

        # do we need to create a node
        elif not self.current["server"]:

            self.action = "create"

            self.create_server(self.target["server"])

            for volume in self.target["volumes"]:
                self.create_volume(volume)

            for port in self.target["ports"]:
                self.create_port(port)

        # do we need to update a node
        else:

            self.action = "none"

            # some shortcuts
            server1  = self.current["server"]
            server2  = self.target["server"]
            volumes1 = self.current["volumes"]
            volumes2 = self.target["volumes"]
            ports1   = self.current["ports"]
            ports2   = self.target["ports"]

            # determine changes
            server_changed    = (server1 == server2)
            volumes_changeset = self.compare(volumes1, volumes2)
            ports_changeset   = self.compare(ports1,   ports2)

            # update procedure
            if not server_changed:

                if ports_changeset.has_changed():
                    for port in ports_changeset.delete: self.delete_port(port)
                    for port in ports_changeset.update: self.update_port(port)
                    for port in ports_changeset.create: self.create_port(port)
                    self.action = "update"

                if volumes_changeset.has_changed():
                    for volume in volumes_changeset.delete: self.delete_volume(volume)
                    for volume in volumes_changeset.update: self.update_volume(volume)
                    for volume in volumes_changeset.create: self.create_volume(volume)
                    self.action = "update"

            else:
                self.action = "update"

                for port   in ports1:                   self.delete_port(port)
                for volume in volumes_changeset.delete: self.delete_volume(volume)
                for volume in volumes_changeset.update: volume.detach()
                for volume in volumes_changeset.keep:   volume.detach()

                self.update_server(target_server)

                for volume in volumes_changeset.keep:   volume.attach()
                for volume in volumes_changeset.update: self.update_volume(volume)
                for volume in volumes_changeset.update: volume.attach()
                for port   in ports2:                   self.create_port(port)

    # @log("Server deletion")
    def delete_server(self, server):
        """Delete an existing server"""
        if self.check_mode:
            return

        self.changed = True

        server.delete()

    # @log("Server creation")
    def create_server(self, server):
        """Create a new server"""
        if self.check_mode:
            return

        self.changed = True

        server.save()

    # @log("Server update")
    def update_server(self, server):
        """Update an existing server"""
        if self.check_mode:
            return

        self.changed = True

        server.save()

    # @log("Volume deletion")
    def delete_volume(self, volume):
        """Delete an existing volume"""
        if self.check_mode:
            return

        self.changed = True

        volume.delete()

    # @log("Volume creation")
    def create_volume(self, volume):
        """Create a new volume"""
        if self.check_mode:
            return

        self.changed = True

        volume.save()

    # @log("Volume update")
    def update_volume(self, volume):
        """Update an existing volume"""
        if self.check_mode:
            return

        self.changed = True

        volume.save()

    # @log("Port deletion")
    def delete_port(self, port):
        """Delete an existing port"""
        if self.check_mode:
            return

        self.changed = True

        port.delete()

    # @log("Port creation")
    def create_port(self, port):
        """Create a new port"""
        if self.check_mode:
            return

        self.changed = True

        port.save()

    # @log("Port update")
    def update_volume(self, port):
        """Update an existing port"""
        if self.check_mode:
            return

        self.changed = True

        port.save()

    # @log("Node information")
    def get_result(self):
        """Retrieve the results of the action"""
        self.result = {
            "project":       self.params["project"],
            "cluster":       self.params["cluster"],
            "node":          self.params["node"],
            "placement":     self.params["placement"],
            "flavor":        self.params["flavor"],
            "image":         self.params["image"],
            "volumes":       self.params["volumes"],
            "interfaces":    self.params["interfaces"],
            "state":         self.params["state"],
            "changed":       self.changed,
            "action":        self.action,
            "log":           self.msgs
        }

        return self.result
