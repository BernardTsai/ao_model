#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os               import path
from json             import loads
from pannet.cloud.api import API
from unittest         import TestCase, expectedFailure
from pytest           import mark

class VolumesTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_credentials    = VolumesTest.parse_json("admin_credentials")
        tenant_credentials   = VolumesTest.parse_json("tenant_credentials")
        tenant_configuration = VolumesTest.parse_json("tenant")
        user_configuration   = VolumesTest.parse_json("user")
        role_configuration   = VolumesTest.parse_json("role")
        volume_configuration = VolumesTest.parse_json("volume")

        # establish admin connection
        self.api = API(
            openstack_url = admin_credentials["auth_url"],
            contrail_url  = admin_credentials["contrail_url"],
            project       = admin_credentials["project"],
            username      = admin_credentials["username"],
            password      = admin_credentials["password"])

        self.api.connect()

        # create tenant, administrator, role
        self.tenant = self.api.tenants().define(**tenant_configuration)
        self.administrator = self.api.users().define(**user_configuration)
        self.role = self.api.roles().define(**role_configuration)

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

        # ensure that the testcase volume has been removed
        self.volume = self.api.volumes().undefine(**volume_configuration)

    @classmethod
    def tearDownClass(self):
        admin_credentials  = VolumesTest.parse_json("admin_credentials")
        tenant_credentials = VolumesTest.parse_json("tenant_credentials")

        tenant_configuration = VolumesTest.parse_json("tenant")
        user_configuration   = VolumesTest.parse_json("user")
        role_configuration   = VolumesTest.parse_json("role")
        volume_configuration = VolumesTest.parse_json("volume")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        self.api.connect()

        # ensure that the testcase volume has been removed
        self.api.volumes().undefine(**volume_configuration)

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

    @mark.volumes
    def test__01__new(self):
        # prepare
        params = VolumesTest.parse_json("volume")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.volumes().new(**params)
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)

    @mark.volumes
    def test__02__save(self):
        # prepare
        params = VolumesTest.parse_json("volume")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.volumes().new(**params)
            entity.save()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.volumes
    def test__03__get(self):
        # prepare
        params = VolumesTest.parse_json("volume")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.volumes().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                volume_name  = params["volume_name"])
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.volumes
    def test__04__attributes(self):
        # prepare
        params = VolumesTest.parse_json("volume")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.volumes().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                volume_name  = params["volume_name"])
            attributes = entity.attributes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(attributes)

    @mark.volumes
    def test__05__delete(self):
        # prepare
        params = VolumesTest.parse_json("volume")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.volumes().get(
                tenant_name  = params["tenant_name"],
                cluster_name = params["cluster_name"],
                node_name    = params["node_name"],
                volume_name  = params["volume_name"])
            entity.delete()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)
        self.assertIsNone(entity.id)

    # --------------------------------------------------------------------------
