#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import UnknownEntityError, ParameterError
from ipaddress   import ip_network
from re          import match

class SecurityGroup():
    """SecurityGroup entity"""

    def __init__(self, openstack, entity=None,
        tenant_name  = None,
        cluster_name = None,
        network_name = None,
        rules        = None):
        """Initialize"""
        self.openstack = openstack
        self.type      = "securitygroup"

        # initialize with provided entity
        if entity:
            self.__init_attributes__(entity)

        # initialize via fully qualified name
        elif tenant_name and cluster_name and network_name:
            name  = tenant_name + "_" + cluster_name + "_" + network_name

            self.entity        = None
            self.id            = None
            self.name          = name
            self.state         = "inactive"
            self.tenant_name   = tenant_name
            self.cluster_name  = cluster_name
            self.network_name  = network_name
            self.rules         = rules

        # wrong parameters
        else:
            raise ParameterError("Invalid parameters")

    def __init_attributes__(self, entity):
        """Get attributes"""
        self.entity        = entity
        self.id            = entity.id
        self.name          = entity.name
        self.state         = "active"
        self.tenant_name   = entity.name.split("_",2)[0]
        self.cluster_name  = entity.name.split("_",2)[1]
        self.network_name  = entity.name.split("_",2)[2]
        self.rules         = []
        for rule in entity.security_group_rules:
            if rule["remote_ip_prefix"]:
                target = rule["remote_ip_prefix"]
            else:
                remote_group_id = rule["remote_group_id"]
                remote_group    = self.openstack.network.find_security_group( remote_group_id )
                target          = remote_group.name

            self.rules.append({
                "id":        rule["id"],
                "direction": rule["direction"],
                "protocol":  rule["protocol"],
                "min":       rule["port_range_min"],
                "max":       rule["port_range_max"],
                "target":    target,
                "group":     rule["remote_group_id"],
                "prefix":    rule["remote_ip_prefix"]
            })

    def load(self):
        """Retrieve entity"""

        # load entity via API
        entity = self.find(self.name)

        if not entity:
            raise UnknownEntityError("Invalid {} name: {}".format(self.type, self.name))

        # initialize with provided entity
        self.__init_attributes__(entity)

    def save(self):
        """Persist information"""
        # update an existing entity
        if self.entity:
            # remove existing security group rules
            for rule in self.entity.security_group_rules:
                self.openstack.network.delete_security_group_rule(rule["id"])

            # add required security group rules
            for rule in self.rules:
                self.update_rule(rule)
                self.openstack.network.create_security_group_rule(
                    project_id        = self.entity.project_id,
                    security_group_id = self.id,
                    direction         = rule["direction"],
                    protocol          = rule["protocol"],
                    port_range_min    = rule["min"],
                    port_range_max    = rule["max"],
                    remote_group_id   = rule["group"],
                    remote_ip_prefix  = rule["prefix"]
                )

        # update or create a new securitygroup if it does not exist yet
        else:
            # try to find entity by name
            self.entity = self.find(self.name)

            # create entity if needed
            if not self.entity:
                project_id  = self.openstack.session.get_project_id()
                description = "VNF: {}\nCluster: {}\nNetwork: {}".format(
                    self.tenant_name,
                    self.cluster_name,
                    self.network_name )
                self.entity = self.openstack.network.create_security_group(
                    project_id  = project_id,
                    name        = self.name,
                    description = description)

            # remove default rules
            self.id      = self.entity.id
            self.entity  = self.openstack.network.get_security_group(self.id)
            for rule in self.entity.security_group_rules:
                self.openstack.network.delete_security_group_rule(rule["id"])

            # add required security group rules
            for rule in self.rules:
                self.update_rule(rule)
                self.openstack.network.create_security_group_rule(
                    project_id        = project_id,
                    security_group_id = self.id,
                    direction         = rule["direction"],
                    protocol          = rule["protocol"],
                    port_range_min    = rule["min"],
                    port_range_max    = rule["max"],
                    remote_group_id   = rule["group"],
                    remote_ip_prefix  = rule["prefix"]
                )

            # reload entity
            self.load()

    def delete(self):
        """Remove entity"""
        if self.entity:
            self.openstack.network.delete_security_group(self.id)
            self.entity = None
            self.id     = None

    def find(self,name):
        """Find entity by name"""
        query = {
            "project_id": self.openstack.session.get_project_id()
        }

        for entity in self.openstack.network.security_groups(**query):
            if entity.name == name:
                return entity

        return None

    def attributes(self):
        """Determine attributes as dictionary"""

        # initialize result
        result = {
            "type":          self.type,
            "id":            self.id,
            "name":          self.name,
            "tenant_name":   self.tenant_name,
            "cluster_name":  self.cluster_name,
            "network_name":  self.network_name,
            "rules":         self.rules,
            "state":         self.state }

        return result

    def __eq__(self, other):
        """Compare with another entity"""
        # ToDo: take care of list of rules
        attr1 = self.attributes()
        attr2 = other.attributes()

        # check names
        if attr1["name"] != attr2["name"]:
            return False

        normalize = lambda r: r["direction"]+"-"+r["target"]+"-"+r["protocol"]+"-"+str(r["min"])+"-"+str(r["max"])

        # check rules by normalizing them to a list of sorted strings
        rules1 = list(map(normalize, attr1["rules"]))
        rules2 = list(map(normalize, attr2["rules"]))

        if sorted(rules1) != sorted(rules2):
            return False

        return True

    def update_rule(self, rule):
        """Determine ip prefix or remote group id"""

        # check if rule has been updated already
        if "group" in rule or "prefix" in rule:
            return

        # target can either be a CIDR or a reference to a cluster and network
        rule_target = rule["target"]
        matches     = match( "[a-zA-Z][a-zA-Z0-9_-]*", rule_target )

        # found a cluster name and network name
        if matches and matches.group(0) == rule_target:

            remote_name  = self.tenant_name + "_" + rule_target
            remote_group = self.find(remote_name)

            if not remote_group:
                raise ParameterError("Unknown target: {}".format(remote_name))

            rule["group"]  = remote_group.id
            rule["prefix"] = None

        # check if we have a valid CIDR here
        else:
            try:
                network = ip_network(rule_target)
            except Exception:
                raise ParameterError("Invalid target: {}".format(rule_target))

            rule["group"]  = None
            rule["prefix"] = rule_target

    # --------------------------------------------------------------------------

    @classmethod
    def list(cls, openstack, names=[]):
        """Retrieve entities by name"""
        query = {
            "project_id": openstack.session.get_project_id()
        }

        prefix = "_".join(names)

        entities = []
        for entity in openstack.network.security_groups(**query):
            if entity.name.startswith(prefix):
                entities.append(SecurityGroup(openstack, entity=entity))

        return entities

    # --------------------------------------------------------------------------
