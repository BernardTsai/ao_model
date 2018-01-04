#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# BSD 3-Clause License
#
# Copyright (c) 2017, Bernard Tsai <bernard@tsai.eu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# TODOS:
#
# - better comments and docs
# - tests, tests, tests
# -  check seperators of links "-" maybe replace with = and exclude = from names
# - get_interface delivers None - how to resolve if a false network has been used in xref (=> better validation?)
#
# - better validate IP settings
#
# - better validation messages
#
# - add flavors to tenant
#
# ------------------------------------------------------------------------------
#
# model.py:
#
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
#
# Class Model
#
# ------------------------------------------------------------------------------
class Model():

    supported_schemas = ["V0.1.1"]

    # --------------------------------------------------------------------------
    def __init__(self, context="default", schema="V0.1.1", model=None):
        """Initialize model """

        # check schema compatability
        if not schema in Model.supported_schemas:
            raise AttributeError( "Unsupported schema" )

        self.model  = self._get_default_model(context,schema)
        self.schema = schema

    # --------------------------------------------------------------------------
    def getModel(self):
        """Provide model object"""
        return self.model

    # --------------------------------------------------------------------------
    def getSchema(self):
        """Provide schema"""
        return self.schema

    # --------------------------------------------------------------------------
    def set(self, tosca):
        """Apply change to model"""

        # iterate over all node templates
        templates = tosca["topology_template"]["node_templates"]

        for fqn, template in templates.items():
            data = template["properties"]
            type = template["type"].rsplit( ".", 1)[-1]

            # map to type specific procedures
            if type == "VNF":
                self.set_vnf( fqn, data )
            elif type == "Tenant":
                self.set_tenant( fqn, data )
            elif type == "Network":
                    self.set_network( fqn, data )
            elif type == "ExternalComponent":
                self.set_external_component( fqn, data )
            elif type == "InternalComponent":
                self.set_internal_component( fqn, data )
            elif type == "Node":
                self.set_node( fqn, data )

        # check and create references
        self._set_references()

        # increment version
        self.model["version"] = self.model["version"] + 1

    # --------------------------------------------------------------------------
    def set_external_component(self, fqn, data):
        # determine name
        name  = data["name"]
        state = data["state"]

        components = self.model["components"]
        component = self._get( components, fqn )
        if not component:
            component = self._get_default_external_component( fqn )

        # check if the network has been defined
        networks = []
        for vnf in self.model["vnfs"]:
            for tenant in vnf["tenants"]:
                networks = networks + tenant["networks"]

        for listname in ["services","dependencies"]:
            if listname  in data:
                for entry in data[listname]:
                    network = self._get( networks, entry["network"] )
                    if not network:
                        raise AttributeError( "Invalid network name" )

        # check if the component needs to be undefined
        if state == "undefined":
            self._remove( components, name )
            return

        # update the attributes
        for attr in ["description","version","network","state","ipv4","ipv6","dependencies","services"]:
            self._replace( component, data, attr )

        self._set( components, component )

        # TODO: propagate state if required to all attached interfaces

    # --------------------------------------------------------------------------
    def set_vnf(self, fqn, data):
        # determine vnf and state
        name  = data["name"]
        state = data["state"]

        vnfs = self.model["vnfs"]
        vnf = self._get( vnfs, fqn )
        if not vnf:
            vnf = self._get_default_vnf( fqn )

        # check if the vnf needs to be undefined
        if state == "undefined":
            self._remove( vnfs, name )
            return

        # update the attributes
        for attr in ["name","description","version","vendor","state","public_key"]:
            self._replace( vnf, data, attr )

        self._set( vnfs, vnf )

        # propagate the state
        for tenant in vnf["tenants"]:
            self._set_tenant_state( tenant, state )

    # --------------------------------------------------------------------------
    def set_tenant(self, fqn, data):
        # determine vnf and state
        vnf_fqn = "/".join(fqn.split( "/" )[0:2])
        name    = data["name"]
        state   = data["state"]

        vnfs = self.model["vnfs"]
        vnf = self._get( vnfs, vnf_fqn )
        if not vnf:
            raise AttributeError( "Invalid VNF context" )

        tenants = vnf["tenants"]
        tenant = self._get( tenants, fqn )
        if not tenant:
            tenant = self._get_default_tenant( fqn )

        # check if the vnf needs to be undefined
        if state == "undefined":
            self._remove( tenants, name )
            return

        # update the attributes
        for attr in ["name","description","version","datacenter","state","flavors"]:
            self._replace( tenant, data, attr )

        self._set( tenants, tenant )

        # propagate the state
        for component in tenant["components"]:
            self._set_component_state( component, state )

    # --------------------------------------------------------------------------
    def set_network(self, fqn, data):
        # determine vnf, tenant, name and state
        vnf_fqn    = "/".join(fqn.split( "/" )[0:2])
        tenant_fqn = "/".join(fqn.split( "/" )[0:3])
        name       = data["name"]
        state      = data["state"]

        vnfs = self.model["vnfs"]
        vnf = self._get( vnfs, vnf_fqn )
        if not vnf:
            raise AttributeError( "Invalid VNF context" )

        tenants = vnf["tenants"]
        tenant = self._get( tenants, tenant_fqn )
        if not tenant:
            raise AttributeError( "Invalid tenant context" )

        networks = tenant["networks"]
        network = self._get( networks, fqn )
        if not network:
            network = self._get_default_network( fqn )

        # check if the network needs to be undefined
        if state == "undefined":
            self._remove( networks, name )
            return

        # update the attributes
        for attr in ["name","description","version","target","state"]:
            self._replace( network, data, attr )

        if "ipv4" in data:
            network["ipv4"] = {}
            for attr in ["cidr","gateway","dns","dhcp","start","end"]:
                network["ipv4"][attr] = data["ipv4"].get(attr,"")

        if "ipv6" in data:
            network["ipv6"] = {}
            for attr in ["cidr","gateway","dns","dhcp","start","end"]:
                network["ipv6"][attr] = data["ipv6"].get(attr,"")

        self._set( networks, network )

    # --------------------------------------------------------------------------
    def set_internal_component(self, fqn, data):
        # determine vnf, tenant, name and state
        vnf_fqn    = "/".join(fqn.split( "/" )[0:2])
        tenant_fqn = "/".join(fqn.split( "/" )[0:3])
        name       = data["name"]
        state      = data["state"]

        vnfs = self.model["vnfs"]
        vnf = self._get( vnfs, vnf_fqn )
        if not vnf:
            raise AttributeError( "Invalid VNF context" )

        tenants = vnf["tenants"]
        tenant = self._get( tenants, tenant_fqn)
        if not tenant:
            raise AttributeError( "Invalid tenant context" )

        components = tenant["components"]
        component = self._get( components, fqn )
        if not component:
            component = self._get_default_internal_component( fqn )

        # check if the network has been defined
        networks = self.model["networks"] + tenant["networks"]

        for listname in ["interfaces","services","dependencies"]:
            if listname  in data:
                for entry in data[listname]:
                    # normalize names relative to tenant context
                    if not entry["network"].startswith("/"):
                        entry["network"] = tenant_fqn + "/" + entry["network"]
                    network = self._get( networks, entry["network"] )
                    if not network:
                        raise AttributeError( "Invalid network name" )

        # check if the flavor has been defined
        if not any(f["name"] == data["flavor"] for f in tenant["flavors"] ):
            raise AttributeError( "Invalid flavor name" )

        # check if the vnf needs to be undefined
        if state == "undefined":
            self._remove( components, name )
            return

        # update the attributes
        for attr in ["name","description","version","placement",
                     "flavor","image","sizing",
                     "user_data","metadata","state","volumes","interfaces","dependencies","services"]:
            self._replace( component, data, attr )

        for interface in component["interfaces"]:
            interface["rules"] = []

        self._set( components, component )

        # TODO: propagate state if required to all attached interfaces

    # --------------------------------------------------------------------------
    def set_node(self, fqn, data):
        # determine vnf, tenant, component, name and state
        vnf_fqn       = "/".join(fqn.split( "/" )[0:2])
        tenant_fqn    = "/".join(fqn.split( "/" )[0:3])
        component_fqn = "/".join(fqn.split( "/" )[0:4])
        name          = data["name"]
        state         = data["state"]

        vnfs = self.model["vnfs"]
        vnf = self._get( vnfs, vnf_fqn )
        if not vnf:
            raise AttributeError( "Invalid VNF context" )

        tenants = vnf["tenants"]
        tenant = self._get( tenants, tenant_fqn )
        if not tenant:
            raise AttributeError( "Invalid tenant context" )

        components = tenant["components"]
        component = self._get( components, component_fqn )
        if not component:
            raise AttributeError( "Invalid component context" )

        nodes = component["nodes"]
        node = self._get( nodes, fqn )
        new_node = False
        if not node:
            new_node = True
            node = self._get_default_node( fqn )

        # check if the network has been defined
        networks = self.model["networks"] + tenant["networks"]

        for listname in ["interfaces","services","dependencies"]:
            if listname  in data:
                for entry in data[listname]:
                    # normalize names relative to tenant context
                    if not entry["network"].startswith("/"):
                        entry["network"] = tenant_fqn + "/" + entry["network"]
                    network = self._get( networks, entry["network"] )
                    if not network:
                        raise AttributeError( "Invalid network name" )

        # check if the change fits into the cluster dimensions
        current_size = len( nodes )
        new_size     = current_size
        sizing       = component["sizing"]
        if new_node and state != "undefined":
            new_size = current_size + 1
            if sizing["max"] < new_size:
                raise AttributeError( "Too many nodes" )
        elif not new_node and state == "undefined":
            new_size = current_size + 1
            if new_size < sizing["min"]:
                raise AttributeError( "Too few nodes" )

        # check if the vnf needs to be undefined
        if state == "undefined":
            self._remove( nodes, name )
            return

        # update the attributes
        for attr in ["description","version","placement","flavor","image",
                     "user_data","metadata","state","volumes","interfaces","dependencies","services"]:
            self._replace( node, data, attr )

        for interface in node["interfaces"]:
            interface["rules"] = []

        self._set( nodes, node )

        # TODO: propagate state if required to all attached interfaces

    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def _set_tenant_state(self, tenant, state):
        tenant["state"] = state

        # propagate the state
        for network in tenant["networks"]:
            self._set_network_state( network, state )
        for component in tenant["components"]:
            self._set_component_state( component, state )

    # --------------------------------------------------------------------------
    def _set_network_state(self, network, state):
        network["state"] = state

    # --------------------------------------------------------------------------
    def _set_component_state(self, component, state):
        component["state"] = state

        # propagate the state
        for node in component["nodes"]:
            self._set_node_state( node, state )

    # --------------------------------------------------------------------------
    def _set_node_state(self, node, state):
        node["state"] = state

        # propagate the state
        for volume in node["volumes"]:
            self._set_volume_state( volume, state )
        for interface in node["interface"]:
            self._set_interace_state( interface, state )

    # --------------------------------------------------------------------------
    def _set_volume_state(self, volume, state):
        volume["state"] = state

    # --------------------------------------------------------------------------
    def _set_interface_state(self, interface, state):
        interface["state"] = state

    # --------------------------------------------------------------------------
    def _get_default_model(self,context,schema):
        model = {
            "schema":      schema,
            "type":        "Model",
            "context":     context,
            "version":     0,
            "vnfs":        [],
            "networks":    [],
            "components":  [],
            "consistent":  True
        }

        return model

    # --------------------------------------------------------------------------
    def _get_default_external_component(self,fqn):
        component = {
            "fqn":          fqn,
            "type":         "ExternalComponent",
            "name":         fqn[1:],
            "description":  "",
            "version":      "V0.0.0",
            "state":        "defined",
            "network":      "",
            "ipv4":         [],
            "ipv6":         [],
            "dependencies": [],
            "services":     []
        }

        return component

    # --------------------------------------------------------------------------
    def _get_default_vnf(self, fqn):
        vnf = {
            "fqn":         fqn,
            "type":        "VNF",
            "name":        fqn[1:],
            "description": "",
            "version":     "V0.0.0",
            "vendor":      "undefined",
            "state":       "defined",
            "public_key":  "",
            "tenants":     [],
            "networks":    [],
            "partners":    []
        }

        return vnf

    # --------------------------------------------------------------------------
    def _get_default_tenant(self,fqn):
        parts  = fqn.split("/")
        vnf    = parts[1]
        name   = parts[2]

        tenant = {
            "fqn":         fqn,
            "type":        "Tenant",
            "name":        name,
            "description": "",
            "version":     "V0.0.0",
            "vnf":         vnf,
            "state":       "defined",
            "flavors":     [],
            "components":  [],
            "networks":    []
        }

        return tenant

    # --------------------------------------------------------------------------
    def _get_default_network(self,fqn):
        parts  = fqn.split("/")
        vnf    = parts[1]
        tenant = parts[2]
        name   = parts[3]

        network = {
            "fqn":         fqn,
            "type":        "Network",
            "name":        name,
            "description": "",
            "version":     "V0.0.0",
            "state":       "defined",
            "target":      ""
        }

        return network

    # --------------------------------------------------------------------------
    def _get_default_internal_component(self,fqn):
        parts  = fqn.split("/")
        vnf    = parts[1]
        tenant = parts[2]
        name   = parts[3]

        component = {
            "fqn":          fqn,
            "type":         "InternalComponent",
            "name":         name,
            "description":  "",
            "version":      "V0.0.0",
            "state":        "defined",
            "placement":    "EXT",
            "flavor":       "undefined",
            "image":        "undefined",
            "sizing":       { "min": 1, "max": 1, "size": 1 },
            "user_data":    [],
            "metadata":     [],
            "nodes":        [],
            "volumes":      [],
            "interfaces":   [],
            "dependencies": [],
            "services":     []
        }

        return component

    # --------------------------------------------------------------------------
    def _get_default_node(self,fqn):
        parts     = fqn.split("/")
        vnf       = parts[1]
        tenant    = parts[2]
        component = parts[3]
        name      = parts[4]

        node = {
            "fqn":          fqn,
            "type":         "Node",
            "name":         name,
            "description":  "",
            "version":      "V0.0.0",
            "state":        "defined",
            "placement":    "EXT",
            "flavor":       "undefined",
            "image":        "undefined",
            "user_data":    [],
            "metadata":     [],
            "nodes":        [],
            "volumes":      [],
            "interfaces":   [],
            "dependencies": [],
            "services":     []
        }

        return node

    # --------------------------------------------------------------------------
    def _set_references(self):
        networks     = self._get_networks()
        components   = self._get_components()
        services     = self._get_services(components)
        links        = self._get_links(components,services)

        self._set_rules(networks,components,links)

    # --------------------------------------------------------------------------
    def _get_networks(self):
        networks = self.model["networks"]

        for vnf in self.model["vnfs"]:
            for tenant in vnf["tenants"]:
                networks = networks + tenant["networks"]

        return networks

    # --------------------------------------------------------------------------
    def _get_components(self):
        components = self.model["components"]

        vnfs = self.model["vnfs"]
        for vnf in vnfs:
            tenants = vnf["tenants"]
            for tenant in tenants:
                components = components + tenant["components"]

        return components

    # --------------------------------------------------------------------------
    def _get_services(self,components):
        services = dict()
        for component in components:
            for service in component["services"]:
                network  = service["network"]
                external = (component["type"] == "ExternalComponent")
                fqn      = component["fqn"] + "/" + service["name"]

                services[ fqn ] = {
                    "fqn":        fqn,
                    "component":  component["fqn"],
                    "service":    service["name"],
                    "network":    network,
                    "ports":      service["ports"],
                    "external":   external
                }

        return services

    # --------------------------------------------------------------------------
    def _get_links(self,components,services):
        links = []

        self.model["consistent"] = True

        for component in components:
            for dependency in component["dependencies"]:

                # find service
                service_fqn = dependency["service"]

                # not found
                if not service_fqn in services:
                    self.model["consistent"] = False
                    continue

                # found
                service = services[ service_fqn ]

                # add new link
                name = component["fqn"] + '-' + service["fqn"]

                external = (component["type"] == "ExternalComponent")
                network  = dependency["network"]

                link = {
                    'name':              name,
                    "service":           service["service"],
                    'ports':             service["ports"],
                    "source_component":  component["fqn"],
                    "source_network":    network,
                    "source_external":   external,
                    "target_component":  service["component"],
                    "target_network":    service["network"],
                    "target_external":   service["external"]
                }

                links.append(link)

        return links

    # --------------------------------------------------------------------------
    def _get_interface(self,component,network):
        for interface in component["interfaces"]:
            if interface["network"] == network["fqn"]:
                return interface
        return None

    # --------------------------------------------------------------------------
    def _get_network(self,networks,fqn):
        for network in networks:
            if network["fqn"] == fqn:
                return network
        return None

    # --------------------------------------------------------------------------
    def _get_component(self,components,fqn):
        for component in components:
            if component["fqn"] == fqn:
                return component
        return None

    # --------------------------------------------------------------------------
    def _clear_rules(self,components):
        for component in components:
            if component["type"] == "InternalComponent":
                for interface in component["interfaces"]:
                    interface["rules"] = []
                for node in component["nodes"]:
                    for interface in node["interfaces"]:
                        interface["rules"] = []

    # --------------------------------------------------------------------------
    def _set_rules(self,networks,components,links):

        # remove all existing rules first
        self._clear_rules(components)

        # loop over all links and calculate rules
        for link in links:

            # determine source and target networks and components
            source_network   = self._get_network( networks,     link["source_network"]   )
            target_network   = self._get_network( networks,     link["target_network"]   )
            source_component = self._get_component( components, link["source_component"] )
            target_component = self._get_component( components, link["target_component"] )
            ports            = link["ports"]

            # ----- egress rules for internal source components -----
            if not link["source_external"]:
                interface = self._get_interface(source_component,source_network)

                # external targets
                if link["target_external"]:
                    for port in ports:
                        for prefix in target_component["ipv4"]:
                            rule = {
                                "direction": "egress",
                                "mode":      "cidr",
                                "group":     link["target_component"],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv4",
                                "prefix":    prefix
                            }
                            interface["rules"].append(rule)
                        for prefix in target_component["ipv6"]:
                            rule = {
                                "direction": "egress",
                                "mode":      "cidr",
                                "group":     link["target_component"],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv6",
                                "prefix":    prefix
                            }
                            interface["rules"].append(rule)
                # internal targets
                else:
                    if "ipv4" in target_network:
                        for port in ports:
                            rule = {
                                "direction": "egress",
                                "mode":      "group",
                                "group":     link["target_component"] + "/" + link["target_network"].split("/")[-1],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv4",
                                "prefix":    target_network["ipv4"]["cidr"]
                            }
                            interface["rules"].append(rule)
                    if "ipv6" in target_network:
                        for port in ports:
                            rule = {
                                "direction": "egress",
                                "mode":      "group",
                                "group":     link["target_component"] + "/" + link["target_network"].split("/")[-1],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv6",
                                "prefix":    target_network["ipv6"]["cidr"]
                            }
                            interface["rules"].append(rule)

            # ----- ingress rules for internal target components -----
            if not link["target_external"]:
                interface = self._get_interface(target_component, target_network)

                # external sources
                if link["source_external"]:
                    for port in ports:
                        for prefix in source_component["ipv4"]:
                            rule = {
                                "direction": "ingress",
                                "mode":      "cidr",
                                "group":     link["source_component"],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv4",
                                "prefix":    prefix
                            }
                            interface["rules"].append(rule)
                        for prefix in source_component["ipv6"]:
                            rule = {
                                "direction": "ingress",
                                "mode":      "cidr",
                                "group":     link["source_component"],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv6",
                                "prefix":    prefix
                            }
                            interface["rules"].append(rule)
                # internal sources
                else:
                    if "ipv4" in source_network:
                        for port in ports:
                            rule = {
                                "direction": "ingress",
                                "mode":      "group",
                                "group":     link["source_component"] + "/" + link["source_network"].split("/")[-1],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv4",
                                "prefix":    target_network["ipv4"]["cidr"]
                            }
                            interface["rules"].append(rule)
                    if "ipv6" in target_network:
                        for port in ports:
                            rule = {
                                "direction": "egress",
                                "mode":      "group",
                                "group":     link["source_component"] + "/" + link["source_network"].split("/")[-1],
                                "protocol":  port["protocol"],
                                "min":       port["min"],
                                "max":       port["max"],
                                "family":    "IPv6",
                                "prefix":    target_network["ipv6"]["cidr"]
                            }
                            interface["rules"].append(rule)

        # apply component interface rules to node interfaces
        for component in components:
            if component["type"] == "InternalComponent":
                for index, interface in enumerate(component["interfaces"]):
                    for node in component["nodes"]:
                        node["interfaces"][index]["rules"] = interface["rules"]

    # --------------------------------------------------------------------------
    def _get(self,list,fqn):
        for item in list:
            if item["fqn"] == fqn:
                return item
        return None

    # --------------------------------------------------------------------------
    def _set(self,list,new_item):
        name = new_item["name"]

        for index, item in enumerate(list):
            if item["name"] == name:
                list[index] = new_item
                return

        list.append( new_item )

    # --------------------------------------------------------------------------
    def _remove(self,list,name):
        for index, item in enumerate(list):
            if item["name"] == name:
                del list[index]
                return

    # --------------------------------------------------------------------------
    def _replace(self,object1,object2,name):
        if name in object2:
            object1[name] = object2[name]

# ------------------------------------------------------------------------------
