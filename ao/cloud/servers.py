#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .server import Server

class Servers():
    """Servers entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name="", cluster_name="", node_name="", placement="", flavor_name="", image_name="", network_name=""):
        """Initialize by parameters"""
        return Server(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name,
            placement    = placement,
            flavor_name  = flavor_name,
            image_name   = image_name,
            network_name = network_name)

    def get(self, tenant_name, cluster_name, node_name):
        """Retrieve by name"""
        entity = Server(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name)
        try:
            entity.load()
        except:
            entity = None

        return entity

    def list(self, tenant_name, cluster_name="", node_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, cluster_name, node_name] if x is not None and x != ""]
        entities = Server.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "cluster_name", "node_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "cluster_name", "node_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
