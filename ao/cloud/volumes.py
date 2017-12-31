#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .volume import Volume

class Volumes():
    """Volumes entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name="", cluster_name="", node_name="", volume_name="", volume_size=10, volume_type="INT"):
        """Initialize by parameters"""
        return Volume(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name,
            volume_name  = volume_name,
            volume_size  = volume_size,
            volume_type  = volume_type )

    def get(self, tenant_name, cluster_name, node_name, volume_name):
        """Retrieve by name"""
        entity = Volume(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            node_name    = node_name,
            volume_name  = volume_name)
        try:
            entity.load()
        except:
            entity = None

        return entity

    def list(self, tenant_name, cluster_name="", node_name="", volume_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, cluster_name, node_name, volume_name] if x is not None and x != ""]
        entities = Volume.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "cluster_name", "node_name", "volume_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "cluster_name", "node_name", "volume_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
