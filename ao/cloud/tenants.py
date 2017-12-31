#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .tenant import Tenant

class Tenants():
    """Tenants entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name, description=""):
        """Initialize entity by parameters"""
        return Tenant(
            openstack   = self.openstack,
            tenant_name = tenant_name,
            description = description)

    def get(self, tenant_name):
        """Retrieve entity by name"""
        entity = Tenant(
            openstack   = self.openstack,
            tenant_name = tenant_name)
        try:
            entity.load()
        except:
            entity = None

        return entity

    def list(self, tenant_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name] if x is not None and x != ""]
        entities = Tenant.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
