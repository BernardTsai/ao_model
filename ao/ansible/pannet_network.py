#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status':           ['preview'],
    'supported_by':     'community'
}

DOCUMENTATION = '''
---
module: pannet_network

short_description: Module to manage contrail virtual networks.

version_added: "2.4"

author: "Bernard Tsai (bernard@tsai.eu)"

description:
    - "Allows to create, configure and delete virtual networks."

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
    network:
        description:
            - Name to be assigned to the network.
        required: true
    ipv4_prefix:
        description:
            -  IPv4 subnet network prefix
    ipv4_length:
        description:
            -  IPv4 subnet network prefix length
    ipv4_start:
        description:
            -  IPv4 subnet start of allocation pool
    ipv4_end:
        description:
            -  IPv4 subnet end of allocation pool
    ipv4_gateway:
        description:
            -  IPv4 subnet gateway address
    ipv4_dns:
        description:
            -  IPv4 subnet dns address
    ipv6_prefix:
        description:
            -  IPv6 subnet network prefix
    ipv6_length:
        description:
            -  IPv6 subnet network prefix length
    ipv6_start:
        description:
            -  IPv6 subnet start of allocation pool
    ipv6_end:
        description:
            -  IPv6 subnet end of allocation pool
    ipv6_gateway:
        description:
            -  IPv6 subnet gateway address
    ipv6_dns:
        description:
            -  IPv6 subnet dns address
    route_target:
        description:
            - Route target
        required: false
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
'''

EXAMPLES = '''
# Create an externally accessible network named 'oam'.
- pannet_network:
    contrail_url  ...
    auth_url      ...
    username      ...
    password      ...
    project:      abc
    network:      oam
    ipv4_prefix:  192.168.178.1
    ipv4_length:  24
    ipv4_start:   192.168.178.128
    ipv4_end:     192.168.178.250
    route_target: 65412:12
'''

RETURN = '''
project:
    description:
        - Project name or ID containing the network (name admin-only).
network:
    description:
        - Name to be assigned to the network.
ipv4_prefix:
    description:
        -  IPv4 subnet network prefix
ipv4_length:
    description:
        -  IPv4 subnet network prefix length
ipv4_start:
    description:
        -  IPv4 subnet start of allocation pool
ipv4_end:
    description:
        -  IPv4 subnet end of allocation pool
ipv4_gateway:
    description:
        -  IPv4 subnet gateway address
ipv4_dns:
    description:
        -  IPv4 subnet dns address
ipv6_prefix:
    description:
        -  IPv6 subnet network prefix
ipv6_length:
    description:
        -  IPv6 subnet network prefix length
ipv6_start:
    description:
        -  IPv6 subnet start of allocation pool
ipv6_end:
    description:
        -  IPv6 subnet end of allocation pool
ipv6_gateway:
    description:
        -  IPv6 subnet gateway address
ipv6_dns:
    description:
        -  IPv6 subnet dns address
route_target:
    description:
        - Route target
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

from ansible.module_utils.basic  import AnsibleModule
from pannet.cloud.networkManager import NetworkManager
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
        network      = dict(type="str", required=True),
        ipv4_prefix  = dict(type="str", required=False, default=None),
        ipv4_length  = dict(type="int", required=False, default=None),
        ipv4_gateway = dict(type="str", required=False, default=None),
        ipv4_start   = dict(type="str", required=False, default=None),
        ipv4_end     = dict(type="str", required=False, default=None),
        ipv4_dns     = dict(type="str", required=False, default=None),
        ipv6_prefix  = dict(type="str", required=False, default=None),
        ipv6_length  = dict(type="int", required=False, default=None),
        ipv6_gateway = dict(type="str", required=False, default=None),
        ipv6_start   = dict(type="str", required=False, default=None),
        ipv6_end     = dict(type="str", required=False, default=None),
        ipv6_dns     = dict(type="str", required=False, default=None),
        route_target = dict(type="str", required=False, default=""),
        state        = dict(type="str", required=False, default="active"),
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
        manager = NetworkManager( module.params, module.check_mode )

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
