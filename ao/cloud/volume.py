#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError, TimeoutError
from time        import sleep

class Volume():
    """Volume entity"""

    def __init__(self, openstack, entity=None,
        tenant_name  = None,
        cluster_name = None,
        node_name    = None,
        volume_name  = None,
        volume_size  = None,
        volume_type  = None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "volume"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize with provided parameters
        elif tenant_name and cluster_name and node_name and volume_name:
            name  = tenant_name + "_" + cluster_name + "_" + node_name + "_" + volume_name

            self.entity       = None
            self.id           = None
            self.name         = name
            self.state        = "inactive"
            self.tenant_name  = tenant_name
            self.cluster_name = cluster_name
            self.node_name    = node_name
            self.volume_name  = volume_name
            self.volume_size  = volume_size
            self.volume_type  = volume_type

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity       = entity
        self.id           = entity.id
        self.name         = entity.name
        self.state        = "active"
        self.tenant_name  = entity.name.split("_",3)[0]
        self.cluster_name = entity.name.split("_",3)[1]
        self.node_name    = entity.name.split("_",3)[2]
        self.volume_name  = entity.name.split("_",3)[3]
        self.volume_size  = entity.size
        self.volume_type  = entity.volume_type

    def load(self):
        """Retrieve entity"""

        # load volume via API
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
            self.entity = self.openstack.block_store.create_volume(
                name        = self.name,
                size        = self.volume_size,
                volume_type = self.volume_type,
                description = "VNF: " + self.tenant_name + "\nCluster: " + self.cluster_name + "\nNode: " + self.node_name + "\nVolume: " + self.volume_name)

        # reload entity
        self.load()

        # attach to server
        self.attach()

    def delete(self):
        """Remove entity"""
        if self.entity:
            # detach volume from server
            self.detach()

            # wait until volume has been detached or timeout
            for i in range(10):
                try:
                    volume = self.openstack.block_store.get_volume(self.id)
                except:
                    return

                if volume.status == "available":
                    self.openstack.block_store.delete_volume(self.id)
                    self.entity = None
                    self.id     = None
                    return

                sleep( 0.2 )

            raise TimeoutError("Timeout while attempting to delete a volume")

    def find(self, name):
        """Find first entity matching the name"""
        query = {
            "project_id": self.openstack.session.get_project_id()
        }

        for entity in self.openstack.block_store.volumes( **query ):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine volume attributes as dictionary"""
        result = {
            "type":         self.type,
            "id":           self.id,
            "name":         self.name,
            "tenant_name":  self.tenant_name,
            "cluster_name": self.cluster_name,
            "node_name":    self.node_name,
            "volume_name":  self.volume_name,
            "volume_size":  self.volume_size,
            "volume_type":  self.volume_type }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        # check other attributes
        if attr1["volume_size"] != attr2["volume_size"] or \
           attr1["volume_type"] != attr2["volume_type"]:
            return False

        return True

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {}

        prefix = "_".join(names)

        entities = []
        for entity in openstack.block_store.volumes(**query):
            if entity.name.startswith(prefix):
                entities.append(Volume(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------

    def attach(self):
        """Attach a volume"""

        # only existing volumes can be attached
        if not self.id:
            return

        # determine server
        name  = self.tenant_name + "_" + self.cluster_name + "_" + self.node_name
        query = {"project_id": self.openstack.session.get_project_id()}

        server = None
        for entity in self.openstack.block_store.volumes( **query ):
            if entity.name == name:
                server = entity
                break

        # leave if no server is available
        if not server:
            return

        # check if already has been attached
        for attachment in self.openstack.compute.volume_attachments(server):
            if attachment["volume_id"] == self.id:
                return

        # attachment needs to be created
        self.openstack.compute.create_volume_attachment(
            server    = server,
            volume_id = self.id
        )

    def detach(self):
        """Detach a volume"""

        # only existing volumes can be attached
        if not self.id:
            return

        # determine server
        name  = self.tenant_name + "_" + self.cluster_name + "_" + self.node_name
        query = {"project_id": self.openstack.session.get_project_id()}

        server = None
        for entity in self.openstack.block_store.volumes( **query ):
            if entity.name == name:
                server = entity
                break

        # leave if no server is available
        if not server:
            return

        # check if volume is attached
        for attachment in self.openstack.compute.volume_attachments(server):
            if attachment["volume_id"] == self.id:
                # attachment needs to be deleted
                self.openstack.compute.delete_volume_attachment(
                    volume_attachment = attachment,
                    server            = server
                )

    # --------------------------------------------------------------------------
