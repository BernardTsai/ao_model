#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError

class Port():
    """Port entity"""

    def __init__(self, openstack, entity=None,
        node         = None,
        network      = None,
        tenant_name  = None,
        cluster_name = None,
        node_name    = None,
        network_name = None,
        allowed      = None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "port"

        # initialize with provided port
        if entity:
            self.__init_attributes__(entity)

        # initialize with node and network parameters
        elif node and network:
            self.entity       = None
            self.id           = None
            self.name         = node.name + "_" + network.name.split("_",1)[1]
            self.state        = "inactive"
            self.node         = node
            self.network      = network
            self.tenant_name  = node.name.split("_",2)[0]
            self.cluster_name = node.name.split("_",2)[1]
            self.node_name    = node.name.split("_",2)[2]
            self.network_name = network.name.split("_",1)[1]
            self.allowed      = allowed

        # initialize via fully qualified name
        elif tenant_name and cluster_name and node_name and network_name:
            name  = tenant_name + "_" + cluster_name + "_" + node_name + "_" + network_name

            self.entity       = None
            self.id           = None
            self.name         = name
            self.state        = "inactive"
            self.node         = node
            self.network      = network
            self.tenant_name  = tenant_name
            self.cluster_name = cluster_name
            self.node_name    = node_name
            self.network_name = network_name
            self.allowed      = allowed

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity       = entity
        self.id           = entity.id
        self.name         = entity.name
        self.state        = "active" if entity.is_admin_state_up else "inactive"
        self.node         = None
        self.network      = None
        self.tenant_name  = entity.name.split("_",3)[0]
        self.cluster_name = entity.name.split("_",3)[1]
        self.node_name    = entity.name.split("_",3)[2]
        self.network_name = entity.name.split("_",3)[3]
        self.allowed      = []
        if entity.allowed_address_pairs:
            for aap in entity.allowed_address_pairs:
                self.allowed.append( aap["ip_address"] )

    def load(self):
        """Retrieve entity"""

        # load volume via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided entity
        self.__init_attributes__(entity)

    def save(self):
        """Persist information"""

        # update an existing port
        if self.entity:
            allowed_address_pairs = []
            for addr in self.allowed:
                allowed_address_pairs.append({ "ip_address": addr })

            self.openstack.network.update_port(self.id, allowed_address_pairs=allowed_address_pairs)

        # create a new port if it does not exist yet
        else:
            # create port
            security_group_name = self.tenant_name + "_" + self.cluster_name + "_" + self.network_name
            security_group      = None

            # load securitygroup via API (limit the query)
            query = {"project_id": self.openstack.session.get_project_id()}
            for entity in self.openstack.network.security_groups(**query):
                if entity.name == security_group_name:
                    security_group = entity
                    break

            if not security_group:
                security_group = self.openstack.network.create_security_group(name=security_group_name)

            security_group_ids  = [security_group.id]

            allowed_address_pairs = []
            for addr in self.allowed:
                allowed_address_pairs.append({ "ip_address": addr })

            description = "VNF: " + self.tenant_name + "\nCluster: " + self.cluster_name + "\nNode: " + self.node_name + "\nNetwork: " + self.network_name

            if not self.network:
                query = {"project_id": self.openstack.session.get_project_id()}
                for entity in self.openstack.network.networks(**query):
                    if entity.name == self.tenant_name + "_" + self.network_name:
                        self.network = entity
                        break

            if not self.node:
                self.node = self.openstack.compute.find_server(self.tenant_name + "_" + self.cluster_name + "_" + self.node_name)

            self.entity = self.openstack.network.create_port(
                name                  = self.name,
                allowed_address_pairs = allowed_address_pairs,
                security_group_ids    = security_group_ids,
                device_id             = self.node.id,
                network_id            = self.network.id,
                is_admin_state_up     = True,
                description           = description)

            # reload port
            self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.network.delete_port(self.id)
            self.entity = None
            self.id     = None

    def find(self, name):
        """Find first entity matching the name"""
        query = {
            "project_id": self.openstack.session.get_project_id()
        }

        for entity in self.openstack.network.ports( **query ):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine port as dictionary"""

        # initialize result
        result = {
            "type":          self.type,
            "id":            self.id,
            "name":          self.name,
            "tenant_name":   self.tenant_name,
            "cluster_name":  self.cluster_name,
            "node_name":     self.node_name,
            "network_name":  self.network_name,
            "allowed":       self.allowed,
            "state":         self.state }

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
        if sorted(attr1["allowed"]) != sorted(attr2["allowed"]):
            return False

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {"project_id": openstack.session.get_project_id()}

        prefix = "_".join(names)

        entities = []
        for entity in openstack.network.ports(**query):
            if entity.name.startswith(prefix):
                entities.append(Port(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
