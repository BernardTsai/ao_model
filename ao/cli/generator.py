#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  file:    generator.py
#  Schema:  V0.1.1
#  date:    29.11.2017
#  author:  Bernard Tsai (bernard@tsai.eu)
#  description:
#    This script:
#    - reads a VNF descriptor from stdin
#    - creates an internal model of the VNF
#    - maps the contents of the model into a template and
#    - writes the results to stdout.
# ------------------------------------------------------------------------------

from argparse         import ArgumentParser
from logging          import info, error, basicConfig, ERROR, WARNING, INFO, DEBUG
from ao.model.input   import Input
from ao.model.model   import Model
from ao.model.render  import Render
from sys              import stderr, exit
from os               import path

# ------------------------------------------------------------------------------
# schema version
# ------------------------------------------------------------------------------
VERSION = "V0.1.1"

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
def main():
    # setup command line parser
    parser = ArgumentParser(
        prog='generator.py',
        description='Generate information from a VNF descriptor',
    )

    parser.add_argument('-t', '--template', type=str,  default="canonical", help='name of the template')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='set logging level: -v, -vv, -vvv')

    args = parser.parse_args()

    # setup logging
    loglevel = args.verbose
    levels   = [ERROR, WARNING, INFO, DEBUG]
    level    = levels[min(len(levels)-1,loglevel)]  # capped to number of levels
    basicConfig(level=level,
                format='%(asctime)-15s %(levelname)5s %(filename)s:%(funcName)s:%(lineno)s %(message)s')

    # setup generator
    module_dir = path.dirname(__file__)
    tmpl_dir   = path.join(module_dir, "..", "data", "templates")
    renderer   = Render(version=VERSION, directory=tmpl_dir)

    # retrieve descriptor from stdin
    try:
        reader     = Input()
        descriptor = reader.read()
    except KeyboardInterrupt:
        error("Keyboard interrupt")
        exit( 1 )

    # create internal model
    model = Model()
    model.set(descriptor)
    data = model.getModel()

    # render model
    try:
        template_name = args.template

        result = renderer.render(data=data, template_name=template_name)
    except Exception as exc:
        error("Error while rendering:{}".format(exc))
        exit(2)

    print(result)

# ----- MAIN -------------------------------------------------------------------

if __name__ == '__main__':
    main()
