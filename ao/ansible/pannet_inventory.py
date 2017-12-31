#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status':           ['preview'],
    'supported_by':     'community'
}

DOCUMENTATION = '''
---
module: pannet_inventory

short_description: Module to retrieve the current inventory of a tenant.

version_added: "2.4"

author: "Bernard Tsai (bernard@tsai.eu)"

description:
    - "Allows to retrieve an inventory of virtual resources of a tenant."

options:
    contrail_url:
        description:
            - URL for the contrail API endpint
        required: true
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
            - Project name or ID containing the network (name admin-only).
        required: true
    loglevel:
        description:
            - Indicate desired logging level.
        choices:  ["debug", "error"]
        required: false
        default:  error
'''

EXAMPLES = '''
# Retrieve an inventory of virtual resources of a tenant "test".
- pannet_inventory:
    contrail_url  ...
    auth_url      ...
    username      ...
    password      ...
    project:      test
'''

RETURN = '''
project:
    description:
        - Project name or ID containing the network (name admin-only).
model:
    description:
        - Descriptor of the tenant.
changed:
    description:
        - Indicates if anything has been changed
action:
    description:
        - The action which has been performed
log:
    description:
        - List of log messages
'''

# ------------------------------------------------------------------------------

from pannet.cloud.inventoryManager import InventoryManager
from ansible.module_utils.basic    import AnsibleModule
from traceback                   import format_exc

# ------------------------------------------------------------------------------
def main():
    # define the available arguments/parameters
    # that a user can pass to the module
    module_args = dict(
        contrail_url = dict(type="str", required=True),
        auth_url     = dict(type="str", required=True),
        username     = dict(type="str", required=True),
        password     = dict(type="str", required=True),
        project      = dict(type="str", required=True),
        secret       = dict(type="str", required=True),
        loglevel     = dict(type="str", required=False, default="error")
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
        manager = InventoryManager( module.params, module.check_mode )

        result = manager.get_result()

        module.exit_json(**result)
    except KeyboardInterrupt:
        module.fail_json(msg='Execution was aborted')
    except Exception as exc:
        tb  = format_exc()
        msg = "\n".join( manager.msgs) + "\n" if manager else ""
        module.fail_json(msg=msg+tb)

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
