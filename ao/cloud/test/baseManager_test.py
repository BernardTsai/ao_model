#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pannet.cloud.baseManager import BaseManager
from unittest                   import TestCase, expectedFailure

class BaseManagerTest(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__01__baseManager__init__pass(self):
        # prepare
        pass

        # run - test should fail if any exception occurs
        try:
            manager = BaseManager()
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( manager )

    def test__02__baseManager__loglevel__pass(self):
        # prepare
        pass

        # run - test should fail if any exception occurs
        try:
            manager = BaseManager()

            manager.loglevel("debug")
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( manager.level, "debug" )

    def test__03__baseManager__log__pass(self):
        # prepare
        pass

        # run - test should fail if any exception occurs
        try:
            manager = BaseManager()

            manager.log("test")
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertEqual( manager.msgs, ["test"] )

    @expectedFailure
    def test__04__baseManager__fail__pass(self):
        # prepare
        pass

        # run - test should fail if any exception occurs
        try:
            manager = BaseManager()

            manager.fail("test")
        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))
