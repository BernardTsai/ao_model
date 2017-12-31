#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError

class Keypair():
    """Keypair entity"""

    def __init__(self, openstack, entity=None,
        tenant_name  = None,
        keypair_name = None,
        public_key   = None):
        """Initialize"""
        self.openstack  = openstack
        self.type       = "keypair"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize with provided parameters
        elif tenant_name and keypair_name:
            name  = tenant_name + "_" + keypair_name

            self.entity       = None
            self.id           = None
            self.name         = name
            self.state        = "inactive"
            self.tenant_name  = tenant_name
            self.keypair_name = keypair_name
            self.public_key   = public_key
            self.fingerprint  = ""

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
        self.keypair_name = entity.name.split("_",1)[1]
        self.public_key   = entity.public_key
        self.fingerprint  = entity.fingerprint

    def load(self):
        """Retrieve entity"""

        # load securitygroup via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided volume
        self.__init_attributes__(entity)

    def save(self):
        """Persist information"""
        # try to find entity by name
        self.entity = self.find(self.name)

        if not self.entity:
            self.entity = self.openstack.compute.create_keypair(
                name        = self.name,
                public_key  = self.public_key)

        # reload entity
        self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.compute.delete_keypair(self.id)
            self.entity = None
            self.id     = None

    def find(self, name):
        """Find first entity matching the name"""
        query = {}

        for entity in self.openstack.compute.keypairs( **query ):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""
        result = {
            "type":         self.type,
            "id":           self.id,
            "name":         self.name,
            "tenant_name":  self.tenant_name,
            "keypair_name": self.keypair_name,
            "public_key":   self.public_key,
            "fingerprint":  self.fingerprint }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        # check other attributes
        pass

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {}

        prefix = "_".join(names)

        entities = []
        for entity in openstack.compute.keypairs(**query):
            if entity.name.startswith(prefix):
                entities.append(Keypair(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
