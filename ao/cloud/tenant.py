#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError
from requests    import put

class Tenant():
    """Tenant entity"""

    def __init__(self, openstack, entity=None,
        tenant_name=None,
        description=None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "tenant"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize via fully qualified name
        elif tenant_name:
            name = tenant_name

            self.entity      = None
            self.id          = None
            self.name        = name
            self.state       = "inactive"
            self.tenant_name = tenant_name
            self.description = description

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity        = entity
        self.id            = entity.id
        self.name          = entity.name
        self.state         = "active"
        self.tenant_name   = entity.name
        self.description   = entity.description

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
            self.entity = self.openstack.identity.create_project( name=self.tenant_name, description=self.description )
        elif self.entity.description != self.description:
            self.openstack.identity.update_project( self.entity.id, description=self.description )

        # reload entity
        self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.identity.delete_project( self.id )
            self.entity = None
            self.id     = None

    def find(self, name):
        """Find first entity matching the name"""
        query = {}

        for entity in self.openstack.identity.projects(**query):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""
        result = {
            "type":          self.type,
            "id":            self.id,
            "name":          self.name,
            "tenant_name":   self.tenant_name,
            "description":   self.description,
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
        query = {
            "project_id": openstack.session.get_project_id()
        }

        prefix = "_".join(names)

        entities = []
        for entity in openstack.identity.projects(**query):
            if entity.name.startswith(prefix):
                entities.append(Tenant(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------

    def grant(self, user, role):
        """Grant access privilege"""
        if self.entity and user and role:
            token    = self.openstack.authorize()
            base_url = self.openstack.authenticator.auth_url
            url      = base_url + "/tenants/{}/users/{}/roles/OS-KSADM/{}".format(self.entity.id,user.id,role.id)
            headers  = { "Content-type": "application/json", "X-Auth-Token": token }
            response = put(url, headers=headers )

            # update default project
            user.default_project = self.entity.id
            user.save()

            return( response )

        return None

    # --------------------------------------------------------------------------
