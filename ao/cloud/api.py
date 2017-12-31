#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions       import ParameterError, ConnectionError
from .roles            import Roles
from .tenants          import Tenants
from .users            import Users
from .keypairs         import Keypairs
from .networks         import Networks
from .volumes          import Volumes
from .ports            import Ports
from .securitygroups   import SecurityGroups
from .servers          import Servers
from pycontrail.client import Client
from openstack         import connection

class API():
    """VIM/SDN Application Programming Interface"""

    def __init__(self, openstack_url, username, password, project, contrail_url=None):
        """Initialize"""
        self.contrail_url  = contrail_url
        self.openstack_url = openstack_url
        self.username      = username
        self.password      = password
        self.project       = project
        self.openstack     = None
        self.contrail      = None
        self.project_id    = None

    def connect(self):
        """Connect to the API endpoints"""

        try:
            # reset connections
            self.openstack = None
            self.contrail  = None

            # connect to the OpenStack API
            self.openstack = connection.Connection(
                auth_url=     self.openstack_url,
                username=     self.username,
                password=     self.password,
                project_name= self.project )

            self.project_id = self.openstack.session.get_project_id()

            # connect to the contrail API?
            if self.contrail_url:
                self.contrail = Client(
                    url         = self.contrail_url,
                    auth_params = { "type":       "keystone",
                                    "auth_url":    self.openstack_url,
                                    "username":    self.username,
                                    "password":    self.password,
                                    "tenant_name": self.project } )
        except Exception as exc:
            raise ConnectionError("Failed with {}".format(exc.message))

    def token(self):
        """Obtain token"""
        return self.openstack.authorize() if self.openstack else None

    def tenants(self):
        """Tenants factory"""
        return Tenants(self.openstack)

    def roles(self):
        """Roles factory"""
        return Roles(self.openstack)

    def users(self):
        """Users factory"""
        return Users(self.openstack)

    def keypairs(self):
        """Keypairs factory"""
        return Keypairs(self.openstack)

    def networks(self):
        """Networks factory"""
        return Networks(self.openstack, self.contrail)

    def volumes(self):
        """Volumes factory"""
        return Volumes(self.openstack)

    def ports(self):
        """Ports factory"""
        return Ports(self.openstack)

    def securitygroups(self):
        """Security Groups factory"""
        return SecurityGroups(self.openstack)

    def servers(self):
        """Servers factory"""
        return Servers(self.openstack)
