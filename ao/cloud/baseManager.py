#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .exceptions import ModuleError

class ChangeSet():
    def __init__(self,create,update,delete,keep):
        self.create = create
        self.update = update
        self.delete = delete
        self.keep   = keep

    def has_changed(self):
        return (len(self.create) + len(self.update) + len(self.delete) > 0)

class BaseManager():
    """Manage lifecycle of entities"""

    def __init__(self, level="default"):
        """Initialize"""
        self.msgs  = []      # log information
        self.level = level   # degree of logging

    def loglevel(self,level):
        """Log message"""
        self.level = level

    def log(self,msg):
        """Log message"""
        line = str(msg)

        if self.level == "debug":
            print(str(line))

        self.msgs.append(line)

    def fail(self,msg):
        """Log failure and raise exception"""
        self.log(msg)
        raise ModuleError(msg)

    def compare(self, current, target):
        """Derive change set based on two lists of entities"""
        create = []
        update = []
        delete = []
        keep   = []

        # determine which entities need to updated/created or kept
        for current_entity in current:
            # try to find corresponding group in target
            found = False
            for target_entity in target:
                if current_entity.name == target_entity.name:
                    found = True
                    if current_entity != target_entity:
                        update.append(target_entity)
                    else:
                        keep.append(current_entity)
                    break

            if not found:
                delete.append(current_entity)

        # determine entities to be added
        for target_entity in target:
            # try to find corresponding group in target
            found = False
            for current_entity in current:
                if current_entity.name == target_entity.name:
                    found = True
                    break
            if not found:
                create.append(target_entity)

        # return change set
        return ChangeSet(create, update, delete, keep)
