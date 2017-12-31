    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                           import path
from json                         import loads
from unittest                     import TestCase, expectedFailure
from pytest                       import mark, raises
from pannet.cloud.api             import API
from pannet.ansible.pannet_tenant import main

import sys

class Pannet_TenantTest(TestCase):
    @staticmethod
    def fixture(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        return filepath

    @staticmethod
    def parse_text(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, 'r') as stream:
            return stream.read()

    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.json'.format(filename))
        with open(filepath, 'r') as stream:
            return loads(stream.read())

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        admin_credentials           = Pannet_TenantTest.parse_json("admin_credentials")
        tenant_credentials          = Pannet_TenantTest.parse_json("tenant_credentials")
        tenant_configuration        = Pannet_TenantTest.parse_json("tenant")
        user_configuration          = Pannet_TenantTest.parse_json("user")
        role_configuration          = Pannet_TenantTest.parse_json("role")
        keypair_configuration       = Pannet_TenantTest.parse_json("keypair")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # remove keypair
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

    @mark.ansible
    @mark.pannet_tenant
    def test__01__tenant(self):
        # prepare
        args     = Pannet_TenantTest.fixture("pannet_tenant")
        sys.argv = ["", args]

        # run - test should fail if any exception occurs
        with raises(SystemExit) as sysexit:
            result = main()
            print( result )

        assert sysexit.type       == SystemExit
        assert sysexit.value.code == 0

    # --------------------------------------------------------------------------
