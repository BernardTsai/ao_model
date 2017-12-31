#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os               import path
from json             import loads
from pannet.cloud.api import API
from unittest         import TestCase, expectedFailure
from pytest           import mark

class PortsTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @staticmethod
    def parse_text(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}'.format(filename))
        with open(filepath, 'r') as stream:
            return (stream.read())

    @classmethod
    def setUpClass(self):
        admin_credentials           = PortsTest.parse_json("admin_credentials")
        tenant_credentials          = PortsTest.parse_json("tenant_credentials")
        tenant_configuration        = PortsTest.parse_json("tenant")
        user_configuration          = PortsTest.parse_json("user")
        role_configuration          = PortsTest.parse_json("role")
        keypair_configuration       = PortsTest.parse_json("keypair")
        network_configuration       = PortsTest.parse_json("network")
        server_configuration        = PortsTest.parse_json("server")
        securitygroup_configuration = PortsTest.parse_json("securitygroup")
        port_configuration          = PortsTest.parse_json("port")

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
        self.securitygroup = self.api.securitygroups().define(**securitygroup_configuration)

        # ensure that the testcase port has been removed
        self.api.ports().undefine(**port_configuration)

    @classmethod
    def tearDownClass(self):
        admin_credentials           = PortsTest.parse_json("admin_credentials")
        tenant_credentials          = PortsTest.parse_json("tenant_credentials")
        tenant_configuration        = PortsTest.parse_json("tenant")
        user_configuration          = PortsTest.parse_json("user")
        role_configuration          = PortsTest.parse_json("role")
        keypair_configuration       = PortsTest.parse_json("keypair")
        network_configuration       = PortsTest.parse_json("network")
        server_configuration        = PortsTest.parse_json("server")
        securitygroup_configuration = PortsTest.parse_json("securitygroup")
        port_configuration          = PortsTest.parse_json("port")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

        # ensure that the testcase port has been removed
        self.api.ports().undefine(**port_configuration)

        # remove server, network, security group and keypair
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

    @mark.ports
    def test__01__new(self):
        # prepare
        params = PortsTest.parse_json("port")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.ports().new(**params)
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)

    @mark.ports
    def test__02__save(self):
        # prepare
        params = PortsTest.parse_json("port")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.ports().new(**params)
            entity.save()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.ports
    def test__03__get(self):
        # prepare
        params = PortsTest.parse_json("port")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.ports().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                network_name = params["network_name"])
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.ports
    def test__04__attributes(self):
        # prepare
        params = PortsTest.parse_json("port")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.ports().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                network_name = params["network_name"])
            attributes = entity.attributes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(attributes)

    @mark.ports
    def test__05__delete(self):
        # prepare
        params = PortsTest.parse_json("port")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.ports().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                network_name = params["network_name"])
            entity.delete()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)
        self.assertIsNone(entity.id)

    # --------------------------------------------------------------------------
