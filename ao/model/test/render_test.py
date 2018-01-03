#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os              import path
from yaml            import safe_load
from ao.model.render import Render
from unittest        import TestCase, expectedFailure
from pytest          import mark

class RenderTest(TestCase):
    @staticmethod
    def parse_yaml(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.yaml'.format(filename))
        with open(filepath, 'r') as stream:
            return safe_load(stream.read())

    def test__01__render__pass(self):
        # prepare
        directory = path.join(path.dirname(__file__),"../../data/templates")
        data      = RenderTest.parse_yaml("render")

        # run - test should fail if any exception occurs
        try:
            render = Render(directory=directory)

            dirpath   = render.getDirectory()
            version   = render.getVersion()
            templates = render.getTemplates()
            result = render.render( data=data, template_name="action")
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual(dirpath, directory)
        self.assertIsNotNone(version)
        self.assertIsNotNone(templates)
        self.assertIsNotNone(result)
