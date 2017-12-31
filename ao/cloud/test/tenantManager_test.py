#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                         import path
from json                       import loads
from pannet.cloud.api           import API
from pannet.cloud.tenantManager import TenantManager
from unittest                   import TestCase, expectedFailure
from pytest                     import mark

class TenantManagerTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    def setUp(self):
        admin_credentials     = TenantManagerTest.parse_json("admin_credentials")
        tenant_credentials    = TenantManagerTest.parse_json("tenant_credentials")
        tenant_configuration  = TenantManagerTest.parse_json("tenant")
        user_configuration    = TenantManagerTest.parse_json("user")
        role_configuration    = TenantManagerTest.parse_json("role")
        keypair_configuration = TenantManagerTest.parse_json("keypair")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # ensure that the testcase keypair has been removed
            self.api.keypairs().undefine(**keypair_configuration)
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

    def tearDown(self):
        admin_credentials     = TenantManagerTest.parse_json("admin_credentials")
        tenant_credentials    = TenantManagerTest.parse_json("tenant_credentials")
        tenant_configuration  = TenantManagerTest.parse_json("tenant")
        user_configuration    = TenantManagerTest.parse_json("user")
        role_configuration    = TenantManagerTest.parse_json("role")
        keypair_configuration = TenantManagerTest.parse_json("keypair")

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # ensure that the testcase keypair has been removed
            self.api.keypairs().undefine(**keypair_configuration)
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

    @mark.tenantManager
    def test__01__create(self):
        # prepare
        params = TenantManagerTest.parse_json("tenantManager")

        # run - test should fail if any exception occurs
        try:
            manager = TenantManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], True )

        self.assertEqual( result["action"],  "create" )

        self.assertEqual( result["state"], "active" )

        self.assertIsNotNone( result["id"] )

    @mark.tenantManager
    def test__02__2x_create(self):
        # prepare
        params = TenantManagerTest.parse_json("tenantManager")

        # run - test should fail if any exception occurs
        try:
            manager = TenantManager(params=params)
            manager = TenantManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], False )

        self.assertEqual( result["action"], "none" )

        self.assertEqual( result["state"], "active" )

        self.assertIsNotNone( result["id"] )

    # --------------------------------------------------------------------------
