    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                            import path, environ
from json                          import loads
from unittest                      import TestCase, expectedFailure
from pytest                        import mark, raises
from pannet.cloud.api              import API
from pannet.ansible.pannet_cluster import main

import sys

class Pannet_ClusterTest(TestCase):
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
        admin_credentials           = Pannet_ClusterTest.parse_json("admin_credentials")
        tenant_credentials          = Pannet_ClusterTest.parse_json("tenant_credentials")
        tenant_configuration        = Pannet_ClusterTest.parse_json("tenant")
        user_configuration          = Pannet_ClusterTest.parse_json("user")
        role_configuration          = Pannet_ClusterTest.parse_json("role")
        keypair_configuration       = Pannet_ClusterTest.parse_json("keypair")
        securitygroup_configuration = Pannet_ClusterTest.parse_json("securitygroup")

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

    @classmethod
    def tearDownClass(self):
        admin_credentials           = Pannet_ClusterTest.parse_json("admin_credentials")
        tenant_credentials          = Pannet_ClusterTest.parse_json("tenant_credentials")
        tenant_configuration        = Pannet_ClusterTest.parse_json("tenant")
        user_configuration          = Pannet_ClusterTest.parse_json("user")
        role_configuration          = Pannet_ClusterTest.parse_json("role")
        keypair_configuration       = Pannet_ClusterTest.parse_json("keypair")
        securitygroup_configuration = Pannet_ClusterTest.parse_json("securitygroup")

        # establish admin connection
        self.api = API(
            openstack_url = tenant_credentials["auth_url"],
            contrail_url  = tenant_credentials["contrail_url"],
            project       = tenant_credentials["project"],
            username      = tenant_credentials["username"],
            password      = tenant_credentials["password"])

        try:
            self.api.connect()

            # remove securitygroup, keypair
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

    @mark.ansible
    @mark.pannet_cluster
    def test__01__cluster(self):
        # prepare
        # global _ANSIBLE_ARGS

        # _ANSIBLE_ARGS = None
        args          = Pannet_ClusterTest.fixture("pannet_cluster")
        sys.argv      = ["", args]

        environ["ANSIBLE_MODULE_ARGS"] = Pannet_ClusterTest.parse_text("pannet_cluster")

        # run - test should fail if any exception occurs
        with raises(SystemExit) as sysexit:
            result = main()
            print( result )

        assert sysexit.type       == SystemExit
        assert sysexit.value.code == 0

    # --------------------------------------------------------------------------
