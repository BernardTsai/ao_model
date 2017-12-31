#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os               import path
from json             import loads
from pannet.cloud.api import API
from unittest         import TestCase, expectedFailure
from pytest           import mark

class SecurityGroupsTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_credentials           = SecurityGroupsTest.parse_json("admin_credentials")
        tenant_credentials          = SecurityGroupsTest.parse_json("tenant_credentials")
        tenant_configuration        = SecurityGroupsTest.parse_json("tenant")
        user_configuration          = SecurityGroupsTest.parse_json("user")
        role_configuration          = SecurityGroupsTest.parse_json("role")
        securitygroup_configuration = SecurityGroupsTest.parse_json("securitygroup")

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

        # ensure that the testcase security group has been removed
        self.api.securitygroups().undefine(**securitygroup_configuration)

    @classmethod
    def tearDownClass(self):
        admin_credentials           = SecurityGroupsTest.parse_json("admin_credentials")
        tenant_credentials          = SecurityGroupsTest.parse_json("tenant_credentials")
        tenant_configuration        = SecurityGroupsTest.parse_json("tenant")
        user_configuration          = SecurityGroupsTest.parse_json("user")
        role_configuration          = SecurityGroupsTest.parse_json("role")
        securitygroup_configuration = SecurityGroupsTest.parse_json("securitygroup")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

        # ensure that the testcase security group has been removed
        self.api.securitygroups().undefine(**securitygroup_configuration)

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

    @mark.securitygroups
    def test__01__new(self):
        # prepare
        params = SecurityGroupsTest.parse_json("securitygroup")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.securitygroups().new(**params)
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)

    @mark.securitygroups
    def test__02__save(self):
        # prepare
        params = SecurityGroupsTest.parse_json("securitygroup")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.securitygroups().new(**params)
            entity.save()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.securitygroups
    def test__03__get(self):
        # prepare
        params = SecurityGroupsTest.parse_json("securitygroup")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.securitygroups().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                network_name = params["network_name"] )
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.securitygroups
    def test__04__attributes(self):
        # prepare
        params = SecurityGroupsTest.parse_json("securitygroup")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.securitygroups().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                network_name = params["network_name"] )
            attributes = entity.attributes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(attributes)

    @mark.securitygroups
    def test__05__delete(self):
        # prepare
        params = SecurityGroupsTest.parse_json("securitygroup")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.securitygroups().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                network_name = params["network_name"] )
            entity.delete()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)
        self.assertIsNone(entity.id)

    # --------------------------------------------------------------------------
