#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os               import path
from json             import loads
from pannet.cloud.api import API
from unittest         import TestCase, expectedFailure
from pytest           import mark

class RolesTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_configuration = RolesTest.parse_json("admin_credentials")
        params              = RolesTest.parse_json("user")

        # establish admin connection
        self.api = API(
            openstack_url = admin_configuration["auth_url"],
            contrail_url  = admin_configuration["contrail_url"],
            project       = admin_configuration["project"],
            username      = admin_configuration["username"],
            password      = admin_configuration["password"])

        self.api.connect()

    @classmethod
    def tearDownClass(self):
        pass

    # --------------------------------------------------------------------------

    @mark.roles
    def test__01__get(self):
        # prepare
        params = RolesTest.parse_json("role")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.roles().get(role_name = params["role_name"])
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.roles
    def test__02__attributes(self):
        # prepare
        params = RolesTest.parse_json("role")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.roles().get(role_name = params["role_name"])
            attributes = entity.attributes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(attributes)
