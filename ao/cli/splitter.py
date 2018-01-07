#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  file:    splitter.py
#  date:    06.01.2018
#  author:  Bernard Tsai (bernard@tsai.eu)
#  description:
#    This script:
#    - reads data from stdin
#    - splits the data into different parts and
#    - writes these parts into different files.
# ------------------------------------------------------------------------------

from argparse         import ArgumentParser
from logging          import info, error, basicConfig, ERROR, WARNING, INFO, DEBUG
from ao.model.input   import Input
from ao.model.output  import Output
from sys              import exit
from os               import getcwd, path

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
def main():
    # setup command line parser
    parser = ArgumentParser(
        prog='splitter.py',
        description='Split input stream and write to different files',
    )

    parser.add_argument('-p', '--path', type=str,  default="", help='path to which the output should be sent')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='set logging level: -v, -vv, -vvv')

    args = parser.parse_args()

    # setup logging
    loglevel = args.verbose
    levels   = [ERROR, WARNING, INFO, DEBUG]
    level    = levels[min(len(levels)-1,loglevel)]  # capped to number of levels
    basicConfig(level=level,
                format='%(asctime)-15s %(levelname)5s %(filename)s:%(funcName)s:%(lineno)s %(message)s')

    # setup splitter
    module_directory_name = path.dirname(__file__)
    output_directory_name = path.join(module_directory_name, args.path)

    current_directory_name = getcwd()
    if args.path == '':
        output_directory_name = current_directory_name
    elif args.path.startswith('/'):
        output_directory_name = args.path
    else:
        output_directory_name = path.join(current_directory_name, args.path)

    # check if the output_directory_name points to a directory
    if not path.isdir(output_directory_name):
        error("Invalid path")
        exit( 1 )

    # retrieve data from stdin
    try:
        reader = Input()
        data   = reader.read(yaml=False)
    except KeyboardInterrupt:
        error("Keyboard interrupt")
        exit( 2 )

    print(data)

    # write data
    try:
        output = Output(directory=output_directory_name)
        output.write(data)
    except Exception as exc:
        error("Unable to write data: {}".format(exc))
        exit( 3 )

# ----- MAIN -------------------------------------------------------------------

if __name__ == '__main__':
    main()
