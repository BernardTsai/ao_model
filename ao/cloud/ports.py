#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .port import Port

class Ports():
    """Ports entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name, cluster_name, node_name, network_name, allowed=None):
        """Initialize port by parameters"""
        return Port(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name,
            network_name = network_name,
            allowed      = allowed)

    def add(self, node, network, allowed=None):
        """Initialize port by parameters"""
        return Port(
            openstack = self.openstack,
            node      = node,
            network   = network,
            allowed   = allowed)

    def get(self, tenant_name, cluster_name, node_name, network_name):
        """Retrieve port by name"""
        port = Port(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name,
            network_name = network_name)
        try:
            port.load()
        except:
            port = None

        return port

    def list(self, tenant_name, cluster_name="", node_name="", network_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, cluster_name, node_name, network_name] if x is not None and x != ""]
        entities = Port.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "cluster_name", "node_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "cluster_name", "node_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
