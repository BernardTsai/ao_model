#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError

class Role():
    """Role entity"""

    def __init__(self, openstack, entity=None,
        role_name=None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "tenant"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize via fully qualified name
        elif role_name:
            name = role_name

            self.entity      = None
            self.id          = None
            self.name        = name
            self.state       = "inactive"
            self.role_name   = role_name

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity    = entity
        self.id        = entity.id
        self.name      = entity.name
        self.state     = "active"
        self.role_name = entity.name

    def load(self):
        """Retrieve entity"""

        # load entity via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided entity
        self.__init_attributes__(entity)

    def find(self, name):
        """Find first entity matching the name"""
        query = {
            "name": name
        }

        for entity in self.openstack.identity.roles(**query):
            return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""
        result = {
            "type":          self.type,
            "id":            self.id,
            "name":          self.name,
            "role_name":     self.role_name,
            "state":         self.state }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {}

        prefix = "_".join(names)

        entities = []
        for entity in openstack.identity.projects(**query):
            if entity.name.startswith(prefix):
                entities.append(Role(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
