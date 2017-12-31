#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import Handler, Formatter

class LogHandler(Handler):
    def __init__(self):
        """Initialize"""
        self.logs = []

    def emit(self, record):
        self.logs.append(record)

class LogFormatter(Formatter):
    def __init__(self, task_name=None):
        """Initialize"""
        self.task_name = task_name

        super(LogFormatter, self).__init__()

    def format(self, record):
        """Construct record"""
        data = {
            "@message":   record.msg,
            "@timestamp": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            '@type':      'PanNet'
        }

        return data
