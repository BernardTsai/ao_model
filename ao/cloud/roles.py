#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .role import Role

class Roles():
    """Roles entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def get(self, role_name):
        """Retrieve entity by name"""
        entity = Role(
            openstack = self.openstack,
            role_name = role_name)
        try:
            entity.load()
        except:
            entity = None

        return entity

    def list(self, role_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[role_name] if x is not None and x != ""]
        entities = Role.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["role_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        pass
