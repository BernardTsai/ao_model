#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .network import Network

class Networks():
    """Networks entity"""

    def __init__(self, openstack, contrail):
        """Initialize"""
        self.openstack = openstack
        self.contrail  = contrail

    def new(self, tenant_name, network_name,
        route_target = None,
        ipv4_prefix  = None, ipv4_length = None,
        ipv4_start   = None, ipv4_end    = None,
        ipv4_gateway = None, ipv4_dns    = None,
        ipv6_prefix  = None, ipv6_length = None,
        ipv6_start   = None, ipv6_end    = None,
        ipv6_gateway = None, ipv6_dns    = None):
        """Initialize network by parameters"""
        return Network(
            openstack    = self.openstack,
            contrail     = self.contrail,
            tenant_name  = tenant_name,
            network_name = network_name,
            route_target = route_target,
            ipv4_prefix  = ipv4_prefix,
            ipv4_length  = ipv4_length,
            ipv4_start   = ipv4_start,
            ipv4_end     = ipv4_end,
            ipv4_gateway = ipv4_gateway,
            ipv4_dns     = ipv4_dns,
            ipv6_prefix  = ipv6_prefix,
            ipv6_length  = ipv6_length,
            ipv6_start   = ipv6_start,
            ipv6_end     = ipv6_end,
            ipv6_gateway = ipv6_gateway,
            ipv6_dns     = ipv6_dns)

    def get(self, tenant_name, network_name):
        """Retrieve user by name"""
        network = Network(
            openstack    = self.openstack,
            contrail     = self.contrail,
            tenant_name  = tenant_name,
            network_name = network_name )
        try:
            network.load()
        except:
            network = None

        return network

    def list(self, tenant_name, network_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, network_name] if x is not None and x != ""]
        entities = Network.list(openstack=self.openstack, contrail=self.contrail, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
