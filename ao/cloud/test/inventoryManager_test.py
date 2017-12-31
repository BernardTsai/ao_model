#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                            import path
from json                          import loads
from pannet.cloud.api              import API
from pannet.cloud.inventoryManager import InventoryManager
from unittest                      import TestCase, expectedFailure
from pytest                        import mark

class InventoryManagerTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_credentials           = InventoryManagerTest.parse_json("admin_credentials")
        tenant_credentials          = InventoryManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = InventoryManagerTest.parse_json("tenant")
        user_configuration          = InventoryManagerTest.parse_json("user")
        role_configuration          = InventoryManagerTest.parse_json("role")
        keypair_configuration       = InventoryManagerTest.parse_json("keypair")
        network_configuration       = InventoryManagerTest.parse_json("network")
        server_configuration        = InventoryManagerTest.parse_json("server")
        securitygroup_configuration = InventoryManagerTest.parse_json("securitygroup")
        volume_configuration        = InventoryManagerTest.parse_json("volume")
        port_configuration          = InventoryManagerTest.parse_json("port")

        # establish admin connection
        self.api = API(
            openstack_url = admin_credentials["auth_url"],
            contrail_url  = admin_credentials["contrail_url"],
            project       = admin_credentials["project"],
            username      = admin_credentials["username"],
            password      = admin_credentials["password"])

        self.api.connect()

        # create tenant, administrator, role
        self.tenant        = self.api.tenants().define(**tenant_configuration)
        self.administrator = self.api.users().define(**user_configuration)
        self.role          = self.api.roles().define(**role_configuration)

        # grant admin rights to user
        self.tenant.grant(self.administrator, self.role)

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

        # create keypair, network, server and security group
        self.keypair       = self.api.keypairs().define(**keypair_configuration)
        self.network       = self.api.networks().define(**network_configuration)
        self.server        = self.api.servers().define(**server_configuration)
        self.volume        = self.api.volumes().define(**volume_configuration)
        self.securitygroup = self.api.securitygroups().define(**securitygroup_configuration)
        self.port          = self.api.ports().define(**port_configuration)

    @classmethod
    def tearDownClass(self):
        admin_credentials           = InventoryManagerTest.parse_json("admin_credentials")
        tenant_credentials          = InventoryManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = InventoryManagerTest.parse_json("tenant")
        user_configuration          = InventoryManagerTest.parse_json("user")
        role_configuration          = InventoryManagerTest.parse_json("role")
        keypair_configuration       = InventoryManagerTest.parse_json("keypair")
        network_configuration       = InventoryManagerTest.parse_json("network")
        server_configuration        = InventoryManagerTest.parse_json("server")
        securitygroup_configuration = InventoryManagerTest.parse_json("securitygroup")
        volume_configuration        = InventoryManagerTest.parse_json("volume")
        port_configuration          = InventoryManagerTest.parse_json("port")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

        # remove port, volume, server, network, security group and keypair
        self.api.ports().undefine(**port_configuration)
        self.api.volumes().undefine(**volume_configuration)
        self.api.servers().undefine(**server_configuration)
        self.api.securitygroups().undefine(**securitygroup_configuration)
        self.api.keypairs().undefine(**keypair_configuration)
        self.api.networks().undefine(**network_configuration)

        # establish admin connection
        self.api = API(
            openstack_url = admin_credentials["auth_url"],
            contrail_url  = admin_credentials["contrail_url"],
            project       = admin_credentials["project"],
            username      = admin_credentials["username"],
            password      = admin_credentials["password"])

        self.api.connect()

        # delete administrator and tenant
        self.api.users().undefine(**user_configuration)
        self.api.tenants().undefine(**tenant_configuration)
    # --------------------------------------------------------------------------

    @mark.inventoryManager
    def test__01__inventory(self):
        # prepare
        params = InventoryManagerTest.parse_json("inventoryManager")

        # run - test should fail if any exception occurs
        try:
            manager = InventoryManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], False )

        self.assertEqual( result["action"],  "none" )

        self.assertIsNotNone( result["id"] )

    # --------------------------------------------------------------------------
