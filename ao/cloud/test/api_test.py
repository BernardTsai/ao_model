#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                 import path
from json               import loads
from pannet.cloud.api import API
from unittest           import TestCase, expectedFailure

class APITest(TestCase):
    @staticmethod
    def parse_json(filename):
        filepath = path.join(path.dirname(__file__), "fixtures/{}.json".format(filename))
        with open(filepath, "r") as stream:
            return loads(stream.read())

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__01__api__init__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        # run - test should fail if any exception occurs
        try:
            api = API(
                openstack_url=openstack_url,
                contrail_url=contrail_url,
                username=username,
                password=password,
                project=project)
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( api.openstack_url, openstack_url)
        self.assertEqual( api.contrail_url,  contrail_url )
        self.assertEqual( api.username,      username     )
        self.assertEqual( api.password,      password     )
        self.assertEqual( api.project ,      project      )

    def test__02__api__connect__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        # run - test should fail if any exception occurs
        try:
            api.connect()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( api.openstack )
        self.assertIsNotNone( api.contrail )

    @expectedFailure
    def test__03__api__wrong__auth__connect__exception(self):
        # prepare
        configuration = APITest.parse_json("wrong_credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        # run - test should fail if any exception occurs
        try:
            api.connect()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

    def test__04__api__roles__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            roles = api.roles()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( roles )

    def test__05__api__tenants__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            tenants = api.tenants()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( tenants )

    def test__06__api__users__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            users = api.users()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( users )

    def test__07__api__keypairs__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            keypairs = api.keypairs()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( keypairs )

    def test__08__api__networks__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            networks = api.networks()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( networks )

    def test__09__api__volumes__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            volumes = api.volumes()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( volumes )

    def test__10__api__ports__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            ports = api.ports()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( ports )

    def test__11__api__securitygroups__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            securitygroups = api.securitygroups()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( securitygroups )

    def test__12__api__servers__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            servers = api.servers()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( servers )

    def test__13__api__token__pass(self):
        # prepare
        configuration = APITest.parse_json("credentials")

        openstack_url = configuration["auth_url"]
        contrail_url  = configuration["contrail_url"]
        username      = configuration["username"]
        password      = configuration["password"]
        project       = configuration["project"]

        api = API(
            openstack_url=openstack_url,
            contrail_url=contrail_url,
            username=username,
            password=password,
            project=project)

        api.connect()

        # run - test should fail if any exception occurs
        try:
            token = api.token()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( token )
