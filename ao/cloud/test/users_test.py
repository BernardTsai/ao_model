#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os               import path
from json             import loads
from pannet.cloud.api import API
from unittest         import TestCase, expectedFailure
from pytest           import mark

class UsersTest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        admin_configuration = UsersTest.parse_json("admin_credentials")
        user_configuration  = UsersTest.parse_json("user")

        # establish admin connection
        self.api = API(
            openstack_url = admin_configuration["auth_url"],
            contrail_url  = admin_configuration["contrail_url"],
            project       = admin_configuration["project"],
            username      = admin_configuration["username"],
            password      = admin_configuration["password"])

        self.api.connect()

        # ensure that the user has been removed
        self.api.users().undefine(**user_configuration)

    @classmethod
    def tearDownClass(self):
        return
        admin_configuration = UsersTest.parse_json("admin_credentials")
        user_configuration  = UsersTest.parse_json("user")

        # establish admin connection
        self.api = API(
            openstack_url = admin_configuration["auth_url"],
            contrail_url  = admin_configuration["contrail_url"],
            project       = admin_configuration["project"],
            username      = admin_configuration["username"],
            password      = admin_configuration["password"])

        self.api.connect()

        # ensure that the user has been removed
        self.api.users().undefine(**user_configuration)

    # --------------------------------------------------------------------------

    @mark.users
    def test__01__new(self):
        # prepare
        params = UsersTest.parse_json("user")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.users().new(**params)
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)

    @mark.users
    def test__02__save(self):
        # prepare
        params = UsersTest.parse_json("user")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.users().new(**params)
            entity.save()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.users
    def test__03__get(self):
        # prepare
        params = UsersTest.parse_json("user")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.users().get(
                tenant_name = params["tenant_name"],
                user_name   = params["user_name"])
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity.id)

    @mark.users
    def test__04__attributes(self):
        # prepare
        params = UsersTest.parse_json("user")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.users().get(
                tenant_name = params["tenant_name"],
                user_name   = params["user_name"])
            attributes = entity.attributes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(attributes)

    @mark.users
    def test__05__delete(self):
        # prepare
        params = UsersTest.parse_json("user")

        # run - test should fail if any exception occurs
        try:
            entity = self.api.users().get(
                tenant_name = params["tenant_name"],
                user_name   = params["user_name"])
            entity.delete()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone(entity)
        self.assertIsNone(entity.id)

    # --------------------------------------------------------------------------
