#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                          import path
from json                        import loads
from pannet.cloud.api            import API
from pannet.cloud.cleanupManager import CleanupManager
from unittest                    import TestCase, expectedFailure
from pytest                      import mark

class CleanupManagerTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_credentials           = CleanupManagerTest.parse_json("admin_credentials")
        tenant_credentials          = CleanupManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = CleanupManagerTest.parse_json("tenant")
        user_configuration          = CleanupManagerTest.parse_json("user")
        role_configuration          = CleanupManagerTest.parse_json("role")
        keypair_configuration       = CleanupManagerTest.parse_json("keypair")
        network_configuration       = CleanupManagerTest.parse_json("network")
        server_configuration        = CleanupManagerTest.parse_json("server")
        securitygroup_configuration = CleanupManagerTest.parse_json("securitygroup")
        volume_configuration        = CleanupManagerTest.parse_json("volume")
        port_configuration          = CleanupManagerTest.parse_json("port")

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
        admin_credentials           = CleanupManagerTest.parse_json("admin_credentials")
        tenant_credentials          = CleanupManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = CleanupManagerTest.parse_json("tenant")
        user_configuration          = CleanupManagerTest.parse_json("user")
        role_configuration          = CleanupManagerTest.parse_json("role")
        keypair_configuration       = CleanupManagerTest.parse_json("keypair")
        network_configuration       = CleanupManagerTest.parse_json("network")
        server_configuration        = CleanupManagerTest.parse_json("server")
        securitygroup_configuration = CleanupManagerTest.parse_json("securitygroup")
        volume_configuration        = CleanupManagerTest.parse_json("volume")
        port_configuration          = CleanupManagerTest.parse_json("port")

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # remove port, volume, server, network, security group and keypair
            self.api.ports().undefine(**port_configuration)
            self.api.volumes().undefine(**volume_configuration)
            self.api.servers().undefine(**server_configuration)
            self.api.securitygroups().undefine(**securitygroup_configuration)
            self.api.keypairs().undefine(**keypair_configuration)
            self.api.networks().undefine(**network_configuration)
        except:
            pass

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

    @mark.cleanupManager
    def test__01__cleanup(self):
        # prepare
        params = CleanupManagerTest.parse_json("cleanupManager")

        # run - test should fail if any exception occurs
        try:
            manager = CleanupManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], True )

        self.assertEqual( result["action"], "delete" )
    # --------------------------------------------------------------------------
