#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions  import ParameterError, SchemaError, ConnectionError, UnknownEntityError, UnknownError
from .api         import API
from .baseManager import BaseManager
from jsonschema   import validate

class InventoryManager(BaseManager):
    """Collect inventory information from a tenant"""

    def __init__(self, params, check_mode=False):
        """Initialize"""
        BaseManager.__init__(self)

        # check parameters
        tenant_name = params.get("project", None)
        if not tenant_name or tenant_name in ["", "admin", "service"]:
            raise ParameterError("Invalid parameters")

        # initialize attributes
        self.params         = params
        self.check_mode     = check_mode
        self.api            = None        # admin API connection
        self.action         = "none"      # default action
        self.changed        = False       # default status
        self.name           = tenant_name # name of tenant
        self.tenant         = None        # tenant
        self.users          = []          # users
        self.keypairs       = []          # keypairs
        self.networks       = []          # networks
        self.securitygroups = []          # security groups
        self.servers        = []          # servers
        self.volumes        = []          # volumes
        self.ports          = []          # ports

        # collection information
        try:
            # determine administrative information
            self.switch_to_admin_context()

            # determine tenant information
            self.tenant = self.api.tenants().get(tenant_name=tenant_name)
            if not self.tenant:
                return

            # determine user information
            self.users = self.api.users().list(tenant_name=tenant_name)

            # determine tenant related information
            self.switch_to_tenant_context()

            self.networks       = self.api.networks().list(tenant_name=tenant_name)
            self.securitygroups = self.api.securitygroups().list(tenant_name=tenant_name)
            self.servers        = self.api.servers().list(tenant_name=tenant_name)
            self.volumes        = self.api.volumes().list(tenant_name=tenant_name)
            self.ports          = self.api.ports().list(tenant_name=tenant_name)
        except Exception as exc:
            raise UnknownError(str(exc))

    def switch_to_admin_context(self):
        """Establish administrator connection"""
        try:
            self.api = API(
                openstack_url = self.params["auth_url"],
                project       = "admin",
                username      = self.params["username"],
                password      = self.params["password"])

            self.api.connect()
        except Exception:
            raise ConnectionError( "Unable to connect to API")

    def switch_to_tenant_context(self):
        """Establish tenant connection"""
        try:
            self.api = API(
                openstack_url = self.params["auth_url"],
                project       = self.params["project"],
                username      = self.params["project"] + "_administrator",
                password      = self.params["secret"])

            self.api.connect()
        except Exception:
            raise ConnectionError( "Unable to connect to API")

    # @log("Tenant information")
    def get_result(self):
        """Retrieve the results of the action"""
        self.result = {
            "project":         self.params["project"],
            "id":              self.tenant.id if self.tenant else "",
            "changed":         self.changed,
            "action":          self.action,
            "log":             self.msgs,
            "tenant":          None,
            "users":           [],
            "networks":        [],
            "securitygroups":  [],
            "servers":         [],
            "volumes":         [],
            "ports":           []
        }

        if self.tenant:
            self.result["tenant"] = self.tenant.attributes()

            for user in self.users:
                self.result["users"].append(user.attributes())

            for network in self.networks:
                self.result["networks"].append(network.attributes())

            for securitygroup in self.securitygroups:
                self.result["securitygroups"].append(securitygroup.attributes())

            for server in self.servers:
                self.result["servers"].append(server.attributes())

            for volume in self.volumes:
                self.result["volumes"].append(volume.attributes())

            for port in self.ports:
                self.result["ports"].append(port.attributes())

        return self.result
