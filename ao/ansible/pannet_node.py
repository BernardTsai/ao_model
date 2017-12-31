#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status':           ['preview'],
    'supported_by':     'community'
}

DOCUMENTATION = '''
---
module: pannet_node_manager

short_description: Module to manage a cloud node (server/volumes/interfaces).

version_added: "2.4"

author: "Bernard Tsai (bernard@tsai.eu)"

description:
    - "Allows to create, configure and delete cloud nodes."

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
            - Project name or ID containing the network (name admin-only).
        required: true
    component:
        description:
            - Name of the component to which the node belongs.
        required: true
    index:
        description:
            - Index of the node belonging to the component.
        required: true
    placement:
        description:
            - Placement zone
        required: true
    flavor:
        description:
            - Name of server flavor
        required: true
    image:
        description:
            - Name of base image
        required: true
    volumes:
        description:
            - List of dicitionaries with 'name', 'size', and 'type'
        required: false
    interfaces:
        description:
            - List of dicitionaries with 'network' and optional 'allowed'
        required: false
    state:
        description:
            - Indicate desired state of the resource.
        choices:  ['initial','inactive', 'active']
        required: false
        default:  active
'''

EXAMPLES = '''
# Create an externally accessible network named 'ext_network'.
- pannet_node_manager:
    auth_url:     ...
    username:     ...
    password:     ...
    project:      test_project
    component:    web
    index:        10
    placement:    EXT
    flavor:       m1.small
    image:        ubuntu-17.04.5-x86_64
    volumes:
        - name:   data
          size:   50
          type:   INT
    interfaces:
        - network: oam
          allowed: ['192.168.178.13']
        - network: m2m
    state:        active
'''

RETURN = '''
project:
    description:
        - Project name or ID containing the network (name admin-only).
component:
    description:
        - Name of the server cluster.
index:
    description:
        - Index of the cluster node.
placement:
    description:
        - Placement zone
flavor:
    description:
        - Name of server flavor
image:
    description:
        - Name of base image
volumes:
    description:
        - List of dicitionaries with 'name', 'size', and 'type'
interfaces:
    description:
        - List of dicitionaries with 'network' and optional 'allowed'
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
'''
# ------------------------------------------------------------------------------

from ansible.module_utils.basic import AnsibleModule
from pannet.cloud.nodeManager   import NodeManager
from traceback                   import format_exc

# ------------------------------------------------------------------------------
def main():
    # define the available arguments/parameters
    # that a user can pass to the module
    module_args = dict(
        auth_url    = dict(type="str",  required=True),
        username    = dict(type="str",  required=True),
        password    = dict(type="str",  required=True),
        project     = dict(type="str",  required=True),
        cluster     = dict(type="str",  required=True),
        node        = dict(type="str",  required=True),
        placement   = dict(type="str",  required=True),
        flavor      = dict(type="str",  required=True),
        image       = dict(type="str",  required=True),
        volumes     = dict(type="list", required=False),
        interfaces  = dict(type="list", required=False),
        state       = dict(type="str",  required=False, default="active"),
        loglevel    = dict(type="str",  required=False, default="error")
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
        manager = NodeManager( module.params, module.check_mode )

        result = manager.get_result()

        module.exit_json(**result)
    except KeyboardInterrupt:
        module.fail_json(msg="Execution was aborted")
    except Exception as exc:
        tb  = format_exc()
        msg = "\n".join( manager.msgs) + "\n" if manager else ""
        module.fail_json(msg=msg+tb)

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
