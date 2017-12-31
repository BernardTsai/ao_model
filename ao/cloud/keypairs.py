#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .keypair import Keypair

class Keypairs():
    """Keypairs entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name="", keypair_name="", public_key=""):
        """Initialize by parameters"""
        return Keypair(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            keypair_name = keypair_name,
            public_key   = public_key)

    def get(self, tenant_name, keypair_name):
        """Retrieve by name"""
        keypair = Keypair(
            openstack    = self.openstack,
            tenant_name  = tenant_name,
            keypair_name = keypair_name)
        try:
            keypair.load()
        except:
            keypair = None

        return keypair

    def list(self, tenant_name, keypair_name):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, keypair_name] if x is not None and x != ""]
        entities = Keypair.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "keypair_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "keypair_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
