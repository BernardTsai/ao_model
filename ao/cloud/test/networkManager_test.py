#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                          import path
from json                        import loads
from pannet.cloud.api            import API
from pannet.cloud.networkManager import NetworkManager
from unittest                    import TestCase, expectedFailure
from pytest                      import mark

class NetworkManagerTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    def setUp(self):
        admin_credentials     = NetworkManagerTest.parse_json("admin_credentials")
        tenant_credentials    = NetworkManagerTest.parse_json("tenant_credentials")
        tenant_configuration  = NetworkManagerTest.parse_json("tenant")
        user_configuration    = NetworkManagerTest.parse_json("user")
        role_configuration    = NetworkManagerTest.parse_json("role")

        # establish admin connection
        self.api = API(
            openstack_url = admin_credentials["auth_url"],
            contrail_url  = admin_credentials["contrail_url"],
            project       = admin_credentials["project"],
            username      = admin_credentials["username"],
            password      = admin_credentials["password"])

        self.api.connect()

        self.tenant = self.api.tenants().define(**tenant_configuration)
        self.user   = self.api.users().define(**user_configuration)
        self.role   = self.api.roles().define(**role_configuration)

        self.tenant.grant(self.user, self.role)

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

    def tearDown(self):
        admin_credentials     = NetworkManagerTest.parse_json("admin_credentials")
        tenant_credentials    = NetworkManagerTest.parse_json("tenant_credentials")
        tenant_configuration  = NetworkManagerTest.parse_json("tenant")
        user_configuration    = NetworkManagerTest.parse_json("user")
        role_configuration    = NetworkManagerTest.parse_json("role")
        network_configuration = NetworkManagerTest.parse_json("network")

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # ensure that the testcase  network has been removed
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

    @mark.networkManager
    def test__01__create(self):
        # prepare
        params = NetworkManagerTest.parse_json("networkManager")

        # run - test should fail if any exception occurs
        try:
            manager = NetworkManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], True )

        self.assertEqual( result["action"],  "create" )

        self.assertEqual( result["state"], "active" )

        self.assertIsNotNone( result["id"] )

    @mark.networkManager
    def test__02__2x(self):
        # prepare
        params = NetworkManagerTest.parse_json("networkManager")

        # run - test should fail if any exception occurs
        try:
            manager = NetworkManager(params=params)
            manager = NetworkManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], False )

        self.assertEqual( result["action"], "none" )

        self.assertEqual( result["state"], "active" )

        self.assertIsNotNone( result["id"] )

    # --------------------------------------------------------------------------
