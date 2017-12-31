#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                       import path
from json                     import loads
from pannet.cloud.api         import API
from pannet.cloud.nodeManager import NodeManager
from unittest                 import TestCase, expectedFailure
from pytest                   import mark

class NodeManagerTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    @staticmethod
    def parse_text(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}'.format(filename))
        with open(filepath, 'r') as stream:
            return (stream.read())

    def setUp(self):
        admin_credentials           = NodeManagerTest.parse_json("admin_credentials")
        tenant_credentials          = NodeManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = NodeManagerTest.parse_json("tenant")
        user_configuration          = NodeManagerTest.parse_json("user")
        role_configuration          = NodeManagerTest.parse_json("role")
        keypair_configuration       = NodeManagerTest.parse_json("keypair")
        securitygroup_configuration = NodeManagerTest.parse_json("securitygroup")
        network_configuration       = NodeManagerTest.parse_json("network")
        server_configuration        = NodeManagerTest.parse_json("server")
        volume_configuration        = NodeManagerTest.parse_json("volume")
        port_configuration          = NodeManagerTest.parse_json("port")

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

        self.keypair       = self.api.keypairs().define(**keypair_configuration)
        self.network       = self.api.networks().define(**network_configuration)
        self.securitygroup = self.api.securitygroups().define(**securitygroup_configuration)

        # ensure non existence of server, volume and port
        self.api.ports().undefine(**port_configuration)
        self.api.volumes().undefine(**volume_configuration)
        self.api.servers().undefine(**server_configuration)

    def tearDown(self):
        admin_credentials           = NodeManagerTest.parse_json("admin_credentials")
        tenant_credentials          = NodeManagerTest.parse_json("tenant_credentials")
        tenant_configuration        = NodeManagerTest.parse_json("tenant")
        user_configuration          = NodeManagerTest.parse_json("user")
        role_configuration          = NodeManagerTest.parse_json("role")
        keypair_configuration       = NodeManagerTest.parse_json("keypair")
        securitygroup_configuration = NodeManagerTest.parse_json("securitygroup")
        network_configuration       = NodeManagerTest.parse_json("network")
        server_configuration        = NodeManagerTest.parse_json("server")
        volume_configuration        = NodeManagerTest.parse_json("volume")
        port_configuration          = NodeManagerTest.parse_json("port")

        # establish tenant connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # ensure that the testcase artefacts have been removed
            self.api.ports().undefine(**port_configuration)
            self.api.volumes().undefine(**volume_configuration)
            self.api.servers().undefine(**server_configuration)
            self.api.networks().undefine(**network_configuration)
            self.api.securitygroups().undefine(**securitygroup_configuration)
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

    @mark.nodeManager
    def test__01__create(self):
        # prepare
        params = NodeManagerTest.parse_json("nodeManager")

        # run - test should fail if any exception occurs
        try:
            manager = NodeManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], True )

        self.assertEqual( result["action"], "create" )

        self.assertEqual( result["state"], "active" )

    @mark.nodeManager
    def test__02__2x_create(self):
        # prepare
        params = NodeManagerTest.parse_json("nodeManager")

        # run - test should fail if any exception occurs
        try:
            manager = NodeManager(params=params)
            manager = NodeManager(params=params)
            result  = manager.get_result()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( result["changed"], False )

        self.assertEqual( result["action"], "none" )

        self.assertEqual( result["state"], "active" )

    # --------------------------------------------------------------------------
