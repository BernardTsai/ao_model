#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .securitygroup import SecurityGroup

class SecurityGroups():
    """SecurityGroups entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name="", cluster_name="", network_name="", rules=None):
        """Initialize by parameters"""
        return SecurityGroup(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            network_name = network_name,
            rules        = rules)

    def get(self, tenant_name, cluster_name, network_name):
        """Retrieve by name"""
        securitygroup = SecurityGroup(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            cluster_name = cluster_name,
            network_name = network_name)
        try:
            securitygroup.load()
        except:
            securitygroup = None

        return securitygroup

    def list(self, tenant_name, cluster_name="", network_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, cluster_name, network_name] if x is not None and x != ""]
        entities = SecurityGroup.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "cluster_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "cluster_name", "network_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
