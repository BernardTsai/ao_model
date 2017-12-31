#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions  import ParameterError, SchemaError, ConnectionError, UnknownEntityError
from .api         import API
from .baseManager import BaseManager
from jsonschema   import validate

class TenantManager(BaseManager):
    """Manage lifecycle of tenants"""

    # schema for attributes
    schema = {
        "$schema":    "http://json-schema.org/schema#",
        "type":       "object",
        "properties": {
            "auth_url":     {"type": "string"},
            "username":     {"type": "string"},
            "password":     {"type": "string"},
            "project":      {"type": "string"},
            "secret":       {"type": ["string","null"]},
            "public_key":   {"type": ["string","null"]},
            "state":        {"type": ["string","null"], "enum": ["inactive", "active"] },
            "loglevel":     {"type": ["string","null"], "enum": ["debug", "error"] }
        },
        "required":["auth_url","username","password","project"]
    }

    def __init__(self, params, check_mode=False):
        """Initialize"""
        BaseManager.__init__(self)

        # initialize attributes
        self.params        = params
        self.check_mode    = check_mode
        self.current       = {}
        self.target        = {}
        self.result        = {}
        self.api           = None        # admin API connection
        self.action        = "none"      # default action
        self.changed       = False       # default status
        self.tenant        = None        # tenant
        self.administrator = None        # administrator user
        self.role          = None        # administrator role
        self.keypair       = None        # administrator keypair

        # process request
        try:
            self.validate_parameters()        # validate based on schema
            self.initialize()                 # connect to the contrail API
            self.get_current_configuration()  # get current state
            self.get_target_configuration()   # get target state
            self.update_configuration()       # update configuration
            self.get_result()                 # retrieve the results
        except Exception as exc:
            raise UnknownError(str(exc))

    # @log("Schema validation")
    def validate_parameters(self):
        """Validate schema of parameters"""
        # check schema
        try:
            validate(self.params, TenantManager.schema)
        except:
            raise SchemaError("Schema error")

        # make sure we are not manipulating the "admin" tenant
        if self.params["project"] == "admin":
            raise ParameterError("Tenant must not be 'admin'")

        # check if a secret has been provided if needed
        # check if a public key has been provided if needed
        if self.params["state"] == "active":
            if not "secret" in self.params:
                raise ParameterError("Missing secret")

            if not "public_key" in self.params:
                raise ParameterError("Missing public key")

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

    # @log("Initialization")
    def initialize(self):
        """Initialize connections"""
        self.switch_to_admin_context()

    # @log("Determination of current state")
    def get_current_configuration(self):
        """Determine current configuration"""
        tenant_name = self.params["project"]

        # try to read the required role
        self.role = self.api.roles().get(role_name="admin")

        # try to read the required tenant
        self.tenant = self.api.tenants().get(tenant_name=tenant_name)

        # try to read the required administrator
        self.administrator = self.api.users().get(tenant_name=tenant_name, user_name="administrator")

        # keypair needs to be retrieved from within user context
        if self.administrator:

            self.switch_to_tenant_context()
            self.keypair = self.api.keypairs().get(tenant_name=tenant_name, keypair_name="keypair")
            self.switch_to_tenant_context()

        # currently available information
        self.current["project"] = self.tenant.name if self.tenant else ""
        self.current["id"]      = self.tenant.id   if self.tenant else ""


    # @log("Determination of target state")
    def get_target_configuration(self):
        """Determine target configuration"""
        self.target["project"] = self.params["project"]
        self.target["id"]      = None

    # @log("Update configuration")
    def update_configuration(self):
        """Update tenant configuration"""

        # change/update tenant to desired state
        if self.tenant:
            if self.params["state"] != "active":
                self.action = "delete"
                self.delete_tenant()
            else:
                if self.administrator and self.keypair:
                    self.action = "none"
                else:
                    self.action = "update"
                    self.update_tenant()
        else:
            if self.params["state"] == "active":
                self.action = "create"
                self.create_tenant()

    # @log("Tenant deletion")
    def delete_tenant(self):
        """Delete an existing virtual data center"""
        if self.check_mode:
            return

        self.changed = True

        # delete keypair if needed
        if self.keypair:
            self.keypair.delete()
            self.keypair = None

        # delete administrator if needed
        if self.administrator:
            self.administrator.delete()
            self.administrator = None

        # delete tenant
        self.tenant.delete()
        self.tenant = None

    # @log("Tenant creation")
    def create_tenant(self):
        """Create a new virtual server"""
        if self.check_mode:
            return

        self.changed = True

        # create tenant
        tenant_name = self.params["project"]

        self.tenant = self.api.tenants().new(tenant_name=tenant_name)
        self.tenant.save()

        # create administrator
        if not self.administrator:
            self.administrator = self.api.users().new(
                tenant_name = tenant_name,
                user_name   = "administrator",
                password    = self.params["secret"])
            self.administrator.save()

        # always ensure access privileges
        self.tenant.grant(self.administrator, self.role)

        # create keypair from within user context
        if not self.keypair:
            # keypair needs to be created within user context
            self.switch_to_tenant_context()

            self.keypair = self.api.keypairs().new(
                tenant_name  = tenant_name,
                keypair_name = "keypair",
                public_key   = self.params["public_key"])
            self.keypair.save()

            self.switch_to_admin_context()

    # @log("Tenant update")
    def update_tenant(self):
        """Update an existing virtual tenant"""
        if self.check_mode:
            return

        self.changed = True

        tenant_name = self.params["project"]

        # create administrator
        if not self.administrator:
            self.administrator = self.api.users().new(
                tenant_name = tenant_name,
                user_name   = "administrator",
                password    = self.params["secret"])
            self.administrator.save()

        # always ensure access privileges
        self.tenant.grant(self.administrator, self.role)

        # create keypair from within user context
        if not self.keypair:
            # keypair needs to be created within user context
            self.switch_to_tenant_context()

            self.keypair = self.api.keypairs().new(
                tenant_name  = tenant_name,
                keypair_name = "keypair",
                public_key   = self.params["public_key"])
            self.keypair.save()

            self.switch_to_admin_context()

    # @log("Tenant information")
    def get_result(self):
        """Retrieve the results of the action"""
        self.result = {
            "project":   self.params["project"],
            "id":        self.tenant.id if self.tenant else "",
            "state":     "active" if self.tenant else "inactive",
            "changed":   self.changed,
            "action":    self.action,
            "log":       self.msgs
        }

        return self.result
