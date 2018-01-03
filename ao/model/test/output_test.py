#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os              import path
from json            import loads
from ao.model.output import Output
from unittest        import TestCase, expectedFailure
from pytest          import mark

class OutputTest(TestCase):
    @staticmethod
    def parse_text(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}'.format(filename))
        with open(filepath, 'r') as stream:
            return (stream.read())

    def test__01__model__write_1__pass(self):
        # prepare
        txt = OutputTest.parse_text("output.txt")

        # run - test should fail if any exception occurs
        try:
            stream = Output(directory="/tmp")
            stream.write(data=txt)

            directory = stream.getDirectory()
            data      = stream.getData()
            filenames = stream.getFilenames()
            blocks    = stream.getBlocks()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual(directory, "/tmp")
        self.assertIsNotNone(data)
        self.assertIsNotNone(filenames)
        self.assertIsNotNone(blocks)
