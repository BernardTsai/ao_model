#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status":           ["preview"],
    "supported_by":     "community"
}

DOCUMENTATION = """
---
module: pannet_tenant

short_description: Module to manage a cloud tenant.

version_added: "2.4"

author: "Bernard Tsai (bernard@tsai.eu)"

description:
    - "Allows to create, configure and delete cloud tenants."

options:
    auth_url:
        description:
            - URL for the keystone API endpint
        required: true
    username:
        description:
            - User credentials.
        required: true
    password:
        description:
            - Password credentials.
        required: true
    project:
        description:
            - Project name.
        required: true
    secret:
        description:
            - Password for the newly created tenant.
        required: true
    public_key:
        description:
            - Public key of the keypair for the tenant administrator.
    state:
        description:
            - Indicate desired state of the resource.
        choices:  ["inactive", "active"]
        required: false
        default:  active
    loglevel:
        description:
            - Indicate desired logging level.
        choices:  ["debug", "error"]
        required: false
        default:  error
"""

EXAMPLES = """
# Create an externally accessible tenant named "test".
- pannet_tenant:
    auth_url:     ...
    username:     ...
    password:     ...
    project:      test
    secret:       secret_password
"""

RETURN = """
project:
    description:
        - Project name.
id:
    description:
        - Project ID.
state:
    description:
        - Indicate desired state of the resource.
changed:
    description:
        - Indicates if anything has been changed
action:
    description:
        - The action which has been performed
log:
    description:
        - List of log messages
"""
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
from pannet.cloud.tenantManager import TenantManager
from traceback                  import format_exc

# ------------------------------------------------------------------------------
def main():
    # define the available arguments/parameters
    # that a user can pass to the module
    module_args = dict(
        auth_url   = dict(type="str", required=True),
        username   = dict(type="str", required=True),
        password   = dict(type="str", required=True),
        project    = dict(type="str", required=True),
        secret     = dict(type="str", required=False),
        public_key = dict(type="str", required=False),
        state      = dict(type="str", required=False, default="active"),
        loglevel   = dict(type="str", required=False, default="error")
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec       = module_args,
        supports_check_mode = True
    )

    # create manager and execute it
    manager = None
    try:
        manager = TenantManager( module.params, module.check_mode )

        result = manager.get_result()

        module.exit_json(**result)
    except KeyboardInterrupt:
        module.fail_json(msg="Execution was aborted")
    except Exception as exc:
        tb  = format_exc()
        msg = "\n".join( manager.msgs) + "\n" if manager else ""
        module.fail_json(msg=msg+tb)

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
