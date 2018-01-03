#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  file:    validator.py
#  Schema:  V0.1.1
#  date:    29.11.2017
#  author:  Bernard Tsai (bernard@tsai.eu)
#  description:
#    This script reads a VNF descriptor from stdin and validates if it
#    complies with a given schema.
# ------------------------------------------------------------------------------

from argparse          import ArgumentParser
from logging           import info, error, basicConfig, ERROR, WARNING, INFO, DEBUG
from ao.model.input    import Input
from ao.model.validate import Validate
from sys               import stderr, exit
from os                import path

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
        prog='validator.py',
        description='Validate a VNF descriptor',
    )

    parser.add_argument('-v', '--verbose', action='count', default=0, help='set logging level: -v, -vv, -vvv')

    args = parser.parse_args()

    # setup logging
    loglevel = args.verbose
    levels   = [ERROR, WARNING, INFO, DEBUG]
    level    = levels[min(len(levels)-1,loglevel)]  # capped to number of levels
    basicConfig(level=level,
                format='%(asctime)-15s %(levelname)5s %(filename)s:%(funcName)s:%(lineno)s %(message)s')

    # setup validator
    module_dir = path.dirname(__file__)
    schema_dir = path.join(module_dir, "..", "data", "schemas")
    validator  = Validate(version=VERSION, directory=schema_dir)

    # retrieve descriptor from stdin
    try:
        reader     = Input()
        descriptor = reader.read()
    except KeyboardInterrupt:
        error("Keyboard interrupt")
        exit( 1 )

    # validate
    issues = validator.validate(descriptor)

    # check for issues
    if issues:
        for issue in issues:
            info(issue)
            print(issue)

        exit( 2 )

# ----- MAIN -------------------------------------------------------------------

if __name__ == '__main__':
    main()
