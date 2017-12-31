#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions  import ParameterError, SchemaError, ConnectionError, UnknownEntityError, UnknownError
from .api         import API
from .baseManager import BaseManager
from jsonschema   import validate
from ipaddress    import ip_address, ip_network

class NetworkManager(BaseManager):
    """Manage lifecycle of networks"""

    # schema for attributes
    schema = {
        "$schema":    "http://json-schema.org/schema#",
        "type":       "object",
        "properties": {
            "project":      {"type": "string"},
            "network":      {"type": "string"},
            "ipv4_prefix":  {"format": "ipv4"},
            "ipv4_length":  {"type": ["number","null"],"minimum": 0, "maximum": 32},
            "ipv4_start":   {"format": "ipv4"},
            "ipv4_end":     {"format": "ipv4"},
            "ipv4_gateway": {"format": "ipv4"},
            "ipv4_dns":     {"format": "ipv4"},
            "ipv6_prefix":  {"format": "ipv6"},
            "ipv6_length":  {"type": ["number","null"],"minimum": 0, "maximum": 128},
            "ipv6_start":   {"format": "ipv6"},
            "ipv6_end":     {"format": "ipv6"},
            "ipv6_gateway": {"format": "ipv6"},
            "ipv6_dns":     {"format": "ipv6"},
            "route_target": {"type": ["string","null"] },
            "state":        {"type": ["string","null"], "enum": ["inactive", "active"] },
            "loglevel":     {"type": ["string","null"], "enum": ["debug", "error"] }
        },
        "required":["project","network","state"]
    }

    # attributes
    attributes = [
        "project", "network", "route_target",
        "ipv4_prefix","ipv4_length",
        "ipv4_gateway","ipv4_dns",
        "ipv4_start","ipv4_end",
        "ipv6_prefix","ipv6_length",
        "ipv6_gateway","ipv6_dns",
        "ipv6_start","ipv6_end"]
    parameters = [
        "ipv4_prefix","ipv4_length",
        "ipv4_start","ipv4_end",
        "ipv4_gateway","ipv4_dns",
        "ipv6_prefix","ipv6_length",
        "ipv6_start","ipv6_end",
        "ipv6_gateway","ipv6_dns"]

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
            validate(self.params, NetworkManager.schema)
        except:
            raise SchemaError("Schema error")

        # validate parameters
        params = self.params

        # cidrs
        cidr = {"4": None, "6": None}

        # check networks
        for family in ["4","6"]:

            # check networks
            prefix = "ipv" + family + "_prefix"
            length = "ipv" + family + "_length"
            if prefix in params and params[prefix]:
                try:
                    net_addr     = str(params[prefix]) + "/" + str(params[length])
                    net          = ip_network( net_addr )
                    if str(net.version) != family: raise Exception()
                    cidr[family] = net
                except Exception:
                    raise ParameterError( "Wrong IPv{} network specification".format(family))

            # check ip addresses
            for suffix in ["gateway","start","end","dns"]:
                addr_name = "ipv" + family + "_" + suffix
                if addr_name in params and params[addr_name]:
                    try:
                        addr   = params[addr_name]
                        ipaddr = ip_address( addr )
                        if str(ipaddr.version) != family: raise Exception()
                        if not ipaddr in cidr[family]: raise Exception()
                    except Exception:
                        raise ParameterError("Wrong IPv{} {} specification".format(family,suffix))

            # check start and end addresses
            start = "ipv{}_start".format(family)
            end   = "ipv{}_end".format(family)
            if start in params and params[start]:
                try:
                    ip_start = ip_address(params[start])
                    ip_end   = ip_address(params[end])
                    if ip_start > ip_end: raise Exception()
                except Exception:
                    raise ParameterError("Wrong IPv{} pool range".format(family))

    # @log("Initialization")
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
        # read network information
        self.network = self.api.networks().get(
            tenant_name=self.params["project"],
            network_name=self.params["network"])

        # determine configuration
        self.current["project"] = self.params["project"]
        self.current["network"] = self.params["network"]

        if not self.network:
            for attr in NetworkManager.attributes:
                self.current[attr] = None
        else:
            result = self.network.attributes()

            for attr in result:
                if attr in NetworkManager.attributes:
                    self.current[attr] = result[attr]

    # @log("Determination of target state")
    def get_target_configuration(self):
        """Determine target configuration"""

        # copy configuration to target configuration
        for attr in NetworkManager.attributes:
            self.target[attr] = None
            if attr in self.params and self.params[attr]:
                self.target[attr] = self.params[attr]

    # @log("Update configuration")
    def update_configuration(self):
        """Update network configuration"""
        # change/update network to desired state
        if self.network:
            if self.params["state"] != "active":
                self.action = "delete"
                self.delete()
            else:
                self.action = "none"
                for item in ["ipv4_prefix","ipv4_length","ipv4_start","ipv4_end",
                             "ipv4_gateway","ipv4_dns",
                             "ipv6_prefix","ipv6_length","ipv6_start","ipv6_end",
                             "ipv6_gateway","ipv6_dns"]:
                    current = self.current[item]
                    target  = self.target[item]
                    if target and str(target) != "" and str(current) != str(target):
                        self.action = "redeploy"
                        self.delete_network()
                        self.create_network()
                        break

                # is an update needed?
                # if self.action == "none":
                #     for item in ["route_target"]:
                #         if self.current[item] != self.target[item]:
                #             self.action = "update"
                #             self.update()
                #             break
        else:
            if self.params["state"] == "active":
                self.action = "create"
                self.create_network()

    # @log("Network deletion")
    def delete_network(self):
        """Delete an existing virtual network"""
        if self.check_mode:
            return

        self.changed = True

        self.network.delete()
        self.network = None

    # @log("Network creation")
    def create_network(self):
        """Create a new virtual network"""
        if self.check_mode:
            return

        self.changed = True

        # create network
        tenant_name  = self.params["project"]
        network_name = self.params["network"]

        # extract parameters
        params = {}
        for attr in self.params:
            if attr in NetworkManager.parameters:
                params[attr] = self.params[attr]

        self.network = self.api.networks().new( tenant_name=tenant_name, network_name=network_name, **params)
        self.network.save()

    # @log("Network update")
    def update_network(self):
        """Update an existing virtual network"""
        if self.check_mode:
            return

        self.changed = True

        # currently all changes of attributes lead to a redeployment
        pass

    # @log("Network information")
    def get_result(self):
        """Retrieve the results of the action"""
        self.result = {
            "project": self.params["project"],
            "network": self.params["network"],
            "id":      self.network.id if self.network else "",
            "state":   self.params["state"],
            "changed": self.changed,
            "action":  self.action,
            "log":     self.msgs
        }

        for attr in NetworkManager.parameters:
            self.result[attr] = self.target[attr] if self.changed else self.current[attr]

        return self.result
