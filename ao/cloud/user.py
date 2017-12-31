#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError

class User():
    """User entity"""

    def __init__(self, openstack, entity=None,
        tenant_name = None,
        user_name   = None,
        password    = None,
        description = None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "user"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize via fully qualified name
        elif tenant_name and user_name:
            name  = tenant_name + "_" + user_name

            self.entity      = None
            self.id          = None
            self.name        = name
            self.state       = "inactive"
            self.tenant_name = tenant_name
            self.user_name   = user_name
            self.password    = password
            self.description = description

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity          = entity
        self.id              = entity.id
        self.name            = entity.name
        self.state           = "active"
        self.tenant_name     = entity.name.split("_",1)[0]
        self.user_name       = entity.name.split("_",1)[1]
        self.password        = ""
        self.description     = entity.description
        self.default_project = entity.default_project_id


    def load(self):
        """Retrieve entity"""

        # load entity via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided entity
        self.__init_attributes__(entity)

    def save(self):
        """Persist information"""
        # try to find entity by name
        self.entity = self.find(self.name)

        if not self.entity:
            if self.name != "" and self.password != "":
                self.entity = self.openstack.identity.create_user(
                    name               = self.name,
                    password           = self.password,
                    description        = self.description,
                    default_project_id = self.openstack.session.get_project_id() )
            else:
                raise ParameterError("Missing password")
        elif self.entity.description        != self.description or \
             self.entity.default_project_id != self.default_project:
            self.openstack.identity.update_user(
                self.entity.id,
                default_project_id = self.default_project,
                description        = self.description)
        else:
            pass

        # reload entity
        self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.identity.delete_user(self.id)
            self.entity = None
            self.id     = None

    def find(self, name):
        """Find first entity matching the name"""
        query = {}

        for entity in self.openstack.identity.users(**query):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""
        result = {
            "type":        self.type,
            "id":          self.id,
            "name":        self.name,
            "tenant_name": self.tenant_name,
            "user_name":   self.user_name,
            "description": self.description,
            "password":    self.password,
            "state":       self.state }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        # check other attributes
        if attr1["description"] != attr2["description"]:
            return False

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {}

        prefix = "_".join(names)

        entities = []
        for entity in openstack.identity.users(**query):
            if entity.name.startswith(prefix):
                entities.append(User(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
