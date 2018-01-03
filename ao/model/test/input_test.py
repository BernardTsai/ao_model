#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys            import stdin
from os             import path
from json           import loads
from ao.model.input import Input
from unittest       import TestCase, expectedFailure
from pytest         import mark

class InputTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.stdin = stdin

    @classmethod
    def tearDownClass(self):
        stdin = self.stdin

    def test__01__model__read_file_1__pass(self):
        # prepare
        filepath  = path.join(path.dirname(__file__), "fixtures")
        filename  = path.join(filepath, "clearwater1.yaml")

        # run - test should fail if any exception occurs
        try:
            stream = Input(directory=filepath)
            stream.read("clearwater1.yaml")

            directory = stream.getDirectory()
            filename  = stream.getFilename()
            data      = stream.getData()
            obj       = stream.getObject()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual(directory, filepath)
        self.assertEqual(filename,  filename)
        self.assertIsNotNone(data)
        self.assertIsNotNone(obj)

    def test__02__model__read_file_2__pass(self):
        # prepare
        filepath  = path.join(path.dirname(__file__), "fixtures")
        filename  = path.join(filepath, "clearwater1.yaml")

        # run - test should fail if any exception occurs
        try:
            stream = Input()
            stream.read(filename=filename)

            directory = stream.getDirectory()
            filename  = stream.getFilename()
            data      = stream.getData()
            obj       = stream.getObject()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNone(directory)
        self.assertIsNotNone(filename)
        self.assertIsNotNone(data)
        self.assertIsNotNone(obj)
