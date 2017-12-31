#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError
from time        import sleep

class Server():
    """Server entity"""

    def __init__(self, openstack, entity=None,
        tenant_name   = None,
        cluster_name  = None,
        node_name     = None,
        placement     = None,
        flavor_name   = None,
        image_name    = None,
        network_name  = None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "server"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize via fully qualified name
        elif tenant_name and cluster_name and node_name:
            name = tenant_name + "_" + cluster_name + "_" + node_name

            self.entity        = None
            self.id            = None
            self.name          = name
            self.state         = "inactive"
            self.tenant_name   = tenant_name
            self.cluster_name  = cluster_name
            self.node_name     = node_name
            self.placement     = placement
            self.flavor        = None
            self.flavor_name   = flavor_name
            self.image         = None
            self.image_name    = image_name
            self.key_name      = tenant_name + "_keypair"
            self.network_name  = network_name
            self.network       = None

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity       = entity
        self.id           = entity.id
        self.name         = entity.name
        self.state        = "active"
        self.tenant_name  = entity.name.split("_",2)[0]
        self.cluster_name = entity.name.split("_",2)[1]
        self.node_name    = entity.name.split("_",2)[2]
        self.placement    = entity.availability_zone
        self.flavor       = self.openstack.compute.get_flavor(entity.flavor["id"])
        self.flavor_name  = self.flavor.name
        self.image        = self.openstack.compute.get_image(entity.image["id"])
        self.image_name   = self.image.name
        self.key_name     = entity.key_name
        self.network_name = ""

        for key in entity.addresses.keys():
            self.network_name = key
            break

    def load(self):
        """Retrieve entity"""

        # load entity via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided entity
        self.__init_attributes__(entity)

    def save(self):
        """Persist  information"""
        # try to find entity by name
        entity = self.find(self.name)

        # update an existing server
        if self.entity:

            # TODO: currently no update procedure
            pass

        # create a new server if it does not exist yet
        else:
            # determine flavor
            if not self.flavor:
                self.flavor = self.openstack.compute.find_flavor( self.flavor_name )

            # determine image
            if not self.image:
                self.image = self.openstack.image.find_image( self.image_name )

            # determine network
            query = {
                "project_id": self.openstack.session.get_project_id(),
                "name":       self.tenant_name + "_" + self.network_name }
            for entity in self.openstack.network.networks(**query):
                self.network = entity
                break

            # create server
            self.entity = self.openstack.compute.create_server(
                    name              = self.name,
                    availability_zone = self.placement,
                    flavor_id         = self.flavor.id,
                    image_id          = self.image.id,
                    networks          = [{"uuid": self.network.id}],
                    key_name          = self.key_name
                )

            self.entity = self.openstack.compute.wait_for_server(self.entity)

            # reload entity
            self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.compute.delete_server(self.id)

            # try to wait for server to be deleted
            entity = self.entity
            max    = 20
            count  = 0
            while entity:
                entity = self.find(self.name)
                sleep(0.2)
                count = count + 1
                if count > max:
                    break

            self.entity  = None
            self.id      = None
            self.flavor  = None
            self.image   = None
            self.network = None

    def find(self,name):
        # load entity via API (limit the query)
        query = {
            "project_id": self.openstack.session.get_project_id()
        }

        for entity in self.openstack.compute.servers(**query):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""

        # initialize result
        result = {
            "type":         self.type,
            "id":           self.id,
            "name":         self.name,
            "tenant_name":  self.tenant_name,
            "cluster_name": self.cluster_name,
            "node_name":    self.node_name,
            "placement":    self.placement,
            "flavor_name":  self.flavor_name,
            "image_name":   self.image_name,
            "network_name": self.network_name,
            "state":        self.state }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        # ToDo: take care of list of rules
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        # check attributes
        if attr1["flavor_name"] != attr2["flavor_name"]:
            return False

        if attr1["image_name"] != attr2["image_name"]:
            return False

        if sorted(attr1["network_name"]) != sorted(attr2["network_name"]):
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
        for entity in openstack.compute.servers(**query):
            if entity.name.startswith(prefix):
                entities.append(Server(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
