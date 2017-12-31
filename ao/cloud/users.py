#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .user import User

class Users():
    """Users entity"""

    def __init__(self, openstack):
        """Initialize"""
        self.openstack = openstack

    def new(self, tenant_name, user_name, password="", description=""):
        """Initialize entity by name"""
        return User(
            openstack   = self.openstack,
            tenant_name = tenant_name,
            user_name   = user_name,
            password    = password,
            description = description)

    def get(self, tenant_name, user_name):
        """Retrieve entity by name"""
        entity = User(
            openstack   = self.openstack,
            tenant_name = tenant_name,
            user_name   = user_name)
        try:
            entity.load()
        except:
            entity = None

        return entity

    def list(self, tenant_name="", user_name=""):
        """Retrieve entities by name"""
        names    = [x for x in[tenant_name, user_name] if x is not None and x != ""]
        entities = User.list(openstack=self.openstack, names=names)

        return entities

    def define(self, **kwargs):
        """Define entity"""
        names  = ["tenant_name", "user_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if not entity:
            entity = self.new(**kwargs)
            entity.save()

        return entity

    def undefine(self, **kwargs):
        """Undefine entity"""
        names  = ["tenant_name", "user_name"]
        params = {k: v for k, v in kwargs.items() if k in names}
        entity = self.get(**params)
        if entity:
            entity.delete()
