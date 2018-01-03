#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os                import path
from yaml              import safe_load
from ao.model.input    import Input
from ao.model.validate import Validate
from ao.model.model    import Model
from ao.model.render   import Render
from ao.model.delta    import Delta
from ao.model.action   import Action
from unittest          import TestCase, expectedFailure
from pytest            import mark

class ModelTest(TestCase):
    @staticmethod
    def parse_yaml(filename):
        filepath = path.join(path.dirname(__file__), 'fixtures/{}.yaml'.format(filename))
        with open(filepath, 'r') as stream:
            return safe_load(stream.read())

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test__01__model__create_model__pass(self):
        # prepare
        clearwater1 = ModelTest.parse_yaml("clearwater1")
        clearwater2 = ModelTest.parse_yaml("clearwater2")

        # determine directories
        root_dir   = path.dirname(__file__)
        schema_dir = path.join( root_dir, "..", "..", "data", "schemas" )
        tmpl_dir   = path.join( root_dir, "..", "..", "data", "templates" )

        # create functions
        validator = Validate(directory=schema_dir)
        renderer  = Render(directory=tmpl_dir)

        # run - test should fail if any exception occurs
        try:
            model = Model( context="test" )

            # apply first change
            validation_results = validator.validate( clearwater1 )

            if validation_results:
                for result in validation_results:
                    print( "  " + result )

            # apply change
            model.set( clearwater1 )

            # render new version of the model
            obj1    = model.getModel()
            result1 = renderer.render( obj1, "canonical" )

            # apply second change
            validation_results = validator.validate( clearwater2 )

            if validation_results:
                for result in validation_results:
                    print( "  " + result )

            # apply change
            model.set( clearwater2 )

            # render new version of the model
            obj2    = model.getModel()
            result2 = renderer.render( obj2, "canonical" )

            # determine difference
            model1 = Model( model=result1 )
            model2 = Model( model=result2 )

            delta = Delta( model1, model2 )

            delta_model  = delta.getModel()
            delta_model1 = delta.getModel1()
            delta_model2 = delta.getModel2()

            txt = renderer.render( delta.model, "delta" )

            print( "----------" )
            print( txt )

            # # derive action plan
            action = Action( delta )
            txt    = renderer.render( action.model, "action" )

            print( "----------" )
            print( txt )

        except Exception as exc:
            self.fail("Failed with {}".format(str(exc)))

        # check
        self.assertIsNotNone( result1 )
        self.assertIsNotNone( result2 )
        self.assertIsNotNone( delta_model  )
        self.assertIsNotNone( delta_model1 )
        self.assertIsNotNone( delta_model2 )
