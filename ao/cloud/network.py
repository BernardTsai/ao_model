#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions                    import UnknownEntityError, ParameterError
from pycontrail.gen.resource_client import VirtualNetwork
from pycontrail.gen.resource_xsd    import RouteTargetList

class Network():
    """Network entity"""

    def __init__(self, openstack, contrail, entity=None,
        tenant_name  =None,
        network_name = None,
        route_target = None,
        ipv4_prefix  = None, ipv4_length = None,
        ipv4_start   = None, ipv4_end    = None,
        ipv4_gateway = None, ipv4_dns    = None,
        ipv6_prefix  = None, ipv6_length = None,
        ipv6_start   = None, ipv6_end    = None,
        ipv6_gateway = None, ipv6_dns    = None):
        """Initialize"""
        self.openstack = openstack
        self.contrail  = contrail
        self.type      = "network"

        # initialize with provided network
        if entity:
            self.__init_attributes__(entity)

        # initialize with provided parameters
        elif tenant_name and network_name and tenant_name != "" and network_name != "":
            name  = tenant_name + "_" + network_name

            self.entity       = None
            self.id           = None
            self.subnet4      = None
            self.subnet6      = None
            self.name         = name
            self.state        = "inactive"
            self.tenant_name  = tenant_name
            self.network_name = network_name
            self.route_target = route_target
            self.ipv4_prefix  = ipv4_prefix
            self.ipv4_length  = ipv4_length
            self.ipv4_start   = ipv4_start
            self.ipv4_end     = ipv4_end
            self.ipv4_gateway = ipv4_gateway
            self.ipv4_dns     = ipv4_dns
            self.ipv6_prefix  = ipv6_prefix
            self.ipv6_length  = ipv6_length
            self.ipv6_start   = ipv6_start
            self.ipv6_end     = ipv6_end
            self.ipv6_gateway = ipv6_gateway
            self.ipv6_dns     = ipv6_dns

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity       = entity
        self.id           = entity.id
        self.name         = entity.name
        self.state        = "active"
        self.tenant_name  = entity.name.split("_",1)[0]
        self.network_name = entity.name.split("_",1)[1]
        self.route_target = ""
        self.ipv4_prefix  = ""
        self.ipv4_length  = ""
        self.ipv4_start   = ""
        self.ipv4_end     = ""
        self.ipv4_gateway = ""
        self.ipv4_dns     = ""
        self.ipv6_prefix  = ""
        self.ipv6_length  = ""
        self.ipv6_start   = ""
        self.ipv6_end     = ""
        self.ipv6_gateway = ""
        self.ipv6_dns     = ""

        # determine subnet configurations
        for subnet_id in self.entity.subnet_ids:
            subnet = self.openstack.network.get_subnet(subnet_id)

            ipvX = "ipv" + str(subnet.ip_version)

            if str(subnet.ip_version) == "4":
                self.subnet4 = subnet
            else:
                self.subnet6 = subnet

            # prefix and length
            setattr(self, ipvX + "_prefix",  subnet.cidr.split( "/", 1)[0] )
            setattr(self, ipvX + "_length",  subnet.cidr.split( "/", 1)[1] )

            # start and stop
            for pool in subnet.allocation_pools:
                setattr(self, ipvX + "_start", pool["start"] )
                setattr(self, ipvX + "_end",   pool["end"] )
                break

            # dns
            if subnet.dns_nameservers:
                setattr(self, ipvX + "_dns", subnet.dns_nameservers[0] )

            # gateway
            if subnet.gateway_ip:
                setattr(self, ipvX + "_gateway", subnet.gateway_ip )

        # TODO: determine route target
        # targets           = self.network.get_route_target_list()
        # target            = targets.get_route_target() if targets else None
        # self.route_target = target[0][7:] if target else ""
        self.route_target = ""

    def load(self):
        """Retrieve entity"""

        # load network via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided network
        self.__init_attributes__(entity)

    def save(self):
        """Persist information"""

        # try to find entity by name
        entity = self.find(self.name)

        # update an existing network
        if entity:
            # initialize attributes
            self.__init_attributes__(entity)

            # TODO: only update if subnets have changed
            pass

        # create a new network if it does not exist yet
        else:
            # create network
            self.entity = self.openstack.network.create_network(name=self.name)

            # create IPv4 subnet if required
            if self.ipv4_prefix:
                prefix  = self.ipv4_prefix
                length  = str(self.ipv4_length)
                gateway = self.ipv4_gateway
                dns     = self.ipv4_dns
                pool    = None
                if self.ipv4_start and self.ipv4_end:
                    pool = { "start": self.ipv4_start, "end": self.ipv4_end }

                self.subnet4 = self.openstack.network.create_subnet(
                    name             = self.name + "_ipv4",
                    network_id       = self.entity.id,
                    ip_version       = "4",
                    cidr             = prefix + "/" + length,
                    allocation_pools = [pool]  if pool    else [],
                    gateway_ip       = gateway if gateway else None,
                    dns_nameservers  = [dns]   if dns     else [] )

            # create IPv6 subnet if required
            if self.ipv6_prefix:
                prefix  = self.ipv6_prefix
                length  = str(self.ipv6_length)
                gateway = self.ipv6_gateway
                dns     = self.ipv6_dns
                pool    = None
                if self.ipv6_start and self.ipv6_end:
                    pool = { "start": self.ipv6_start, "end": self.ipv6_end }

                self.subnet6 = self.openstack.network.create_subnet(
                    name             = self.name + "_ipv6",
                    network_id       = self.entity.id,
                    ip_version       = "6",
                    cidr             = prefix + "/" + length,
                    allocation_pools = [pool]  if pool    else [],
                    gateway_ip       = gateway if gateway else None,
                    dns_nameservers  = [dns]   if dns     else [] )

            # create route target if required
            # if self.route_target:
            #     # determine virtual network
            #     fq_name = ['default-domain', self.tenant_name, self.name]
            #     vnet    = VirtualNetwork( fq_name[-1], parent_type = 'project', fq_name=fq_name  )

            #     route_target = "target:" + self.route_target

            #     rtl = RouteTargetList( [ route_target ] )

            #     vnet.set_route_target_list( rtl )

            #     self.contrail.virtual_network_update( vnet )

            # reload network
            self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.network.delete_network(self.id)
            self.entity  = None
            self.id      = None
            self.subnet4 = None
            self.subnet6 = None

    def find(self,name):
        """Find entity by name"""
        query = {
            "project_id": self.openstack.session.get_project_id()
        }

        for entity in self.openstack.network.networks(**query):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""

        # initialize result
        result = {
            "type":         self.type,
            "id":           self.id,
            "name":         self.name,
            "tenant_name":  self.tenant_name,
            "network_name": self.network_name,
            "route_target": self.route_target,
            "ipv4_prefix":  self.ipv4_prefix,
            "ipv4_length":  self.ipv4_length,
            "ipv4_start":   self.ipv4_start,
            "ipv4_end":     self.ipv4_end,
            "ipv4_gateway": self.ipv4_gateway,
            "ipv4_dns":     self.ipv4_dns,
            "ipv6_prefix":  self.ipv6_prefix,
            "ipv6_length":  self.ipv6_length,
            "ipv6_start":   self.ipv6_start,
            "ipv6_end":     self.ipv6_end,
            "ipv6_gateway": self.ipv6_gateway,
            "ipv6_dns":     self.ipv6_dns}

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        # ToDo: take care of list of rules
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        # compare attributes
        for attr in  [      "route_target",
            "ipv4_prefix",  "ipv4_length",
            "ipv4_gateway", "ipv4_dns",
            "ipv4_start",   "ipv4_end",
            "ipv6_prefix",  "ipv6_length",
            "ipv6_gateway", "ipv6_dns",
            "ipv6_start",   "ipv6_end"]:
            if attr1[attr] != attr2[attr]:
                return False

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, contrail, names=[]):
        """Retrieve entities by name"""
        query = {
            "project_id": openstack.session.get_project_id()
        }

        prefix = "_".join(names)

        entities = []
        for entity in openstack.network.networks(**query):
            if entity.name.startswith(prefix):
                entities.append(Network(openstack, contrail, entity=entity))

        return entities

    # --------------------------------------------------------------------------
